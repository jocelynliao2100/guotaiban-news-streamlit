import streamlit as st
from docx import Document
from collections import defaultdict
import matplotlib.pyplot as plt
import re
from datetime import datetime
from io import BytesIO
from matplotlib.font_manager import FontProperties

st.set_page_config(layout="wide")
st.title("國台辦新聞稿分析：2020–2025年4月各欄目發稿趨勢")

uploaded_files = st.file_uploader("請上傳五個國台辦 Word 文件", type="docx", accept_multiple_files=True)

if uploaded_files and len(uploaded_files) == 5:
    column_names = ["新聞要聞", "政務要聞", "交流交往", "部門涉台", "台辦動態"]
    date_pattern = re.compile(r"\b(202[0-5])[-年/.](\d{1,2})[-月/.]?(?:\d{1,2})?日?\b")
    year_month_counts = defaultdict(lambda: defaultdict(int))  # {欄目: {年月: 數量}}

    for file, column in zip(uploaded_files, column_names):
        try:
            document = Document(BytesIO(file.read()))
            for para in document.paragraphs:
                match = date_pattern.search(para.text)
                if match:
                    year, month = match.group(1), match.group(2)
                    ym_key = f"{year}-{int(month):02d}"
                    if "2020-01" <= ym_key <= "2025-04":
                        year_month_counts[column][ym_key] += 1
        except Exception as e:
            st.error(f"{column} 檔案讀取失敗：{e}")

    # 所有月份排序
    all_months = sorted(set(k for d in year_month_counts.values() for k in d.keys()))

    # 設定中文字型
    font_path = "path/to/your/chinese_font.ttf"  # 替換為你的中文字型檔案路徑
    font_prop = FontProperties(fname=font_path)

    # 畫圖
    fig, ax = plt.subplots(figsize=(12, 6))
    for column, counts in year_month_counts.items():
        y_vals = [counts.get(month, 0) for month in all_months]
        ax.plot(all_months, y_vals, label=column)

    ax.set_title("2020–2025年4月 國台辦各欄目新聞稿量變化", fontproperties=font_prop)
    ax.set_xlabel("年月", fontproperties=font_prop)
    ax.set_ylabel("新聞稿數量", fontproperties=font_prop)
    ax.set_xticks(range(len(all_months)))
    ax.set_xticklabels(all_months, rotation=45, fontproperties=font_prop)
    ax.legend(prop=font_prop)  # 圖例也設定字型
    ax.grid(True)
    st.pyplot(fig)
else:
    st.warning("請一次上傳五個 Word 文件，並依序對應五個欄目。")
