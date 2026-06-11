import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="아우내농협 농약 검색 시스템 (실험용)", layout="wide")
st.title("🧪 아우내농협 농약 검색 프로그램 (실험용 Prototype)")
st.write("지운님이 설계하신 마스터 DB 기반의 농약 검색 실험실입니다.")

# 파일 경로 설정
excel_path = "실험용.xlsx"

@st.cache_data
def load_data(path):
    if os.path.exists(path):
        df = pd.read_excel(path, dtype=str)
        return df
    else:
        return None

df = load_data(excel_path)

if df is None:
    st.error(f"📂 엑셀 파일을 찾을 수 없습니다. 경로를 확인해 주세요!\n현재 설정된 경로: {excel_path}")
else:
    st.success("✅ 엑셀 데이터베이스를 성공적으로 불러왔습니다!")
    
    # 💡 핵심 방어 코드: 엑셀 제목 열에 숨어있는 띄어쓰기/공백을 모두 자동으로 지워줍니다.
    df.columns = df.columns.str.strip()
    
    # '약명' 열이 무사히 인식되었는지 확인합니다.
    if '약명' not in df.columns:
        st.error("🚨 엑셀의 첫 번째 줄에서 '약명' 열을 찾을 수 없습니다. 엑셀 1번 행에 제목들이 잘 적혀 있는지 확인해 주세요!")
        st.write("현재 파이썬이 읽어들인 엑셀 제목들은 다음과 같습니다:", list(df.columns))
    else:
        df['약명'] = df['약명'].str.strip()
        
        st.subheader("🔍 농약 이름 검색")
        search_query = st.text_input("검색할 농약 이름을 입력하세요 (예: 디져스, 캡틴 등)", "")

        if search_query:
            filtered_df = df[df['약명'].str.contains(search_query, case=False, na=False)]
            
            if not filtered_df.empty:
                st.write(f"📊 총 **{len(filtered_df)}**개의 약제가 검색되었습니다.")
                
                for idx, row in filtered_df.iterrows():
                    with st.container():
                        st.markdown(f"### 💊 {row.get('약명', '-')} *(품목번호: {row.get('품목번호', '-')})*")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown("**[기본 정보]**")
                            st.write(f"• **병명/해충명:** {row.get('병명', '-')}")
                            st.write(f"• **작용기작:** {row.get('작용 기작', '-')}")
                            st.write(f"• **제형:** {row.get('제형', '-')}")
                            st.write(f"• **제조/유통사:** {row.get('유통사 (제조사)', '-')}")
                            st.write(f"• **판매단가:** {row.get('판매 단가', '-')} 원")
                            
                        with col2:
                            st.markdown("**[성분 및 약효 특성]**")
                            st.write(f"• **성분 1:** {row.get('성분1 (한글)', '-')} ({row.get('성분 1계통', '-')}) - 기작: {row.get('성분1 작용기작', '-')}")
                            st.write(f"• **중독 방식:** {row.get('중독 방식 (살충 경로)', '-')}")
                            st.write(f"• **침투이행/침달성:** 이행성({row.get('침투이행성', '-')}) / 침달성({row.get('침달성', '-')})")
                            
                        with col3:
                            st.markdown("**[사용 기준 및 혼용]**")
                            st.write(f"• **안전사용기준:** {row.get('안전사용기준', '-')}")
                            st.write(f"• **희석배수/사용량:** {row.get('희석배수', '-')} / {row.get('사용량', '-')}")
                            st.write(f"• **⚠️ 혼용 불가:** {row.get('혼용불가(주의)약제', '-')}")
                        
                        st.markdown("---")
            else:
                st.warning("❌ 검색 결과가 없습니다.")

        st.subheader("📂 전체 데이터베이스 확인")
        if st.checkbox("전체 농약 목록 표로 보기"):
            st.dataframe(df)
