from flask import Flask, render_template,request # 导入flask库：flask是一个轻量级的python web应用框架
# render_template() 是 flask 提供的一个函数，用于渲染 HTML 模板文件。
# 它会从 flask 应用的模板目录（默认是 templates 文件夹）中加载 index.html 文件，并将其内容返回给客户端。
# 如果 index.html 文件中包含模板变量或逻辑，render_template() 会根据传入的参数进行渲染。
# 在 Web 开发中，当用户通过 HTML 表单提交数据时，数据会被发送到服务器。Flask 提供了 request 对象来访问这些提交的数据。
# 在 Flask 中，request 对象是一个全局变量，
# 它包含了关于当前请求的所有信息，包括请求方法（GET、POST）、请求头、请求体、表单数据、查询参数等。
from engine.searchEngine import SearchEngine

from collections import defaultdict 
#defaultdict 是 Python 中 collections 模块提供的一个字典子类，它在处理不存在的键时提供默认值，避免了 KeyError 异常
from pypinyin import lazy_pinyin, Style # 添加pypinyin库，方便实现按首字母分组词条
import string
import json
import os

app = Flask(__name__)
# Flask 是 flask 框架的主类，用于创建一个 flask 应用实例
# __name__ 是一个 Python 内置变量，表示当前模块的名称
# 当你的脚本作为主程序运行时，__name__ 的值为 '__main__'
# 当你的脚本被其他模块引入时，__name__ 的值为模块名
# app 是 Flask 应用实例的变量名，你可以使用它来配置应用、定义路由和视图函数等
# 它是 Flask 应用的核心对象，所有的 Flask 功能都围绕它展开
search_engine = SearchEngine()  # 创建 Elasticsearch 搜索引擎实例

@app.route('/') # 主页路由装饰器
def index():
    return render_template('index.html') # 返回渲染后的 HTML
# 这个装饰器告诉 Flask，当用户访问应用的根 URL（即 http://127.0.0.1:5000/ 或类似的地址）时，调用 index() 函数来处理该请求。

#@app.route('/search', methods=['GET']) # 搜索处理路由装饰器 指定接受GET/POST请求
@app.route('/search', methods=['GET', 'POST']) # 搜索处理路由装饰器
def search():
    # 获取表单数据，'query' 是表单输入框的 name 属性值
    query = ''
    if request.method == 'POST':
        query = request.form.get('query', '')
    elif request.method == 'GET':
        query = request.args.get('query', '')
    #query = request.form['query'] # 如果是GET请求，使用request.args # 如果是POST请求，使用request.form  
    #  
    search_results = search_engine.search(query)  # 在 Elasticsearch 中搜索
    return render_template('result.html', query=query, results=search_results)

# 加载 JSON 词条数据
def load_entries():
    path = os.path.join(os.path.dirname(__file__), './data/entries.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# 财经百科页面 路由
@app.route('/encyclopedia')
def encyclopedia():
    data = load_entries()
    # 按拼音首字母分组
    grouped = defaultdict(list)
    for entry_id, entry in data.items():
        if not entry['title']:
            continue
        # 提取首字拼音字母
        first_letter = lazy_pinyin(entry['title'][0], style=Style.FIRST_LETTER)[0].upper()
        key = first_letter if 'A' <= first_letter <= 'Z' else '#'
        grouped[key].append({"id": entry_id, "title": entry["title"]}) # 非字母归为“#”
    # 所有导航字母 A-Z
    all_letters = list(string.ascii_uppercase) + ['#']
    # 排序
    grouped_sorted = dict(sorted(grouped.items()))
    return render_template('encyclopedia.html', entries_by_letter=grouped_sorted, all_letters=all_letters)

# 词条详情页路由
@app.route('/encyclopedia/<entry_id>')
def encyclopedia_entry(entry_id):
    data = load_entries()
    entry = data.get(entry_id)
    if not entry:
        return "词条不存在", 404
    return render_template('entry_detail.html', entry=entry)

if __name__ == '__main__':
    app.run(debug=True) # 启动 Flask 开发服务器，debug=True 表示开启调试模式，方便开发时自动重载和显示错误信息