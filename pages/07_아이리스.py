
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score


# ==========================================
# 1. 페이지 설정
# ==========================================

st.set_page_config(
    page_title="아이리스 품종 예측",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 아이리스 품종 예측 프로그램")
st.write(
    "꽃의 길이와 너비를 입력하고 "
    "다양한 분류 알고리즘으로 붓꽃의 품종을 예측해 보세요!"
)

st.divider()


# ==========================================
# 2. 데이터 불러오기
# ==========================================

@st.cache_data
def load_data():

    file_path = Path(__file__).parent / "아이리스.csv"

    if not file_path.exists():
        raise FileNotFoundError(
            "아이리스.csv 파일이 없습니다. "
            "GitHub 저장소에 CSV 파일을 업로드해 주세요."
        )

    try:
        data = pd.read_csv(file_path, encoding="cp949")
    except UnicodeDecodeError:
        data = pd.read_csv(file_path, encoding="utf-8-sig")

    required_columns = [
        "꽃받침길이",
        "꽃받침너비",
        "꽃잎길이",
        "꽃잎너비",
        "품종"
    ]

    for col in required_columns:
        if col not in data.columns:
            raise ValueError(f"데이터에 '{col}' 컬럼이 없습니다.")

    return data


# ==========================================
# 3. 알고리즘 생성 함수
# ==========================================

def create_model(algorithm):

    if algorithm == "SVM":

        model = Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", SVC(
                kernel="rbf",
                C=1.0,
                gamma="scale",
                probability=True,
                random_state=42
            ))
        ])

    elif algorithm == "랜덤 포레스트":

        model = RandomForestClassifier(
            n_estimators=200,
            random_state=42
        )

    elif algorithm == "KNN":

        model = Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", KNeighborsClassifier(
                n_neighbors=5
            ))
        ])

    return model


# ==========================================
# 4. 품종 한글 이름
# ==========================================

species_names = {
    "Iris-setosa": "세토사 (Setosa)",
    "Iris-versicolor": "버시컬러 (Versicolor)",
    "Iris-virginica": "버지니카 (Virginica)"
}


# ==========================================
# 5. 알고리즘 목록
# ==========================================

algorithms = [
    "SVM",
    "랜덤 포레스트",
    "KNN"
]


# ==========================================
# 6. 예측 및 그래프 출력 함수
# ==========================================

def prediction_system(
    df,
    feature_x,
    feature_y,
    tab_key
):

    st.subheader("🤖 분류 알고리즘 선택")

    algorithm = st.selectbox(
        "사용할 알고리즘을 선택하세요.",
        algorithms,
        key=f"{tab_key}_algorithm"
    )

    st.caption(
        f"선택한 속성: {feature_x}, {feature_y}"
    )

    # 학습에 사용할 데이터
    X = df[[feature_x, feature_y]]
    y = df["품종"]

    # 학습 데이터와 테스트 데이터 분리
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    # 모델 생성 및 평가
    evaluation_model = create_model(algorithm)

    evaluation_model.fit(X_train, y_train)

    test_prediction = evaluation_model.predict(X_test)

    accuracy = accuracy_score(
        y_test,
        test_prediction
    )

    # 전체 데이터를 사용하여 최종 모델 학습
    model = create_model(algorithm)
    model.fit(X, y)

    st.divider()

    # ======================================
    # 사용자 입력
    # ======================================

    st.subheader("✏️ 측정값 입력")

    col1, col2 = st.columns(2)

    x_min = float(df[feature_x].min())
    x_max = float(df[feature_x].max())

    y_min = float(df[feature_y].min())
    y_max = float(df[feature_y].max())

    x_default = float(df[feature_x].median())
    y_default = float(df[feature_y].median())

    with col1:

        input_x = st.slider(
            f"{feature_x} (cm)",
            min_value=x_min,
            max_value=x_max,
            value=x_default,
            step=0.1,
            key=f"{tab_key}_input_x"
        )

    with col2:

        input_y = st.slider(
            f"{feature_y} (cm)",
            min_value=y_min,
            max_value=y_max,
            value=y_default,
            step=0.1,
            key=f"{tab_key}_input_y"
        )

    st.info(
        f"{feature_x} 입력 범위: {x_min} ~ {x_max}cm\n\n"
        f"{feature_y} 입력 범위: {y_min} ~ {y_max}cm"
    )

    # ======================================
    # 예측 버튼
    # ======================================

    if st.button(
        "🌸 품종 예측하기",
        use_container_width=True,
        key=f"{tab_key}_predict"
    ):

        input_data = pd.DataFrame(
            [[input_x, input_y]],
            columns=[feature_x, feature_y]
        )

        prediction = model.predict(input_data)[0]

        probabilities = model.predict_proba(input_data)[0]

        st.success(
            f"예측된 품종은 "
            f"{species_names.get(prediction, prediction)}입니다!"
        )

        # ==================================
        # 예측 확률
        # ==================================

        st.subheader("📊 품종별 예측 확률")

        probability_col1, probability_col2 = st.columns(2)

        for i, (name, probability) in enumerate(
            zip(model.classes_, probabilities)
        ):

            target_col = (
                probability_col1 if i % 2 == 0
                else probability_col2
            )

            with target_col:

                st.write(
                    f"**{species_names.get(name, name)}**"
                )

                st.progress(float(probability))

                st.write(
                    f"{probability * 100:.2f}%"
                )

        st.divider()

        # ==================================
        # 그래프
        # ==================================

        st.subheader("📈 측정값 시각화")

        fig, ax = plt.subplots(figsize=(10, 6))

        # 품종별 핑크 색상
        colors = {
            "Iris-setosa": "#F8BBD0",
            "Iris-versicolor": "#EC407A",
            "Iris-virginica": "#880E4F"
        }

        for species in sorted(df["품종"].unique()):

            subset = df[df["품종"] == species]

            ax.scatter(
                subset[feature_x],
                subset[feature_y],
                color=colors.get(species, "#EC407A"),
                label=species_names.get(species, species),
                alpha=0.75,
                s=65,
                edgecolors="white"
            )

        # 사용자가 입력한 값
        ax.scatter(
            input_x,
            input_y,
            color="#FF1493",
            marker="*",
            s=500,
            edgecolors="black",
            linewidths=1,
            label="사용자 입력값",
            zorder=5
        )

        ax.set_xlabel(f"{feature_x} (cm)", fontsize=12)
        ax.set_ylabel(f"{feature_y} (cm)", fontsize=12)

        ax.set_title(
            f"{feature_x} & {feature_y}",
            fontsize=15
        )

        ax.legend()
        ax.grid(alpha=0.2)

        st.pyplot(fig)
        plt.close(fig)

        # ==================================
        # 모델 정확도
        # ==================================

        st.divider()

        st.subheader("📌 모델 평가 결과")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "전체 데이터",
            f"{len(df)}개"
        )

        col2.metric(
            "선택 알고리즘",
            algorithm
        )

        col3.metric(
            "테스트 정확도",
            f"{accuracy * 100:.2f}%"
        )

        st.caption(
            "정확도는 전체 데이터 중 20%를 테스트 데이터로 "
            "분리하여 측정한 결과입니다."
        )


# ==========================================
# 7. 메인 프로그램
# ==========================================

try:

    df = load_data()

    st.success(
        f"데이터 불러오기 완료! "
        f"전체 {len(df)}개 데이터, "
        f"{df['품종'].nunique()}개 품종"
    )

    # ======================================
    # 탭 만들기
    # ======================================

    tab1, tab2 = st.tabs([
        "🌸 기본 예측 (꽃잎)",
        "🔍 속성 선택 예측"
    ])

    # ======================================
    # TAB 1. 기존 꽃잎 예측
    # ======================================

    with tab1:

        st.header("🌷 꽃잎 측정값으로 품종 예측")

        st.write(
            "꽃잎 길이와 꽃잎 너비를 이용하여 "
            "붓꽃의 품종을 예측합니다."
        )

        prediction_system(
            df,
            "꽃잎길이",
            "꽃잎너비",
            "petal"
        )

    # ======================================
    # TAB 2. 속성 직접 선택
    # ======================================

    with tab2:

        st.header("🔎 원하는 속성 2개로 품종 예측")

        st.write(
            "아래 4가지 측정 속성 중 원하는 2개를 "
            "직접 선택해 품종을 예측해 보세요."
        )

        st.info(
            "같은 속성을 두 번 선택할 수 없습니다. "
            "서로 다른 두 가지 속성을 골라주세요."
        )

        features = [
            "꽃받침길이",
            "꽃받침너비",
            "꽃잎길이",
            "꽃잎너비"
        ]

        select_col1, select_col2 = st.columns(2)

        with select_col1:

            selected_x = st.selectbox(
                "첫 번째 측정 속성",
                features,
                index=0,
                key="custom_feature_x"
            )

        # 첫 번째로 고른 속성 제외
        available_features = [
            feature for feature in features
            if feature != selected_x
        ]

        default_y = (
            "꽃받침너비"
            if "꽃받침너비" in available_features
            else available_features[0]
        )

        with select_col2:

            selected_y = st.selectbox(
                "두 번째 측정 속성",
                available_features,
                index=available_features.index(default_y),
                key="custom_feature_y"
            )

        st.write(
            f"**현재 선택된 조합:** "
            f"{selected_x} + {selected_y}"
        )

        st.divider()

        prediction_system(
            df,
            selected_x,
            selected_y,
            "custom"
        )


    # ======================================
    # 8. 알고리즘 작동 원리 설명
    # ======================================

    st.divider()

    st.header("📚 분류 알고리즘 작동 원리")

    st.write(
        "이번 프로그램에서 사용하는 세 가지 알고리즘의 "
        "원리를 알아보세요."
    )

    # SVM
    with st.expander("① SVM (서포트 벡터 머신)"):

        st.subheader("데이터 사이의 최적 경계 찾기")

        st.write(
            """
            SVM은 서로 다른 품종의 데이터를 가장 잘 구분할 수 있는
            경계선을 찾는 분류 알고리즘입니다.

            1. 입력된 측정값을 데이터 공간에 배치합니다.
            2. 서로 다른 품종 사이를 구분하는 경계를 찾습니다.
            3. 경계와 가장 가까운 데이터 사이의 거리가
               최대가 되도록 경계를 결정합니다.
            4. 새로운 데이터가 어느 영역에 속하는지 판단하여
               품종을 예측합니다.

            이 프로그램에서는 RBF 커널을 사용하여
            직선으로 구분하기 어려운 데이터도 분류할 수 있습니다.
            """
        )

        st.caption(
            "핵심: 품종을 가장 잘 구분하는 경계선을 찾는 방법"
        )

    # Random Forest
    with st.expander("② 랜덤 포레스트 (Random Forest)"):

        st.subheader("여러 개의 결정 트리를 활용하기")

        st.write(
            """
            랜덤 포레스트는 여러 개의 결정 트리를 만들고
            각각의 예측 결과를 종합하는 분류 알고리즘입니다.

            1. 학습 데이터에서 일부 데이터를 무작위로 선택합니다.
            2. 선택된 데이터로 여러 개의 결정 트리를 만듭니다.
            3. 각 트리가 입력된 꽃의 품종을 각각 예측합니다.
            4. 가장 많은 트리가 선택한 품종을 최종 결과로 결정합니다.

            여러 트리의 결과를 종합하기 때문에
            하나의 결정 트리보다 안정적인 예측을 기대할 수 있습니다.
            """
        )

        st.caption(
            "핵심: 여러 결정 트리의 투표로 품종을 결정하는 방법"
        )

    # KNN
    with st.expander("③ KNN (K-최근접 이웃)"):

        st.subheader("가장 가까운 데이터 참고하기")

        st.write(
            """
            KNN은 새롭게 입력된 데이터와 가까운 기존 데이터를
            찾아 품종을 예측하는 알고리즘입니다.

            1. 사용자가 입력한 꽃의 측정값을 확인합니다.
            2. 기존 데이터와의 거리를 계산합니다.
            3. 가장 가까운 데이터 5개를 선택합니다.
            4. 선택된 5개 데이터 중 가장 많은 품종을
               새로운 데이터의 품종으로 예측합니다.

            이 프로그램에서는 K값을 5로 설정했습니다.
            """
        )

        st.caption(
            "핵심: 주변에서 가장 많이 나타나는 품종을 선택하는 방법"
        )


    # ======================================
    # 9. 데이터 정보
    # ======================================

    st.divider()

    with st.expander("📋 아이리스 데이터 정보 확인"):

        st.write("**전체 데이터 미리보기**")

        st.dataframe(
            df,
            use_container_width=True
        )

        st.write("**품종별 데이터 개수**")

        st.dataframe(
            df["품종"].value_counts().rename("데이터 개수"),
            use_container_width=True
        )

        st.write("**측정 속성별 기초 통계**")

        st.dataframe(
            df[
                [
                    "꽃받침길이",
                    "꽃받침너비",
                    "꽃잎길이",
                    "꽃잎너비"
                ]
            ].describe(),
            use_container_width=True
        )

except FileNotFoundError as e:

    st.error(str(e))

except Exception as e:

    st.error(f"오류가 발생했습니다: {e}")
