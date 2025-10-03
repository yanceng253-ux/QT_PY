import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import Qt

class BlackRedTextDisplay(QWidget):
    
    def __init__(self, title_text="默认标题"):  # 增加标题文字传入参数
        super().__init__()

        # 窗口基本设置
        self.setWindowTitle("OLED显示模拟")
        self.setFixedSize(1000, 700)  # 大尺寸显示框（1000x700）
        
        # 设置黑底红字样式
        self.set_black_red_style()
        
        # 存储显示的标签对象（方便后续更新）
        self.title_label = None
        
        # 创建布局和显示内容（传入初始标题）
        self.init_ui(title_text)

    def set_black_red_style(self):
        """设置黑底红字的整体样式"""
        # 窗口背景色：纯黑
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(0, 0, 0))  # 黑色背景
        self.setPalette(palette)
        
        # 确保背景色生效
        self.setAutoFillBackground(True)

    def init_ui(self, title_text):
        """初始化界面元素，添加汉字显示"""
        # 创建垂直布局（方便内容居中）
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)  # 布局内元素居中
        self.setLayout(layout)
        
        # 1. 大标题（大号汉字）
        self.title_label = QLabel(title_text)  # 使用传入的文字
        title_font = QFont("SimHei", 48, QFont.Bold)  # 黑体，48号，加粗
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("color: rgb(255, 50, 50);")  # 红色文字
        self.title_label.setAlignment(Qt.AlignCenter)  # 文字居中
        layout.addWidget(self.title_label)

    def update_title(self, new_text):
        """提供更新标题的接口方法"""
        if self.title_label:
            self.title_label.setText(new_text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # 确保中文显示正常
    font = QFont("SimHei")
    app.setFont(font)
    wc="欢迎您"
    # 1. 实例化时直接传入显示内容（例如：传入"寒函数传参示例"）
    window = BlackRedTextDisplay(title_text="鲁J1234567"+wc)
    
    # # 2. 也可以后续通过接口动态更新（示例：2秒后更新为新内容）
    # from PyQt5.QtCore import QTimer
    # timer = QTimer()
    # timer.singleShot(2000, lambda: window.update_title("动态更新的文字内容"))  # 2秒后执行
    
    window.show()
    sys.exit(app.exec_())
