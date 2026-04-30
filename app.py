import streamlit as st
import feedparser
import pandas as pd
from urllib.parse import quote
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="임상병리 뉴스 스크랩", layout="wide")

# 1. 뉴스 바구니 초기화
if 'news_basket' not in st.session_state:
    st.session_state.news_basket = []

st.title("🔬 임상병리 & AI 뉴스 바구니")
st.caption("기사를 바구니에 담고 엑셀로 저장하세요. (보안 안심 🛡️)")

# 2. 뉴스 수집 설정
SEARCH_KEYWORDS = ["임상병리사", "분자진단", "AI 의료기기", "디지털 병리"]

@st.cache_data(ttl=3600)
def fetch_news(keywords):
    all_entries = []
    for kw in keywords:
        url = f"https://news.google.com/rss/search?q={quote(kw)}&hl=ko&gl=KR&ceid=KR:ko"
        feed = feedparser.parse(url)
        all_entries.extend(feed.entries)
    # 중복 제거
    unique = {e.link: e for e in all_entries}.values()
    return sorted(unique, key=lambda x: x.published_parsed, reverse=True)

# 사이드바 설정
st.sidebar.header("🧺 내 뉴스 바구니")
st.sidebar.write(f"현재 **{len(st.session_state.news_basket)}개** 담김")

if st.session_state.news_basket:
    df = pd.DataFrame(st.session_state.news_basket)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='ScrappedNews')
    
    st.sidebar.download_button(
        label="📥 엑셀 파일로 저장하기",
        data=output.getvalue(),
        file_name=f"news_scrap_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.ms-excel"
    )
    
    if st.sidebar.button("🗑️ 바구니 비우기"):
        st.session_state.news_basket = []
        st.rerun()

# 3. 메인 뉴스 리스트 표시
with st.spinner("최신 기사 불러오는 중..."):
    news_data = fetch_news(SEARCH_KEYWORDS)

for entry in news_data[:20]:
    # [에러 해결 포인트] 언론사 이름이 없을 경우를 대비해 안전하게 가져오기
    source_name = getattr(entry, 'source', {}).get('text', '알 수 없음')
    
    with st.container():
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**[{source_name}]** {entry.title}")
            st.caption(f"📅 {entry.published}")
        with col2:
            if st.button("📌 담기", key=entry.link):
                item = {
                    "수집일": datetime.now().strftime("%Y-%m-%d"),
                    "언론사": source_name,
                    "제목": entry.title,
                    "링크": entry.link
                }
                if not any(d['link'] == entry.link for d in st.session_state.news_basket):
                    st.session_state.news_basket.append(item)
                    st.toast("바구니에 추가되었습니다!")
                else:
                    st.toast("이미 담겨있습니다.")
        st.write("---")
