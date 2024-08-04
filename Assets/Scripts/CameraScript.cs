using UnityEngine;
using UnityEngine.UI;

public class CameraScript : MonoBehaviour
{
    private int currentCamIndex = 6;

    public RawImage rawImage; // 用于显示摄像头画面的 RawImage

    private WebCamTexture webcamTexture; // 摄像头纹理

    void Start()
    {

        WebCamDevice device = WebCamTexture.devices[currentCamIndex];
        
        int width = 1920;
        int height =1080;

        webcamTexture = new WebCamTexture(device.name,width,height,24);

        // 将摄像头纹理赋值给 RawImage 组件的纹理属性
        rawImage.texture = webcamTexture;

        // 开始播放摄像头画面
        webcamTexture.Play();
        
    }

    void Update()
    {
        // 如果摄像头纹理存在但尚未播放，则开始播放
        if (webcamTexture != null && !webcamTexture.isPlaying)
        {
            webcamTexture.Play();
        }
    }

    void OnDestroy()
    {
        // 当脚本销毁时停止摄像头画面的播放
        if (webcamTexture != null)
        {
            webcamTexture.Stop();
        }
    }
}

