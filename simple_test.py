#!/usr/bin/env python3
import sys
import traceback

try:
    from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QGroupBox, QGridLayout, QLineEdit, QComboBox, QCheckBox, QProgressBar, QTextEdit, QStatusBar
    from PyQt5.QtCore import QTimer

    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QMainWindow { background-color: #1e1e1e; color: #d4d4d4; }
        QGroupBox { border: 1px solid #3c3c3c; border-radius: 5px; margin-top: 10px; font-weight: bold; color: #d4d4d4; }
        QLabel { color: #d4d4d4; }
        QLineEdit { background-color: #2d2d2d; border: 1px solid #3c3c3c; border-radius: 3px; padding: 5px; color: #d4d4d4; }
        QPushButton { background-color: #0e639c; border: none; border-radius: 3px; padding: 8px 16px; color: white; font-weight: bold; }
        QComboBox { background-color: #2d2d2d; border: 1px solid #3c3c3c; border-radius: 3px; padding: 5px; color: #d4d4d4; }
        QCheckBox { color: #d4d4d4; }
        QProgressBar { border: 1px solid #3c3c3c; border-radius: 3px; background-color: #2d2d2d; text-align: center; }
        QProgressBar::chunk { background-color: #0e639c; }
        QTextEdit { background-color: #1e1e1e; border: 1px solid #3c3c3c; color: #d4d4d4; font-family: Consolas; }
        QStatusBar { background-color: #007acc; color: white; }
    """)

    window = QMainWindow()
    window.setWindowTitle("视频转文字工具 - 测试版")
    window.setMinimumSize(900, 700)

    central = QWidget()
    window.setCentralWidget(central)
    layout = QVBoxLayout(central)

    # 文件选择
    file_group = QGroupBox("文件选择")
    file_layout = QGridLayout()
    file_layout.addWidget(QLabel("视频文件:"), 0, 0)
    file_layout.addWidget(QLineEdit(), 0, 1)
    file_layout.addWidget(QPushButton("浏览"), 0, 2)
    file_layout.addWidget(QLabel("输出位置:"), 1, 0)
    file_layout.addWidget(QLineEdit(), 1, 1)
    file_layout.addWidget(QPushButton("浏览"), 1, 2)
    file_group.setLayout(file_layout)
    layout.addWidget(file_group)

    # 参数设置
    config_group = QGroupBox("参数设置")
    config_layout = QGridLayout()
    config_layout.addWidget(QLabel("Whisper 模型:"), 0, 0)
    config_layout.addWidget(QComboBox(), 0, 1)
    config_layout.addWidget(QLabel("量化类型:"), 0, 2)
    config_layout.addWidget(QComboBox(), 0, 3)
    config_layout.addWidget(QLabel("分段时长:"), 1, 0)
    config_layout.addWidget(QComboBox(), 1, 1)
    config_layout.addWidget(QCheckBox("本地标点"), 1, 2)
    config_layout.addWidget(QCheckBox("MiniMax 润色"), 1, 3)
    config_group.setLayout(config_layout)
    layout.addWidget(config_group)

    # 进度
    progress_group = QGroupBox("处理进度")
    progress_layout = QVBoxLayout()
    progress_layout.addWidget(QLabel("状态: 待机"))
    progress_layout.addWidget(QProgressBar())
    progress_group.setLayout(progress_layout)
    layout.addWidget(progress_group)

    # 日志
    log_group = QGroupBox("日志")
    log_layout = QVBoxLayout()
    log_layout.addWidget(QTextEdit())
    log_group.setLayout(log_layout)
    layout.addWidget(log_group)

    window.setStatusBar(QStatusBar())
    window.statusBar().showMessage("测试模式 - 就绪")

    window.show()
    print("窗口已显示")
    sys.exit(app.exec_())

except Exception as e:
    print(f"错误: {e}")
    traceback.print_exc()
    input("按回车退出...")
