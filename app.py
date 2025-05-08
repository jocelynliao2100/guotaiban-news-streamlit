import streamlit as st
from docx import Document
import pandas as pd
import matplotlib.pyplot as plt
import re
from collections import Counter
from io import StringIO

st.title("國台辦《政務要聞》新聞稿月統計圖表")

uploaded_file = st.file_uploader("上傳 Word 檔（政務要聞原始碼）", type="docx")

if uploaded_file:
    doc = Document(uploaded_file)
    text = "\n".join([para.text for para in doc.paragraphs])

    # 抓取 yyyy-mm-dd 格式日期
    pattern = r"\b(2020|2021|2022|2023|2024|2025)-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])\b"
    matches = re.findall(pattern, text)
    year_months = [f"{y}-{m}" for y, m, d in matches]

    # 統計每月新聞數
    counts = Counter(year_months)
    all_months = pd.date_range("2020-01-01", "2025-04-30", freq="MS").strftime("%Y-%m").tolist()
    data = {"date": [], "count": []}
    for ym in all_months:
        data["date"].append(ym)
        data["count"].append(counts.get(ym, 0))

    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])

    # 繪製圖表
    st.subheader("2020–2025 每月新聞稿發佈數量")
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df["date"], df["count"], marker="o")
    ax.set_xlabel("日期")
    ax.set_ylabel("新聞數")
    ax.set_title("國台辦《政務要聞》新聞稿數量變化（2020–2025.04）")
    ax.grid(True)
    plt.xticks(rotation=45)
    st.pyplot(fig)
