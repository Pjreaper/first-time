import streamlit as st
import pandas as pd

# 1. 페이지 기본 설정 (웹 브라우저 탭 이름, 아이콘, 화면 넓게 쓰기)
st.set_page_config(page_title="아우내 영농조합법인 농약 검색기", page_icon="🐛", layout="wide")

# 2. 엑셀 데이터 불러오기 (캐시를 사용해 로딩 속도 향상)
@st.cache_data
def load_data():
    # 지운님의 엑셀 파일 이름과 똑같이 맞췄습니다.
    file_name = "26아우내영농조합법인 농약 혼용가부표(충).xlsx"
    df = pd.read_excel(file_name)
    # 데이터가 비어있는 칸(NaN)을 빈 문자열로 깔끔하게 처리
    df = df.fillna("")
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"엑셀 파일을 찾을 수 없습니다. 파일 이름이 정확한지 확인해주세요.\n에러: {e}")
    st.stop()

# 3. 화면 상단 타이틀 및 설명
st.title("🌱 아우내 영농조합법인 살충제 검색 시스템")
st.markdown("**현장 처방과 혼용 가부를 한눈에!** 검색창에 약 이름(상표명)을 입력하세요.")
st.markdown("---")

# 4. 검색창 만들기
search_keyword = st.text_input("🔍 검색할 약 이름을 입력하세요 (예: 엑시렐, 벨룸, 렘페이지)", "")

# 검색어가 입력되었을 때만 결과 보여주기
if search_keyword:
    # '약명' 열에서 검색어가 포함된 데이터만 필터링
    result_df = df[df['약명'].astype(str).str.contains(search_keyword, case=False, na=False)]

    if result_df.empty:
        st.warning(f"'{search_keyword}'에 대한 검색 결과가 없습니다. 이름을 다시 확인해주세요.")
    else:
        st.success(f"총 {len(result_df)}건의 약제가 검색되었습니다.")

        # 검색된 약들을 하나씩 예쁘게 화면에 출력
        for index, row in result_df.iterrows():
            st.subheader(f"🏷️ {row['약명']} ({row['유통사(제조사)']})")
            
            # 화면을 세 칸(3단 컬럼)으로 나누어 정보 배치
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("#### 📌 기본 정보")
                st.write(f"**· 적용 대상:** {row['병명']}")
                st.write(f"**· 작용 기작:** {row['작용 기작']}")
                st.write(f"**· 제형:** {row['제형']}")
                st.write(f"**· 목적/구분:** {row['목적']} / {row['구분']}")
                st.write(f"**· 규격 및 단가:** {row['규격']}{row['단위']} / {row['판매 단가']}원")

            with col2:
                st.markdown("#### 🧪 성분 및 침투 정보")
                # 성분 1 정보
                st.write(f"**· 성분1:** {row['성분1 (한글)']} ({row['성분1 함량(&)']})")
                st.write(f"  - 계통: {row['성분1 계통']} [{row['성분1 작용기작']}]")
                # 성분 2 정보 (있는 경우에만 출력)
                if row['성분2 (한글)'] != "":
                    st.write(f"**· 성분2:** {row['성분2 (한글)']} ({row['성분2 함량(&)']})")
                    st.write(f"  - 계통: {row['성분2 계통']} [{row['성분2 작용기작']}]")
                
                st.write(f"**· 살충 경로:** {row['중독 방식 (살충 경로)']}")
                st.write(f"**· 침투/침달성:** {row['침투이행성']} / {row['침달성']}")

            with col3:
                st.markdown("#### 📋 사용 및 혼용 정보")
                st.write(f"**· 사용량/희석:** {row['사용량']} (희석: {row['희석배수']})")
                st.write(f"**· 안전사용기준:** {row['안전사용기준']}")
                st.write(f"**· 혼용 가능(살충):** {row['혼용가능한 살충제']}")
                st.write(f"**· 혼용 가능(살균):** {row['혼용가능한 살균제']}")
                st.markdown(f"**· 🚨 혼용 불가/주의:** <span style='color:red'>{row['혼용불가(주의) 약제']}</span>", unsafe_allow_html=True)
            
            # 작용원리 및 특성은 내용이 길기 때문에 클릭해서 열어보도록 아코디언(Expander)으로 처리
            with st.expander(f"💡 {row['약명']} 작용원리 및 상세 특성 보기", expanded=False):
                st.markdown(f"**[작용 원리]**\n{row['작용원리']}")
                st.markdown("---")
                st.markdown(f"**[상세 특성]**\n{row['특성']}")
            
            # 다음 약제와의 구분을 위한 선
            st.markdown("---")
