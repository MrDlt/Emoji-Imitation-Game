using UnityEngine;
using UnityEngine.UI;

public class TextScript : MonoBehaviour
{
    public Text uiText;
    public int score=0;

    

    void Start()
    {
        uiText.text = "Hello, world!";
    }

    void Update()
    {
        // 更新文本内容
        uiText.text = "Score: " + score;
        score++;
    }
}