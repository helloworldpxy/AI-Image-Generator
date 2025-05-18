# AI Image Generator
# AI 图片生成工具

一个基于PyQt5的桌面应用程序，通过调用Midjourney API实现图片风格转换与生成。

## 功能特性

- 🖼️ **上传本地图片**：支持PNG、JPG、JPEG格式的图片上传与预览。
- ✨ **风格化生成**：输入风格描述（如“赛博朋克”），生成对应风格的图像。
- 💾 **结果保存**：支持将生成的图片保存到本地。
- 🚀 **异步处理**：使用多线程避免界面卡顿。
- 🎨 **简洁UI**：提供直观的交互界面和实时预览功能。

### 依赖环境
- Python 3.7+
- 依赖库：
  ```bash
  PyQt5==5.15.9
  requests==2.31.0
  ```
### 安装方法
1. 克隆仓库：
   ```bash
   git clone https://github.com/helloworldpxy/AI-Image-Generator.git
   cd AI-Image-Generator
   ```
2. 安装依赖：
   ```bash
   pip install pyqt5 requests
   ```

## 使用说明

1. **运行程序**：
   ```bash
   python AI_Image_Generator.py
   ```

2. **操作流程**：
   - 点击 **上传图片** 按钮选择本地图片。
   - 在输入框中填写风格要求（如“水墨画风格”）。
   - 点击 **生成图片** 启动AI处理（需等待数秒）。
   - 生成完成后，点击 **保存图片** 导出结果。

## 注意事项

⚠️ **API密钥安全**  
当前代码内置测试用API token（`22b91a38cb874299bcd9ac9b1cf949eb`），如需长期使用：
1. 前往 [智数云](https://www.zhishuyun.com/) 注册并获取自己的API token。
2. 修改代码中 `API_URL` 的token参数。

## 开源协议

本项目基于 [MIT License](LICENSE) 开源，核心条款包括：
- 允许自由使用、修改和分发代码
- 需保留原始版权声明
- 作者不承担任何责任

## 作者信息

- **开发者**: HelloWorld05
- **反馈建议**: [提交Issue](https://github.com/helloworldpxy/AI-Image-Generator/issues)
