
@st.cache_data
def load_data():

    # 현재 실행 위치 확인
    current_dir = Path.cwd()
    app_dir = Path(__file__).resolve().parent

    # CSV 파일을 찾을 경로 목록
    possible_paths = [
        app_dir / "아이리스.csv",
        current_dir / "아이리스.csv",
        app_dir.parent / "아이리스.csv",
        app_dir / "data" / "아이리스.csv",
        current_dir / "data" / "아이리스.csv"
    ]

    # 파일 찾기
    file_path = None

    for path in possible_paths:
        if path.exists():
            file_path = path
            break

    if file_path is None:
        raise FileNotFoundError(
            "아이리스.csv 파일을 찾을 수 없습니다. "
            "GitHub 저장소의 파일 위치를 확인해 주세요."
        )

    # CSV 읽기
    data = pd.read_csv(
        file_path,
        encoding="cp949"
    )

    return data
