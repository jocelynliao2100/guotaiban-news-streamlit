import streamlit as st
from docx import Document
import pandas as pd
import matplotlib.pyplot as plt
import re
import jieba
from collections import Counter
from datetime import datetime

st.title("國台辦「政務要聞」新聞稿分析")

uploaded_file = st.file_uploader("上傳 Word 檔案（.docx）", type="docx")

if uploaded_file:
    doc = Document(uploaded_file)
    paragraphs = [para.text.strip() for para in doc.paragraphs if para.text.strip()]

    # 抽取日期與標題
    date_title_pairs = []
    pattern = re.compile(r'\[\s*(\d{4})[-年](\d{1,2})[-月](\d{1,2})\s*\]')

    for para in paragraphs:
        match = pattern.search(para)
        if match:
            year, month, day = match.groups()
            date = datetime(int(year), int(month), int(day)).date()
            title_match = re.search(r'(?<=\]）?(?P<title>.+)$', para)
            title = title_match.group("title") if title_match else "未知標題"
            date_title_pairs.append((date, title))

    if date_title_pairs:
        df = pd.DataFrame(date_title_pairs, columns=["date", "title"])
        df['month'] = df['date'].apply(lambda d: d.strftime('%Y-%m'))
        df['count'] = 1

        st.subheader("📈 發布量時間折線圖")
        df_daily = df.groupby("date").count().rename(columns={"count": "news_count"})
        st.line_chart(df_daily["news_count"])

        st.subheader("📰 新聞發布紀錄（前20筆）")
        st.dataframe(df[['date', 'title']].head(20))

        # 前20大中文關鍵字
        all_text = " ".join(df['title'].tolist())
        words = jieba.lcut(all_text)
        words = [w for w in words if len(w) > 1 and not re.match(r'[\d\W]+', w)]
        counter = Counter(words)
        most_common = counter.most_common(20)

        st.subheader("🔑 新聞稿前20大中文關鍵字")
        for word, freq in most_common:
            st.write(f"{word}: {freq}")

        # 發稿最多的月份
        st.subheader("📅 新聞稿最多的月份")
        month_count = df.groupby("month")["count"].sum()
        top_month = month_count.idxmax()
        st.write(f"最多發稿月份：{top_month}（{month_count.max()} 篇）")

        # 該月份關鍵字分析
        top_month_titles = df[df['month'] == top_month]['title'].tolist()
        month_text = " ".join(top_month_titles)
        month_words = jieba.lcut(month_text)
        month_words = [w for w in month_words if len(w) > 1 and not re.match(r'[\d\W]+', w)]
        month_counter = Counter(month_words)
        month_common = month_counter.most_common(20)

        st.subheader("🗓️ 最多月份的前20大關鍵字")
        for word, freq in month_common:
            st.write(f"{word}: {freq}")

        # 與「兩岸」有關的關鍵字（簡體）
        st.subheader("🔍 與「两岸」相關的關鍵字")
        liangan_related = [w for w in counter if '两岸' in w]
        for word in liangan_related:
            st.write(f"{word}: {counter[word]}")

        # 與「台獨」有關的關鍵字（簡體）
        st.subheader("🧨 與「台独」相關的關鍵字")
        taidu_related = [w for w in counter if '台独' in w]
        for word in taidu_related:
            st.write(f"{word}: {counter[word]}")
