using System.Net.Sockets;
using System.Text;
using UnityEngine;
using UnityEngine.UI;
using System.Diagnostics;
using System.Collections;


public class SocketClient : MonoBehaviour
{
    Process pythonProcess;

    private TcpClient client;
    private NetworkStream stream;
    private byte[] dataBuffer = new byte[1024];

    public Sprite[] emojiSprites; // 存储七个Emoji图像
    public Image emojiImage; // 需要显示Emoji的Image组件

    public int randomIndex = -1;

    private int currentCamIndex = 6;   # Modify: Virtual Camera Index On your PC.

    public RawImage rawImage; // 用于显示摄像头画面的 RawImage

    private WebCamTexture webcamTexture; // 摄像头纹理

    public Text uiText; // UI 文本元素用于显示文字

    public Text MyText; // UI 文本元素用于显示文字

    public Text SuccessText; // UI 文本元素用于显示文字

    public Text ScoreText; // UI 文本元素用于显示文字

    public GameObject firework;  // 需要显示的prefab


    public int score = 0;


    // public Text successText;

    private string[] EmotionsLabel = { "Surprised", "Scared", "Disgusted", "Happy", "Sad", "Angry", "Neutral" };

    public void DisplayRandomEmoji()
    {
        randomIndex = Random.Range(0, emojiSprites.Length);
        emojiImage.sprite = emojiSprites[randomIndex];
        //return randomIndex;
        //emojiText.text = "Random Emoji Index: " + randomIndex;
    }

    void Start()
    {

        firework.SetActive(false); // 隐藏Prefab

        // 连接到服务器
        // 启动 Python 服务器
        pythonProcess = new Process();
        pythonProcess.StartInfo.FileName = "D:/Anaconda/python.exe"; //Modify: Path to your Python interpreter.
        pythonProcess.StartInfo.Arguments = "D:backend.py"; //Modify: Path to the Python script on your PC.
        pythonProcess.Start();

        WebCamDevice device = WebCamTexture.devices[currentCamIndex];
        
        int width = 1920;
        int height =1080;

        webcamTexture = new WebCamTexture(device.name,width,height,24);

        // 将摄像头纹理赋值给 RawImage 组件的纹理属性
        rawImage.texture = webcamTexture;

        // 开始播放摄像头画面
        webcamTexture.Play();

        client = new TcpClient("127.0.0.1", 55555);
        stream = client.GetStream();
        
        string message = "Hello from Unity!";
        byte[] data = Encoding.UTF8.GetBytes(message);
        stream.Write(data, 0, data.Length);

        DisplayRandomEmoji();
        uiText.text = EmotionsLabel[randomIndex];
        uiText.color = Color.yellow;

        MyText.text = "None";
        MyText.color = Color.red;

        SuccessText.text = "";
        SuccessText.color = Color.blue;

        ScoreText.text = "Score: "+score;
        ScoreText.color = Color.green;



    }

    public void OnButtonClick()
    {
        DisplayRandomEmoji();
        uiText.text = EmotionsLabel[randomIndex];
    }

    void Update()
    {
        // 接收服务器发送的数据
        if (stream.DataAvailable)
        {
            int bytesRead = stream.Read(dataBuffer, 0, dataBuffer.Length);
            string response = Encoding.UTF8.GetString(dataBuffer, 0, bytesRead);

            // 分割接收到的数据，以换行符为分隔符
            string[] responses = response.Split('\n');

            // 遍历分割后的数据，输出每个数字
            foreach (string r in responses)
            {
                if (!string.IsNullOrEmpty(r))
                {
                    //if(int.Parse())
                    // 输出接收到的数字
                    //int.TryParse(r, out receivedNumber);

                    //UnityEngine.Debug.Log("Received: " + r);
                    MyText.text = "My"+"\u00A0"+"Expression:"+EmotionsLabel[int.Parse(r)];

                    if(randomIndex == int.Parse(r))
                    {
                        //UnityEngine.Debug.Log("Success!");

                        score++;
                        ScoreText.text = "Score: "+score;

                        StartCoroutine(DisplayTextForDuration());

                        // successText.text = "Correct!";

                        // yield return new WaitForSeconds(3f); // 等待至少3秒

                        DisplayRandomEmoji();
                        uiText.text = EmotionsLabel[randomIndex];
                        
                    }
                    // else successText.text = "";

                    //判断数字是否与图片索引相等，若相等，调用DisplayRandomEmoji()

                }
            }
        }

        // 如果摄像头纹理存在但尚未播放，则开始播放
        if (webcamTexture != null && !webcamTexture.isPlaying)
        {
            webcamTexture.Play();
        }
    }

    private IEnumerator DisplayTextForDuration()
    {
        // 设置文本内容并显示
        SuccessText.text = "Success!";

        

        firework.SetActive(true); // 显示Prefab

        // 等待指定时间
        yield return new WaitForSeconds(3f);

        firework.SetActive(false); // 隐藏Prefab

        // 隐藏文本
        SuccessText.text = "";

        //ContinueWithOtherFunctions();
    }

    void OnApplicationQuit()
    {
        //关闭连接
        stream.Close();
        client.Close();

        // 当脚本销毁时停止摄像头画面的播放
        if (webcamTexture != null)
        {
            webcamTexture.Stop();
        }

        // 当 Unity 客户端关闭时，结束 Python 服务器进程
        if (!pythonProcess.HasExited)
        {
            pythonProcess.Kill();
        }

    }
}
