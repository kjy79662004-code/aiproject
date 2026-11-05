
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import koreanize_matplotlib
import math

# --------------------------------
# 1. 페이지 설정
# --------------------------------

st.set_page_config(
    page_title="서울시 인구 통계 그래프",
    page_icon="📊",
    layout="wide"
)

st.title("📊 서울시 연령별 인구 통계")
st.write("행정구역, 성별, 연도를 선택하여 연령별 인구를 확인할 수 있습니다.")

# --------------------------------
# 2. 데이터 불러오기
# --------------------------------

@st.cache_data
def load_data():

    df = pd.read_csv(
        "population.csv",
        encoding="cp949"
    )

    # 행정구역 이름 정리
    df["행정구역"] = (
        df["행정구역"]
        .astype(str)
        .str.replace(r"\s*\(\d+\)\s*$", "", regex=True)
        .str.strip()
    )

    # 인구수 쉼표 제거 및 숫자 변환
    for col in df.columns[1:]:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(",", "", regex=False),
            errors="coerce"
        )

    return df


df = load_data()

# --------------------------------
# 3. 선택 항목 설정
# --------------------------------

st.subheader("🔎 검색 조건 선택")

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
# 4. 연령별 데이터 추출
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

# 선택한 행정구역 검색
selected_data = df[
    df["행정구역"] == region
]

if selected_data.empty:
    st.error("선택한 행정구역의 데이터를 찾을 수 없습니다.")
    st.stop()

selected_data = selected_data.iloc[0]

# 연령별 인구수 가져오기
population = []

for age in age_columns:

    column_name = f"{year}년_{gender}_{age}"

    if column_name not in df.columns:
        st.error(f"데이터 열을 찾을 수 없습니다: {column_name}")
        st.stop()

    value = selected_data[column_name]

    population.append(value)

# 데이터프레임 생성
chart_data = pd.DataFrame({
    "나이": age_columns,
    "인구수": population
})

# 결측치 확인
if chart_data["인구수"].isna().any():
    st.error("인구 데이터에 비어 있는 값이 있습니다.")
    st.stop()

# --------------------------------
# 5. 선택 정보 표시
# --------------------------------

st.divider()

st.subheader(
    f"📍 {region} / {gender} / {year}년"
)

st.caption(
    "연령별 인구수는 10세 단위로 구분됩니다."
)

# --------------------------------
# 6. 꺾은선 그래프 만들기
# --------------------------------

fig, ax = plt.subplots(figsize=(13, 6))

# 눈이 편안한 차분한 청록색
line_color = "#719E99"

# 인구수 천 명 단위로 변환
population_thousand = [
    value / 1000 for value in population
]

# 꺾은선 그래프
ax.plot(
    range(len(age_columns)),
    population_thousand,
    color=line_color,
    linewidth=2.5,
    marker="o",
    markersize=7,
    markerfacecolor="#A8C5BF",
    markeredgecolor=line_color
)

# 제목과 축 이름
ax.set_title(
    f"{region} {gender} {year}년 연령별 인구",
    fontsize=17,
    pad=20
)

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
# 7. 가로축 설정
# --------------------------------

ax.set_xticks(range(len(age_columns)))

ax.set_xticklabels(
    age_columns,
    rotation=0,
    fontsize=9
)

# 각 연령대마다 세로 구분선
ax.grid(
    axis="x",
    linestyle=":",
    linewidth=0.8,
    alpha=0.5
)

# --------------------------------
# 8. 세로축 설정
# --------------------------------

max_population = max(population_thousand)

# 100단위로 최대값 올림
y_max = max(
    100,
    math.ceil(max_population / 100) * 100
)

# 100단위 눈금 설정
ax.set_yticks(
    range(0, int(y_max) + 1, 100)
)

ax.set_ylim(
    0,
    y_max
)

# 가로 구분선
ax.grid(
    axis="y",
    linestyle="--",
    linewidth=0.8,
    alpha=0.5
)

# --------------------------------
# 9. 그래프 디자인
# --------------------------------

# 배경색
fig.patch.set_facecolor("#FAFAF8")
ax.set_facecolor("#FAFAF8")

# 테두리 정리
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.spines["left"].set_color("#CCCCCC")
ax.spines["bottom"].set_color("#CCCCCC")

# 여백 조절
plt.tight_layout()

# Streamlit에 그래프 출력
st.pyplot(fig, use_container_width=True)

plt.close(fig)

# --------------------------------
# 10. 인구 데이터 표
# --------------------------------

st.divider()

st.subheader("📋 연령별 인구 데이터")

display_data = chart_data.copy()

display_data["인구수"] = display_data["인구수"].map(
    lambda x: f"{int(x):,}명"
)

st.dataframe(
    display_data,
    use_container_width=True,
    hide_index=True
)

st.caption(
    "자료: population.csv | 인구수는 명 단위이며, "
    "그래프 세로축은 천 명 단위입니다."
)
