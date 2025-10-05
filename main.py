import os
plugin_path = r'D:\.conda\envs\xjz\Lib\site-packages\PyQt5\Qt5\plugins'
os.environ['QT_PLUGIN_PATH'] = plugin_path
import sys

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication

from QTMainUI import QTMainUI


def main():
    app = QApplication(sys.argv)
    font = QFont("SimHei")
    app.setFont(font)
    window = QTMainUI()

    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()