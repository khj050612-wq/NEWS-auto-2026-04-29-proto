import streamlit as st
import feedparser
from urllib.parse import quote
from collections import Counter
import re

st.set_page_config(page_title="임상병리 뉴스 트렌드", layout="wide")

# CSS 커스텀: 메트릭 글자 크기 조절 및 레이아웃 최적화
st.markdown("""
    <style>
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 1.0rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🔬 임상병리 & AI 의료 실시간 트렌드")
st.caption("최근 의료계 소식을 통합하여 보여주고 주요 키워드를 분석합니다.")

SEARCH_KEYWORDS = ["임상병리사", "분자진단", "AI 의료기기", "디지털 병리"]

@st.cache_data(ttl=3600)
def fetch_all_news(keywords):
    all_entries = []
    for kw in keywords:
        encoded_kw = quote(kw)
        url = f"https://news.google.com/rss/search?q={encoded_kw}&hl=ko&gl=KR&ceid=KR:ko"
        feed = feedparser.parse(url)
        all_entries.extend(feed.entries)
    
    unique_news = {entry.link: entry for entry in all_entries}.values()
    return sorted(unique_news, key=lambda x: x.published_parsed, reverse=True)

with st.spinner("데이터 분석 중..."):
    news_data = fetch_all_news(SEARCH_KEYWORDS)

# --- 1. 키워드 분석 및 배치 수정 ---
st.subheader("📊 지금 화제인 키워드")

all_titles = " ".join([entry.title for entry in news_data])
words = re.findall(r'\b[가-힣]{2,8}\b', all_titles)
# 의미 없는 단어 제외 (필터링)
exclude_words = ["의학신문", "기반", "국내", "기자", "개최", "출시"]
filtered_words = [w for w in words if w not in exclude_words]
common_words = Counter(filtered_words).most_common(10)

# [수정] 10개를 5개씩 2줄로 배치하여 글자 잘림 방지
for row in [common_words[:5], common_words[5:]]:
    cols = st.columns(5)
    for i, (word, count) in enumerate(row):
        cols[i].metric(label=f"TOP {filtered_words.index(word) if word in filtered_words else ''}", 
                       value=word, 
                       delta=f"{count}회")

st.divider()

# --- 2. 통합 뉴스 리스트 ---
st.subheader("📰 최근 1시간 주요 소식")

for entry in news_data[:15]:
    # 카드 스타일처럼 박스 안에 배치
    with st.expander(f"[{entry.source.text}] {entry.title}", expanded=False):
        st.write(f"📅 **발행일:** {entry.published}")
        
        # 간이 요약 처리
        summary_text = entry.summary if 'summary' in entry else ""
        clean_summary = re.sub('<[^<]+?>', '', summary_text)[:200]
        
        st.markdown(f"**📝 요약 내용:**")
        st.write(f"{clean_summary}...")
        
        st.markdown(f"🔗 [기사 원문 읽기]({entry.link})")
        
        # 저장 버튼 (기능은 추후 구글 시트 연동 시 구현)
        if st.button("📌 이 기사 스크랩하기", key=entry.link):
            st.success("구글 시트 연동 설정 후 저장 가능합니다!")

st.divider()
st.info("💡 **Tip:** 5개씩 2줄로 배치하여 모바일이나 작은 화면에서도 글자가 잘리지 않도록 개선했습니다.")
