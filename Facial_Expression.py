import numpy as np
import cv2
import os
import onnxruntime
import socket
import datetime

def area_of(left_top, right_bottom):
    """Compute the areas of rectangles given two corners.

    Args:
        left_top (N, 2): left top corner.
        right_bottom (N, 2): right bottom corner.

    Returns:
        area (N): return the area.
    """
    hw = np.clip(right_bottom - left_top, 0.0, None)
    return hw[..., 0] * hw[..., 1]


def iou_of(boxes0, boxes1, eps=1e-5):
    """Return intersection-over-union (Jaccard index) of boxes.

    Args:
        boxes0 (N, 4): ground truth boxes.
        boxes1 (N or 1, 4): predicted boxes.
        eps: a small number to avoid 0 as denominator.
    Returns:
        iou (N): IoU values.
    """
    overlap_left_top = np.maximum(boxes0[..., :2], boxes1[..., :2])
    overlap_right_bottom = np.minimum(boxes0[..., 2:], boxes1[..., 2:])

    overlap_area = area_of(overlap_left_top, overlap_right_bottom)
    area0 = area_of(boxes0[..., :2], boxes0[..., 2:])
    area1 = area_of(boxes1[..., :2], boxes1[..., 2:])
    return overlap_area / (area0 + area1 - overlap_area + eps)

def hard_nms(box_scores, iou_threshold, top_k=-1, candidate_size=200):
    """

    Args:
        box_scores (N, 5): boxes in corner-form and probabilities.
        iou_threshold: intersection over union threshold.
        top_k: keep top_k results. If k <= 0, keep all the results.
        candidate_size: only consider the candidates with the highest scores.
    Returns:
         picked: a list of indexes of the kept boxes
    """
    scores = box_scores[:, -1]
    boxes = box_scores[:, :-1]
    picked = []
    # _, indexes = scores.sort(descending=True)
    indexes = np.argsort(scores)
    # indexes = indexes[:candidate_size]
    indexes = indexes[-candidate_size:]
    while len(indexes) > 0:
        # current = indexes[0]
        current = indexes[-1]
        picked.append(current)
        if 0 < top_k == len(picked) or len(indexes) == 1:
            break
        current_box = boxes[current, :]
        # indexes = indexes[1:]
        indexes = indexes[:-1]
        rest_boxes = boxes[indexes, :]
        iou = iou_of(
            rest_boxes,
            np.expand_dims(current_box, axis=0),
        )
        indexes = indexes[iou <= iou_threshold]

    return box_scores[picked, :]


def predict(width, height, confidences, boxes, prob_threshold, iou_threshold=0.3, top_k=-1):
    boxes = boxes[0]
    confidences = confidences[0]
    picked_box_probs = []
    for class_index in range(1, confidences.shape[1]):
        probs = confidences[:, class_index]
        mask = probs > prob_threshold
        probs = probs[mask]
        if probs.shape[0] == 0:
            continue
        subset_boxes = boxes[mask, :]
        box_probs = np.concatenate([subset_boxes, probs.reshape(-1, 1)], axis=1)
        box_probs = hard_nms(box_probs,
                                       iou_threshold=iou_threshold,
                                       top_k=top_k,
                                       )
        picked_box_probs.append(box_probs)
    if not picked_box_probs:
        return np.array([]), np.array([]), np.array([])
    picked_box_probs = np.concatenate(picked_box_probs)
    picked_box_probs[:, 0] *= width
    picked_box_probs[:, 1] *= height
    picked_box_probs[:, 2] *= width
    picked_box_probs[:, 3] *= height
    return picked_box_probs[:, :4].astype(np.int32)

def fd_preprocess(orig_image):
    image = cv2.resize(orig_image, (320, 240))
    image_mean = np.array([127, 127, 127])
    image = (image - image_mean) / 128
    image = np.transpose(image, [2, 0, 1])
    image = np.expand_dims(image, axis=0)
    image = image.astype(np.float32)

    return image


class Model():
    def __init__(self):
        self.labels = ['surprised', 'fearful', 'disgusted', 'happy', 'sad', 'angry','neutral']
        self.ort_session = onnxruntime.InferenceSession("C:models/face_emotions_model.onnx")    # Modify: Path to your facial expression recognition(FER) model.  
        self.ort_detector = onnxruntime.InferenceSession("D:models/version-RFB-320.onnx")    # Modify: Path to your face detection model.
        #self.timer = Timer()
    
    def detect(self, img0, threshold=0.7):
        img0 = np.array(img0)
        image = fd_preprocess(img0)
        in_name = self.ort_detector.get_inputs()[0].name

        # timer = Timer()
        # timer.start()
        confidences, boxes = self.ort_detector.run(None, {in_name: image})
        # print("Face Detector inference time: ", timer.end())

        boxes = predict(img0.shape[1], img0.shape[0], confidences, boxes, threshold)
        face = []
        if boxes is None or len(boxes) == 0:
            return face
        
        for i in range(boxes.shape[0]):
            box = boxes[i, :]
            face.append([box[0],box[1],box[2]-box[0],box[3]-box[1]])
        return face

    def fer(self, img0):
        faces = self.detect(img0)

        if len(faces) == 0:
            return -1,faces

        ##  single face detection
        x, y, w, h = faces[0]

        
        img = img0[y:y+h, x:x+w]
        img = cv2.resize(img,(224, 224))
        img = np.array(img).astype(np.float32)

        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        img /= 255.0  # 将像素值归一化到 [0, 1]
        img -= mean  # 减去均值
        img /= std   # 除以标准差

        img = np.transpose(img, (2, 0, 1))
        img = np.expand_dims(img, axis=0)

        input_name = self.ort_session.get_inputs()[0].name
        output_name = self.ort_session.get_outputs()[0].name

        # timer = Timer()
        # timer.start()
        out = self.ort_session.run([output_name], {input_name: img})
        # print("FER Model inference time: ", timer.end())

        pred = np.argmax(out)
        index = int(pred)
        #label = self.labels[index]
        return index, faces[0]
