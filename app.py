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

# 4. 엑셀에서 검색용 '전체 목록' 자동 추출하기
# (1) 약 이름 목록 뽑기 (중복 제거 후 가나다순 정렬)
drug_list = sorted([str(x) for x in df['약명'].unique() if str(x).strip() != ""])

# (2) 해충 이름 목록 뽑기 ("진딧물, 굴파리" 처럼 섞인 것을 다 쪼개서 개별 목록으로 만듦)
all_pests = []
for pests in df['병명'].dropna().astype(str):
    # 콤마(,)나 슬래시(/)로 여러 마리가 적혀있을 경우 쪼개기
    split_pests = [p.strip() for p in pests.replace('/', ',').split(',')]
    all_pests.extend(split_pests)
# 중복 해충 제거 후 가나다순 정렬
pest_list = sorted(list(set([p for p in all_pests if p])))

# 5. 검색창 만들기 (selectbox 적용!)
col_search1, col_search2 = st.columns(2)

with col_search1:
    # 빈칸("")을 리스트 맨 앞에 넣어서 처음엔 아무것도 선택 안 된 상태로 만듦
    search_keyword = st.selectbox(
        "💊 검색할 '약 이름'을 선택하거나 입력하세요", 
        options=[""] + drug_list
    )

with col_search2:
    pest_keyword = st.selectbox(
        "🐛 방제할 '해충(적용대상)'을 선택하거나 입력하세요", 
        options=[""] + pest_list
    )

# 6. 검색 로직 (둘 중 하나라도 선택되면 검색 시작)
if search_keyword or pest_keyword:
    filtered_df = df.copy()
    
    # 약 이름 필터링
    if search_keyword:
        filtered_df = filtered_df[filtered_df['약명'].astype(str).str.contains(search_keyword, case=False, na=False)]
        
    # 해충 이름 필터링
    if pest_keyword:
        filtered_df = filtered_df[filtered_df['병명'].astype(str).str.contains(pest_keyword, case=False, na=False)]

    if filtered_df.empty:
        st.warning("검색 조건에 맞는 약제가 없습니다. 이름을 다시 확인해주세요.")
    else:
        unique_drugs = filtered_df['약명'].unique()
        st.success(f"총 {len(unique_drugs)}가지의 약제가 검색되었습니다.")

        for drug_name in unique_drugs:
            drug_all_data = df[df['약명'] == drug_name]
            base_info = drug_all_data.iloc[0]

            st.subheader(f"🏷️ {base_info['약명']} ({base_info['유통사(제조사)']})")
            
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
                for _, row in drug_all_data.iterrows():
                    st.markdown(f"**[{row['병명']}]** <span style='color: #D35400; font-weight: bold;'>{row['사용량']}</span> / {row['안전사용기준']}", unsafe_allow_html=True)
                
                st.markdown("---")
                st.write(f"**· 혼용 가능(살충):** {base_info['혼용가능한 살충제']}")
                st.write(f"**· 혼용 가능(살균):** {base_info['혼용가능한 살균제']}")
                st.markdown(f"**· 🚨 혼용 불가/주의:** <span style='color:red'>{base_info['혼용불가(주의)약제']}</span>", unsafe_allow_html=True)
            
            with st.expander(f"💡 {base_info['약명']} 작용원리 보기", expanded=False):
                st.markdown(f"{base_info['작용원리']}")
            
            st.markdown("---")
