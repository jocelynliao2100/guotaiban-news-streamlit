
import streamlit as st
from docx import Document
import pandas as pd
import re
from datetime import datetime

st.title("國台辦《政務要聞》新聞稿分析")

uploaded_file = st.file_uploader("上傳 Word 檔（政務要聞原始碼）", type="docx")

if uploaded_file:
    doc = Document(uploaded_file)
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    pattern = re.compile(r"\[\s*(\d{4}-\d{2}-\d{2})\s*\].*?href=\"(.*?)\".*?title=\"(.*?)\"")
    records = []

    for para in paragraphs:
        match = pattern.search(para)
        if match:
            date_str, url, title = match.groups()
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
                records.append((date, title.strip(), url.strip()))
            except ValueError:
                continue

    df = pd.DataFrame(records, columns=["日期", "標題", "連結"])
    years = sorted(set(df["日期"].dt.year))
    selected_years = st.multiselect("選擇年份", years, default=years)
    filtered_df = df[df["日期"].dt.year.isin(selected_years)]

    st.dataframe(filtered_df)

    st.subheader("發稿頻率統計")
    monthly_count = (
        filtered_df["日期"]
        .apply(lambda d: d.strftime("%Y-%m"))
        .value_counts()
        .sort_index()
    )
    st.bar_chart(monthly_count)

    keyword = st.text_input("關鍵字搜尋（標題）")
    if keyword:
        result_df = filtered_df[filtered_df["標題"].str.contains(keyword)]
        st.write(f"🔍 找到 {len(result_df)} 則相關新聞：")
        st.dataframe(result_df)

if not df.empty:
    df["日期"] = pd.to_datetime(df["日期"], errors='coerce')  # 加上這行自動轉型，錯誤會變 NaT
    df = df.dropna(subset=["日期"])  # 避免 NaT 資料導致錯誤

    years = sorted(set(df["日期"].dt.year))
    selected_years = st.multiselect("選擇年份", years, default=years)
    filtered_df = df[df["日期"].dt.year.isin(selected_years)]

    st.dataframe(filtered_df)

    st.subheader("發稿頻率統計")
    monthly_count = (
        filtered_df["日期"]
        .apply(lambda d: d.strftime("%Y-%m"))
        .value_counts()
        .sort_index()
    )
    st.bar_chart(monthly_count)
