# 开发日志

## 0.0.1 (2025-1-18)

### 改动

- 初始化git仓库，添加许可证，开发日志，README。

## 0.0.2 (2025-1-20)

### 改动

- 创建运行软件需要的虚拟环境，并添加/environment.yml文件。
- 创建/test.py文件测试网页爬虫是否可用。
- 创建/main.py文件尝试搭建一个flask框架应用。
- 创建/templates文件夹，用于存放flask应用的html界面文件。
- 创建/templates/index.html文件作为flask应用的主页html文件。

## 0.0.3 (2025-1-21)

### 改动

- /environment.yml文件中添加pandas库用于将网页保存为csv文件。
- 修改/test.py文件中爬取网页相关代码，添加了更为合理的验证爬取成功机制。
- 修改/main.py文件，添加了搜索处理的相关代码。
- 修改/test.py文件，添加了函数save_page()用于将网页链接、标题与正文保存为csv文件。

## 0.0.4 (2025-1-24)

### 改动

- 创建/engine文件夹，用于存放搜索引擎搜索相关代码。
- 创建/engine/search.py文件，创建searchEngine类用于搜索处理。
- 创建/templates/result.html用于存放搜索结果html文件。
- 创建.gitignore文件用于避免提交不必要的文件。
- 修改/main.py文件，通过调用/engine/search.py实现搜索处理的相关功能。
