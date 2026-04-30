import streamlit as st
import feedparser
import pandas as pd
from urllib.parse import quote
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="임상병리 면접 마스터", layout="wide")

if 'news_basket' not in st.session_state:
    st.session_state.news_basket = []

st.title("🏥 대학병원 임상병리사 면접 아카이브")
st.caption("잡다한 소식은 제외하고, 보건의료·학술 전문 자료만 정밀 추출합니다.")

# 2. 데이터 추출 함수 (검색 필터 대폭 강화)
@st.cache_data(ttl=3600)
def fetch_refined_data(query, source_type="naver"):
    # 의료/보건 관련 핵심 키워드 강제 추가 (잡동사니 제거용)
    medical_filter = " (보건 OR 의료 OR 병원 OR 진단 OR 의학)"
    
    if source_type == "naver":
        # site:naver.com 대신 전문 뉴스 포털 필터링 적용
        # 블로그(-blog)와 카페(-cafe) 결과 제외 규칙 추가
        url = f"https://news.google.com/rss/search?q={quote(query + medical_filter)}+-blog+-cafe+-map&hl=ko&gl=KR&ceid=KR:ko"
    else:
        # 해외 전문 저널/학술지 타겟팅 강화
        url = f"https://news.google.com/rss/search?q={quote(query)}+journal+OR+research+OR+clinical&hl=en&gl=US&ceid=US:en"
    
    feed = feedparser.parse(url)
    results = []
    for entry in feed.entries:
        # 출처 정보 가독성 개선
        source = getattr(entry, 'source', {}).get('text', '전문 언론사')
        
        # 날짜 포맷 변경 (보기 편하게)
        raw_date = entry.published
        try:
            clean_date = datetime.strptime(raw_date, '%a, %d %b %Y %H:%M:%S %Z').strftime('%Y-%m-%d')
        except:
            clean_date = raw_date[:16]

        results.append({
            'title': entry.title,
            'link': entry.link,
            'published': clean_date,
            'source': source
        })
    return results[:15]

# --- 화면 구성 (기존 탭/바구니 로직과 동일) ---
tab1, tab2 = st.tabs(["🇰🇷 국내 보건의료 이슈", "🔬 해외 전문 저널/기술"])

with tab1:
    st.subheader("국내 의료/진단 최신 뉴스")
    # 예: '평택'만 쳐도 '평택 의료', '평택 병원' 결과가 나오도록 유도
    q_kr = st.text_input("지역명 또는 키워드 입력", value="대학병원 채용")
    data_kr = fetch_refined_data(q_kr, "naver")
    
    if not data_kr:
        st.write("검색 결과가 없습니다. 키워드를 조절해보세요.")
        
    for item in data_kr:
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"**{item['title']}**")
            st.caption(f"📍 출처: {item['source']} | 📅 날짜: {item['published']}")
        with col2:
            if st.button("📌 스크랩", key=f"kr_{item['link']}"):
                st.session_state.news_basket.append({
                    "분류": "국내이슈", "출처": item['source'], "제목": item['title'], "날짜": item['published'], "링크": item['link']
                })
                st.toast("면접 레퍼런스 추가!")
        st.write("---")

# (해외 탭과 사이드바 로직은 이전과 동일하게 유지)
