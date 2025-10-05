import base64

import cv2
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage


class VideoCaptureWorker(QThread):
    """
    一个后台线程，用于使用 OpenCV 捕获视频帧。
    捕获到的帧通过信号发送给主线程。
    """
    # 定义一个信号，用于发送 QImage 格式的帧
    frame_ready_signal = pyqtSignal(QImage)

    def __init__(self, camera_index=0):
        super().__init__()
        self.camera_index = camera_index
        self.running = False
        self.cap = None
        self._frame = None

    def run(self):
        """线程的主执行函数"""
        self.running = True
        self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)  # 使用 CAP_DSHOW 可以解决某些 Windows 下的问题

        if not self.cap.isOpened():
            print("Error: Could not open camera.")
            self.running = False

        while self.running:
            ret, frame = self.cap.read()
            if ret:
                # --- 格式转换: OpenCV Mat -> QImage ---
                # 1. BGR -> RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self._frame = rgb_frame

                # 2. 将 numpy 数组转换为 QImage
                # 参数: (宽度, 高度, 字节数/行, 格式)
                height, width, channels = rgb_frame.shape
                bytes_per_line = channels * width
                q_image = QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)

                # 3. 发送信号
                self.frame_ready_signal.emit(q_image.copy())

        # 清理工作
        if self.cap:
            self.cap.release()

    def stop(self):
        """停止线程"""
        self.running = False
        self.wait()  # 等待线程完全结束

    def get_current_frame(self):
        """
        返回当前视频帧的一个副本（numpy.ndarray）。
        如果没有可用帧，则返回 None。
        """
        if self._frame:
            image_base64 = base64.b64encode(self._frame.read()).decode("utf-8")
            return image_base64