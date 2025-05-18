import sys
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QPushButton,
                             QTextEdit, QFileDialog, QMessageBox, QVBoxLayout, QHBoxLayout)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal

API_URL = "https://api.zhishuyun.com/midjourney/imagine?token=22b91a38cb874299bcd9ac9b1cf949eb"

class Worker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, payload):
        super().__init__()
        self.payload = payload

    def run(self):
        try:
            response = requests.post(API_URL, json=self.payload, headers={
                "accept": "application/json",
                "content-type": "application/json"
            }, timeout=480)
            self.finished.emit(response.json())
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_image_id = "none"
        self.generated_image_url = ""
        self.initUI()

    def initUI(self):
        self.setWindowTitle("AI 图片生成工具v1.0")
        #self.setWindowIcon(QIcon('icon.png'))  # 可指定图标
        self.setGeometry(100, 100, 800, 600)

        # 创建菜单栏
        menubar = self.menuBar()
        help_menu = menubar.addMenu('帮助')
        about_action = help_menu.addAction('关于')
        about_action.triggered.connect(self.show_about)

        # 主界面布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout()
        main_widget.setLayout(layout)

        # 左侧控制面板
        control_panel = QWidget()
        control_layout = QVBoxLayout()
        control_panel.setLayout(control_layout)

        # 上传图片区域
        self.upload_btn = QPushButton("上传图片")
        self.upload_btn.clicked.connect(self.upload_image)
        control_layout.addWidget(self.upload_btn)

        self.image_preview = QLabel()
        self.image_preview.setFixedSize(200, 200)
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setText("图片预览")
        self.image_preview.setStyleSheet("border: 2px dashed #aaa;")
        control_layout.addWidget(self.image_preview)

        # 输入区域
        control_layout.addWidget(QLabel("风格要求:"))
        self.style_input = QTextEdit()
        self.style_input.setFixedHeight(100)
        control_layout.addWidget(self.style_input)

        self.generate_btn = QPushButton("生成图片")
        self.generate_btn.clicked.connect(self.generate_image)
        control_layout.addWidget(self.generate_btn)

        # 右侧结果区域
        result_panel = QWidget()
        result_layout = QVBoxLayout()
        result_panel.setLayout(result_layout)

        self.result_preview = QLabel()
        self.result_preview.setAlignment(Qt.AlignCenter)
        self.result_preview.setText("生成结果预览")
        self.result_preview.setStyleSheet("border: 2px dashed #aaa;")
        result_layout.addWidget(self.result_preview)

        self.save_btn = QPushButton("保存图片")
        self.save_btn.clicked.connect(self.save_image)
        self.save_btn.setEnabled(False)
        result_layout.addWidget(self.save_btn)

        layout.addWidget(control_panel, 1)
        layout.addWidget(result_panel, 2)

        # 样式美化
        self.setStyleSheet("""
            QMainWindow {background: #f0f0f0;}
            QPushButton {
                background: #4CAF50;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {background: #45a049;}
            QTextEdit {border: 1px solid #ccc; padding: 4px;}
        """)

    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "", "Image Files (*.png *.jpg *.jpeg)")
        if file_path:
            pixmap = QPixmap(file_path)
            self.image_preview.setPixmap(
                pixmap.scaled(200, 200, Qt.KeepAspectRatio))

    def generate_image(self):
        style = self.style_input.toPlainText().strip()
        if not style:
            QMessageBox.warning(self, "警告", "请输入风格要求")
            return

        payload = {
            "timeout": 480,
            "action": "generate",
            "prompt": f"修改图像为{style}风格",
            "image_id": self.current_image_id,
            "callback_url": "none",
            "translation": True
        }

        self.worker = Worker(payload)
        self.worker.finished.connect(self.handle_response)
        self.worker.error.connect(self.handle_error)
        self.worker.start()
        self.generate_btn.setEnabled(False)
        self.generate_btn.setText("生成中...")

    def handle_response(self, response):
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("生成图片")
        if response.get("code") == 200:
            self.current_image_id = response.get("image_id", "none")
            self.generated_image_url = response.get("image_url", "")
            self.show_generated_image()
        else:
            QMessageBox.critical(self, "错误", response.get("msg", "未知错误"))

    def handle_error(self, error_msg):
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("生成图片")
        QMessageBox.critical(self, "错误", f"API调用失败: {error_msg}")

    def show_generated_image(self):
        if self.generated_image_url:
            try:
                image_data = requests.get(self.generated_image_url).content
                pixmap = QPixmap()
                pixmap.loadFromData(image_data)
                self.result_preview.setPixmap(
                    pixmap.scaled(self.result_preview.width(), 
                                self.result_preview.height(),
                                Qt.KeepAspectRatio))
                self.save_btn.setEnabled(True)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"图片加载失败: {str(e)}")

    def save_image(self):
        if self.generated_image_url:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "保存图片", "", "PNG Image (*.png);;JPEG Image (*.jpg)")
            if file_path:
                try:
                    image_data = requests.get(self.generated_image_url).content
                    with open(file_path, 'wb') as f:
                        f.write(image_data)
                    QMessageBox.information(self, "成功", "图片保存成功")
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")

    def show_about(self):
        about_text = """AI 图片生成工具
版本: 1.0
作者: HelloWorld05
功能说明:
1. 上传本地图片并输入风格要求
2. 调用Midjourney API生成新图片
3. 支持结果预览和保存"""
        QMessageBox.about(self, "关于", about_text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())