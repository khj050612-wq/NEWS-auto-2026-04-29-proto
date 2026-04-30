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

# 2. [UI] 페이지 설정 및 스타일
st.set_page_config(page_title="2026 임상병리 전략 마스터", layout="wide")
st.markdown("""
    <style>
    .main-title { font-size: 0.95rem; font-weight: 600; margin-top: 10px; margin-bottom: 2px; }
    .caption-style { font-size: 0.8rem; color: #777; margin-bottom: 5px; }
    hr { margin: 8px 0px; border: 0; border-top: 1px solid #f0f0f0; }
    div.stButton > button { border-radius: 12px; font-size: 11px; height: 26px; }
    </style>
    """, unsafe_allow_html=True)

# 3. [로직] 데이터 수집 함수
@st.cache_data(ttl=600)
def fetch_refined_data(query_text, lang='ko'):
    # 잡동사니 필터 강화
    final_query = f"{query_text} -양체험 -원장 -의사 -공무원 -모집"
    url = f"https://news.google.com/rss/search?q={quote(final_query)}&hl={lang}&gl=KR&ceid=KR:{lang}"
    feed = feedparser.parse(url)
    
    grouped = defaultdict(list)
    for entry in feed.entries:
        clean_t = re.sub(r" - .*$", "", entry.title).strip()
        unique_key = clean_t.replace(" ", "")[:12]
        grouped[unique_key].append(entry)
        
    final = []
    for key, items in grouped.items():
        items.sort(key=lambda x: x.published_parsed, reverse=True)
        rep = items[0]
        rep.dt = datetime.datetime(*rep.published_parsed[:6])
        title_match = re.search(r" - (.*)$", rep.title)
        rep.media_name = title_match.group(1) if title_match else "뉴스"
        rep.clean_title = rep.title.replace(f" - {rep.media_name}", "").strip() if title_match else rep.title
        final.append(rep)
    return sorted(final, key=lambda x: x.dt, reverse=True)

# 영어 키워드 강조 함수
def bold_keywords(title):
    kws = ["Pathology", "Clinical", "Diagnostic", "Molecular", "Hematology", "EEG", "ECG", "AI"]
    for kw in kws:
        title = re.sub(f"({kw})", r"**\1**", title, flags=re.IGNORECASE)
    return title

# --- 4. 메인 화면 ---
st.title("🔬 2026 임상병리 커리어 전략 마스터")

tab_news, tab_paper, tab_cal = st.tabs(["🗞️ 보건/의료 사회 이슈", "🧬 전공 분과별 학술 자료", "📅 일정/링크"])

# [탭 1] 의료 뉴스 (보건계열, 사회 이슈 동향 파악용)
with tab_news:
    st.subheader("📰 의료계 주요 현안 및 정책 동향")
    # 특정 파트가 아닌 전체적인 보건/의료 정책 키워드
    news_data = fetch_refined_data("보건복지부 의료 정책 OR 대한의사협회 동향 OR 의료 대란 OR 공공의료 정책")
    for e in news_data[:15]:
        st.markdown(f'<div class="main-title">📍 {e.clean_title}</div>', unsafe_allow_html=True)
        c1, c2 = st.columns([0.85, 0.15])
        c1.markdown(f'<div class="caption-style">{e.media_name} | {e.dt.strftime("%Y-%m-%d")}</div>', unsafe_allow_html=True)
        c2.link_button("원문", e.link, use_container_width=True)
        st.markdown("<hr>", unsafe_allow_html=True)

# [탭 2] 전공 학술 자료 (희진님의 찐 전공 파트들)
with tab_paper:
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("🇰🇷 국내 전공 분과별 동향")
        
        # 1. 진단검사 파트
        with st.expander("🧪 진단검사의학 파트 (혈액, 미생물, 분자유전 등)", expanded=True):
            jin_query = "진단검사의학과 (세포유전 OR 혈액응고 OR 요경검 OR 미생물 OR 분자유전 OR 혈액은행)"
            for e in fetch_refined_data(jin_query)[:5]:
                st.write(f"🔹 {e.clean_title}")
                st.link_button(f"{e.media_name} 보기", e.link)
        
        # 2. 생리 기능 파트
        with st.expander("🧠 생리 기능 파트 (신경, 순환기, 심초음파 등)"):
            sang_query = "임상병리사 (신경과 OR 순환기과 OR EEG OR NCS OR 심초음파 OR TCD)"
            for e in fetch_refined_data(sang_query)[:5]:
                st.write(f"🔹 {e.clean_title}")
                st.link_button(f"{e.media_name} 보기", e.link)

        # 3. 병리 파트
        with st.expander("🔬 병리 파트 (조직, 세포, 면역, 디지털병리)"):
            byung_query = "병리과 (조직병리 OR 세포병리 OR 면역병리 OR 디지털병리)"
            for e in fetch_refined_data(byung_query)[:5]:
                st.write(f"🔹 {e.clean_title}")
                st.link_button(f"{e.media_name} 보기", e.link)
                
        # 4. 학생 수상
        with st.expander("🏆 학생 포럼 및 수상 실적"):
            for e in fetch_refined_data("임상병리학과 학생포럼 수상 OR 학술상")[:5]:
                st.write(f"🥇 {e.clean_title}")
                st.link_button("기사 보기", e.link)

    with col_right:
        st.subheader("🌐 Global Journals (English Only)")
        foreign = fetch_refined_data("Pathology OR Clinical Diagnostic", lang='en')
        for fp in foreign[:12]:
            if not re.search('[가-힣]', fp.clean_title):
                st.markdown(f"📄 {bold_keywords(fp.clean_title)}")
                st.caption(f"Source: {fp.media_name}")
                st.link_button("Read Paper", fp.link)
                st.markdown("<hr>", unsafe_allow_html=True)

# [탭 3] 일정 및 링크
with tab_cal:
    st.success("🎯 제54회 임상병리사 국가고시 D-Day: 2026-12-13 (일)")
    st.divider()
    l_cols = st.columns(len(ASSOC_LINKS))
    for i, (name, info) in enumerate(ASSOC_LINKS.items()):
        l_cols[i].link_button(f"{info['icon']} {name}", info['url'], use_container_width=True)
