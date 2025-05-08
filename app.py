!pip install python-docx

from docx import Document
import re
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
# from matplotlib.font_manager import FontProperties  # 移除這行
from io import BytesIO
from google.colab import files

# 設定中文字體 (移除這部分)
# font_path = './NotoSansCJKjp-Regular.otf'
# font = FontProperties(fname=font_path)


# 載入 Word 文件
uploaded = files.upload() #Colab上傳檔案
for filename in uploaded.keys():
  try:
      document = Document(BytesIO(uploaded[filename]))
  except Exception as e:
      print(f"讀取文件時發生錯誤：{e}")
      exit()  # 終止程式，因為無法繼續處理


# 取得段落文字，並提取 2020–2025 年的日期（格式：yyyy-mm-dd）
text_for_analysis = "\n".join([para.text for para in document.paragraphs])
pattern = r"\b(2020|2021|2022|2023|2024|2025)-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])\b"
matches = re.findall(pattern, text_for_analysis)
year_months = [f"{y}-{m}" for y, m, d in matches]  # 保留年月


# 統計每個年月的新聞稿數量
counts = Counter(year_months)


# 建立每年每月新聞數的表格
years = list(range(2020, 2026))  # 包含2025
months = [f"{i:02d}" for i in range(1, 13)]
data = []
for y in years:
    row = {'year': y}
    for m in months:
        row[m] = counts.get(f"{y}-{m}", 0)
    data.append(row)
df = pd.DataFrame(data)

# 在Colab中安裝中文字體
!apt-get -qq install fonts-noto-cjk fonts-noto-cjk-extra

# 重新設置matplotlib字體緩存 (使用新的方法)
import matplotlib.font_manager as fm
fm.fontManager.addfont('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
# 如果上述方法不存在，則忽略錯誤，繼續執行
# 較新版本的matplotlib已經在安裝字體後會自動刷新緩存

# 設定使用Noto Sans CJK字體（Colab預裝）
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK TC', 'Noto Sans CJK SC', 'Noto Sans CJK JP']
plt.rcParams['axes.unicode_minus'] = False

# 下載思源黑體並使用（確保可用）
!wget -q https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/Japanese/NotoSansCJKjp-Regular.otf -O NotoSansCJKjp-Regular.otf
font_path = './NotoSansCJKjp-Regular.otf'
font = FontProperties(fname=font_path)

# 將寬表轉為長表，準備畫圖
df_long = df.melt(id_vars='year', value_vars=months, var_name='month', value_name='count')
df_long['date'] = pd.to_datetime(df_long['year'].astype(str) + '-' + df_long['month'])
df_long = df_long[df_long['date'] <= '2025-04-30']  # 僅保留至2025年4月
df_long = df_long.sort_values('date')


# 繪製折線圖
plt.figure(figsize=(12, 6))
plt.plot(df_long['date'], df_long['count'], marker='o')
plt.xlabel('日期')  # 移除 fontproperties
plt.ylabel('新聞稿數量') # 移除 fontproperties
plt.title('國台辦「政務要聞」新聞稿每月數量 (2020–2025.04)') # 移除 fontproperties
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.show()
