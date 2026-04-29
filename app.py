import streamlit as st
import feedparser
from urllib.parse import quote
from collections import Counter # 단어 개수 세기용
import re

st.set_page_config(page_title="임상병리 뉴스 트렌드", layout="wide")

st.title("🔬 임상병리 & AI 의료 실시간 트렌드")
st.caption("최근 의료계 소식을 통합하여 보여주고 주요 키워드를 분석합니다.")

# 1. 설정: 검색 키워드 모음 (최근 화제 중심)
SEARCH_KEYWORDS = ["임상병리사", "분자진단", "AI 의료기기", "디지털 병리"]

@st.cache_data(ttl=3600) # 1시간마다 데이터 새로고침
def fetch_all_news(keywords):
    all_entries = []
    for kw in keywords:
        encoded_kw = quote(kw)
        url = f"https://news.google.com/rss/search?q={encoded_kw}&hl=ko&gl=KR&ceid=KR:ko"
        feed = feedparser.parse(url)
        all_entries.extend(feed.entries)
    
    # 중복 기사 제거 (링크 기준) 및 최신순 정렬
    unique_news = {entry.link: entry for entry in all_entries}.values()
    return sorted(unique_news, key=lambda x: x.published_parsed, reverse=True)

# 2. 뉴스 데이터 가져오기
with st.spinner("최신 기사를 수집하고 분석 중입니다..."):
    news_data = fetch_all_news(SEARCH_KEYWORDS)

# 3. 키워드 빈도 분석 (상단 배치)
st.subheader("📊 지금 화제인 키워드 (최근 뉴스 제목 기준)")
all_titles = " ".join([entry.title for entry in news_data])
# 불용어(조사 등) 대략 제거하고 명사 위주로 추출 (간이 방식)
words = re.findall(r'\b[가-힣]{2,8}\b', all_titles) 
common_words = Counter(words).most_common(10)

# 가로로 키워드 칩(Chip) 보여주기
kw_cols = st.columns(len(common_words))
for i, (word, count) in enumerate(common_words):
    kw_cols[i].metric(label=f"TOP {i+1}", value=word, delta=f"{count}회 언급")

st.divider()

# 4. 통합 뉴스 리스트 & 요약
st.subheader("📰 최신 뉴스 통합 리스트")

# 개수가 너무 많으면 성능이 저하되므로 최근 15개만 출력
for entry in news_data[:15]:
    with st.container():
        col1, col2 = st.columns([1, 4])
        with col1:
            # 발행 날짜를 간단하게 변환
            st.write(f"📅 {entry.published[:16]}")
        with col2:
            st.markdown(f"#### [{entry.source.text}] {entry.title}")
            
            # 요약 로직 (현재는 맛보기용으로 본문의 앞부분만 추출)
            # 나중에 OpenAI API를 연결하면 이 부분이 실제 요약문으로 바뀝니다.
            summary_text = entry.summary if 'summary' in entry else "본문 요약 내용을 가져올 수 없습니다."
            clean_summary = re.sub('<[^<]+?>', '', summary_text)[:150] # HTML 태그 제거
            
            st.write(f"📄 **요약:** {clean_summary}...")
            st.write(f"🔗 [기사 읽기]({entry.link})")
        st.write("---")

st.info("💡 Tip: OpenAI API를 연결하면 '요약' 부분이 3줄 핵심 정리로 업그레이드됩니다!")
