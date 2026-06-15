import streamlit as st
import pandas as pd

# 1. 페이지 기본 설정
st.set_page_config(page_title="아우내 영농조합법인 농약 검색기", page_icon="🐛", layout="wide")

# 2. 엑셀 데이터 불러오기
@st.cache_data
def load_data():
    file_name = "26아우내영농조합법인 농약 혼용가부표(충).xlsx"
    df = pd.read_excel(file_name)
    df = df.fillna("")
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"엑셀 파일을 찾을 수 없습니다...\n에러: {e}")
    st.stop()

# 3. 화면 상단 타이틀
st.title("🌱 아우내 영농조합법인 살충제 검색 시스템")
st.markdown("**현장 처방과 혼용 가부를 한눈에!** 검색 조건을 입력하세요.")
st.markdown("---")

# 4. 검색창을 두 칸으로 나누기 (약 이름 / 적용 대상)
col_search1, col_search2 = st.columns(2)

with col_search1:
    search_keyword = st.text_input("💊 검색할 '약 이름'을 입력하세요 (예: 엑시렐)", "")

with col_search2:
    pest_keyword = st.text_input("🐛 방제할 '해충(적용대상)'을 입력하세요 (예: 진딧물, 굴파리)", "")

# 5. 검색 로직 (둘 중 하나라도 입력되면 검색 시작)
if search_keyword or pest_keyword:
    result_df = df.copy()
    
    # 약 이름이 입력된 경우 필터링
    if search_keyword:
        result_df = result_df[result_df['약명'].astype(str).str.contains(search_keyword, case=False, na=False)]
        
    # 해충 이름이 입력된 경우 필터링
    if pest_keyword:
        result_df = result_df[result_df['병명'].astype(str).str.contains(pest_keyword, case=False, na=False)]

    # 검색 결과 출력
    if result_df.empty:
        st.warning("검색 조건에 맞는 약제가 없습니다. 이름을 다시 확인해주세요.")
    else:
        st.success(f"총 {len(result_df)}건의 약제가 검색되었습니다.")

        for index, row in result_df.iterrows():
            st.subheader(f"🏷️ {row['약명']} ({row['유통사(제조사)']})")
            
            # --- 단가 콤마(천단위) 처리 로직 ---
            price = row['판매단가']
            if pd.isna(price) or str(price).strip() == "":
                price_formatted = "가격 정보 없음"
            else:
                try:
                    # 숫자로 변환 가능하면 콤마 찍기
                    price_formatted = f"{int(float(price)):,}원"
                except ValueError:
                    # '단종', '미정' 등의 글씨가 들어있으면 그대로 출력
                    price_formatted = f"{price}"
            # --------------------------------

            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("#### 📌 기본 정보")
                # 수정 1: 적용대상 글씨 키우기 (초록색, 1.3배 크기)
                st.markdown(f"**· 적용대상:** <span style='font-size: 1.3em; font-weight: bold; color: #1E8449;'>{row['병명']}</span>", unsafe_allow_html=True)
                st.write(f"**· 작용기작:** {row['작용기작']}")
                st.write(f"**· 제형:** {row['제형']}")
                st.write(f"**· 목적/구분:** {row['목적']} / {row['구분']}")
                # 수정 2: 단가에 천단위 콤마 적용
                st.write(f"**· 규격 및 단가:** {row['규격']}{row['단위']} / **{price_formatted}**")

            with col2:
                st.markdown("#### 🧪 성분 및 침투 정보")
                st.write(f"**· 성분1:** {row['성분1(한글)']} ({row['성분1함량(&)']})")
                st.write(f"  - 계통: {row['성분1계통']} [{row['성분1작용기작']}]")
                if row['성분2 (한글)'] != "":
                    st.write(f"**· 성분2:** {row['성분2(한글)']} ({row['성분2함량(&)']})")
                    st.write(f"  - 계통: {row['성분2계통']} [{row['성분2작용기작']}]")
                
                st.write(f"**· 살충경로:** {row['중독 방식(살충 경로)']}")
                st.write(f"**· 침투/침달성:** {row['침투이행성']} / {row['침달성']}")

            with col3:
                st.markdown("#### 📋 사용 및 혼용 정보")
                # 수정 3: 사용량/희석 글씨 키우기 (주황색, 1.2배 크기)
                st.markdown(f"**· 사용량/희석:** <span style='font-size: 1.2em; font-weight: bold; color: #D35400;'>{row['사용량']} (희석: {row['희석배수']})</span>", unsafe_allow_html=True)
                st.write(f"**· 안전사용기준:** {row['안전사용기준']}")
                st.write(f"**· 혼용 가능(살충):** {row['혼용가능한 살충제']}")
                st.write(f"**· 혼용 가능(살균):** {row['혼용가능한 살균제']}")
                st.markdown(f"**· 🚨 혼용 불가/주의:** <span style='color:red'>{row['혼용불가(주의) 약제']}</span>", unsafe_allow_html=True)
            
            with st.expander(f"💡 {row['약명']} 작용원리 및 상세 특성 보기", expanded=False):
                st.markdown(f"**[작용 원리]**\n{row['작용원리']}")
                st.markdown("---")
            
            st.markdown("---")
