import traceback
import sys

try:
    from PyQt5.QtWidgets import QApplication, QMessageBox
    from PyQt5.QtCore import Qt
    
    app = QApplication(sys.argv)
    QMessageBox.information(None, "测试", "PyQt5 可以正常工作!")
    sys.exit(0)
    
except Exception as e:
    print(f"错误: {e}")
    traceback.print_exc()
    input("按回车退出...")
