import streamlit as st
from docx import Document
import pandas as pd
import plotly.express as px
import jieba
import re
from collections import Counter

st.title("國台辦《政務要聞》新聞稿分析系統")

uploaded_file = st.file_uploader("上傳 Word 檔（政務要聞原始碼）", type="docx")

if uploaded_file:
    doc = Document(uploaded_file)
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    text = "\n".join(paragraphs)

    # 擷取日期 yyyy-mm-dd 並建立日期 → 段落 map
    pattern = r"\[\s*(\d{4}-\d{2}-\d{2})\s*\]"
    data = []
    current_date = None
    for para in paragraphs:
        m = re.search(pattern, para)
        if m:
            current_date = m.group(1)
        elif current_date:
            data.append((current_date, para))

    df = pd.DataFrame(data, columns=["日期", "標題"])
    df["日期"] = pd.to_datetime(df["日期"])
    df["年月"] = df["日期"].dt.to_period("M").astype(str)

    # 每月統計圖表
    monthly_count = df["年月"].value_counts().sort_index()
    df_count = pd.DataFrame({
        "日期": pd.to_datetime(monthly_count.index),
        "新聞數量": monthly_count.values
    })

    st.subheader("🗓️ 每月新聞數量變化")
    fig = px.line(df_count, x="日期", y="新聞數量", title="國台辦《政務要聞》新聞稿數量變化（2020–2025.04）")
    st.plotly_chart(fig)

    # 原始資料表格
    st.subheader("📄 新聞資料表")
    st.dataframe(df)

    # 全部關鍵詞統計
    all_text = " ".join(df['標題'].tolist())
    words = jieba.lcut(all_text)
    words = [w for w in words if len(w) > 1 and not re.match(r'[\d\W]+', w)]
    counter = Counter(words)
    most_common = counter.most_common(20)

    st.subheader("🔑 全部新聞標題前20大關鍵詞")
    for word, freq in most_common:
        st.write(f"{word}: {freq}")

    # 發稿最多月份
    top_month = df["年月"].value_counts().idxmax()
    st.subheader(f"📆 發稿最多的月份：{top_month}")

    top_month_titles = df[df["年月"] == top_month]["標題"].tolist()
    month_text = " ".join(top_month_titles)
    month_words = jieba.lcut(month_text)
    month_words = [w for w in month_words if len(w) > 1 and not re.match(r'[\d\W]+', w)]
    month_counter = Counter(month_words)
    month_common = month_counter.most_common(20)

    st.subheader("🗓️ 最多月份的前20大關鍵詞")
    for word, freq in month_common:
        st.write(f"{word}: {freq}")

    # 關聯詞搜尋
    st.subheader("🔍 與「两岸」相關的關鍵詞")
    liangan_related = [w for w in counter if "两岸" in w]
    for word in liangan_related:
        st.write(f"{word}: {counter[word]}")

    st.subheader("🧨 與「台独」相關的關鍵詞")
    taidu_related = [w for w in counter if "台独" in w]
    for word in taidu_related:
        st.write(f"{word}: {counter[word]}")
