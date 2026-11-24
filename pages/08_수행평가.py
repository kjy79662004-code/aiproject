import os
import zipfile
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="영양 성분 기반 메뉴 추천 & 분류기",
    page_icon="🍽️",
    layout="wide",
)

st.title("🍽️ 영양 성분 기반 맞춤 메뉴 추천 및 분류 시스템")
st.markdown(
    "원하는 **열량, 당류, 단백질, 지방** 함량을 입력하면 조건과 가장 가까운 **디저트 1개**와 **일반 조리품(음식) 1개**를 추천합니다."
)


# 1. 데이터 로드 (CSV 직접 로드 또는 ZIP 압축 해제 지원)
@st.cache_data
def load_data():
    csv_filename = "food_menu_nutrition_dataset.csv"
    zip_filename = "archive (2).zip"

    if os.path.exists(csv_filename):
        df = pd.read_csv(csv_filename)
    elif os.path.exists(zip_filename):
        with zipfile.ZipFile(zip_filename, "r") as z:
            with z.open(csv_filename) as f:
                df = pd.read_csv(f)
    else:
        st.error(
            f"'{csv_filename}' 또는 '{zip_filename}' 파일을 GitHub 저장소 최상단 경로에 업로드해주세요."
        )
        st.stop()
    return df


raw_df = load_data()


# 컬럼 자동 탐색 헬퍼 함수 (데이터셋 컬럼명 유연 대응)
def find_col(df, candidates):
    cols_lower = {c.lower().strip(): c for c in df.columns}
    for cand in candidates:
        for col_l, orig_col in cols_lower.items():
            if cand in col_l:
                return orig_col
    return None


col_name = (
    find_col(raw_df, ["menu", "food", "item", "name", "메뉴", "음식"])
    or raw_df.columns[0]
)
col_cat = find_col(
    raw_df, ["category", "type", "group", "class", "종류", "분류", "카테고리"]
)
col_cal = find_col(raw_df, ["calor", "energy", "kcal", "열량", "칼로리"])
col_sugar = find_col(raw_df, ["sugar", "당"])
col_protein = find_col(raw_df, ["protein", "단백질"])
col_fat = find_col(raw_df, ["total fat", "fat", "지방"])

# 필수 컬럼 매핑 확인
required_cols = {
    "열량": col_cal,
    "당류": col_sugar,
    "단백질": col_protein,
    "지방": col_fat,
}
if any(v is None for v in required_cols.values()):
    st.warning(
        "⚠️ 일부 영양 성분 컬럼을 자동으로 찾지 못했습니다. 아래에서 데이터셋의 실제 컬럼을 직접 지정해주세요."
    )
    cols = list(raw_df.columns)
    col_name = st.selectbox("메뉴명 컬럼", cols, index=0)
    col_cat = st.selectbox("카테고리 컬럼", cols, index=min(1, len(cols) - 1))
    col_cal = st.selectbox("열량 컬럼", cols, index=min(2, len(cols) - 1))
    col_sugar = st.selectbox("당류 컬럼", cols, index=min(3, len(cols) - 1))
    col_protein = st.selectbox("단백질 컬럼", cols, index=min(4, len(cols) - 1))
    col_fat = st.selectbox("지방 컬럼", cols, index=min(5, len(cols) - 1))

# 데이터 전처리
df = raw_df.copy()
feature_cols = [col_cal, col_sugar, col_protein, col_fat]

for c in feature_cols:
    df[c] = pd.to_numeric(df[c], errors="coerce")

df = df.dropna(subset=feature_cols + [col_name]).reset_index(drop=True)

# 디저트 여부 판별 로직 (카테고리명 또는 메뉴명 기반)
dessert_keywords = [
    "dessert",
    "sweet",
    "cake",
    "cookie",
    "ice cream",
    "pastry",
    "bakery",
    "pie",
    "pudding",
    "chocolate",
    "donut",
    "muffin",
    "디저트",
    "케이크",
    "쿠키",
    "아이스크림",
    "빵",
    "과자",
]


def classify_dessert(row):
    text = str(row[col_cat]).lower() if col_cat else ""
    name_text = str(row[col_name]).lower()
    if any(k in text for k in dessert_keywords) or any(
        k in name_text for k in dessert_keywords
    ):
        return "디저트"
    return "조리품"


df["구분"] = df.apply(classify_dessert, axis=1)

# 2. 사이드바: 사용자 영양 성분 입력
st.sidebar.header("🔍 원하는 영양 성분 조건 설정")

target_cal = st.sidebar.slider(
    "열량 (kcal)",
    min_value=float(df[col_cal].min()),
    max_value=float(df[col_cal].max()),
    value=float(df[col_cal].median()),
    step=10.0,
)
target_sugar = st.sidebar.slider(
    "당류 (g)",
    min_value=float(df[col_sugar].min()),
    max_value=float(df[col_sugar].max()),
    value=float(df[col_sugar].median()),
    step=1.0,
)
target_protein = st.sidebar.slider(
    "단백질 (g)",
    min_value=float(df[col_protein].min()),
    max_value=float(df[col_protein].max()),
    value=float(df[col_protein].median()),
    step=1.0,
)
target_fat = st.sidebar.slider(
    "지방 (g)",
    min_value=float(df[col_fat].min()),
    max_value=float(df[col_fat].max()),
    value=float(df[col_fat].median()),
    step=1.0,
)

# 3. 조건과 가장 가까운 디저트 1개 + 일반 조리품 1개 검색 (표준화 유클리드 거리 계산)
scaler = StandardScaler()
scaled_features = scaler.fit_transform(df[feature_cols])
target_scaled = scaler.transform(
    [[target_cal, target_sugar, target_protein, target_fat]]
)

df["거리점수"] = np.linalg.norm(scaled_features - target_scaled, axis=1)

dessert_df = df[df["구분"] == "디저트"].sort_values("거리점수")
food_df = df[df["구분"] == "조리품"].sort_values("거리점수")

selected_rows = []
if not dessert_df.empty:
    selected_rows.append(dessert_df.iloc[0])
if not food_df.empty:
    selected_rows.append(food_df.iloc[0])

result_df = pd.DataFrame(selected_rows).reset_index(drop=True)

# 출력용 컬럼 정리
display_df = pd.DataFrame({
    "구분": result_df["구분"],
    "메뉴명": result_df[col_name],
    "열량 (kcal)": result_df[col_cal].round(1),
    "당류 (g)": result_df[col_sugar].round(1),
    "단백질 (g)": result_df[col_protein].round(1),
    "지방 (g)": result_df[col_fat].round(1),
})

# 4. 결과 표 출력 (디저트 상단 고정 + 하늘색/분홍색 스타일링)
st.subheader("📋 추천 메뉴 결과 (디저트 상단 우선 표시)")
st.caption(
    "🟦 하늘색 행: 디저트류 (예외 구분) / 🩷 분홍색 행: 일반 조리품(음식)"
)


def highlight_category(row):
    if row["구분"] == "디저트":
        return ["background-color: #D6EAF8; color: #1B4F72; font-weight: bold;"] * len(row)  # 하늘색
    else:
        return ["background-color: #FADBD8; color: #78281F; font-weight: bold;"] * len(row)  # 분홍색


styled_table = display_df.style.apply(highlight_category, axis=1).format({
    "열량 (kcal)": "{:.1f}",
    "당류 (g)": "{:.1f}",
    "단백질 (g)": "{:.1f}",
    "지방 (g)": "{:.1f}",
})

st.dataframe(styled_table, use_container_width=True, hide_index=True)

# 5. 막대 그래프 및 그래프 요약 표
st.divider()
st.subheader("📊 추천 메뉴 영양 성분 비교 (막대 그래프 & 요약 표)")

col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("**1) 영양 성분 비교 막대 그래프**")
    chart_df = display_df.set_index("메뉴명")[
        ["열량 (kcal)", "당류 (g)", "단백질 (g)", "지방 (g)"]
    ]
    st.bar_chart(chart_df)

with col2:
    st.markdown("**2) 그래프 데이터 간단 요약 표 (사용자 입력 목표치 대비)**")
    summary_data = {
        "영양 항목": ["열량 (kcal)", "당류 (g)", "단백질 (g)", "지방 (g)"],
        "사용자 설정값": [
            target_cal,
            target_sugar,
            target_protein,
            target_fat,
        ],
    }
    for _, r in display_df.iterrows():
        label = f"[{r['구분']}] {r['메뉴명']}"
        summary_data[label] = [
            r["열량 (kcal)"],
            r["당류 (g)"],
            r["단백질 (g)"],
            r["지방 (g)"],
        ]

    summary_table = pd.DataFrame(summary_data)
    st.table(summary_table)

# 6. 머신러닝 알고리즘 기반 음식 종류(디저트 vs 조리품) 예측 섹션
st.divider()
st.subheader("🤖 머신러닝 기반 메뉴 종류 예측 (Random Forest Classifier)")


@st.cache_resource
def train_classifier(data, features):
    X = data[features]
    y = data["구분"]

    # 클래스가 2개 이상일 때만 학습
    if y.nunique() < 2:
        return None, 0.0

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    acc = clf.score(X_test, y_test)
    return clf, acc


clf, accuracy = train_classifier(df, feature_cols)

if clf is not None:
    user_input_df = pd.DataFrame(
        [[target_cal, target_sugar, target_protein, target_fat]],
        columns=feature_cols,
    )
    pred_class = clf.predict(user_input_df)[0]
    pred_proba = clf.predict_proba(user_input_df)[0]
    classes = list(clf.classes_)
    prob_dict = {
        cls: f"{prob * 100:.1f}%" for cls, prob in zip(classes, pred_proba)
    }

    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("현재 입력 조건의 예측 종류", f"{pred_class}")
    m_col2.metric("예측 확률 분포", f"{prob_dict}")
    m_col3.metric("모델 테스트 정확도", f"{accuracy * 100:.1f}%")
else:
    st.info(
        "데이터셋 내 '디저트'와 '조리품' 두 분류가 모두 존재해야 모델 학습이 가능합니다."
    )

# 알고리즘 설명 코멘트
st.info("""
💡 **사용된 알고리즘 설명: 랜덤 포레스트 분류기 (Random Forest Classifier)**
* **작동 원리**: 여러 개의 결정 트리(Decision Tree)를 무작위로 학습시킨 뒤, 각 트리의 예측 결과를 종합(다수결 투표)하여 최종 종류(`디저트` 또는 `조리품`)를 판별하는 **앙상블(Ensemble) 머신러닝 알고리즘**입니다.
* **선택 이유**: 영양 성분 데이터는 *'당류와 지방이 높으면 디저트일 확률이 높다'*처럼 변수 간 비선형적인 경계가 뚜렷합니다. 랜덤 포레스트는 단일 결정 트리의 과적합(Overfitting)을 방지하면서도 열량·당류·단백질·지방의 복합적인 조합 패턴을 안정적이고 정확하게 분류해 줍니다.
""")
