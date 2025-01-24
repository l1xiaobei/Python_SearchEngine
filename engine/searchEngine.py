import pandas
import os

class searchEngine:
    def __init__(self, csv_file):
        """
        初始化SearchEngine类，加载CSV文件
        :param csv_file: 包含文章数据的CSV文件路径
        """
        self.df = pandas.read_csv(csv_file)
        
    def search(self, query):
        """
        搜索CSV文件中的数据，查找匹配的文章，并将结果保存到HTML文件
        :param query: 用户的查询词
        """
        query = query.lower()  # 转换为小写，确保大小写不敏感

        # 搜索标题和正文中的匹配项
        results = self.df[self.df['title'].str.contains(query, case=False, na=False) | 
                          self.df['body'].str.contains(query, case=False, na=False)]

        # 设置输出目录
        output_dir = './templates/'  # 结果文件存储路径

        # 如果输出目录不存在，创建它
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 输出 HTML 文件
        with open(os.path.join(output_dir, 'result.html'), 'w', encoding='utf-8') as f:
            f.write('<html><head><title>Search Results</title></head><body>')
            f.write(f'<h1>Search Results for "{query}"</h1>')

            if not results.empty:
                f.write(f'<p>找到 {len(results)} 个符合条件的结果：</p>')
                f.write('<ul>')  # 创建一个列表

                # 遍历结果，并写入到 HTML 文件
                for index, row in results.iterrows():
                    f.write(f'<li><a href="{row["link"]}" target="_blank">{row["title"]}</a><br>')
                    f.write(f'<strong>部分正文:</strong> {row["body"][:100]}...<br>')
                    f.write('-' * 80 + '<br>')  # 用于分隔各个结果
                f.write('</ul>')  # 结束列表
            else:
                f.write('<p>没有找到符合条件的结果。</p>')

            f.write('</body></html>')

        print("搜索结果已保存到 result.html 文件中。")