using UnityEngine;
using UnityEngine.UI;

public class RandomEmojiDisplay : MonoBehaviour
{
    public Sprite[] emojiSprites; // 存储七个Emoji图像
    public Image emojiImage; // 需要显示Emoji的Image组件

    //private int lastReceivedIndex = -1; // 上次接收到的数字索引

    //private bool isButtonClicked = false;

    // 方法在按钮点击后调用
    // public void BottonClicked()
    // {
    //     //isButtonClicked = true;
    //     DisplayRandomEmoji();
    // }

    private void Start()
    {
        DisplayRandomEmoji();
    }

    public void DisplayRandomEmoji()
    {
        int randomIndex = Random.Range(0, emojiSprites.Length);
        emojiImage.sprite = emojiSprites[randomIndex];
        //return randomIndex;
    }

    // private void DisplayRandomEmoji()
    // {
    //     int randomIndex;
    //     do
    //     {
    //         randomIndex = Random.Range(0, emojiSprites.Length);
            
    //     }
    //     while (randomIndex == lastReceivedIndex); // 如果随机索引与上次接收到的索引相等，则重新生成随机索引

    //     emojiImage.sprite = emojiSprites[randomIndex];

    // }

    // // 接收到数字后调用此方法，并传入数字索引
    // public void OnReceivedNumber(int receivedIndex)
    // {
    //     UnityEngine.Debug.Log("Received: " + receivedIndex);
    //     lastReceivedIndex = receivedIndex;
    //     DisplayRandomEmoji(); // 更换下一张图片
    // }

}

