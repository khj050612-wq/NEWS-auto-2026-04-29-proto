import streamlit as st
import feedparser
import pandas as pd
from urllib.parse import quote

st.set_page_config(page_title="임상병리 전략 보드", layout="wide")

# [임시] 저녁에 구글 시트 연동 전까지 사용할 희진님의 경험/가치관 데이터
# 나중에 이 부분이 구글 시트에서 불러온 텍스트로 대체됩니다.
MY_EXPERIENCE = "분자진단 실습 경험, 환자 중심의 정확한 검사 지향, 꼼꼼한 데이터 관리"

if 'news_basket' not in st.session_state:
    st.session_state.news_basket = []

# --- 핵심 추출 로직 ---
def get_strategic_analysis(title, experience):
    # 1. 기사 한줄 요약 (제목 기반)
    summary = f"{title[:30]}..." 
    
    # 2. 핵심 키워드 추출 (간단 로직)
    keywords = "의료 트렌드 / 보건 정책"
    if "AI" in title: keywords = "디지털 전환 / 진단 보조"
    elif "검사" in title: keywords = "검사 정확도 / 효율성"
    
    # 3. 임상병리 연결
    connection = "임상병리사의 직무 전문성과 검체 관리 역량이 강조되는 이슈입니다."
    
    # 4. 내 경험/가치관과 연결 (이게 핵심!)
    my_link = f"내 가치관('{experience}')을 바탕으로 면접에서 직무 적합성을 어필하기 좋은 소재입니다."
    
    return {
        "요약": summary,
        "핵심": keywords,
        "연결": connection,
        "매칭": my_link
    }

st.title("🔬 임상병리 전략적 뉴스 분석")

# 뉴스 수집 로직 (네이버 뉴스 중심)
@st.cache_data(ttl=3600)
def fetch_news():
    SEARCH_KEYWORDS = ["임상병리사", "진단기술", "대학병원 의료"]
    all_entries = []
    for kw in SEARCH_KEYWORDS:
        url = f"https://news.google.com/rss/search?q={quote(kw)}+-blog+-cafe&hl=ko&gl=KR&ceid=KR:ko"
        feed = feedparser.parse(url)
        all_entries.extend(feed.entries)
    return sorted({e.link: e for e in all_entries}.values(), key=lambda x: x.published_parsed, reverse=True)

for entry in fetch_news()[:15]:
    analysis = get_strategic_analysis(entry.title, MY_EXPERIENCE)
    
    with st.container():
        st.markdown(f"### 📍 {entry.title}")
        st.caption(f"출처: {getattr(entry, 'source', {}).get('text', '뉴스')} | [원문보기]({entry.link})")
        
        # 딱 필요한 4가지만 표로 구성
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**📝 기사 한줄 요약:** {analysis['요약']}")
            st.markdown(f"**🔑 핵심 키워드:** {analysis['핵심']}")
        with col2:
            st.markdown(f"**🧬 임상병리 연결:** {analysis['연결']}")
            st.markdown(f"**🎯 내 경험과 연결:** {analysis['매칭']}")
            
        # 내 생각 입력은 선택사항 (안 써도 그만)
        user_comment = st.text_input("메모 (필요할 때만 작성)", key=f"note_{entry.link}")
        
        if st.button("바구니에 담기", key=f"btn_{entry.link}"):
            st.session_state.news_basket.append
            
