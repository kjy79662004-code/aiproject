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


# 컬럼 자동 탐색 헬퍼 함수
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
    st.warning("⚠️ 일부 영양 성분 컬럼을 자동으로 찾지 못했습니다.")
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


# 디저트 여부 판별 로직
def classify_dessert(row):
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
    min_value=float(df[col_protein].\
