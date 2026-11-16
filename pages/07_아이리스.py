
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

from sklearn.datasets import load_iris
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score

# --------------------------------
# 1. 페이지 설정
# --------------------------------
st.set_page_config(
    page_title="Iris 품종 예측",
    page_icon="🌸",
    layout="centered"
)

st.title("🌸 Iris 꽃 품종 예측 시스템")
st.write("꽃잎의 길이와 너비를 입력하면 붓꽃의 품종을 예측합니다.")

# --------------------------------
# 2. 데이터 불러오기
# --------------------------------
iris = load_iris()

# 꽃잎 길이, 꽃잎 너비만 사용
X = iris.data[:, 2:4]
y = iris.target

species_names = [
    "Iris Setosa",
    "Iris Versicolor",
    "Iris Virginica"
]

# --------------------------------
# 3. 머신러닝 모델 생성
# --------------------------------
model = make_pipeline(
    StandardScaler(),
    SVC(
        kernel="rbf",
        C=1.0,
        gamma="scale",
        probability=True,
        random_state=42
    )
)

# 전체 데이터로 모델 학습
model.fit(X, y)

# 5-Fold 교차검증 정확도
scores = cross_val_score(
    model,
    X,
    y,
    cv=5,
    scoring="accuracy"
)

# --------------------------------
# 4. 사용자 입력
# --------------------------------
st.subheader("📏 꽃잎 크기 입력")

col1, col2 = st.columns(2)

with col1:
    petal_length = st.number_input(
        "꽃잎 길이 (cm)",
        min_value=1.0,
        max_value=6.9,
        value=3.5,
        step=0.1
    )

with col2:
    petal_width = st.number_input(
        "꽃잎 너비 (cm)",
        min_value=0.1,
        max_value=2.5,
        value=1.0,
        step=0.1
    )

st.caption(
    "입력 가능 범위: 꽃잎 길이 1.0~6.9cm / "
    "꽃잎 너비 0.1~2.5cm"
)

# --------------------------------
# 5. 품종 예측
# --------------------------------
input_data = np.array([
    [petal_length, petal_width]
])

prediction = model.predict(input_data)
probabilities = model.predict_proba(input_data)

predicted_species = species_names[prediction[0]]

st.divider()
st.subheader("🔍 예측 결과")

st.success(f"예측된 꽃 품종: {predicted_species}")

# 예측 확률
st.write("품종별 예측 확률")

for i, name in enumerate(species_names):
    st.write(
        f"{name}: {probabilities[0][i] * 100:.2f}%"
    )

# --------------------------------
# 6. 그래프 시각화
# --------------------------------
st.divider()
st.subheader("📊 꽃잎 길이와 너비 그래프")

fig, ax = plt.subplots(figsize=(8, 5))

# 기존 Iris 데이터 표시
ax.scatter(
    X[:, 0],
    X[:, 1],
    color="lightgray",
    alpha=0.5,
    label="Iris Dataset"
)

# 사용자가 입력한 값: 분홍색 별
ax.scatter(
    petal_length,
    petal_width,
    color="#FF1493",
    marker="*",
    s=350,
    edgecolors="black",
    linewidths=0.8,
    label="Your Input",
    zorder=5
)

ax.set_xlabel("Petal Length (cm)")
ax.set_ylabel("Petal Width (cm)")
ax.set_title("Iris Petal Measurement")
ax.legend()
ax.grid(alpha=0.3)

st.pyplot(fig)

# --------------------------------
# 7. 모델 성능
# --------------------------------
st.divider()
st.subheader("📈 머신러닝 모델 성능")

st.metric(
    "5-Fold 교차검증 평균 정확도",
    f"{scores.mean() * 100:.2f}%"
)

st.write(
    "사용 알고리즘: Support Vector Machine (SVM)"
)

st.write(
    "커널: RBF (Radial Basis Function)"
)

st.write(
    "입력 특성: Petal Length, Petal Width"
)

st.caption(
    "본 프로그램은 Scikit-learn의 Iris 데이터셋을 사용합니다."
)
