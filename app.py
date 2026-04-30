import streamlit as st
import feedparser
import pandas as pd
from urllib.parse import quote
from collections import defaultdict
import datetime
import re

# 1. [데이터] 전역 변수 설정
ASSOC_LINKS = {
    "대한임상병리사협회": {"url": "http://www.kamt.or.kr/", "icon": "🏠"}, 
    "임상검사정보학회": {"url": "http://www.ksclis.or.kr/", "icon": "💻"}, 
    "대한임상미생물검사학회": {"url": "http://www.kscm.or.kr/", "icon": "🧫"}, 
    "대한임상혈액검사학회": {"url": "http://www.ksch.or.kr/", "icon": "🩸"}, 
    "대한진단검사의학회": {"url": "https://www.kslm.org/", "icon": "🔬"}
}

CALENDAR_EVENTS = [
    {"날짜": "2026-05-15", "항목": "📌 경기도임상병리사회 학생포럼 (두원공대 등)"},
    {"날짜": "2026-06-20", "항목": "📜 분자진단 전문가 교육 수료 (대학생 가능)"},
    {"날짜": "2026-09-10", "항목": "📝 임상병리사 국가고시 원서 접수 시작"},
    {"날짜": "2026-12-13", "항목": "🔥 제54회 임상병리사 국가고시 필기/실기"}
]

# 2. [UI] 페이지 설정 및 CSS
st.set_page_config(page_title="2026 임상병리 전략 마스터", layout="wide")
st.markdown("""
    <style>
    .news-badge {
        background-color: #D32F2F; color: white; padding: 2px 8px; border-radius: 4px;
        font-size: 0.75rem; font-weight: bold; margin-left: 8px; display: inline-block; vertical-align: middle;
    }
    .main-title { font-size: 1.1rem; font-weight: 600; margin-top: 15px; margin-bottom: 5px; }
    .month-header {
        background-color: #f1f3f6; padding: 8px 15px; border-radius: 6px; color: #2c3e50;
        font-weight: bold; margin-top: 25px; margin-bottom: 10px; border-left: 6px solid #D32F2F;
    }
    div.stButton > button { border-radius: 20px; font-size: 12px; padding: 2px 15px; }
    </style>
    """, unsafe_allow_html=True)

# 3. [로직] 데이터 수집 함수
@st.cache_data(ttl=600)
def fetch_refined_data(keywords, lang='ko'):
    all_entries = []
    for kw in keywords:
        query = f"{kw} -공무원 -모집"
        url = f"https://news.google.com/rss/search?q={quote(query)}&hl={lang}&gl=KR&ceid=KR:{lang}"
        feed = feedparser.parse(url)
        all_entries.extend(feed.entries)
    
    grouped = defaultdict(list)
    for entry in all_entries:
        clean_t = re.sub(r" - .*$", "", entry.title).strip()
        unique_key = clean_t.replace(" ", "")[:12]
        grouped[unique_key].append(entry)
        
    final = []
    for key, items in grouped.items():
        items.sort(key=lambda x: x.published_parsed, reverse=True)
        rep = items[0]
        rep.count = len(items)
        rep.dt = datetime.datetime(*rep.published_parsed[:6])
        
        title_match = re.search(r" - (.*)$", rep.title)
        if title_match:
            rep.media_name = title_match.group(1)
            rep.clean_title = rep.title.replace(f" - {rep.media_name}", "").strip()
        else:
            rep.media_name = rep.get('source', {}).get('text', '뉴스 매체')
            rep.clean_title = rep.title
        final.append(rep)
    return sorted(final, key=lambda x: x.dt, reverse=True)

# --- 4. 메인 화면 ---
st.title("🔬 2026 임상병리 커리어 전략 마스터")
st.divider()

tab_news, tab_paper, tab_cal = st.tabs(["🗞️ 의료 뉴스 분석", "🔬 전공 학술 자료", "📅 학사/교육 일정"])

# [탭 1] 의료 뉴스 분석 (기술 및 정책 위주)
with tab_news:
    with st.spinner("최신 의료 트렌드 로딩 중..."):
        # 수상 소식 키워드를 여기서 뺌
        news_data = fetch_refined_data(["임상병리 디지털 AI", "분자진단 신기술", "검사 자동화 시스템"])
        st.markdown(f"### 📋 오늘 분석된 주요 뉴스: 총 **{len(news_data)}**건")
        for entry in news_data:
            st.markdown(f'<div class="main-title">📍 {entry.clean_title}</div>', unsafe_allow_html=True)
            with st.expander("🔎 분석 리포트 확인"):
                st.info(f"**출처**: {entry.media_name} | **일자**: {entry.dt.strftime('%Y-%m-%d')}")
                st.link_button("원문 읽기", entry.link)

# [탭 2] 전공 학술 자료 (학생 수상 및 학술대회 집중)
with tab_paper:
    cl, cr = st.columns(2)
    with cl:
        st.subheader("🇰🇷 국내 학술 및 학생 수상 동향")
        # [수정] 수상 및 포럼 관련 키워드를 이쪽으로 배치
        academic = fetch_refined_data(["임상병리학과 학술상 수상", "임상병리 학생포럼", "대학생 논문 발표"])
        curr_month = ""
        for p in academic:
            m_str = p.dt.strftime('%B %Y')
            if m_str != curr_month:
                st.markdown(f'<div class="month-header">{m_str}</div>', unsafe_allow_html=True)
                curr_month = m_str
            
            col_t, col_b = st.columns([0.8, 0.2])
            with col_t:
                st.write(f"🏆 {p.clean_title}") # 수상 느낌 나게 트로피 아이콘
            with col_b:
                st.link_button("보기", p.link, use_container_width=True)

    with cr:
        st.subheader("🌐 Global Journals (English)")
        foreign = fetch_refined_data(["site:nature.com pathology", "site:sciencedirect.com diagnostic"], lang='en')
        for fp in foreign[:10]:
            if not re.search('[가-힣]', fp.clean_title):
                col_ft, col_fb = st.columns([0.8, 0.2])
                with col_ft:
                    st.write(f"📄 {fp.clean_title}")
                with col_fb:
                    st.link_button("Read", fp.link, use_container_width=True)

# [탭 3] 학사 일정 및 퀵 링크
with tab_cal:
    st.subheader("📅 임상병리학과 대학생 필수 일정")
    st.table(pd.DataFrame(CALENDAR_EVENTS))
    st.divider()
    st.subheader("🔗 공식 사이트 퀵 링크")
    l_cols = st.columns(len(ASSOC_LINKS))
    for i, (name, info) in enumerate(ASSOC_LINKS.items()):
        l_cols[i].link_button(f"{info['icon']} {name}", info['url'], use_container_width=True)
