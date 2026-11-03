
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# =====================================
# 1. 페이지 설정
# =====================================
st.set_page_config(
    page_title="세계 국가별 MBTI 분석",
    page_icon="🌎",
    layout="wide"
)

st.title("🌎 세계 국가별 MBTI 분석")
st.write("국가를 선택하면 해당 국가의 MBTI 16가지 유형별 비율을 확인할 수 있습니다.")

# =====================================
# 2. CSV 파일 불러오기
# =====================================
@st.cache_data
def load_data():
    # 프로젝트 최상위 폴더에서 CSV 파일 찾기
    file_path = Path(__file__).resolve().parent.parent / "countriesMBTI_16types.csv"

    if not file_path.exists():
        raise FileNotFoundError(
            f"CSV 파일을 찾을 수 없습니다: {file_path}"
        )

    data = pd.read_csv(file_path, encoding="utf-8-sig")

    if "Country" not in data.columns:
        raise ValueError("Country 열이 없습니다.")

    mbti_columns = [
        col for col in data.columns if col != "Country"
    ]

    if len(mbti_columns) != 16:
        raise ValueError("MBTI 데이터 열이 16개가 아닙니다.")

    for col in mbti_columns:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    data = data.dropna(subset=["Country"])
    data[mbti_columns] = data[mbti_columns].fillna(0)

    # 소수 비율을 백분율로 변환
    if data[mbti_columns].max().max() <= 1:
        data[mbti_columns] = data[mbti_columns] * 100

    return data, mbti_columns


try:
    df, mbti_columns = load_data()

except Exception as e:
    st.error(f"데이터를 불러올 수 없습니다: {e}")
    st.stop()

# =====================================
# 3. 국가 선택
# =====================================
countries = sorted(df["Country"].unique())

selected_country = st.selectbox(
    "🌍 분석할 국가를 선택하세요.",
    countries
)

# =====================================
# 4. 선택한 국가의 MBTI 데이터 정리
# =====================================
country_data = df[
    df["Country"] == selected_country
][mbti_columns].iloc[0]

ranked = country_data.sort_values(
    ascending=False
).reset_index()

ranked.columns = ["MBTI", "비율"]

ranked["순위"] = range(1, 17)

# =====================================
# 5. 가장 높은 MBTI 표시
# =====================================
top_mbti = ranked.iloc[0]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("선택한 국가", selected_country)

with col2:
    st.metric("가장 높은 MBTI", top_mbti["MBTI"])

with col3:
    st.metric("1위 비율", f'{top_mbti["비율"]:.2f}%')

st.divider()

# =====================================
# 6. 그래프 색상 설정
# =====================================
# 1위: 눈에 띄는 코랄색
# 2~16위: 뒤로 갈수록 채도가 낮아지는 블루 계열

colors = [
    "#FF5252",  # 1위
    "#397DB8",  # 2위
    "#5288BB",
    "#6895BF",
    "#7FA2C5",
    "#91AFCB",
    "#A2BCD1",
    "#B1C7D8",
    "#BFD1DE",
    "#CADAE4",
    "#D3E1E9",
    "#DBE7ED",
    "#E2ECF1",
    "#E9F1F4",
    "#EFF5F7",
    "#F4F7F9"   # 16위
]

# =====================================
# 7. 막대그래프 제작
# =====================================
st.subheader(f"📊 {selected_country} MBTI 비율")

fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=ranked["비율"],
        y=ranked["MBTI"],
        orientation="h",
        marker=dict(
            color=colors,
            line=dict(width=0)
        ),
        text=[
            f"{value:.2f}%"
            for value in ranked["비율"]
        ],
        textposition="outside",
        hovertemplate=(
            "<b>%{y}</b><br>"
            "비율: %{x:.2f}%"
            "<extra></extra>"
        )
    )
)

fig.update_layout(
    height=650,
    xaxis_title="MBTI 비율 (%)",
    yaxis_title="MBTI 유형",
    yaxis=dict(
        categoryorder="array",
        categoryarray=ranked["MBTI"].tolist()[::-1]
    ),
    xaxis=dict(
        rangemode="tozero",
        showgrid=True,
        gridcolor="rgba(150,150,150,0.2)"
    ),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(
        l=40,
        r=70,
        t=30,
        b=50
    ),
    showlegend=False
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =====================================
# 8. MBTI 전체 순위표
# =====================================
with st.expander("📋 MBTI 전체 순위 확인하기"):

    display_data = ranked[
        ["순위", "MBTI", "비율"]
    ].copy()

    display_data["비율"] = display_data[
        "비율"
    ].map(lambda x: f"{x:.2f}%")

    st.dataframe(
        display_data,
        hide_index=True,
        use_container_width=True
    )

# =====================================
# 9. 안내 문구
# =====================================
st.caption(
    "※ 제공된 CSV 데이터를 기준으로 분석한 결과입니다. "
    "실제 국가 전체 인구의 MBTI 분포를 확정하는 통계는 아닙니다."
)
