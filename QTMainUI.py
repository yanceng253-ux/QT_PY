import base64
import os
import sqlite3
import serial
import time

from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QListWidget, QTabWidget
)
from PyQt5.QtCore import Qt, QDateTime, QTimer
from playsound import playsound

import Config
import demo5
from TTSWorker import TTSWorker
from VideoCaptureWorker import VideoCaptureWorker


class QTMainUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title_label = None
        self.tabs = None

        self.setWindowTitle("车牌管理与道闸控制系统")
        self.resize(1366, 720)

        self.worker = VideoCaptureWorker()
        self.tts_worker = None

        # 初始化组件
        self.init_ui()

        self.init_database()
        self.init_serial()

    def init_ui(self):
        self.init_camera()
        """初始化界面，使用标签页整合两个功能"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 创建标签页控件
        self.tabs = QTabWidget()

        # 将标签页添加到主布局
        self.tabs.addTab(self.cameraTab(), "摄像头识别与oled显示模拟")
        self.tabs.addTab(self.create_plate_tab(), "车牌信息管理")
        self.tabs.addTab(self.create_gate_tab(), "道闸控制")
        main_layout.addWidget(self.tabs)

    def init_camera(self):
        # --- UI 控件 ---
        self.video_label = QLabel("Camera feed will appear here...")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setFixedSize(640, 480)
        self.start_button = QPushButton("Start Camera")
        self.stop_button = QPushButton("Stop Camera")
        self.capture_button = QPushButton("Capture Image (OpenCV)")
        self.stop_button.setEnabled(False)
        self.capture_button.setEnabled(False)

        self.start_button.clicked.connect(self.start_camera)
        self.stop_button.clicked.connect(self.stop_camera)
        self.capture_button.clicked.connect(self.capture_image)
        self.worker.frame_ready_signal.connect(self.update_video_label)

    def cameraTab(self):
        camera_tab = QWidget()
        # --- 布局 ---
        video_layout = QHBoxLayout()
        video_layout.addWidget(self.video_label)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.capture_button)

        # 1. 大标题（大号汉字）
        self.title_label = QLabel("default")  # 使用传入的文字
        title_font = QFont("SimHei", 48, QFont.Bold)  # 黑体，48号，加粗
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #d0d0d0;color: rgb(255, 50, 50);")  # 灰色背景和边框红色文字
        self.title_label.setAlignment(Qt.AlignCenter)  # 文字居中

        video_layout.addWidget(self.title_label)

        main_layout = QVBoxLayout()
        main_layout.addLayout(video_layout)
        main_layout.addLayout(button_layout)

        camera_tab.setLayout(main_layout)

        return camera_tab


    def update_title(self, new_text):
        """提供更新标题的接口方法"""
        if self.title_label:
            self.title_label.setText(new_text)

    def capture_image(self):
        """
        通过调用 worker 的方法获取当前帧（numpy.ndarray），然后使用 OpenCV 保存。
        """
        # 1. 从 worker 线程安全地获取当前帧 (numpy.ndarray)
        # frame_to_save = self.worker.get_current_frame()
        #
        # if frame_to_save is not None:
        #     print(frame_to_save)
        with open(r"E:\云盘同步\竞赛\小金砖\QT_PY\1.png",'rb') as f:
            frame = base64.b64encode(f.read()).decode("utf-8")
            # frame = self.worker.get_current_frame()
            if not frame:
                print("未获取到有效图片，程序终止")
                return
            access_token = demo5.get_baidu_access_token()
            plate_number = demo5.recognize_plate(access_token, frame)
            if plate_number:
                print(f"\n最终识别结果：车牌号 = {plate_number}")
                self.compareAllPlate(plate_number)

            else:
                print("\n未成功识别车牌号")

    def compareAllPlate(self,plate):
        plate_list = self.readAllPlateInDataBase()
        if plate in plate_list:
            if plate in Config.carIsIn.keys():
                text = plate + ",停车"+str(int(time.time()-Config.carIsIn[plate])/10)+"秒"
                Config.carIsIn.pop(plate)
            else:
                Config.carIsIn.update({plate:time.time()})
                text = plate+",通行"
            self.on_recognition_success()
        else:
            text = plate+",禁行"
        if text:
            self.update_title(text)
            self.tts_worker = TTSWorker(text)
            self.tts_worker.finished.connect(self.on_tts_finished)
            self.tts_worker.error_occurred.connect(self.on_tts_error)
            self.tts_worker.start()
            self.capture_button.setEnabled(False)

    def on_recognition_success(self):
        print("道闸开启")
        self.open_gate()
        def close():
            print("道闸关闭")
            self.close_gate()
        QTimer.singleShot(10000, close)


    def readAllPlateInDataBase(self):
        """
        从数据库读取所有车牌号，返回一个字符串列表。
        """
        try:
            # 1. 执行 SQL 查询
            self.cursor.execute("SELECT plate_number FROM plates ORDER BY id")

            # 2. 获取所有结果 (结果是一个元组列表，例如 [('粤A12345',), ('京B54321',)])
            results = self.cursor.fetchall()

            # 3. 将元组列表转换为字符串列表
            plate_list = [row[0] for row in results]

            return plate_list

        except sqlite3.Error as e:
            print(f"数据库读取失败: {e}")
            return []

    def start_camera(self):
        """启动摄像头"""
        self.worker.start()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.capture_button.setEnabled(True)
        self.video_label.setText("Starting camera...")

    def stop_camera(self):
        """停止摄像头"""
        self.worker.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.capture_button.setEnabled(False)
        self.video_label.setText("Camera stopped. Click 'Start Camera' to begin.")

    def update_video_label(self, q_image):
        """槽函数：更新视频显示标签"""
        # 将 QImage 转换为 QPixmap 并缩放以适应标签
        # 使用 scaled 方法可以保持 aspect ratio
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.video_label.setPixmap(scaled_pixmap)

    def closeEvent(self, event):
        """窗口关闭时，确保线程被正确停止"""
        if self.worker.isRunning():
            self.worker.stop()
        # 关闭数据库连接
        if hasattr(self, 'conn'):
            self.conn.close()
        # 关闭串口
        if hasattr(self, 'serial_port') and self.serial_port.is_open:
            self.serial_port.close()
        if self.tts_worker and self.tts_worker.isRunning():
            self.tts_worker.quit()  # 请求线程退出
            self.tts_worker.wait()  # 等待线程完全结束
        event.accept()


    def create_plate_tab(self):
        """创建车牌信息管理标签页内容"""
        plate_tab = QWidget()
        plate_layout = QVBoxLayout(plate_tab)

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
        return plate_tab

    def create_gate_tab(self):
        """创建道闸控制标签页内容"""
        gate_tab = QWidget()
        gate_layout = QVBoxLayout(gate_tab)

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
        return gate_tab

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

    def on_tts_finished(self):
        """语音合成成功完成后的处理"""
        self.capture_button.setEnabled(True)  # 重新启用按钮

    def on_tts_error(self, error_message):
        """语音合成出错后的处理"""
        self.capture_button.setEnabled(True)  # 重新启用按钮

























