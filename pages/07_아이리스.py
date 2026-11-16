
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score

# 페이지 설정
st.set_page_config(
    page_title="아이리스 품종 예측",
    page_icon="🌸",
    layout="wide"
)

# 제목
st.title("🌸 아이리스 품종 예측 프로그램")
st.write("꽃잎의 길이와 너비를 입력하면 붓꽃의 품종을 예측합니다.")

st.divider()

# 데이터 불러오기
@st.cache_data
def load_data():
    try:
        data = pd.read_csv("아이리스.csv", encoding="cp949")
    except UnicodeDecodeError:
        data = pd.read_csv("아이리스.csv", encoding="utf-8-sig")

    return data

try:
    df = load_data()

    # 사용할 변수
    X = df[["꽃잎길이", "꽃잎너비"]]
    y = df["품종"]

    # 데이터 범위
    petal_length_min = float(X["꽃잎길이"].min())
    petal_length_max = float(X["꽃잎길이"].max())

    petal_width_min = float(X["꽃잎너비"].min())
    petal_width_max = float(X["꽃잎너비"].max())

    # 학습 데이터와 테스트 데이터 분리
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    # SVM 모델 생성
    model = Pipeline([
        ("scaler", StandardScaler()),
        ("svm", SVC(kernel="rbf", C=1.0, gamma="scale"))
    ])

    # 모델 학습
    model.fit(X_train, y_train)

    # 정확도 평가
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    # 입력 영역
    st.subheader("✏️ 꽃잎 크기 입력")

    col1, col2 = st.columns(2)

    with col1:
        petal_length = st.slider(
            "꽃잎 길이 (cm)",
            min_value=petal_length_min,
            max_value=petal_length_max,
            value=4.0,
            step=0.1
        )

    with col2:
        petal_width = st.slider(
            "꽃잎 너비 (cm)",
            min_value=petal_width_min,
            max_value=petal_width_max,
            value=1.2,
            step=0.1
        )

    st.caption(
        f"꽃잎 길이: {petal_length_min}~{petal_length_max}cm "
        f"/ 꽃잎 너비: {petal_width_min}~{petal_width_max}cm"
    )

    # 예측
    if st.button("🌸 품종 예측하기", use_container_width=True):

        input_data = pd.DataFrame(
            [[petal_length, petal_width]],
            columns=["꽃잎길이", "꽃잎너비"]
        )

        prediction = model.predict(input_data)[0]

        # 품종 한글 변환
        species_names = {
            "Iris-setosa": "세토사 (Setosa)",
            "Iris-versicolor": "버시컬러 (Versicolor)",
            "Iris-virginica": "버지니카 (Virginica)"
        }

        st.success(
            f"예측된 품종은 {species_names.get(prediction, prediction)}입니다! 🌷"
        )

        # 예측 확률 표시
        probabilities = model.predict_proba(input_data)[0]

        st.subheader("📊 품종별 예측 확률")

        for name, probability in zip(
            model.classes_, probabilities
        ):
            st.write(
                f"{species_names.get(name, name)} : "
                f"{probability * 100:.1f}%"
            )
            st.progress(float(probability))

        # 그래프
        st.subheader("🌸 꽃잎 길이와 너비 그래프")

        fig, ax = plt.subplots(figsize=(9, 6))

        # 핑크 계열 색상
        colors = [
            "#F8BBD0",
            "#EC407A",
            "#880E4F"
        ]

        # 품종별 데이터 표시
        for species, color in zip(
            sorted(df["품종"].unique()), colors
        ):
            subset = df[df["품종"] == species]

            ax.scatter(
                subset["꽃잎길이"],
                subset["꽃잎너비"],
                color=color,
                label=species_names.get(species, species),
                alpha=0.75,
                s=65,
                edgecolors="white"
            )

        # 사용자 입력값: 별 모양
        ax.scatter(
            petal_length,
            petal_width,
            color="#FF1493",
            marker="*",
            s=450,
            edgecolors="black",
            linewidths=1,
            label="사용자 입력값",
            zorder=5
        )

        ax.set_xlabel("꽃잎 길이 (cm)", fontsize=12)
        ax.set_ylabel("꽃잎 너비 (cm)", fontsize=12)

        ax.set_title(
            "Iris Petal Length & Width",
            fontsize=15
        )

        ax.legend()
        ax.grid(alpha=0.2)

        st.pyplot(fig)

    # 데이터 및 모델 정보
    st.divider()

    st.subheader("📌 모델 분석 정보")

    col1, col2, col3 = st.columns(3)

    col1.metric("전체 데이터", f"{len(df)}개")
    col2.metric("분류 품종", f"{df['품종'].nunique()}종")
    col3.metric("테스트 정확도", f"{accuracy * 100:.1f}%")

    st.info(
        "사용 알고리즘: 서포트 벡터 머신(SVM) "
        "| 커널: RBF "
        "| 데이터 표준화: StandardScaler"
    )

except FileNotFoundError:
    st.error("아이리스.csv 파일을 찾을 수 없습니다.")

except Exception as e:
    st.error(f"오류가 발생했습니다: {e}")
