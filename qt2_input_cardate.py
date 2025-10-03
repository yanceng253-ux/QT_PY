import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QListWidget
)
from PyQt5.QtCore import Qt

class PlateInfoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("车牌信息录入与查看")
        self.resize(400, 300)
        self.init_ui()      # 初始化界面
        self.init_database()# 初始化数据库

    def init_ui(self):
        # 中央部件（承载所有UI元素）
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局（垂直）
        main_layout = QVBoxLayout(central_widget)

        # -------- 车牌录入区域 --------
        input_layout = QHBoxLayout()
        plate_label = QLabel("车牌号码：")
        self.plate_input = QLineEdit()  # 车牌输入框
        self.input_btn = QPushButton("录入")
        self.input_btn.clicked.connect(self.input_plate)  # 绑定录入按钮事件

        input_layout.addWidget(plate_label)
        input_layout.addWidget(self.plate_input)
        input_layout.addWidget(self.input_btn)

        # -------- 车牌查看区域 --------
        self.plate_list = QListWidget()  # 显示已录入车牌的列表
        self.refresh_btn = QPushButton("刷新已录入车牌")
        self.refresh_btn.clicked.connect(self.refresh_plates)  # 绑定刷新按钮事件

        # 将子布局/部件加入主布局
        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.plate_list)
        main_layout.addWidget(self.refresh_btn)

    def init_database(self):
        # 连接（或创建）SQLite数据库文件
        self.conn = sqlite3.connect("plate_database.db")
        self.cursor = self.conn.cursor()
        # 创建“车牌表”（若不存在），确保车牌唯一性（UNIQUE约束）
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS plates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plate_number TEXT UNIQUE
        )
        ''')
        self.conn.commit()  # 提交建表操作
        self.refresh_plates()  # 初始化时刷新列表

    def input_plate(self):
        """处理“录入车牌”逻辑"""
        plate = self.plate_input.text().strip()  # 获取并清理输入的车牌
        if not plate:
            print("请输入有效车牌！")
            return

        try:
            # 向数据库插入车牌（UNIQUE约束会自动拦截重复值）
            self.cursor.execute(
                "INSERT INTO plates (plate_number) VALUES (?)", 
                (plate,)
            )
            self.conn.commit()  # 提交事务
            self.plate_input.clear()  # 清空输入框
            self.refresh_plates()  # 刷新列表，显示新录入的车牌
            print(f"成功录入车牌：{plate}")
        except sqlite3.IntegrityError:
            # 捕获“重复车牌”的异常
            print(f"错误：车牌 {plate} 已存在！")

    def refresh_plates(self):
        """从数据库读取所有车牌，更新列表显示"""
        self.plate_list.clear()  # 清空现有列表
        # 查询所有车牌
        self.cursor.execute("SELECT plate_number FROM plates")
        plates = self.cursor.fetchall()
        # 将查询结果加入列表组件
        for plate in plates:
            self.plate_list.addItem(plate[0])

    def closeEvent(self, event):
        """窗口关闭时，关闭数据库连接（释放资源）"""
        if hasattr(self, 'conn'):
            self.conn.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PlateInfoWindow()
    window.show()
    sys.exit(app.exec_())