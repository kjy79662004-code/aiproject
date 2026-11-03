from pathlib import Path
import zipfile, shutil, os, textwrap

outdir = Path("/mnt/data/mbti_streamlit_app")
outdir.mkdir(exist_ok=True)

app_code = r'''import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# -----------------------------
# 기본 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="세계 국가별 MBTI 비율",
    page_icon="🌎",
    layout="wide"
)

st.title("🌎 세계 국가별 MBTI 비율")
st.caption("국가를 선택하면 해당 국가의 MBTI 16가지 유형별 비율을 확인할 수 있습니다.")

# -----------------------------
# 데이터 불러오기
# app.py와 countriesMBTI_16types.csv를 같은 폴더에 넣어주세요.
# -----------------------------
@st.cache_data
def load_data():
    data = pd.read_csv("countriesMBTI_16types.csv", encoding="utf-8-sig")

    if "Country" not in data.columns:
        raise ValueError("CSV 파일에 'Country' 열이 없습니다.")

    mbti_columns = [column for column in data.columns if column != "Country"]

    if len(mbti_columns) != 16:
        raise ValueError(
            f"MBTI 열은 16개여야 하지만 현재 {len(mbti_columns)}개입니다."
        )

    for column in mbti_columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    data = data.dropna(subset=["Country"])
    data[mbti_columns] = data[mbti_columns].fillna(0)

    # 원본 데이터가 0.0463처럼 소수 비율로 저장되어 있어 백분율로 변환
    # 값이 이미 1보다 큰 경우에는 백분율 데이터로 간주
    max_value = data[mbti_columns].to_numpy().max()
    if max_value <= 1:
        data[mbti_columns] = data[mbti_columns] * 100

    return data, mbti_columns


try:
    df, mbti_columns = load_data()
except FileNotFoundError:
    st.error(
        "CSV 파일을 찾을 수 없습니다. "
        "'countriesMBTI_16types.csv' 파일을 app.py와 같은 폴더에 넣어주세요."
    )
    st.stop()
except Exception as error:
    st.error(f"데이터를 불러오는 중 문제가 발생했습니다: {error}")
    st.stop()

# -----------------------------
# 국가 선택
# -----------------------------
countries = sorted(df["Country"].astype(str).unique().tolist())

col1, col2 = st.columns([2, 1])
with col1:
    selected_country = st.selectbox("국가 선택", countries)
with col2:
    st.metric("분석 국가 수", f"{len(countries)}개")
    st.metric("MBTI 유형 수", f"{len(mbti_columns)}개")

# -----------------------------
# 선택한 국가 데이터 정렬
# -----------------------------
country_data = df.loc[df["Country"].astype(str) == selected_country, mbti_columns]

if country_data.empty:
    st.warning("선택한 국가의 데이터를 찾을 수 없습니다.")
    st.stop()

ranked = (
    country_data.iloc[0]
    .sort_values(ascending=False)
    .rename_axis("MBTI")
    .reset_index(name="비율")
)

ranked["순위"] = range(1, len(ranked) + 1)

# 1위는 선명한 코랄색, 나머지는 순위가 낮아질수록 채도가 낮은 블루 계열
colors = ["#FF5B5B"]
remaining_colors = [
    "#477FB8", "#5689BC", "#6593C0", "#759DC4",
    "#84A7C8", "#93B1CC", "#A2BBD0", "#AEC4D5",
    "#B8CBD9", "#C1D2DE", "#CAD9E3", "#D2DFE8",
    "#DAE5EC", "#E2EBF0", "#EAF1F5"
]
colors.extend(remaining_colors[:len(ranked) - 1])

# -----------------------------
# 핵심 결과
# -----------------------------
top_mbti = ranked.iloc[0]
metric1, metric2, metric3 = st.columns(3)

with metric1:
    st.metric("가장 높은 MBTI", top_mbti["MBTI"])
with metric2:
    st.metric("1위 비율", f'{top_mbti["비율"]:.2f}%')
with metric3:
    st.metric("선택한 국가", selected_country)

st.divider()
st.subheader(f"📊 {selected_country}의 MBTI 비율")

fig = go.Figure(
    go.Bar(
        x=ranked["비율"],
        y=ranked["MBTI"],
        orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"{value:.2f}%" for value in ranked["비율"]],
        textposition="outside",
        cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>비율: %{x:.2f}%<extra></extra>"
    )
)

fig.update_layout(
    height=620,
    xaxis_title="비율 (%)",
    yaxis_title="MBTI 유형",
    yaxis=dict(
        categoryorder="array",
        categoryarray=ranked["MBTI"].tolist()[::-1]
    ),
    xaxis=dict(
        rangemode="tozero",
        showgrid=True,
        gridcolor="rgba(128,128,128,0.18)"
    ),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=30, r=65, t=25, b=45),
    font=dict(size=13),
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# 전체 순위 표
# -----------------------------
with st.expander("📋 MBTI 비율 전체 순위 보기"):
    display_data = ranked[["순위", "MBTI", "비율"]].copy()
    display_data["비율"] = display_data["비율"].map(lambda value: f"{value:.2f}%")
    st.dataframe(display_data, hide_index=True, use_container_width=True)

st.caption(
    "※ 그래프는 제공된 CSV 데이터의 비율을 백분율로 표시한 것입니다. "
    "자료의 조사 방식이나 대표성은 별도로 확인해야 합니다."
)
'''

requirements = """streamlit
pandas
plotly
"""

(outdir / "app.py").write_text(app_code, encoding="utf-8")
(outdir / "requirements.txt").write_text(requirements, encoding="utf-8")
shutil.copy2("/mnt/data/countriesMBTI_16types.csv", outdir / "countriesMBTI_16types.csv")

zip_path = Path("/mnt/data/mbti_streamlit_cloud.zip")
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    for filename in ["app.py", "requirements.txt", "countriesMBTI_16types.csv"]:
        z.write(outdir / filename, arcname=filename)

print("생성 완료:")
print(outdir / "app.py")
print(outdir / "requirements.txt")
print(zip_path)
