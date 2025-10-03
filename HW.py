import sys, serial, serial.tools.list_ports
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget,
                             QHBoxLayout, QPushButton, QComboBox, QLabel)


class ServoWidget(QWidget):
    def __init__(self):
        super().__init__()

        # 串口选择
        self.port_cb = QComboBox()
        self.port_cb.addItems([p.device for p in serial.tools.list_ports.comports()])

        # 两个角度按钮
        self.btn90 = QPushButton("90°")
        self.btn180 = QPushButton("180°")
        self.btn90.setEnabled(False)
        self.btn180.setEnabled(False)
        self.btn90.clicked.connect(lambda: self.send_angle(90))
        self.btn180.clicked.connect(lambda: self.send_angle(180))

        # 打开/关闭串口
        self.open_btn = QPushButton("打开串口")
        self.open_btn.setCheckable(True)
        self.open_btn.toggled.connect(self.toggle_serial)

        # 布局
        top = QHBoxLayout()
        top.addWidget(QLabel("串口:"))
        top.addWidget(self.port_cb)
        top.addWidget(self.open_btn)

        row = QHBoxLayout()
        row.addWidget(self.btn90)
        row.addWidget(self.btn180)

        main = QHBoxLayout(self)
        main.addLayout(top)
        main.addLayout(row)

        self.ser = None

    # ---------- 串口开关 ----------
    def toggle_serial(self, checked):
        if checked:
            try:
                self.ser = serial.Serial(self.port_cb.currentText(), 115200, timeout=0.2)
                self.btn90.setEnabled(True)
                self.btn180.setEnabled(True)
                self.open_btn.setText("关闭串口")
            except Exception as e:
                print("串口打开失败:", e)
                self.open_btn.setChecked(False)
        else:
            if self.ser and self.ser.is_open:
                self.ser.close()
            self.ser = None
            self.btn90.setEnabled(False)
            self.btn180.setEnabled(False)
            self.open_btn.setText("打开串口")

    # ---------- 发送角度 ----------
    def send_angle(self, ang):
        if self.ser and self.ser.is_open:
            self.ser.write(f"{ang}\n".encode())

# -------------------- 主窗口 --------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("舵机 90°/180° 控制")
        self.setCentralWidget(ServoWidget())
        self.resize(300, 60)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())