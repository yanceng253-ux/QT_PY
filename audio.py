from aip import AipSpeech
from playsound import playsound
import os

# 1. 配置百度API（需替换为你的密钥，在百度智能云控制台获取）
APP_ID = "7100595"
API_KEY = "8cMz4rrGJ7iqMax7CQzfIC40"
SECRET_KEY = "fBRoEZqJRdA5sNDZPXYuUWoFL1xXdRu4"
client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

# 2. 合成语音
text = "你好"
result = client.synthesis(
    text,
    'zh',  # 语言
    1,
    {
        'vol': 5,   # 音量（0~15）
        'spd': 5,   # 语速（0~9）
        'pit': 5,   # 音调（0~9）
        'per': 0   # 语音人：0=女声，1=男声，3=情感女声，4=情感男声
    }
)

# 3. 保存并播放
if not isinstance(result, dict):
    with open("baidu_tts.mp3", "wb") as f:
        f.write(result)
    playsound("baidu_tts.mp3")  # 播放
    os.remove("baidu_tts.mp3")  # 可选：删除临时文件
else:
    print(f"合成失败：{result}")
