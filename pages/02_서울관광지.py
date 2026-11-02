
import streamlit as st
import folium
from streamlit_folium import st_folium

# 페이지 기본 설정
st.set_page_config(
    page_title="서울 외국인 인기 관광지 TOP 10",
    page_icon="🗺️",
    layout="wide"
)

# 서울 관광지 데이터
SPOTS = [
    {
        "rank": 1,
        "name": "명동",
        "english": "Myeong-dong",
        "lat": 37.5636,
        "lon": 126.9869,
        "category": "쇼핑·먹거리",
        "description": "화장품 매장과 패션 상점, 길거리 음식이 모여 있는 서울 대표 쇼핑 거리입니다."
    },
    {
        "rank": 2,
        "name": "홍대 거리",
        "english": "Hongdae",
        "lat": 37.5563,
        "lon": 126.9236,
        "category": "문화·공연",
        "description": "버스킹 공연과 개성 있는 카페, 패션 숍과 젊은 문화가 어우러진 거리입니다."
    },
    {
        "rank": 3,
        "name": "경복궁",
        "english": "Gyeongbokgung Palace",
        "lat": 37.5796,
        "lon": 126.9770,
        "category": "역사·문화",
        "description": "조선 왕조의 법궁으로, 한국 전통 건축과 궁궐 문화를 살펴볼 수 있습니다."
    },
    {
        "rank": 4,
        "name": "성수동",
        "english": "Seongsu-dong",
        "lat": 37.5445,
        "lon": 127.0560,
        "category": "카페·트렌드",
        "description": "옛 공장 건물을 활용한 카페와 편집숍, 팝업스토어가 많은 감각적인 동네입니다."
    },
    {
        "rank": 5,
        "name": "강남역 일대",
        "english": "Gangnam Station",
        "lat": 37.4979,
        "lon": 127.0276,
        "category": "쇼핑·도심",
        "description": "대형 상점과 음식점, 다양한 즐길 거리가 모여 있는 서울의 대표 번화가입니다."
    },
    {
        "rank": 6,
        "name": "N서울타워",
        "english": "N Seoul Tower",
        "lat": 37.5512,
        "lon": 126.9882,
        "category": "전망·랜드마크",
        "description": "남산 정상에 있는 전망 명소로 서울 도심의 풍경을 한눈에 감상할 수 있습니다."
    },
    {
        "rank": 7,
        "name": "코엑스·별마당도서관",
        "english": "COEX & Starfield Library",
        "lat": 37.5126,
        "lon": 127.0593,
        "category": "쇼핑·문화",
        "description": "쇼핑몰과 전시 공간, 높은 서가가 인상적인 별마당도서관을 함께 즐길 수 있습니다."
    },
    {
        "rank": 8,
        "name": "동대문디자인플라자(DDP)",
        "english": "Dongdaemun Design Plaza",
        "lat": 37.5671,
        "lon": 127.0095,
        "category": "건축·전시",
        "description": "독특한 곡선형 건축물로 유명하며 전시와 디자인 행사, 야간 산책을 즐기기 좋습니다."
    },
    {
        "rank": 9,
        "name": "광장시장",
        "english": "Gwangjang Market",
        "lat": 37.5700,
        "lon": 126.9997,
        "category": "전통시장·음식",
        "description": "빈대떡과 김밥 등 한국 길거리 음식을 맛보고 전통시장 분위기를 경험할 수 있습니다."
    },
    {
        "rank": 10,
        "name": "북촌한옥마을",
        "english": "Bukchon Hanok Village",
        "lat": 37.5826,
        "lon": 126.9830,
        "category": "전통·골목",
        "description": "전통 한옥이 이어진 골목으로 한국의 주거 문화와 옛 서울의 풍경을 느낄 수 있습니다."
    }
]

# 제목
st.title("🗺️ 서울 외국인 인기 관광지 TOP 10")
st.write(
    "서울을 방문하는 외국인 관광객들이 즐겨 찾는 "
    "대표 관광지를 지도에서 확인해 보세요!"
)

st.info(
    "이 목록은 외국인 관광객 선호 및 방문 관련 자료를 참고해 "
    "구성한 대표 관광지 목록이며, 공식 통합 순위는 아닙니다."
)

# 서울 지도 만들기
m = folium.Map(
    location=[37.5665, 126.9780],
    zoom_start=12,
    tiles="CartoDB positron"
)

# 관광지 마커 표시
for spot in SPOTS:

    popup_html = f"""
    <div style="width:220px;">
        <h4>{spot['rank']}. {spot['name']}</h4>
        <b>{spot['english']}</b>
        <p>{spot['category']}</p>
        <p>{spot['description']}</p>
    </div>
    """

    folium.Marker(
        location=[spot["lat"], spot["lon"]],
        tooltip=f"{spot['rank']}. {spot['name']}",
        popup=folium.Popup(
            popup_html,
            max_width=280
        ),
        icon=folium.DivIcon(
            html=f"""
            <div style="
                background:#26364a;
                color:white;
                border:2px solid white;
                border-radius:50%;
                width:30px;
                height:30px;
                display:flex;
                align-items:center;
                justify-content:center;
                font-weight:bold;
                font-size:13px;
                box-shadow:0 1px 5px rgba(0,0,0,.35);
            ">
                {spot['rank']}
            </div>
            """,
            icon_size=(30, 30),
            icon_anchor=(15, 15)
        )
    ).add_to(m)

# 지도 화면 출력
st.subheader("📍 서울 관광지 위치 지도")

st_folium(
    m,
    use_container_width=True,
    height=560,
    returned_objects=[]
)

# 관광지 설명
st.subheader("✨ 관광지 간단 소개")

# 2열로 관광지 표시
cols = st.columns(2)

for i, spot in enumerate(SPOTS):

    with cols[i % 2]:

        with st.container(border=True):

            st.markdown(
                f"### {spot['rank']}. {spot['name']}"
            )

            st.caption(spot["english"])

            st.write(
                f"📌 분야: {spot['category']}"
            )

            st.write(
                spot["description"]
            )

# 자료 출처
st.divider()

st.subheader("📚 참고 자료")

st.markdown("""
- [서울시 관광 정보](https://english.seoul.go.kr/)
- [서울관광재단](https://www.sto.or.kr/)
- [서울 관광 공식 사이트](https://english.visitseoul.net/)
""")

st.caption(
    "※ 지도 표시에는 인터넷 연결이 필요합니다."
)
