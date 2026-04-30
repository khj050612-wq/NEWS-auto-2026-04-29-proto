import streamlit as st
import feedparser
import pandas as pd
from urllib.parse import quote
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="임상병리 면접 마스터", layout="wide")

# 1. 바구니 설정 (레퍼런스 관리용 필드 추가)
if 'news_basket' not in st.session_state:
    st.session_state.news_basket = []

st.title("🏥 임상병리사 취업 대비: 전문 자료 아카이브")
st.caption("정확한 출처가 포함된 국내외 이슈를 수집하여 면접 답변의 근거를 만드세요.")

# 2. 데이터 추출 함수 (출처 정보 추출 강화)
@st.cache_data(ttl=3600)
def fetch_refined_data(query, source_type="naver"):
    if source_type == "naver":
        url = f"https://news.google.com/rss/search?q={quote(query)}+site:naver.com&hl=ko&gl=KR&ceid=KR:ko"
    else:
        # 해외 논문/저널 (Nature, Science, PubMed 등 주요 출처 위주 검색)
        url = f"https://news.google.com/rss/search?q={quote(query)}+journal+OR+research&hl=en&gl=US&ceid=US:en"
    
    feed = feedparser.parse(url)
    results = []
    for entry in feed.entries:
        # 출처(Source) 정보 안전하게 추출
        source = getattr(entry, 'source', {}).get('text', 'Unknown Source')
        results.append({
            'title': entry.title,
            'link': entry.link,
            'published': entry.published,
            'source': source
        })
    return results[:15]

# 3. 사이드바: 엑셀 저장 (면접 레퍼런스 형식)
st.sidebar.header("📋 면접 레퍼런스 리스트")
if st.session_state.news_basket:
    df = pd.DataFrame(st.session_state.news_basket)
    
    # 엑셀 다운로드 버튼
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Interview_Reference')
    
    st.sidebar.download_button(
        label="📥 레퍼런스 엑셀 다운로드",
        data=output.getvalue(),
        file_name=f"reference_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.ms-excel"
    )
    
    if st.sidebar.button("리스트 초기화"):
        st.session_state.news_basket = []
        st.rerun()

# 4. 메인 화면: 탭 구성
tab1, tab2 = st.tabs(["🇰🇷 국내 취업/의료 이슈", "🔬 해외 연구/기술 트렌드"])

with tab1:
    st.subheader("국내 주요 언론사 및 병원 소식")
    q_kr = st.text_input("국내 키워드", value="임상병리사 채용 트렌드")
    for item in fetch_refined_data(q_kr, "naver"):
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"**{item['title']}**")
            st.caption(f"출처: {item['source']} | 날짜: {item['published']}")
        with col2:
            if st.button("📌 스크랩", key=f"kr_{item['link']}"):
                st.session_state.news_basket.append({
                    "분류": "국내이슈",
                    "출처": item['source'],
                    "제목": item['title'],
                    "날짜": item['published'],
                    "링크": item['link']
                })
                st.toast("레퍼런스 저장!")

with tab2:
    st.subheader("해외 주요 저널 및 연구 소식")
    q_en = st.text_input("해외 키워드", value="Next Generation Sequencing Diagnostics")
    for item in fetch_refined_data(q_en, "paper"):
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"**{item['title']}**")
            # 해외 자료는 저널명이 곧 레퍼런스
            st.caption(f"Source: {item['source']} | Date: {item['published']}")
        with col2:
            if st.button("📌 스크랩", key=f"en_{item['link']}"):
                st.session_state.news_basket.append({
                    "분류": "해외논문/기술",
                    "출처": item['source'],
                    "제목": item['title'],
                    "날짜": item['published'],
                    "링크": item['link']
                })
                st.toast("저널 정보 포함 완료!")
