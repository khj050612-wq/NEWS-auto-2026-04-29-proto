import streamlit as st
import feedparser
from datetime import datetime

st.set_page_config(page_title="임상병리 뉴스 스크랩", layout="wide")

st.title("🔬 임상병리 AI & 분자진단 최신 뉴스")
st.caption("설정한 키워드에 대한 최신 기사를 구글 뉴스에서 실시간으로 가져옵니다.")

# 키워드 설정
keywords = ["임상병리", "AI 의료", "분자진단"]

# 뉴스 수집 함수
def get_google_news(keyword):
    url = f"https://news.google.com/rss/search?q={keyword}&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(url)
    return feed.entries[:5] 

cols = st.columns(len(keywords))

for i, keyword in enumerate(keywords):
    with cols[i]:
        st.subheader(f"📍 {keyword}")
        news_items = get_google_news(keyword)
        
        if not news_items:
            st.write("최신 기사가 없습니다.")
        
        for entry in news_items:
            with st.expander(entry.title):
                st.write(f"📅 발행일: {entry.published}")
                st.write(f"🔗 [기사 원문 보기]({entry.link})")
                st.info("💡 요약 기능은 다음 업데이트(GPT API 연동)에서 추가될 예정입니다.")

st.divider()
st.write("© 2026 임상병리 자동화 프로젝트 프로토타입")
