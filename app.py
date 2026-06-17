import streamlit as st
import pandas as pd

st.set_page_config(page_title="아우내 영농조합법인 농약 검색기", page_icon="🌱", layout="wide")

st.markdown("""
    <style>
        /* (1) 사이드바 라디오 버튼 글씨 크기 대폭 키우기 */
        .stSidebar .stRadio p {
            font-size: 1.4rem !important;
            font-weight: bold !important;
            color: #2C3E50 !important;
            line-height: 2.0 !important;
        }
        /* 사이드바 제목 크기 키우기 */
        .stSidebar h1, .stSidebar h2, .stSidebar h3 {
            font-size: 2.0rem !important;
        }
        
        /* (2) 모바일 전용: 좌측 상단 사이드바 열기 버튼( > 모양 ) 눈에 확 띄게 만들기 */
        button[data-testid="collapsedControl"] {
            background-color: #1E8449 !important; /* 아우내 시그니처 초록색 */
            color: white !important;
            border-radius: 8px !important;
            transform: scale(1.4) !important; /* 버튼 크기 1.4배 확대 */
            margin: 15px !important;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.3) !important; /* 그림자 효과 */
        }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    file_name = "26아우내영농조합법인 농약 혼용가부표(충).xlsx"
    
    df_insect = pd.read_excel(file_name, sheet_name="살충제목록")
    df_insect = df_insect.fillna("")
    
    df_fungi = pd.read_excel(file_name, sheet_name="살균제목록")
    df_fungi = df_fungi.fillna("")
    
    return df_insect, df_fungi

try:
    df_insect, df_fungi = load_data()
except Exception as e:
    st.error(f"엑셀 파일을 찾을 수 없거나 시트 이름이 틀렸습니다...\n에러: {e}")
    st.stop()

st.sidebar.title("🔍 아우내 처방 시스템")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "검색할 농약을 선택하세요", 
    ["🐛 살충제 검색", "🍄 살균제 검색"]
)
st.sidebar.markdown("---")

st.markdown("""
    <div style='background-color: #FEF9E7; padding: 15px; border-radius: 8px; border-left: 6px solid #F4D03F; margin-bottom: 20px;'>
        <span style='font-size: 1.2em; font-weight: bold; color: #7D6608;'>📱 스마트폰(모바일) 이용자 안내:</span> <br>
        화면에 맨 왼쪽 위 '화살표( > ) 버튼'</b>을 누르시면 살충제/살균제 선택 창이 나타납니다!
    </div>
""", unsafe_allow_html=True)


if menu == "🐛 살충제 검색":
    st.title("🐛 살충제 검색 시스템")
    st.markdown("**처방과 혼용 가부를 한눈에!** 검색 조건을 입력하세요.")
    st.markdown("**아직 부족한 점이 많습니다. 많은 피드백 부탁드립니다.**")
    st.markdown("---")

    drug_list = sorted([str(x) for x in df_insect['약명'].unique() if str(x).strip() != ""])
    all_pests = []
    for pests in df_insect['병명'].dropna().astype(str):
        split_pests = [p.strip() for p in pests.replace('/', ',').split(',')]
        all_pests.extend(split_pests)
    pest_list = sorted(list(set([p for p in all_pests if p])))

    def clear_insect_search():
        st.session_state.insect_drug = ""
        st.session_state.insect_pest = ""
        st.session_state.insect_ing = ""

    col_btn1, col_btn2 = st.columns([8, 2])
    with col_btn2:
        st.button("🔄 살충제 검색 초기화", on_click=clear_insect_search, use_container_width=True)

    col_search1, col_search2, col_search3 = st.columns(3)
    with col_search1:
        search_keyword = st.selectbox("💊 검색할 '약 이름' (예: 엑시렐)", options=[""] + drug_list, key='insect_drug')
    with col_search2:
        pest_keyword = st.selectbox("🐛 방제할 '해충' (예: 진딧물)", options=[""] + pest_list, key='insect_pest')
    with col_search3:
        ingredient_keyword = st.text_input("🧪 '성분/계통/기작' 입력 (예: 28)", "", key='insect_ing')

    if search_keyword or pest_keyword or ingredient_keyword:
        filtered_df = df_insect.copy()
        
        if search_keyword:
            filtered_df = filtered_df[filtered_df['약명'].astype(str).str.contains(search_keyword, case=False, na=False, regex=False)]
        if pest_keyword:
            filtered_df = filtered_df[filtered_df['병명'].astype(str).str.contains(pest_keyword, case=False, na=False, regex=False)]
        if ingredient_keyword:
            mask = (
                filtered_df['성분1(한글)'].astype(str).str.contains(ingredient_keyword, case=False, na=False, regex=False) |
                filtered_df['성분2(한글)'].astype(str).str.contains(ingredient_keyword, case=False, na=False, regex=False) |
                filtered_df['성분1계통'].astype(str).str.contains(ingredient_keyword, case=False, na=False, regex=False) |
                filtered_df['성분2계통'].astype(str).str.contains(ingredient_keyword, case=False, na=False, regex=False) |
                filtered_df['작용기작'].astype(str).str.contains(ingredient_keyword, case=False, na=False, regex=False) |
                filtered_df['성분1작용기작'].astype(str).str.contains(ingredient_keyword, case=False, na=False, regex=False) |
                filtered_df['성분2작용기작'].astype(str).str.contains(ingredient_keyword, case=False, na=False, regex=False)
            )
            filtered_df = filtered_df[mask]

        if filtered_df.empty:
            st.warning("검색 조건에 맞는 약제가 없습니다. 이름을 다시 확인해주세요.")
        else:
            unique_drugs = filtered_df['약명'].unique()
            st.success(f"총 {len(unique_drugs)}가지의 살충제가 검색되었습니다.")

            for drug_name in unique_drugs:
                drug_all_data = df_insect[df_insect['약명'] == drug_name]
                base_info = drug_all_data.iloc[0]

                st.markdown(f"### 🏷️ {base_info['약명']} ({base_info['유통사(제조사)']}) &nbsp;&nbsp; <span style='font-weight: bold; color: #1E8449;'>[{base_info['작용기작']}]</span>", unsafe_allow_html=True)
                
                price = base_info['판매단가']
                price_formatted = "가격 정보 없음" if pd.isna(price) or str(price).strip() == "" else (f"{int(float(price)):,}원" if str(price).replace('.','',1).isdigit() else f"{price}")

                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("#### 📌 기본 정보")
                    all_pests_str = ", ".join(drug_all_data['병명'].unique())
                    st.markdown(f"**· 등록된 모든 해충:** <span style='font-size: 1.4em; font-weight: bold; color: #1E8449;'>{all_pests_str}</span>", unsafe_allow_html=True)
                    st.write(f"**· 작용기작:** {base_info['작용기작']}")
                    st.write(f"**· 제형:** {base_info['제형']}")
                    st.write(f"**· 목적/구분:** {base_info['목적']} / {base_info['구분']}")
                    st.markdown(f"**· 규격 및 단가:** {base_info['규격']}{base_info['단위']} / <span style='font-size: 1.4em; font-weight: bold; color: #C0392B;'>{price_formatted}</span>", unsafe_allow_html=True)

                with col2:
                    st.markdown("#### 🧪 성분 및 침투 정보")
                    st.write(f"**· 성분1:** {base_info['성분1(한글)']} ({base_info['성분1함량(%)']}%)")
                    st.write(f"  - 계통: {base_info['성분1계통']} [{base_info['성분1작용기작']}]")
                    if base_info['성분2(한글)'] != "":
                        st.write(f"**· 성분2:** {base_info['성분2(한글)']} ({base_info['성분2함량(%)']}%)")
                        st.write(f"  - 계통: {base_info['성분2계통']} [{base_info['성분2작용기작']}]")
                    st.write(f"**· 살충경로:** {base_info['중독 방식(살충 경로)']}")
                    st.write(f"**· 침투/침달성:** {base_info['침투이행성']} / {base_info['침달성']}")

                with col3:
                    st.markdown("#### 📋 해충별 사용 기준")
                    for _, row in drug_all_data.iterrows():
                        st.markdown(f"**[{row['병명']}]** <span style='font-size: 1.4em; font-weight: bold; color: #D35400;'>{row['사용량']}</span> / {row['안전사용기준']}", unsafe_allow_html=True)
                    st.markdown("---")
                    st.write(f"**· 혼용 가능(살충):** {base_info['혼용가능한 살충제']}")
                    st.write(f"**· 혼용 가능(살균):** {base_info['혼용가능한 살균제']}")
                    st.markdown(f"**· 🚨 혼용 불가/주의:** <span style='color:red'>{base_info['혼용불가(주의)약제']}</span>", unsafe_allow_html=True)
                
                with st.expander(f"💡 {base_info['약명']} 작용원리 보기", expanded=False):
                    st.markdown(f"{base_info['작용원리']}")
                st.markdown("---")

elif menu == "🍄 살균제 검색":
    st.title("🍄 살균제 검색 시스템")
    st.markdown("**처방과 혼용 가부를 한눈에!** 검색 조건을 입력하세요.")
    st.markdown("**아직 부족한 점이 많습니다. 많은 피드백 부탁드립니다.**")
    st.markdown("---")

    drug_list_fungi = sorted([str(x) for x in df_fungi['약명'].unique() if str(x).strip() != ""])
    all_diseases = []
    for disease in df_fungi['병명'].dropna().astype(str):
        split_disease = [d.strip() for d in disease.replace('/', ',').split(',')]
        all_diseases.extend(split_disease)
    disease_list = sorted(list(set([d for d in all_diseases if d])))

    def clear_fungi_search():
        st.session_state.fungi_drug = ""
        st.session_state.fungi_disease = ""
        st.session_state.fungi_ing = ""

    col_btn1, col_btn2 = st.columns([8, 2])
    with col_btn2:
        st.button("🔄 살균제 검색 초기화", on_click=clear_fungi_search, use_container_width=True)

    col_search1, col_search2, col_search3 = st.columns(3)
    with col_search1:
        search_keyword_f = st.selectbox("💊 검색할 '약 이름'", options=[""] + drug_list_fungi, key='fungi_drug')
    with col_search2:
        disease_keyword = st.selectbox("🦠 방제할 '병명(적용대상)'", options=[""] + disease_list, key='fungi_disease')
    with col_search3:
        ingredient_keyword_f = st.text_input("🧪 '성분/계통/기작' 입력", "", key='fungi_ing')

    if search_keyword_f or disease_keyword or ingredient_keyword_f:
        filtered_df_f = df_fungi.copy()
        
        if search_keyword_f:
            filtered_df_f = filtered_df_f[filtered_df_f['약명'].astype(str).str.contains(search_keyword_f, case=False, na=False, regex=False)]
        if disease_keyword:
            filtered_df_f = filtered_df_f[filtered_df_f['병명'].astype(str).str.contains(disease_keyword, case=False, na=False, regex=False)]
        if ingredient_keyword_f:
            mask_f = (
                filtered_df_f['성분1(한글)'].astype(str).str.contains(ingredient_keyword_f, case=False, na=False, regex=False) |
                filtered_df_f['성분1계통'].astype(str).str.contains(ingredient_keyword_f, case=False, na=False, regex=False) |
                filtered_df_f['작용기작'].astype(str).str.contains(ingredient_keyword_f, case=False, na=False, regex=False)
            )
            filtered_df_f = filtered_df_f[mask_f]

        if filtered_df_f.empty:
            st.warning("검색 조건에 맞는 약제가 없습니다.")
        else:
            unique_drugs_f = filtered_df_f['약명'].unique()
            st.success(f"총 {len(unique_drugs_f)}가지의 살균제가 검색되었습니다.")

            for drug_name in unique_drugs_f:
                drug_all_data_f = df_fungi[df_fungi['약명'] == drug_name]
                base_info_f = drug_all_data_f.iloc[0]

                st.markdown(f"### 🏷️ {base_info_f['약명']} ({base_info_f.get('유통사(제조사)', '')}) &nbsp;&nbsp; <span style='font-weight: bold; color: #1E8449;'>[{base_info_f.get('작용기작', '')}]</span>", unsafe_allow_html=True)
                
                price_f = base_info_f.get('판매단가', '')
                price_formatted_f = "가격 정보 없음" if pd.isna(price_f) or str(price_f).strip() == "" else (f"{int(float(price_f)):,}원" if str(price_f).replace('.','',1).isdigit() else f"{price_f}")

                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("#### 📌 기본 정보")
                    all_diseases_str = ", ".join(drug_all_data_f['병명'].unique())
                    st.markdown(f"**· 등록된 모든 병명:** <span style='font-size: 1.4em; font-weight: bold; color: #1E8449;'>{all_diseases_str}</span>", unsafe_allow_html=True)
                    st.write(f"**· 제형:** {base_info_f.get('제형', '')}")
                    st.markdown(f"**· 규격 및 단가:** {base_info_f.get('규격', '')}{base_info_f.get('단위', '')} / <span style='font-size: 1.4em; font-weight: bold; color: #C0392B;'>{price_formatted_f}</span>", unsafe_allow_html=True)

                with col2:
                    st.markdown("#### 🧪 성분 및 작용 원리")
                    st.write(f"**· 성분1:** {base_info_f.get('성분1(한글)', '')} ({base_info_f.get('성분1함량(%)', '')}%)")
                    st.write(f"  - 계통: {base_info_f.get('성분1계통', '')} [{base_info_f.get('성분1작용기작', '')}]")
                    st.write(f"**· 작용원리 1:** {base_info_f.get('작용원리1', '정보 없음')}")
                    st.write(f"**· 작용원리 2:** {base_info_f.get('작용원리2', '정보 없음')}")

               with col3:
                    st.markdown("#### 📋 병해별 사용 기준")
                    for _, row in drug_all_data_f.iterrows():
                        st.markdown(f"**[{row['병명']}]** <span style='font-size: 1.4em; font-weight: bold; color: #D35400;'>{row.get('사용량', '')}</span> / {row.get('안전사용기준', '')}", unsafe_allow_html=True)
                 # 💡 base_info_f 로 이름을 맞추고, .get()을 써서 엑셀에 빈칸이거나 열 이름이 달라도 에러가 안 나게 만들었습니다.
                st.markdown("---")
                st.write(f"**· 혼용 가능(살충):** {base_info_f.get('혼용가능한 살충제', '정보 없음')}")
                st.write(f"**· 혼용 가능(살균):** {base_info_f.get('혼용가능한 살균제', '정보 없음')}")
                st.markdown(f"**· 🚨 혼용 불가/주의:** <span style='color:red'>{base_info_f.get('혼용불가(주의)약제', '정보 없음')}</span>", unsafe_allow_html=True)
                st.markdown("---")
