import os

from PyQt5.QtCore import QThread, pyqtSignal
from playsound import playsound

import Config


class TTSWorker(QThread):
    """
    用于处理语音合成(TTS)和播放的后台线程。
    """
    # 定义信号：任务成功完成时发射
    finished = pyqtSignal()
    # 定义信号：任务出错时发射，附带错误信息
    error_occurred = pyqtSignal(str)

    def __init__(self, text_to_speak):
        super().__init__()
        self.text = text_to_speak

    def run(self):
        """线程的主执行函数，包含所有耗时操作"""
        try:
            # 1. 调用百度API进行语音合成 (这是一个网络请求，耗时)
            result = Config.client.synthesis(
                self.text,
                'zh',
                1,
                {
                    'vol': 5,
                    'spd': 5,
                    'pit': 5,
                    'per': 0
                }
            )

            # 2. 处理合成结果
            if not isinstance(result, dict):
                # 3. 保存音频文件
                with open("baidu_tts.mp3", "wb") as f:
                    f.write(result)

                # 4. 播放音频文件 (这也是一个I/O操作，也会耗时)
                playsound("baidu_tts.mp3")

                # 5. 删除临时文件
                try:
                    os.remove("baidu_tts.mp3")
                except Exception as e:
                    print(f"删除临时文件失败: {e}")

                # 6. 任务成功，发射 finished 信号
                self.finished.emit()
            else:
                # 如果合成失败，发射 error_occurred 信号
                error_msg = f"合成失败：{result}"
                self.error_occurred.emit(error_msg)

        except Exception as e:
            # 捕获其他任何可能的异常
            self.error_occurred.emit(f"发生未知错误: {e}")