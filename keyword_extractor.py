# keyword_extractor.py
import re
import jieba.analyse
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords

# 下载 NLTK 停用词
nltk.download("stopwords")

# 载入英文停用词
stop_words = set(stopwords.words("english"))

# 1检测语言（中文 or 英文）
def detect_language(text):
    """判断文本是中文还是英文"""
    if re.search("[\u4e00-\u9fff]", text):  # 只要文本中含有中文字符，就认为是中文
        return "chinese"
    return "english"

# 2提取关键词（支持中英文）
def extract_keywords(text, topK=5):
    """自动提取关键词（根据语言选择 Jieba 或 TF-IDF）"""
    lang = detect_language(text)
    
    if lang == "chinese":
        return ",".join(jieba.analyse.extract_tags(text, topK=topK))  # 中文用 jieba
    else:
        return ",".join(tfidf_extract_keywords(text, topK))  # 英文用 TF-IDF

# 3使用 TF-IDF 提取英文关键词
def tfidf_extract_keywords(text, topK=5):
    """使用 TF-IDF 提取英文关键词"""
    words = [word.lower() for word in re.findall(r"\b[a-zA-Z]{3,}\b", text) if word.lower() not in stop_words]
    
    if not words:  # 防止文本为空
        return []
    
    corpus = [" ".join(words)]  # 语料库
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(corpus)
    scores = X.toarray()[0]  # 关键词权重
    feature_names = vectorizer.get_feature_names_out()
    
    keywords = sorted(zip(feature_names, scores), key=lambda x: x[1], reverse=True)[:topK]
    return [kw[0] for kw in keywords]
