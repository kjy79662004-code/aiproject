
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re

# =====================================
# 1. 페이지 기본 설정
# =====================================

st.set_page_config(
    page_title="월별 기온분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 기온분석")
st.write(
    "원하는 월을 선택하여 1907년부터 2026년까지 "
    "연도별 최고기온과 최저기온을 비교해 보세요."
)


# =====================================
# 2. 데이터 불러오기
# =====================================

@st.cache_data
def load_data():

    encodings = [
        "cp949",
        "euc-kr",
        "utf-8-sig",
        "utf-8"
    ]

    df = None

    # 한글 인코딩 자동 처리
    for encoding in encodings:
        try:
            df = pd.read_csv(
                "temperature.csv",
                encoding=encoding
            )
            break

        except UnicodeDecodeError:
            continue

    if df is None:
        raise ValueError(
            "CSV 파일의 인코딩을 확인해 주세요."
        )

    # 필요한 열 확인
    required_columns = [
        "일시",
        "최고기온(℃)",
        "최저기온(℃)"
    ]

    for col in required_columns:
        if col not in df.columns:
            raise ValueError(
                f"필수 데이터 열이 없습니다: {col}"
            )

    # 기온 데이터를 숫자로 변환
    for col in [
        "최고기온(℃)",
        "최저기온(℃)"
    ]:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    # =====================================
    # 3. 날짜 데이터 정리
    # =====================================

    month_dict = {
        "Jan": 1,
        "Feb": 2,
        "Mar": 3,
        "Apr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12
    }

    def parse_date(value):

        match = re.fullmatch(
            r"\s*(\d{2})-([A-Za-z]{3})\s*",
            str(value)
        )

        if not match:
            return pd.Series([None, None])

        year = int(match.group(1))
        month_name = match.group(2).title()

        month = month_dict.get(month_name)

        if month is None:
            return pd.Series([None, None])

        # 07~99는 1907~1999년
        # 00~26은 2000~2026년
        if year >= 7:
            year += 1900
        else:
            year += 2000

        return pd.Series([year, month])

    # 연도와 월 분리
    df[["연도", "월"]] = df["일시"].apply(
        parse_date
    )

    # 날짜 변환에 실패한 행 제거
    df = df.dropna(
        subset=["연도", "월"]
    )

    df["연도"] = df["연도"].astype(int)
    df["월"] = df["월"].astype(int)

    # =====================================
    # 4. 분석 연도 범위 제한
    # =====================================

    df = df[
        (df["연도"] >= 1907) &
        (df["연도"] <= 2026)
    ].copy()

    return df


# 데이터 불러오기
try:
    df = load_data()

except Exception as e:
    st.error(
        f"데이터를 불러오는 중 오류가 발생했습니다: {e}"
    )
    st.stop()


# =====================================
# 5. 월 선택 기능
# =====================================

month_names = {
    1: "1월",
    2: "2월",
    3: "3월",
    4: "4월",
    5: "5월",
    6: "6월",
    7: "7월",
    8: "8월",
    9: "9월",
    10: "10월",
    11: "11월",
    12: "12월"
}

selected_month = st.selectbox(
    "📅 분석할 월을 선택하세요.",
    options=list(month_names.keys()),
    format_func=lambda x: month_names[x]
)


# =====================================
# 6. 선택한 월의 데이터 분석
# =====================================

filtered_df = df[
    df["월"] == selected_month
].copy()

# 같은 연도에 여러 기록이 있으면 평균 계산
result = (
    filtered_df
    .groupby("연도", as_index=False)
    .agg({
        "최고기온(℃)": "mean",
        "최저기온(℃)": "mean"
    })
    .sort_values("연도")
)

# 최고기온과 최저기온이 모두 없는 행 제거
result = result.dropna(
    subset=[
        "최고기온(℃)",
        "최저기온(℃)"
    ],
    how="all"
)


# =====================================
# 7. 그래프 생성
# =====================================

if result.empty:

    st.warning(
        "선택한 월에 분석할 데이터가 없습니다."
    )

else:

    fig = go.Figure()

    # ---------------------------------
    # 최고기온 그래프
    # ---------------------------------

    fig.add_trace(
        go.Scatter(
            x=result["연도"],
            y=result["최고기온(℃)"],

            mode="lines+markers",

            name="최고기온",

            line=dict(
                color="#B0002A",
                width=3
            ),

            marker=dict(
                color="#B0002A",
                size=7
            ),

            connectgaps=False,

            hovertemplate=
            "연도: %{x}년<br>" +
            "최고기온: %{y:.1f}℃" +
            "<extra></extra>"
        )
    )

    # ---------------------------------
    # 최저기온 그래프
    # ---------------------------------

    fig.add_trace(
        go.Scatter(
            x=result["연도"],
            y=result["최저기온(℃)"],

            mode="lines+markers",

            name="최저기온",

            line=dict(
                color="#007BFF",
                width=3
            ),

            marker=dict(
                color="#007BFF",
                size=7
            ),

            connectgaps=False,

            hovertemplate=
            "연도: %{x}년<br>" +
            "최저기온: %{y:.1f}℃" +
            "<extra></extra>"
        )
    )

    # ---------------------------------
    # 그래프 디자인
    # ---------------------------------

    # 10년 간격으로 연도 표시
    year_ticks = list(
        range(1907, 2027, 10)
    )

    # 마지막 연도 2026년 추가
    if 2026 not in year_ticks:
        year_ticks.append(2026)

    fig.update_layout(

        # 그래프 제목
        title=dict(
            text="월별 기온분석",
            x=0.5,
            xanchor="center",
            font=dict(
                size=25
            )
        ),

        # 가로축
        xaxis=dict(
            title="연도",

            range=[1907, 2026],

            tickmode="array",

            tickvals=year_ticks,

            ticktext=[
                f"{year}년"
                for year in year_ticks
            ],

            showgrid=True
        ),

        # 세로축
        yaxis=dict(
            title="온도(℃)",
            showgrid=True,
            zeroline=True
        ),

        # 범례
        legend=dict(
            title="기온 구분",

            orientation="h",

            yanchor="bottom",
            y=1.02,

            xanchor="center",
            x=0.5
        ),

        # 마우스 올리면 기온 표시
        hovermode="x unified",

        # 그래프 배경
        template="plotly_white",

        # 그래프 크기
        height=550,

        # 여백
        margin=dict(
            l=60,
            r=30,
            t=100,
            b=60
        )
    )

    # 그래프 출력
    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =====================================
# 8. 연도별 기온 데이터 표
# =====================================

with st.expander("📊 연도별 기온 데이터 확인"):

    display_df = result.copy()

    display_df = display_df.rename(
        columns={
            "연도": "연도",
            "최고기온(℃)": "최고기온(℃)",
            "최저기온(℃)": "최저기온(℃)"
        }
    )

    st.dataframe(
        display_df.round(1),
        use_container_width=True,
        hide_index=True
    )


# =====================================
# 9. 데이터 분석 정보
# =====================================

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "선택한 월",
        month_names[selected_month]
    )

with col2:
    st.metric(
        "분석 연도 수",
        f"{len(result)}개"
    )

with col3:
    st.metric(
        "분석 기간",
        "1907~2026년"
    )

st.caption(
    "※ 분석 범위는 1907년부터 2026년까지입니다."
)

st.caption(
    "※ 동일한 연도와 월에 여러 기록이 있는 경우 "
    "평균값을 사용합니다."
)
