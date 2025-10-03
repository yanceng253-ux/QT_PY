import sys
import serial
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

class GateControlWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("道闸控制系统")
        self.setGeometry(100, 100, 300, 200)

        # 初始化串口（端口需根据实际情况修改，如Windows为'COM3'，Linux为'/dev/ttyUSB0'）
        self.serial_port = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
        time.sleep(2)  # 等待串口初始化完成

        # 界面组件：按钮与状态标签
        self.open_btn = QPushButton("道闸开启")
        self.close_btn = QPushButton("道闸关闭")
        self.status_label = QLabel("道闸状态：未操作")
        self.status_label.setAlignment(Qt.AlignCenter)

        # 布局管理
        layout = QVBoxLayout()
        layout.addWidget(self.open_btn)
        layout.addWidget(self.close_btn)
        layout.addWidget(self.status_label)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # 绑定按钮点击事件
        self.open_btn.clicked.connect(self.open_gate)
        self.close_btn.clicked.connect(self.close_gate)

    def open_gate(self):
        """道闸开启逻辑：发送指令 + 更新状态"""
        try:
            self.serial_port.write(b'O')  # 发送“开启”指令（字节形式）
            time.sleep(0.5)  # 等待硬件响应
            response = self.serial_port.readline().decode('utf-8').strip()
            if response:
                self.status_label.setText(f"道闸状态：{response}")
            else:
                self.status_label.setText("道闸状态：开启中（无响应）")
        except Exception as e:
            self.status_label.setText(f"错误：{str(e)}")

    def close_gate(self):
        """道闸关闭逻辑：发送指令 + 更新状态"""
        try:
            self.serial_port.write(b'C')  # 发送“关闭”指令
            time.sleep(0.5)
            response = self.serial_port.readline().decode('utf-8').strip()
            if response:
                self.status_label.setText(f"道闸状态：{response}")
            else:
                self.status_label.setText("道闸状态：关闭中（无响应）")
        except Exception as e:
            self.status_label.setText(f"错误：{str(e)}")

    def closeEvent(self, event):
        """窗口关闭时，释放串口资源"""
        if self.serial_port.is_open:
            self.serial_port.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GateControlWindow()
    window.show()
    sys.exit(app.exec_())