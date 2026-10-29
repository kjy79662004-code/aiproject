import streamlit as st
st.title('우사기가 세상을 지배')
a=st.text_input('우사기가 먹고 운 음식은?')
b=st.selectbox('좋아하는 우사기를 선택하세요!',['기본우사기','몬스터화 된 우사기','기타'])
if st.button('하이 야하 뿌르뿌르 야하 이이이야하 뿌르르르르'):
  st.write('이야~ 야다 야다')
  st.info(a+'맛있겠다')
  st.warning(b+'를 저도 좋아해요 ㅎㅎ 사실 전 모든 우사기를 좋아합니다')
  st.error('그럼에도 우사기는 제 것입니다.')
  st.balloons()
