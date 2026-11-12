
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from pathlib import Path

# ---------------------------------
# 1. 페이지 기본 설정
# ---------------------------------
st.set_page_config(
    page_title="월평균 기온 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월평균 기온 분석 및 예측")
st.write("과거 기온 데이터를 분석하고 선형회귀 알고리즘으로 미래 기온을 예측합니다.")

st.divider()

# ---------------------------------
# 2. CSV 데이터 불러오기
# ---------------------------------
@st.cache_data
def load_data():
    file_path = Path("temperature.csv")

    # 업로드된 파일명을 그대로 사용하는 경우도 지원
    if not file_path.exists():
        file_path = Path("temperature(1).csv")

    if not file_path.exists():
        raise FileNotFoundError(
            "temperature.csv 파일을 프로젝트에 업로드해주세요."
        )

    # 한글 CSV 인코딩 처리
    try:
        data = pd.read_csv(file_path, encoding="cp949")
    except UnicodeDecodeError:
        data = pd.read_csv(file_path, encoding="utf-8-sig")

    # 날짜 데이터 변환
    data["일시"] = pd.to_datetime(
        data["일시"],
        format="%b-%y",
        errors="coerce"
    )

    # 필요한 데이터만 정리
    data = data.dropna(subset=["일시", "평균기온(℃)"])

    data["연도"] = data["일시"].dt.year
    data["월"] = data["일시"].dt.month

    data["평균기온(℃)"] = pd.to_numeric(
        data["평균기온(℃)"],
        errors="coerce"
    )

    data = data.dropna(subset=["평균기온(℃)"])

    return data.sort_values("일시")


try:
    df = load_data()

except Exception as e:
    st.error(f"데이터를 불러오지 못했습니다: {e}")
    st.stop()


# ---------------------------------
# 3. 사용자 입력
# ---------------------------------
month_names = {
    1: "1월", 2: "2월", 3: "3월",
    4: "4월", 5: "5월", 6: "6월",
    7: "7월", 8: "8월", 9: "9월",
    10: "10월", 11: "11월", 12: "12월"
}

st.subheader("🔎 예측 조건 선택")

col1, col2 = st.columns(2)

with col1:
    selected_month = st.selectbox(
        "분석할 월을 선택하세요.",
        options=list(month_names.keys()),
        format_func=lambda x: month_names[x]
    )

with col2:
    last_year = int(df["연도"].max())

    prediction_year = st.number_input(
        "예측할 연도를 입력하세요.",
        min_value=last_year + 1,
        max_value=2100,
        value=last_year + 1,
        step=1
    )

# ---------------------------------
# 4. 선택한 월의 데이터 추출
# ---------------------------------
monthly_data = df[
    df["월"] == selected_month
].copy()

monthly_data = monthly_data.sort_values("연도")

if len(monthly_data) < 2:
    st.warning("선형회귀 분석을 위해 최소 2개 이상의 데이터가 필요합니다.")
    st.stop()

# X: 연도 / Y: 평균기온
X = monthly_data[["연도"]]
y = monthly_data["평균기온(℃)"]

# ---------------------------------
# 5. 선형회귀 알고리즘 학습
# ---------------------------------
model = LinearRegression()

model.fit(X, y)

# 과거 데이터의 예측값
monthly_data["회귀예측기온"] = model.predict(X)

# 사용자가 선택한 미래 연도의 예측값
future_X = pd.DataFrame({
    "연도": [int(prediction_year)]
})

predicted_temperature = model.predict(future_X)[0]

# 회귀식
slope = model.coef_[0]
intercept = model.intercept_
r2 = model.score(X, y)

# ---------------------------------
# 6. 그래프용 회귀 추세선 데이터
# ---------------------------------
regression_years = np.arange(
    int(monthly_data["연도"].min()),
    int(prediction_year) + 1
)

regression_X = pd.DataFrame({
    "연도": regression_years
})

regression_temperatures = model.predict(regression_X)

# ---------------------------------
# 7. 예측 결과 표시
# ---------------------------------
st.divider()
st.subheader(f"📊 {month_names[selected_month]} 평균기온 분석")

result1, result2, result3 = st.columns(3)

result1.metric(
    "예측 연도",
    f"{int(prediction_year)}년"
)

result2.metric(
    "예측 평균기온",
    f"{predicted_temperature:.2f} ℃"
)

result3.metric(
    "결정계수 (R²)",
    f"{r2:.3f}"
)

# ---------------------------------
# 8. 그래프 작성
# ---------------------------------
fig = go.Figure()

# 실제 관측 데이터
fig.add_trace(go.Scatter(
    x=monthly_data["연도"],
    y=monthly_data["평균기온(℃)"],
    mode="markers",
    name="실제 평균기온",
    marker=dict(
        color="#426B9A",
        size=9,
        symbol="circle"
    ),
    hovertemplate=
    "연도: %{x}년<br>" +
    "실제 평균기온: %{y:.2f}℃<extra></extra>"
))

# 선형회귀 추세선
fig.add_trace(go.Scatter(
    x=regression_years,
    y=regression_temperatures,
    mode="lines",
    name="선형회귀 추세선",
    line=dict(
        color="#B04444",
        width=3
    ),
    hovertemplate=
    "연도: %{x}년<br>" +
    "회귀선 기온: %{y:.2f}℃<extra></extra>"
))

# 미래 예측 지점
fig.add_trace(go.Scatter(
    x=[int(prediction_year)],
    y=[predicted_temperature],
    mode="markers",
    name="미래 예측 기온",
    marker=dict(
        color="#E5A000",
        size=16,
        symbol="star"
    ),
    hovertemplate=
    "예측 연도: %{x}년<br>" +
    "예측 기온: %{y:.2f}℃<extra></extra>"
))

# 예측 지점까지 연결하는 점선
fig.add_shape(
    type="line",
    x0=int(prediction_year),
    x1=int(prediction_year),
    y0=min(
        float(monthly_data["평균기온(℃)"].min()),
        float(predicted_temperature)
    ),
    y1=predicted_temperature,
    line=dict(
        color="#E5A000",
        width=1.5,
        dash="dash"
    )
)

# 그래프 설정
fig.update_layout(
    title=f"{month_names[selected_month]} 연도별 평균기온 및 미래 예측",
    xaxis_title="연도",
    yaxis_title="평균기온 (℃)",
    hovermode="x unified",
    template="plotly_white",
    height=550,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0
    ),
    xaxis=dict(
        tickformat="d",
        showgrid=True
    ),
    yaxis=dict(
        ticksuffix="℃",
        showgrid=True
    )
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------
# 9. 선형회귀 알고리즘 설명
# ---------------------------------
st.divider()

st.subheader("📖 선형회귀 알고리즘이란?")

st.write("""
선형회귀는 과거에 수집된 데이터를 분석하여
두 변수 사이의 관계를 직선으로 나타내는 머신러닝 알고리즘입니다.

이번 프로그램에서는 과거의 연도를 독립변수(X)로,
월평균 기온을 종속변수(Y)로 사용합니다.

과거 데이터의 점들과 가장 잘 맞는 직선을 계산한 다음,
그 직선을 미래 연도까지 연장하여 기온을 예측합니다.
""")

st.latex(r"\hat{y} = b_0 + b_1x")

st.markdown("""
- **X** : 연도
- **ŷ** : 알고리즘이 예측한 평균기온
- **b₀** : 절편
- **b₁** : 기울기

기울기가 양수라면 장기적으로 기온이 상승하는 경향을,
음수라면 하락하는 경향을 나타냅니다.
""")

st.subheader("🔍 이번 분석의 선형회귀 계산 결과")

st.write(
    f"회귀식: ŷ = {intercept:.4f} + ({slope:.4f} × 연도)"
)

st.write(
    f"기울기: {slope:.4f} ℃/년"
)

st.write(
    f"결정계수(R²): {r2:.4f}"
)

st.markdown("""
**결정계수(R²)란?**

실제 기온 데이터의 변동을 회귀모델이 얼마나 설명하는지를
나타내는 지표입니다.

1에 가까울수록 과거 데이터에 대한 설명력이 높다는 의미입니다.
단, 결정계수가 높다고 미래 예측까지 정확하다는 뜻은 아닙니다.
""")

st.info(
    "주의: 기온 예측은 과거 데이터의 선형적인 경향을 "
    "이용한 추정값입니다. 실제 미래 기온은 기후 변화, "
    "대기 순환 등 다양한 요인에 따라 달라질 수 있습니다."
)

# ---------------------------------
# 10. 데이터 확인
# ---------------------------------
with st.expander("📁 분석에 사용된 실제 데이터 확인하기"):
    display_data = monthly_data[
        ["연도", "평균기온(℃)", "회귀예측기온"]
    ].copy()

    display_data.columns = [
        "연도",
        "실제 평균기온(℃)",
        "회귀선 계산 기온(℃)"
    ]

    st.dataframe(
        display_data.round(2),
        use_container_width=True,
        hide_index=True
    )

st.caption(
    "본 프로그램은 temperature.csv의 평균기온 데이터를 "
    "기반으로 선형회귀 분석을 수행합니다."
)
