
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


# -----------------------------------------
# 1. 페이지 기본 설정
# -----------------------------------------
st.set_page_config(
    page_title="월평균 기온 분석 및 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월평균 기온 분석 및 예측")
st.write(
    "과거 기온 데이터를 분석하고 다양한 회귀 알고리즘으로 "
    "미래의 평균기온을 예측해 보세요."
)

st.divider()


# -----------------------------------------
# 2. CSV 데이터 불러오기
# -----------------------------------------
@st.cache_data
def load_data():

    file_path = Path("temperature.csv")

    if not file_path.exists():
        file_path = Path("temperature(1).csv")

    if not file_path.exists():
        raise FileNotFoundError(
            "temperature.csv 파일을 찾을 수 없습니다."
        )

    try:
        data = pd.read_csv(file_path, encoding="cp949")

    except UnicodeDecodeError:
        data = pd.read_csv(file_path, encoding="utf-8-sig")

    # 날짜 변환
    data["일시"] = pd.to_datetime(
        data["일시"],
        format="%b-%y",
        errors="coerce"
    )

    # 평균기온 숫자 변환
    data["평균기온(℃)"] = pd.to_numeric(
        data["평균기온(℃)"],
        errors="coerce"
    )

    # 결측값 제거
    data = data.dropna(
        subset=["일시", "평균기온(℃)"]
    )

    # 연도와 월 추출
    data["연도"] = data["일시"].dt.year
    data["월"] = data["일시"].dt.month

    return data.sort_values("일시")


try:
    df = load_data()

except Exception as e:
    st.error(f"데이터를 불러오지 못했습니다: {e}")
    st.stop()


# -----------------------------------------
# 3. 사용자 입력
# -----------------------------------------
month_names = {
    1: "1월", 2: "2월", 3: "3월",
    4: "4월", 5: "5월", 6: "6월",
    7: "7월", 8: "8월", 9: "9월",
    10: "10월", 11: "11월", 12: "12월"
}

st.subheader("🔎 분석 조건 선택")

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


# -----------------------------------------
# 4. 회귀 알고리즘 선택
# -----------------------------------------
st.subheader("🤖 회귀 알고리즘 선택")

algorithm = st.selectbox(
    "사용할 예측 알고리즘을 선택하세요.",
    options=[
        "선형회귀 (Linear Regression)",
        "랜덤 포레스트 회귀 (Random Forest Regression)",
        "서포트 벡터 회귀 (SVR)"
    ]
)

# -----------------------------------------
# 5. 선택한 월의 데이터 추출
# -----------------------------------------
monthly_data = df[
    df["월"] == selected_month
].copy()

monthly_data = monthly_data.sort_values("연도")

if len(monthly_data) < 2:
    st.warning(
        "회귀 분석을 위해 최소 2개 이상의 데이터가 필요합니다."
    )
    st.stop()

# X: 연도
# Y: 평균기온
X = monthly_data[["연도"]]
y = monthly_data["평균기온(℃)"]


# -----------------------------------------
# 6. 알고리즘 모델 생성
# -----------------------------------------
if algorithm == "선형회귀 (Linear Regression)":

    model = LinearRegression()

    algorithm_description = """
    선형회귀는 과거 연도와 평균기온 사이의 관계를
    하나의 직선으로 표현하는 알고리즘입니다.

    실제 데이터와 직선 사이의 오차 제곱합이
    최소가 되도록 직선을 계산합니다.
    """

    algorithm_principle = """
    1. 과거 연도와 평균기온 데이터를 수집합니다.
    2. 데이터의 전체적인 직선 경향을 찾습니다.
    3. 실제 기온과 직선 사이의 오차를 최소화합니다.
    4. 계산된 직선을 미래 연도까지 연장하여 예측합니다.
    """

elif algorithm == "랜덤 포레스트 회귀 (Random Forest Regression)":

    model = RandomForestRegressor(
        n_estimators=300,
        random_state=42,
        min_samples_leaf=2
    )

    algorithm_description = """
    랜덤 포레스트 회귀는 여러 개의 결정 트리를 만들어
    각각의 예측 결과를 평균 내는 알고리즘입니다.

    하나의 나무가 아닌 여러 나무의 결과를 종합하여
    최종 예측값을 결정합니다.
    """

    algorithm_principle = """
    1. 과거 기온 데이터를 바탕으로 여러 개의 학습용 데이터를 구성합니다.
    2. 각각의 데이터로 여러 결정 트리를 학습시킵니다.
    3. 각 결정 트리가 예상하는 기온을 계산합니다.
    4. 여러 결정 트리의 예측값을 평균 내어 최종 기온을 예측합니다.
    """

else:

    model = make_pipeline(
        StandardScaler(),
        SVR(
            kernel="rbf",
            C=100,
            epsilon=0.1,
            gamma="scale"
        )
    )

    algorithm_description = """
    서포트 벡터 회귀(SVR)는 실제 데이터와 예측 함수 사이의
    오차를 일정 범위 안으로 유지하면서 적절한 예측 함수를 찾습니다.

    RBF 커널을 사용하여 직선으로 표현하기 어려운
    비선형적인 데이터 관계도 분석할 수 있습니다.
    """

    algorithm_principle = """
    1. 과거 연도와 평균기온 데이터를 입력합니다.
    2. 연도 데이터의 크기를 표준화합니다.
    3. 실제 기온과 예측 함수 사이의 오차 범위를 설정합니다.
    4. 설정한 범위 밖의 오차를 줄이는 예측 함수를 학습합니다.
    5. 학습된 함수를 이용하여 미래 기온을 예측합니다.
    """


# -----------------------------------------
# 7. 알고리즘 학습
# -----------------------------------------
model.fit(X, y)

# 과거 데이터에 대한 예측값
monthly_data["회귀예측기온"] = model.predict(X)

# 미래 연도 예측
future_X = pd.DataFrame({
    "연도": [int(prediction_year)]
})

predicted_temperature = model.predict(
    future_X
)[0]

# 결정계수
r2 = model.score(X, y)


# -----------------------------------------
# 8. 그래프용 예측 데이터 생성
# -----------------------------------------
regression_years = np.arange(
    int(monthly_data["연도"].min()),
    int(prediction_year) + 1
)

regression_X = pd.DataFrame({
    "연도": regression_years
})

regression_temperatures = model.predict(
    regression_X
)


# -----------------------------------------
# 9. 예측 결과 표시
# -----------------------------------------
st.divider()

st.subheader(
    f"📊 {month_names[selected_month]} 평균기온 분석 결과"
)

result1, result2, result3 = st.columns(3)

with result1:
    st.metric(
        "예측 연도",
        f"{int(prediction_year)}년"
    )

with result2:
    st.metric(
        "예측 평균기온",
        f"{predicted_temperature:.2f} ℃"
    )

with result3:
    st.metric(
        "결정계수 (R²)",
        f"{r2:.3f}"
    )


# -----------------------------------------
# 10. 그래프 작성
# -----------------------------------------
fig = go.Figure()

# 실제 평균기온
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

# 선택한 알고리즘의 예측 추세선
fig.add_trace(go.Scatter(
    x=regression_years,
    y=regression_temperatures,
    mode="lines",
    name="회귀 알고리즘 예측선",
    line=dict(
        color="#B04444",
        width=3
    ),
    hovertemplate=
    "연도: %{x}년<br>" +
    "예측 기온: %{y:.2f}℃<extra></extra>"
))

# 미래 예측 지점
fig.add_trace(go.Scatter(
    x=[int(prediction_year)],
    y=[predicted_temperature],
    mode="markers",
    name="미래 예측 기온",
    marker=dict(
        color="#E5A000",
        size=17,
        symbol="star"
    ),
    hovertemplate=
    "예측 연도: %{x}년<br>" +
    "예측 기온: %{y:.2f}℃<extra></extra>"
))

# 미래 예측 연도 표시
fig.add_vline(
    x=int(prediction_year),
    line_width=1.5,
    line_dash="dash",
    line_color="#E5A000"
)

fig.update_layout(
    title=(
        f"{month_names[selected_month]} 평균기온 "
        f"- {algorithm}"
    ),
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

st.plotly_chart(
    fig,
    use_container_width=True
)


# -----------------------------------------
# 11. 알고리즘 설명
# -----------------------------------------
st.divider()

st.subheader("📖 선택한 회귀 알고리즘 알아보기")

st.markdown(
    f"### {algorithm}"
)

st.write(algorithm_description)

st.subheader("🔍 알고리즘 작동 순서")

st.write(algorithm_principle)

# 선형회귀일 때만 회귀식 표시
if algorithm == "선형회귀 (Linear Regression)":

    st.subheader("📐 선형회귀 계산식")

    slope = model.coef_[0]
    intercept = model.intercept_

    st.latex(r"\hat{y} = b_0 + b_1x")

    st.write(
        f"회귀식: ŷ = {intercept:.4f} + ({slope:.4f} × 연도)"
    )

    st.write(
        f"기울기: {slope:.4f} ℃/년"
    )

    if slope > 0:
        st.info("과거 데이터에서 장기적인 상승 경향이 나타납니다.")
    elif slope < 0:
        st.info("과거 데이터에서 장기적인 하락 경향이 나타납니다.")
    else:
        st.info("과거 데이터에서 뚜렷한 기온 변화 경향이 없습니다.")

elif algorithm == "랜덤 포레스트 회귀 (Random Forest Regression)":

    st.subheader("🌳 랜덤 포레스트의 구성")

    st.write(
        f"현재 모델은 총 {model.n_estimators}개의 결정 트리를 사용합니다."
    )

    st.write(
        "각 트리가 예측한 기온을 평균 내어 최종 예측 결과를 만듭니다."
    )

elif algorithm == "서포트 벡터 회귀 (SVR)":

    st.subheader("📈 SVR의 주요 설정")

    st.write("사용한 커널: RBF (비선형 커널)")
    st.write("오차 허용 범위: ε = 0.1")
    st.write("규제 매개변수: C = 100")

    st.write(
        "SVR은 실제 데이터와 예측 함수 사이의 오차를 "
        "조절하면서 적절한 예측 함수를 학습합니다."
    )


# -----------------------------------------
# 12. 결정계수 설명
# -----------------------------------------
st.divider()

st.subheader("📊 결정계수 (R²)란?")

st.write("""
결정계수는 모델이 학습에 사용한 실제 기온 데이터의
변동을 얼마나 설명하는지를 나타내는 지표입니다.

일반적으로 1에 가까울수록 학습 데이터에 대한 설명력이 높습니다.

단, 결정계수가 높다고 미래 예측까지 정확하다는 의미는 아닙니다.
""")

st.metric(
    "현재 모델의 학습 데이터 결정계수",
    f"{r2:.4f}"
)


# -----------------------------------------
# 13. 알고리즘 사용 시 주의사항
# -----------------------------------------
st.warning("""
주의사항

1. 선형회귀는 직선적인 기온 변화 경향을 이용합니다.
2. 랜덤 포레스트는 학습 데이터 범위 밖의 새로운 연도에 대해
   기존 데이터의 예측 범위를 크게 벗어나지 못하는 특성이 있습니다.
3. SVR의 RBF 커널도 학습 범위를 벗어나면 예측값이 평균적인
   값에 가까워질 수 있습니다.

따라서 랜덤 포레스트와 SVR은 과거 데이터의 패턴을 분석하는 데
유용하지만, 먼 미래의 기온을 예측할 때는 한계가 있습니다.
실제 미래 기온과는 차이가 발생할 수 있습니다.
""")


# -----------------------------------------
# 14. 실제 데이터 확인
# -----------------------------------------
with st.expander("📁 분석에 사용된 실제 데이터 확인하기"):

    display_data = monthly_data[
        ["연도", "평균기온(℃)", "회귀예측기온"]
    ].copy()

    display_data.columns = [
        "연도",
        "실제 평균기온(℃)",
        "알고리즘 예측기온(℃)"
    ]

    st.dataframe(
        display_data.round(2),
        use_container_width=True,
        hide_index=True
    )


st.caption(
    "본 프로그램은 temperature.csv의 월평균 기온 데이터를 "
    "이용하여 3가지 회귀 알고리즘으로 분석합니다."
)
