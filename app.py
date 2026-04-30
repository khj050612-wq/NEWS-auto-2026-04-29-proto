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

# 2. [UI] 페이지 설정
st.set_page_config(page_title="2026 임상병리 전략 마스터", layout="wide")
st.markdown("""
    <style>
    .main-title { font-size: 0.95rem; font-weight: 600; margin-top: 10px; margin-bottom: 2px; line-height: 1.4; }
    div.stButton > button { border-radius: 12px; font-size: 11px; height: 24px; padding: 0px 8px; }
    hr { margin: 8px 0px; border: 0; border-top: 1px solid #f0f0f0; }
    .caption-style { font-size: 0.8rem; color: #777; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 3. [로직] 데이터 수집 (희진님 맞춤 파트 키워드 적용)
@st.cache_data(ttl=600)
def fetch_refined_data(part_type):
    # 희진님이 정해주신 파트별 키워드 셋
    keywords_map = {
        "진검": "진단검사의학과 (세포유전 OR 특수혈액 OR 혈액응고 OR 일반혈액 OR 요경검 OR 특수화학 OR 진단면역 OR 미생물 OR 분자유전 OR 혈액은행)",
        "생리": "신경과 순환기과 호흡기과 (EP OR NCS OR TCD OR VOG OR EEG OR ANS OR 심전도 OR 심초음파 OR 홀터)",
        "병리": "조직병리 세포병리 분자병리 면역병리 디지털병리",
        "수상": "임상병리학회 학생포럼 학술상 수상"
    }
    
    query = f"{keywords_map[part_type]} -양체험 -원장 -의사 -수의사"
    url = f"https://news.google.com/rss/search?q={quote(query)}&hl=ko&gl=KR&ceid=KR:ko"
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

# 글로벌 저널 키워드 강조 (병리/생리 파트 추가)
def bold_keywords(title):
    kws = ["Pathology", "Clinical", "Diagnostic", "EEG", "ECG", "Echo", "Molecular", "Hematology", "AI"]
    for kw in kws:
        title = re.sub(f"({kw})", r"**\1**", title, flags=re.IGNORECASE)
    return title

# --- 4. 메인 화면 ---
st.title("🔬 2026 임상병리 파트별 전문 모니터링")

t_news, t_paper, t_cal = st.tabs(["🗞️ 파트별 핵심 뉴스", "🏆 학술/수상 동향", "📅 일정/링크"])

# [탭 1] 파트별 뉴스 (진검, 생리, 병리 통합)
with t_news:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader("🧪 진단검사 파트")
        for e in fetch_refined_data("진검")[:8]:
            st.markdown(f'<div class="main-title">{e.clean_title}</div>', unsafe_allow_html=True)
            col_a, col_b = st.columns([0.7, 0.3])
            col_a.markdown(f'<div class="caption-style">{e.media_name} | {e.dt.strftime("%m-%d")}</div>', unsafe_allow_html=True)
            col_b.link_button("원문", e.link, use_container_width=True)
            st.markdown("<hr>", unsafe_allow_html=True)
    with c2:
        st.subheader("🧠 생능 파트")
        for e in fetch_refined_data("생리")[:8]:
            st.markdown(f'<div class="main-title">{e.clean_title}</div>', unsafe_allow_html=True)
            col_a, col_b = st.columns([0.7, 0.3])
            col_a.markdown(f'<div class="caption-style">{e.media_name} | {e.dt.strftime("%m-%d")}</div>', unsafe_allow_html=True)
            col_b.link_button("원문", e.link, use_container_width=True)
            st.markdown("<hr>", unsafe_allow_html=True)
    with c3:
        st.subheader("🔬 병리 파트")
        for e in fetch_refined_data("병리")[:8]:
            st.markdown(f'<div class="main-title">{e.clean_title}</div>', unsafe_allow_html=True)
            col_a, col_b = st.columns([0.7, 0.3])
            col_a.markdown(f'<div class="caption-style">{e.media_name} | {e.dt.strftime("%m-%d")}</div>', unsafe_allow_html=True)
            col_b.link_button("원문", e.link, use_container_width=True)
            st.markdown("<hr>", unsafe_allow_html=True)

# [탭 2] 학술/수상 및 글로벌 저널
with t_paper:
    cl, cr = st.columns(2)
    with cl:
        st.subheader("🏆 국내 학생 수상 및 학술")
        academic = fetch_refined_data("수상")
        for p in academic[:12]:
            st.markdown(f"**{p.clean_title}**")
            st.caption(f"{p.dt.strftime('%Y.%m')} | {p.media_name}")
            st.link_button("내용 보기", p.link)
            st.markdown("<hr>", unsafe_allow_html=True)
    with cr:
        st.subheader("🌐 Global Journals")
        foreign = fetch_refined_data("병리", lang='en') # 병리/진단 키워드로 영어 검색
        for fp in foreign[:12]:
            if not re.search('[가-힣]', fp.clean_title):
                st.markdown(f"📄 {bold_keywords(fp.clean_title)}")
                st.caption(f"Source: {fp.media_name}")
                st.link_button("Read", fp.link)
                st.markdown("<hr>", unsafe_allow_html=True)

# [탭 3] 일정 및 링크
with t_cal:
    st.info("📅 제54회 임상병리사 국가고시: 2026-12-13 (일)")
    l_cols = st.columns(len(ASSOC_LINKS))
    for i, (name, info) in enumerate(ASSOC_LINKS.items()):
        l_cols[i].link_button(f"{info['icon']} {name}", info['url'], use_container_width=True)
