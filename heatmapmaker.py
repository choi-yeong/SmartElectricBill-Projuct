import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import font_manager, rc
import seaborn as sns
# heatmap 그래프 제작 스크립트 공간입니다.
# 다른 코드랑 섞이면 헷갈려서 그냥 따로 빼놨습니다.

# 한글폰트 적용
path = 'C:\\Windows\\Fonts\\malgun.ttf'  # 맑은 고딕 폰트 경로
font = font_manager.FontProperties(fname=path).get_name()
rc('font', family=font)

# 1. CSV 파일 읽기
df1 = pd.read_csv("heatmap_data_2020.csv", index_col=0)
df2 = pd.read_csv("heatmap_data_2021.csv", index_col=0)
df3 = pd.read_csv("heatmap_data_2022.csv", index_col=0)
df4 = pd.read_csv("heatmap_data_2023.csv", index_col=0)

# 2x2 서브플롯 설정
fig, axes = plt.subplots(2, 2, figsize=(15, 10))

# 히트맵 설정 (y축 반전 & 값 표시)
heatmap_params = {
    "cmap": "crest",
    "annot": False,  # 값 표시
    "fmt": ".1f",   # 소수점 1자리
    "cbar": True,
    "yticklabels": True
}

sns.heatmap(df1.iloc[::-1], ax=axes[0, 0], **heatmap_params)
sns.heatmap(df2.iloc[::-1], ax=axes[0, 1], **heatmap_params)
sns.heatmap(df3.iloc[::-1], ax=axes[1, 0], **heatmap_params)
sns.heatmap(df4.iloc[::-1], ax=axes[1, 1], **heatmap_params)

# 타이틀 설정
axes[0, 0].set_title("2020년 사용전력")
axes[0, 1].set_title("2021년 사용전력")
axes[1, 0].set_title("2022년 사용전력")
axes[1, 1].set_title("2023년 사용전력")

plt.tight_layout()
plt.show()
