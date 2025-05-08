import streamlit as st
from docx import Document
import pandas as pd
import plotly.express as px
import re
from collections import Counter

st.title("國台辦《政務要聞》新聞稿月統計圖表（Plotly 中文支援）")

uploaded_file = st.file_uploader("上傳 Word 檔（政務要聞原始碼）", type="docx")

if uploaded_file:
    doc = Document(uploaded_file)
    text = "\n".join([para.text for para in doc.paragraphs])

    # 抓取日期格式 yyyy-mm-dd
    pattern = r"\b(2020|2021|2022|2023|2024|2025)-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])\b"
    matches = re.findall(pattern, text)
    year_months = [f"{y}-{m}" for y, m, d in matches]

    # 統計每月出現次數
    counts = Counter(year_months)
    all_months = pd.date_range("2020-01-01", "2025-04-30", freq="MS").strftime("%Y-%m").tolist()
    data = {"日期": [], "新聞數量": []}
    for ym in all_months:
        data["日期"].append(ym)
        data["新聞數量"].append(counts.get(ym, 0))

    df = pd.DataFrame(data)
    df["日期"] = pd.to_datetime(df["日期"])

    # 顯示互動式折線圖（支援中文）
    fig = px.line(df, x="日期", y="新聞數量", title="國台辦《政務要聞》新聞稿數量變化（2020–2025.04）")
    st.plotly_chart(fig)

    # 表格
    st.subheader("新聞數據表格")
    st.dataframe(df)

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
