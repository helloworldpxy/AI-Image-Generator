import sys
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QPushButton,
                             QTextEdit, QFileDialog, QMessageBox, QVBoxLayout, QHBoxLayout)
from PyQt5.QtGui import QPixmap, QIcon, QImage, QImageReader
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QBuffer
from pathlib import Path

API_URL = "https://api.zhishuyun.com/midjourney/imagine?token=22b91a38cb874299bcd9ac9b1cf949eb"

class Worker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, payload, image_data=None):
        super().__init__()
        self.payload = payload
        self.image_data = image_data

    def run(self):
        try:
            files = None
            if self.image_data:
                files = {'file': ('image.png', self.image_data, 'image/png')}
            
            response = requests.post(
                API_URL,
                json=self.payload,
                headers={"accept": "application/json"},
                files=files,
                timeout=480
            )
            
            if response.status_code != 200:
                raise requests.exceptions.HTTPError(f"HTTP错误 {response.status_code}")
                
            self.finished.emit(response.json())
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_image_id = None
        self.generated_image_url = None
        self.local_image_data = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("AI 图片生成工具v2.0")
        #self.setWindowIcon(QIcon('icon.png'))  # 设置窗口图标
        self.setGeometry(100, 100, 800, 600)

        # 菜单栏
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
        self.image_preview.setFixedSize(300, 300)
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setText("图片预览区域（支持PNG/JPG）")
        self.image_preview.setStyleSheet("border: 2px dashed #aaa;")
        control_layout.addWidget(self.image_preview)

        # 输入区域
        control_layout.addWidget(QLabel("风格描述:"))
        self.style_input = QTextEdit()
        self.style_input.setPlaceholderText("请输入想要的图片风格描述...")
        self.style_input.setFixedHeight(100)
        control_layout.addWidget(self.style_input)

        self.status_label = QLabel("就绪")
        control_layout.addWidget(self.status_label)

        self.generate_btn = QPushButton("生成图片")
        self.generate_btn.clicked.connect(self.generate_image)
        control_layout.addWidget(self.generate_btn)

        # 右侧结果区域
        result_panel = QWidget()
        result_layout = QVBoxLayout()
        result_panel.setLayout(result_layout)

        self.result_preview = QLabel()
        self.result_preview.setAlignment(Qt.AlignCenter)
        self.result_preview.setText("生成结果预览区域")
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
                background: #2196F3;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:disabled {background: #90CAF9;}
            QPushButton:hover {background: #1976D2;}
            QTextEdit {
                border: 1px solid #BDBDBD;
                padding: 4px;
                border-radius: 4px;
            }
            QLabel#status_label {color: #666; font-style: italic;}
        """)

    def upload_image(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "选择图片", "", 
                "Images (*.png *.jpg *.jpeg);;All Files (*)"
            )
            
            if not file_path:
                return

            # 验证图片有效性
            reader = QImageReader(file_path)
            if not reader.canRead():
                raise ValueError("无法读取图片文件")

            # 保存原始图片数据
            with open(file_path, 'rb') as f:
                self.local_image_data = f.read()

            # 显示预览
            pixmap = QPixmap(file_path)
            self.image_preview.setPixmap(
                pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        except Exception as e:
            QMessageBox.critical(self, "上传错误", 
                f"图片上传失败: {str(e)}\n请确认：\n1. 文件是有效图片\n2. 有文件读取权限")
            self.local_image_data = None

    def generate_image(self):
        if not self.local_image_data:
            QMessageBox.warning(self, "警告", "请先上传图片")
            return

        style = self.style_input.toPlainText().strip()
        if not style:
            QMessageBox.warning(self, "警告", "请输入风格描述")
            return

        payload = {
            "timeout": 480,
            "action": "generate",
            "prompt": f"修改图像为{style}风格",
            "image_id": self.current_image_id or "none",
            "translation": True
        }

        try:
            # 转换图片数据为BytesIO
            image_buffer = QBuffer()
            image_buffer.open(QBuffer.ReadWrite)
            qimage = QImage.fromData(self.local_image_data)
            qimage.save(image_buffer, "PNG")
            image_data = image_buffer.data()

            self.worker = Worker(payload, image_data)
            self.worker.finished.connect(self.handle_response)
            self.worker.error.connect(self.handle_error)
            self.worker.start()

            self.set_ui_state(False)
            self.status_label.setText("图片生成中...")

        except Exception as e:
            self.handle_error(str(e))

    def set_ui_state(self, enabled=True):
        self.generate_btn.setEnabled(enabled)
        self.upload_btn.setEnabled(enabled)
        self.save_btn.setEnabled(enabled and bool(self.generated_image_url))
        self.style_input.setEnabled(enabled)
        self.status_label.setText("就绪" if enabled else "处理中...")

    def handle_response(self, response):
        try:
            if response.get("code") != 200:
                raise ValueError(response.get("msg", "未知API错误"))

            self.current_image_id = response.get("image_id")
            self.generated_image_url = response.get("image_url")
            
            if not self.generated_image_url:
                raise ValueError("未获取到有效图片URL")

            self.show_generated_image()
            QMessageBox.information(self, "成功", "图片生成完成！")

        except Exception as e:
            self.handle_error(str(e))
        finally:
            self.set_ui_state(True)

    def handle_error(self, error_msg):
        self.set_ui_state(True)
        QMessageBox.critical(self, "错误", f"操作失败: {error_msg}")
        self.status_label.setText("错误发生，请重试")

    def show_generated_image(self):
        try:
            response = requests.get(self.generated_image_url, timeout=30)
            response.raise_for_status()

            image_data = response.content
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)

            if pixmap.isNull():
                raise ValueError("无效的图片数据")

            self.result_preview.setPixmap(
                pixmap.scaled(
                    self.result_preview.width(),
                    self.result_preview.height(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            )
            self.save_btn.setEnabled(True)

        except requests.exceptions.RequestException as e:
            self.handle_error(f"网络错误: {str(e)}")
        except Exception as e:
            self.handle_error(f"图片加载失败: {str(e)}")

    def save_image(self):
        if not self.generated_image_url:
            return

        try:
            # 获取保存路径
            save_path, _ = QFileDialog.getSaveFileName(
                self, "保存图片", 
                str(Path.home() / "Downloads" / "generated_image.png"),
                "PNG Image (*.png);;JPEG Image (*.jpg)"
            )
            
            if not save_path:
                return

            # 验证路径可写性
            save_path = Path(save_path)
            if save_path.exists() and not save_path.is_file():
                raise PermissionError("目标路径不可用")

            # 获取图片数据
            response = requests.get(self.generated_image_url, timeout=30)
            response.raise_for_status()

            # 写入文件
            with open(save_path, 'wb') as f:
                f.write(response.content)

            QMessageBox.information(self, "成功", 
                f"图片已保存至：\n{save_path}")

        except requests.exceptions.RequestException as e:
            self.handle_error(f"下载失败: {str(e)}")
        except PermissionError as e:
            self.handle_error(f"保存失败: {str(e)}")
        except Exception as e:
            self.handle_error(f"保存错误: {str(e)}")

    def show_about(self):
        about_text = """AI 图片生成工具 v2.0

功能特性：
• 本地图片上传与预览
• Midjourney 风格转换
• 生成结果实时预览
• 高质量图片保存

技术支持：
• 基于PyQt5开发
• 使用Midjourney Imagine API
• 自动翻译与错误处理

作者：HelloWorld05
许可协议：MIT License"""
        QMessageBox.about(self, "关于程序", about_text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())