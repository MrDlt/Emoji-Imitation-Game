import cv2

for i in range(10):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print('Cam found at index: ' + str(i))
        cap.release()