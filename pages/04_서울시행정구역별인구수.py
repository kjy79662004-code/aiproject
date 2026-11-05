
import os
import math
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib as mpl

# --------------------------------
# 1. 페이지 설정
# --------------------------------

st.set_page_config(
    page_title="서울시 연령별 인구 통계",
    page_icon="📊",
    layout="wide"
)

# --------------------------------
# 2. 한글 폰트 설정
# --------------------------------

font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"

if os.path.exists(font_path):
    font_name = fm.FontProperties(
        fname=font_path
    ).get_name()

    mpl.rcParams["font.family"] = font_name

mpl.rcParams["axes.unicode_minus"] = False

# --------------------------------
# 3. 제목
# --------------------------------

st.title("📊 서울시 연령별 인구 통계")
st.write(
    "행정구역, 성별, 연도를 선택하여 "
    "연령별 인구수를 확인할 수 있습니다."
)

# --------------------------------
# 4. CSV 데이터 불러오기
# --------------------------------

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

    # 인구수 쉼표 제거
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

# --------------------------------
# 5. 선택창 만들기
# --------------------------------

st.subheader("🔎 검색 조건")

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

# --------------------------------
# 6. 선택한 데이터 추출
# --------------------------------

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

selected = df[
    df["행정구역"] == region
]

if selected.empty:
    st.error("해당 행정구역을 찾을 수 없습니다.")
    st.stop()

selected = selected.iloc[0]

population = []

for age in age_columns:

    column_name = f"{year}년_{gender}_{age}"

    if column_name not in df.columns:
        st.error(
            f"데이터 열을 찾을 수 없습니다: {column_name}"
        )
        st.stop()

    population.append(selected[column_name])

chart_data = pd.DataFrame({
    "나이": age_columns,
    "인구수": population
})

if chart_data["인구수"].isna().any():
    st.error("인구 데이터에 비어 있는 값이 있습니다.")
    st.stop()

# --------------------------------
# 7. 선택 정보 출력
# --------------------------------

st.divider()

st.subheader(
    f"📍 {region} / {gender} / {year}년"
)

st.caption(
    "연령대별 인구수를 10세 단위로 나타냅니다."
)

# --------------------------------
# 8. 그래프 데이터 변환
# --------------------------------

# 천 명 단위로 변환
population_thousand = [
    value / 1000
    for value in population
]

# --------------------------------
# 9. 꺾은선 그래프
# --------------------------------

fig, ax = plt.subplots(figsize=(13, 6))

# 차분한 청록색
line_color = "#719E99"
marker_color = "#A8C5BF"

ax.plot(
    range(len(age_columns)),
    population_thousand,
    color=line_color,
    linewidth=2.5,
    marker="o",
    markersize=7,
    markerfacecolor=marker_color,
    markeredgecolor=line_color
)

# 그래프 제목
ax.set_title(
    f"{region} {gender} {year}년 연령별 인구",
    fontsize=17,
    pad=20
)

# 축 제목
ax.set_xlabel(
    "나이",
    fontsize=12,
    labelpad=12
)

ax.set_ylabel(
    "인구수 (천 명)",
    fontsize=12,
    labelpad=12
)

# --------------------------------
# 10. 가로축 설정
# --------------------------------

ax.set_xticks(range(len(age_columns)))

ax.set_xticklabels(
    age_columns,
    fontsize=9
)

# 가로축 구분선
ax.grid(
    axis="x",
    linestyle=":",
    linewidth=0.8,
    alpha=0.5
)

# --------------------------------
# 11. 세로축 설정
# --------------------------------

max_population = max(population_thousand)

y_max = max(
    100,
    math.ceil(max_population / 100) * 100
)

ax.set_ylim(0, y_max)

# 100천 명 단위 눈금
ax.set_yticks(
    range(0, int(y_max) + 1, 100)
)

# 세로축 구분선
ax.grid(
    axis="y",
    linestyle="--",
    linewidth=0.8,
    alpha=0.5
)

# --------------------------------
# 12. 그래프 디자인
# --------------------------------

fig.patch.set_facecolor("#FAFAF8")
ax.set_facecolor("#FAFAF8")

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.spines["left"].set_color("#CCCCCC")
ax.spines["bottom"].set_color("#CCCCCC")

plt.tight_layout()

# 그래프 출력
st.pyplot(
    fig,
    use_container_width=True
)

plt.close(fig)

# --------------------------------
# 13. 인구 데이터 표
# --------------------------------

st.divider()

st.subheader("📋 연령별 인구 데이터")

display_data = chart_data.copy()

display_data["인구수"] = display_data[
    "인구수"
].map(
    lambda x: f"{int(x):,}명"
)

st.dataframe(
    display_data,
    use_container_width=True,
    hide_index=True
)

st.caption(
    "자료: population.csv | "
    "그래프 세로축은 천 명 단위입니다."
)
