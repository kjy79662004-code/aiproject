
import os
import re
import glob
import math

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib as mpl

# ----------------------------------------
# 1. 페이지 설정
# ----------------------------------------

st.set_page_config(
    page_title="서울시 인구 통계 분석",
    page_icon="📊",
    layout="wide"
)

# ----------------------------------------
# 2. 한글 폰트 설정
# ----------------------------------------

font_paths = glob.glob(
    "/usr/share/fonts/**/*NanumGothic.ttf",
    recursive=True
)

if font_paths:
    fm.fontManager.addfont(font_paths[0])

    font_name = fm.FontProperties(
        fname=font_paths[0]
    ).get_name()

    mpl.rcParams["font.family"] = font_name

mpl.rcParams["axes.unicode_minus"] = False

# 그래프 공통 색상
LINE_COLOR = "#719E99"
MARKER_COLOR = "#A8C5BF"
BAR_COLOR = "#8BAFA8"
BACKGROUND_COLOR = "#FAFAF8"

# ----------------------------------------
# 3. 제목
# ----------------------------------------

st.title("📊 서울시 인구 통계 분석")

st.write(
    "서울시 행정구역별 인구 현황과 "
    "연령대별 인구 분포를 분석합니다."
)

st.divider()

# ----------------------------------------
# 4. 데이터 불러오기
# ----------------------------------------

@st.cache_data
def load_data():

    df = pd.read_csv(
        "population.csv",
        encoding="cp949"
    )

    df.columns = df.columns.str.strip()

    # 행정구역 이름 정리
    df["행정구역"] = (
        df["행정구역"]
        .astype(str)
        .str.replace(
            r"\s*\(\d+\)\s*$",
            "",
            regex=True
        )
        .str.strip()
    )

    # 서울특별시라는 접두어 제거
    df["행정구역"] = df["행정구역"].apply(
        lambda x: re.sub(
            r"^서울특별시\s*",
            "",
            x
        ).strip()
        if x != "서울특별시"
        else x
    )

    # 인구수 숫자 변환
    for col in df.columns[1:]:

        df[col] = pd.to_numeric(
            df[col]
            .astype(str)
            .str.replace(",", "", regex=False),
            errors="coerce"
        )

    return df


try:
    df = load_data()

except Exception as e:
    st.error(f"데이터를 불러오지 못했습니다: {e}")
    st.stop()

# ----------------------------------------
# 5. 기본 선택창
# ----------------------------------------

st.subheader("🔎 분석 조건 선택")

col1, col2, col3 = st.columns(3)

with col1:

    region = st.selectbox(
        "행정구역 선택",
        df["행정구역"].tolist()
    )

with col2:

    gender = st.selectbox(
        "성별 선택",
        ["계", "남", "여"]
    )

with col3:

    year = st.selectbox(
        "연도 선택",
        [2020, 2021, 2022, 2023, 2024, 2025]
    )

# ----------------------------------------
# 6. 연령대 목록
# ----------------------------------------

age_columns = [
    "0~9세",
    "10~19세",
    "20~29세",
    "30~39세",
    "40~49세",
    "50~59세",
    "60~69세",
    "70~79세",
    "80~89세",
    "90~99세",
    "100세 이상"
]

# ----------------------------------------
# 7. 선택한 행정구역 데이터
# ----------------------------------------

selected = df[
    df["행정구역"] == region
]

if selected.empty:

    st.error("해당 행정구역을 찾을 수 없습니다.")
    st.stop()

selected = selected.iloc[0]

# ----------------------------------------
# 8. 연령별 인구 데이터 추출
# ----------------------------------------

population = []

for age in age_columns:

    column_name = f"{year}년_{gender}_{age}"

    if column_name not in df.columns:

        st.error(
            f"데이터 열을 찾을 수 없습니다: {column_name}"
        )

        st.stop()

    population.append(
        selected[column_name]
    )

chart_data = pd.DataFrame({
    "나이": age_columns,
    "인구수": population
})

if chart_data["인구수"].isna().any():

    st.error("인구 데이터에 비어 있는 값이 있습니다.")
    st.stop()

# ----------------------------------------
# 9. 선택 정보 표시
# ----------------------------------------

st.divider()

st.subheader(
    f"📍 {region} / {gender} / {year}년"
)

# ----------------------------------------
# 10. 총인구수 표시
# ----------------------------------------

total_col = f"{year}년_{gender}_총인구수"

total_population = selected[total_col]

st.metric(
    label="선택한 지역의 총인구수",
    value=f"{int(total_population):,}명"
)

# ----------------------------------------
# 11. 연령별 꺾은선 그래프
# ----------------------------------------

st.subheader("📈 연령별 인구 분포")

st.caption(
    "가로축은 나이, 세로축은 인구수입니다."
)

population_thousand = [
    value / 1000
    for value in population
]

fig1, ax1 = plt.subplots(figsize=(13, 6))

ax1.plot(
    range(len(age_columns)),
    population_thousand,
    color=LINE_COLOR,
    linewidth=2.5,
    marker="o",
    markersize=7,
    markerfacecolor=MARKER_COLOR,
    markeredgecolor=LINE_COLOR
)

ax1.set_title(
    f"{region} {gender} {year}년 연령별 인구",
    fontsize=16,
    pad=20
)

ax1.set_xlabel("나이", fontsize=12)
ax1.set_ylabel("인구수 (천 명)", fontsize=12)

ax1.set_xticks(range(len(age_columns)))
ax1.set_xticklabels(age_columns, fontsize=9)

# 세로축 100천 명 단위
max_pop = max(population_thousand)

y_max = max(
    100,
    math.ceil(max_pop / 100) * 100
)

ax1.set_ylim(0, y_max)

ax1.set_yticks(
    range(0, int(y_max) + 1, 100)
)

ax1.grid(
    axis="both",
    linestyle="--",
    linewidth=0.8,
    alpha=0.4
)

fig1.patch.set_facecolor(BACKGROUND_COLOR)
ax1.set_facecolor(BACKGROUND_COLOR)

ax1.spines["top"].set_visible(False)
ax1.spines["right"].set_visible(False)

plt.tight_layout()

st.pyplot(fig1, use_container_width=True)

plt.close(fig1)

# ----------------------------------------
# 12. 연도별 인구 변화 그래프
# ----------------------------------------

st.divider()

st.subheader("📉 연도별 인구 변화")

st.caption(
    "선택한 행정구역과 성별을 기준으로 "
    "2020년부터 2025년까지의 인구 변화를 나타냅니다."
)

year_population = []

for y in range(2020, 2026):

    col_name = f"{y}년_{gender}_총인구수"

    year_population.append(
        selected[col_name]
    )

year_thousand = [
    value / 1000
    for value in year_population
]

fig2, ax2 = plt.subplots(figsize=(13, 5))

ax2.plot(
    range(2020, 2026),
    year_thousand,
    color=LINE_COLOR,
    linewidth=2.5,
    marker="o",
    markersize=7,
    markerfacecolor=MARKER_COLOR,
    markeredgecolor=LINE_COLOR
)

ax2.set_title(
    f"{region} {gender} 연도별 인구 변화",
    fontsize=16,
    pad=20
)

ax2.set_xlabel("연도")
ax2.set_ylabel("인구수 (천 명)")

ax2.set_xticks(range(2020, 2026))

year_min = min(year_thousand)
year_max = max(year_thousand)

# 변화 추이를 보기 위한 여유 범위
interval = 100
lower = max(0, math.floor(year_min / interval) * interval - interval)
upper = math.ceil(year_max / interval) * interval + interval

if upper <= lower:
    upper = lower + interval

ax2.set_ylim(lower, upper)

ax2.set_yticks(
    range(
        int(lower),
        int(upper) + 1,
        interval
    )
)

ax2.grid(
    axis="both",
    linestyle="--",
    linewidth=0.8,
    alpha=0.4
)

fig2.patch.set_facecolor(BACKGROUND_COLOR)
ax2.set_facecolor(BACKGROUND_COLOR)

ax2.spines["top"].set_visible(False)
ax2.spines["right"].set_visible(False)

plt.tight_layout()

st.pyplot(fig2, use_container_width=True)

plt.close(fig2)

# ----------------------------------------
# 13. 신규 기능: 연령대 선택
# ----------------------------------------

st.divider()

st.subheader("🏆 연령대별 인구가 많은 행정구역")

st.write(
    "원하는 연령대를 선택하면 서울시 25개 자치구 중 "
    "해당 연령대의 인구가 가장 많은 상위 10개 지역을 보여줍니다."
)

selected_age = st.selectbox(
    "비교할 연령대 선택",
    age_columns,
    key="ranking_age"
)

# ----------------------------------------
# 14. 자치구별 인구 데이터 추출
# ----------------------------------------

# 서울특별시 전체 행 제외
district_df = df[
    df["행정구역"] != "서울특별시"
].copy()

age_col = f"{year}년_{gender}_{selected_age}"

if age_col not in district_df.columns:

    st.error("선택한 연령대의 데이터가 없습니다.")
    st.stop()

# 선택한 연령대의 인구수 추출
ranking_df = district_df[
    ["행정구역", age_col]
].copy()

ranking_df = ranking_df.rename(
    columns={
        age_col: "인구수"
    }
)

if ranking_df["인구수"].isna().any():

    st.error("자치구 인구 데이터에 결측값이 있습니다.")
    st.stop()

# 인구수가 많은 순서대로 정렬
ranking_df = ranking_df.sort_values(
    by="인구수",
    ascending=False
)

# 상위 10개 지역 선택
top10_df = ranking_df.head(10).copy()

# ----------------------------------------
# 15. 상위 10개 자치구 막대 그래프
# ----------------------------------------

st.caption(
    f"기준: {year}년 / {gender} / {selected_age}"
)

fig3, ax3 = plt.subplots(figsize=(12, 6))

# 천 명 단위로 변환
bar_values = top10_df["인구수"] / 1000

ax3.barh(
    top10_df["행정구역"].iloc[::-1],
    bar_values.iloc[::-1],
    color=BAR_COLOR,
    height=0.65
)

ax3.set_title(
    f"{selected_age} 인구가 많은 자치구 TOP 10",
    fontsize=16,
    pad=20
)

ax3.set_xlabel("인구수 (천 명)")
ax3.set_ylabel("행정구역")

# 세로축(수평 막대 길이) 100천 명 단위
bar_max = max(bar_values)

x_max = max(
    100,
    math.ceil(bar_max / 100) * 100
)

ax3.set_xlim(0, x_max)

ax3.set_xticks(
    range(0, int(x_max) + 1, 100)
)

ax3.grid(
    axis="x",
    linestyle="--",
    linewidth=0.8,
    alpha=0.4
)

ax3.set_axisbelow(True)

fig3.patch.set_facecolor(BACKGROUND_COLOR)
ax3.set_facecolor(BACKGROUND_COLOR)

ax3.spines["top"].set_visible(False)
ax3.spines["right"].set_visible(False)

# 막대 끝에 인구수 표시
for i, value in enumerate(bar_values.iloc[::-1]):

    ax3.text(
        value + x_max * 0.01,
        i,
        f"{int(value):,}",
        va="center",
        fontsize=9
    )

plt.tight_layout()

st.pyplot(fig3, use_container_width=True)

plt.close(fig3)

# ----------------------------------------
# 16. 자치구별 순위 데이터 표
# ----------------------------------------

st.subheader("📋 자치구별 인구 순위")

display_ranking = ranking_df.copy()

display_ranking.insert(
    0,
    "순위",
    range(1, len(display_ranking) + 1)
)

display_ranking["인구수"] = (
    display_ranking["인구수"]
    .map(lambda x: f"{int(x):,}명")
)

st.dataframe(
    display_ranking,
    use_container_width=True,
    hide_index=True
)

# ----------------------------------------
# 17. 연령별 인구 데이터 표
# ----------------------------------------

st.divider()

st.subheader("📋 선택 지역의 연령별 인구 데이터")

display_data = chart_data.copy()

display_data["인구수"] = (
    display_data["인구수"]
    .map(lambda x: f"{int(x):,}명")
)

st.dataframe(
    display_data,
    use_container_width=True,
    hide_index=True
)

# ----------------------------------------
# 18. 출처
# ----------------------------------------

st.caption(
    "자료: population.csv | "
    "서울시 행정구역별 인구 통계"
)
