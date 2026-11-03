import streamlit as st
import pandas as pd
import plotly.graph_objects as json_plotly
import numpy as np

# 페이지 기본 설정
st.set_page_config(
    page_title="MBTI 국가별 비율 분석",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 MBTI 유형별 국가 순위 시각화")
st.markdown("특정 MBTI 유형의 비율이 가장 높은 국가들을 순서대로 확인해보세요.")

# 1. 예시 데이터 생성 (실제 데이터셋이 있을 경우 pd.read_csv 등으로 대체 가능)
@st.cache_data
def load_data():
    mbti_types = [
        "ISTJ", "ISFJ", "INFJ", "INTJ",
        "ISTP", "ISFP", "INFP", "INTP",
        "ESTP", "ESFP", "ENFP", "ENTP",
        "ESTJ", "ESFJ", "ENFJ", "ENTJ"
    ]
    
    countries = [
        "한국", "일본", "미국", "독일", "영국", 
        "프랑스", "캐나다", "호주", "브라질", "인도",
        "스웨덴", "싱가포르", "스위스", "네덜란드", "스페인"
    ]
    
    np.random.seed(42)
    data = []
    
    for country in countries:
        # 각 국가별 MBTI 비율 임의 생성 (합이 100%가 되도록 조정)
        probs = np.random.dirichlet(np.ones(16)) * 100
        row = {"Country": country}
        for mbti, prob in zip(mbti_types, probs):
            row[mbti] = round(prob, 2)
        data.append(row)
        
    return pd.DataFrame(data), mbti_types

df, mbti_list = load_data()

# 2. 사이드바 - MBTI 선택
st.sidebar.header("설정")
selected_mbti = st.sidebar.selectbox("MBTI 유형을 선택하세요:", mbti_list)

# 3. 데이터 정렬 (선택한 MBTI 비율 기준 내림차순)
df_sorted = df[["Country", selected_mbti]].sort_values(by=selected_mbti, ascending=False).reset_index(drop=True)

# 4. 색상 그라데이션 계산 함수
def generate_colors(n):
    # 1등 색상: 강조용 브라이트 코랄/레드 (#FF4B4B)
    top_color = "hsl(0, 85%, 60%)"
    
    colors = [top_color]
    
    # 2등부터 N등까지: 블루 계열로 채도(Saturation)를 65%에서 15%까지 단계적으로 낮춤
    start_sat = 65
    end_sat = 15
    lightness = 55
    hue = 210  # 차분한 딥블루/스카이블루 계열
    
    for i in range(1, n):
        # 뒤로 갈수록 채도 감소
        current_sat = start_sat - (start_sat - end_sat) * ((i - 1) / max(1, n - 2))
        colors.append(f"hsl({hue}, {int(current_sat)}%, {lightness}%)")
        
    return colors

bar_colors = generate_colors(len(df_sorted))

# 5. Plotly 그래프 생성
import plotly.graph_objects as go

fig = go.Figure(
    data=[
        go.Bar(
            x=df_sorted["Country"],
            y=df_sorted[selected_mbti],
            text=[f"{val}%" for val in df_sorted[selected_mbti]],
            textposition="auto",
            marker=dict(
                color=bar_colors,
                line=dict(color="rgba(0,0,0,0.1)", width=1)
            ),
            hovertemplate="<b>%{x}</b><br>" + selected_mbti + " 비율: %{y}%<extra></extra>"
        )
    ]
)

fig.update_layout(
    title=dict(
        text=f"<b>{selected_mbti}</b> 비율이 높은 국가 순위",
        font=dict(size=20)
    ),
    xaxis=dict(title="국가"),
    yaxis=dict(title="비율 (%)", range=[0, max(df_sorted[selected_mbti]) * 1.15]),
    template="plotly_white",
    height=550,
    margin=dict(l=40, r=40, t=60, b=40)
)

# 6. 화면 출력
col1, col2 = st.columns([2, 1])

with col1:
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📊 순위 요약")
    st.write(f"**1위 국가:** {df_sorted.iloc[0]['Country']} ({df_sorted.iloc[0][selected_mbti]}%)")
    st.dataframe(
        df_sorted.rename(columns={"Country": "국가", selected_mbti: f"{selected_mbti} 비율(%)"}),
        use_container_width=True,
        hide_index=True
    )
