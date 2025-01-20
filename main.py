from flask import Flask, render_template # 导入flask库：flask是一个轻量级的python web应用框架
# render_template() 是 flask 提供的一个函数，用于渲染 HTML 模板文件。
# 它会从 flask 应用的模板目录（默认是 templates 文件夹）中加载 index.html 文件，并将其内容返回给客户端。
# 如果 index.html 文件中包含模板变量或逻辑，render_template() 会根据传入的参数进行渲染。

import requests # 导入requests库：用于发送 HTTP 请求获取网页内容
from bs4 import BeautifulSoup # 导入BeautifulSoup库：用于解析 HTML 页面，提取数据

app = Flask(__name__)
# Flask 是 flask 框架的主类，用于创建一个 flask 应用实例
# __name__ 是一个 Python 内置变量，表示当前模块的名称
# 当你的脚本作为主程序运行时，__name__ 的值为 '__main__'
# 当你的脚本被其他模块引入时，__name__ 的值为模块名
# app 是 Flask 应用实例的变量名，你可以使用它来配置应用、定义路由和视图函数等
# 它是 Flask 应用的核心对象，所有的 Flask 功能都围绕它展开

@app.route('/') # 主页路由装饰器
def index():
    return render_template('index.html')
# 这个装饰器告诉 Flask，当用户访问应用的根 URL（即 http://127.0.0.1:5000/ 或类似的地址）时，调用 index() 函数来处理该请求。


if __name__ == '__main__':
    app.run(debug=True) # 启动 Flask 开发服务器，debug=True 表示开启调试模式，方便开发时自动重载和显示错误信息