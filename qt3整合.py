import sys
import sqlite3
import serial
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QListWidget, QTabWidget
)
from PyQt5.QtCore import Qt

class IntegratedSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("车牌管理与道闸控制系统")
        self.resize(600, 400)
        
        # 初始化组件
        self.init_ui()
        self.init_database()
        self.init_serial()

    def init_ui(self):
        """初始化界面，使用标签页整合两个功能"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 创建标签页控件
        self.tabs = QTabWidget()
        
        # 创建车牌管理标签页
        self.create_plate_tab()
        
        # 创建道闸控制标签页
        self.create_gate_tab()
        
        # 将标签页添加到主布局
        self.tabs.addTab(self.plate_tab, "车牌信息管理")
        self.tabs.addTab(self.gate_tab, "道闸控制")
        main_layout.addWidget(self.tabs)

    def create_plate_tab(self):
        """创建车牌信息管理标签页内容"""
        self.plate_tab = QWidget()
        plate_layout = QVBoxLayout(self.plate_tab)

        # 车牌录入区域
        input_layout = QHBoxLayout()
        plate_label = QLabel("车牌号码：")
        self.plate_input = QLineEdit()
        self.input_btn = QPushButton("录入")
        self.input_btn.clicked.connect(self.input_plate)

        input_layout.addWidget(plate_label)
        input_layout.addWidget(self.plate_input)
        input_layout.addWidget(self.input_btn)

        # 车牌查看区域
        self.plate_list = QListWidget()
        self.refresh_btn = QPushButton("刷新已录入车牌")
        self.refresh_btn.clicked.connect(self.refresh_plates)

        # 添加到布局
        plate_layout.addLayout(input_layout)
        plate_layout.addWidget(self.plate_list)
        plate_layout.addWidget(self.refresh_btn)

    def create_gate_tab(self):
        """创建道闸控制标签页内容"""
        self.gate_tab = QWidget()
        gate_layout = QVBoxLayout(self.gate_tab)

        # 道闸控制按钮与状态
        self.open_btn = QPushButton("道闸开启")
        self.close_btn = QPushButton("道闸关闭")
        self.status_label = QLabel("道闸状态：未连接")
        self.status_label.setAlignment(Qt.AlignCenter)

        # 绑定事件
        self.open_btn.clicked.connect(self.open_gate)
        self.close_btn.clicked.connect(self.close_gate)

        # 添加到布局
        gate_layout.addWidget(self.open_btn)
        gate_layout.addWidget(self.close_btn)
        gate_layout.addWidget(self.status_label)

    def init_database(self):
        """初始化车牌数据库"""
        try:
            self.conn = sqlite3.connect("plate_database.db")
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS plates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plate_number TEXT UNIQUE
            )
            ''')
            self.conn.commit()
            self.refresh_plates()
        except Exception as e:
            print(f"数据库初始化错误：{str(e)}")

    def init_serial(self):
        """初始化串口连接"""
        try:
            # 注意：根据实际设备修改串口名称
            self.serial_port = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
            time.sleep(2)  # 等待串口初始化
            self.status_label.setText("道闸状态：已连接")
        except Exception as e:
            self.status_label.setText(f"道闸状态：串口连接失败 - {str(e)}")
            print(f"串口初始化错误：{str(e)}")

    def input_plate(self):
        """处理车牌录入"""
        plate = self.plate_input.text().strip()
        if not plate:
            print("请输入有效车牌！")
            return

        try:
            self.cursor.execute(
                "INSERT INTO plates (plate_number) VALUES (?)", 
                (plate,)
            )
            self.conn.commit()
            self.plate_input.clear()
            self.refresh_plates()
            print(f"成功录入车牌：{plate}")
        except sqlite3.IntegrityError:
            print(f"错误：车牌 {plate} 已存在！")
        except Exception as e:
            print(f"录入失败：{str(e)}")

    def refresh_plates(self):
        """刷新车牌列表"""
        try:
            self.plate_list.clear()
            self.cursor.execute("SELECT plate_number FROM plates")
            plates = self.cursor.fetchall()
            for plate in plates:
                self.plate_list.addItem(plate[0])
        except Exception as e:
            print(f"刷新失败：{str(e)}")

    def open_gate(self):
        """开启道闸"""
        try:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.write(b'O')
                time.sleep(0.5)
                response = self.serial_port.readline().decode('utf-8').strip()
                self.status_label.setText(f"道闸状态：{response if response else '开启中'}")
            else:
                self.status_label.setText("道闸状态：串口未连接")
        except Exception as e:
            self.status_label.setText(f"错误：{str(e)}")

    def close_gate(self):
        """关闭道闸"""
        try:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.write(b'C')
                time.sleep(0.5)
                response = self.serial_port.readline().decode('utf-8').strip()
                self.status_label.setText(f"道闸状态：{response if response else '关闭中'}")
            else:
                self.status_label.setText("道闸状态：串口未连接")
        except Exception as e:
            self.status_label.setText(f"错误：{str(e)}")

    def closeEvent(self, event):
        """关闭窗口时释放资源"""
        # 关闭数据库连接
        if hasattr(self, 'conn'):
            self.conn.close()
        # 关闭串口
        if hasattr(self, 'serial_port') and self.serial_port.is_open:
            self.serial_port.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IntegratedSystem()
    window.show()
    sys.exit(app.exec_())
