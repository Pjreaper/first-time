import streamlit as st
import pandas as pd

# 1. 페이지 기본 설정
st.set_page_config(page_title="아우내 영농조합법인 농약(충) 검색기", page_icon="🐛", layout="wide")

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
    filtered_df = df.copy()
    
    # 약 이름이 입력된 경우 필터링
    if search_keyword:
        filtered_df = filtered_df[filtered_df['약명'].astype(str).str.contains(search_keyword, case=False, na=False)]
        
    # 해충 이름이 입력된 경우 필터링
    if pest_keyword:
        filtered_df = filtered_df[filtered_df['병명'].astype(str).str.contains(pest_keyword, case=False, na=False)]

    # 검색 결과 출력
    if filtered_df.empty:
        st.warning("검색 조건에 맞는 약제가 없습니다. 이름을 다시 확인해주세요.")
    else:
        # ⭐️ 핵심 해결책: 검색된 데이터에서 약 이름의 중복을 제거하고 '고유한 약 이름' 리스트만 뽑아냄
        unique_drugs = filtered_df['약명'].unique()
        st.success(f"총 {len(unique_drugs)}가지의 약제가 검색되었습니다.")

        for drug_name in unique_drugs:
            # ⭐️ 원본 엑셀(df)에서 이 약의 이름을 가진 '모든 행'을 다 끌어옴 (다른 해충 정보까지 전부 확보)
            drug_all_data = df[df['약명'] == drug_name]
            
            # 성분, 단가 같은 공통 정보는 첫 번째 줄(iloc[0])에서만 가져와서 한 번만 출력함
            base_info = drug_all_data.iloc[0]

            st.subheader(f"🏷️ {base_info['약명']} ({base_info['유통사(제조사)']})")
            
            # 단가 콤마 처리
            price = base_info['판매단가']
            if pd.isna(price) or str(price).strip() == "":
                price_formatted = "가격 정보 없음"
            else:
                try:
                    price_formatted = f"{int(float(price)):,}원"
                except ValueError:
                    price_formatted = f"{price}"

            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("#### 📌 기본 정보")
                # 이 약이 잡을 수 있는 모든 해충을 쉼표로 예쁘게 묶어서 한 번에 보여줌
                all_pests_list = drug_all_data['병명'].unique()
                all_pests_str = ", ".join(all_pests_list)
                
                st.markdown(f"**· 등록된 모든 해충:** <span style='font-size: 1.2em; font-weight: bold; color: #1E8449;'>{all_pests_str}</span>", unsafe_allow_html=True)
                st.write(f"**· 작용기작:** {base_info['작용기작']}")
                st.write(f"**· 제형:** {base_info['제형']}")
                st.write(f"**· 목적/구분:** {base_info['목적']} / {base_info['구분']}")
                st.write(f"**· 규격 및 단가:** {base_info['규격']}{base_info['단위']} / **{price_formatted}**")

            with col2:
                st.markdown("#### 🧪 성분 및 침투 정보")
                st.write(f"**· 성분1:** {base_info['성분1(한글)']} ({base_info['성분1함량(%)']})")
                st.write(f"  - 계통: {base_info['성분1계통']} [{base_info['성분1작용기작']}]")
                if base_info['성분2(한글)'] != "":
                    st.write(f"**· 성분2:** {base_info['성분2(한글)']} ({base_info['성분2함량(%)']})")
                    st.write(f"  - 계통: {base_info['성분2계통']} [{base_info['성분2작용기작']}]")
                
                st.write(f"**· 살충경로:** {base_info['중독 방식(살충 경로)']}")
                st.write(f"**· 침투/침달성:** {base_info['침투이행성']} / {base_info['침달성']}")

            with col3:
                st.markdown("#### 📋 해충별 사용 기준")
                # ⭐️ 이 약이 가진 해충별로 안전사용기준을 반복해서 목록으로 띄워줌
                for _, row in drug_all_data.iterrows():
                    st.markdown(f"**[{row['병명']}]** <span style='color: #D35400; font-weight: bold;'>{row['사용량']}</span> / {row['안전사용기준']}", unsafe_allow_html=True)
                
                st.markdown("---")
                st.write(f"**· 혼용 가능(살충):** {base_info['혼용가능한 살충제']}")
                st.write(f"**· 혼용 가능(살균):** {base_info['혼용가능한 살균제']}")
                st.markdown(f"**· 🚨 혼용 불가/주의:** <span style='color:red'>{base_info['혼용불가(주의)약제']}</span>", unsafe_allow_html=True)
            
            # 작용원리 Expander (특성은 지우셨다고 하니 작용원리만 남겼습니다!)
            with st.expander(f"💡 {base_info['약명']} 작용원리 보기", expanded=False):
                st.markdown(f"{base_info['작용원리']}")
            
            st.markdown("---")
