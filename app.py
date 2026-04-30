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
    .news-badge {
        background-color: #D32F2F; color: white; padding: 2px 8px; border-radius: 4px;
        font-size: 0.75rem; font-weight: bold; margin-left: 8px; display: inline-block; vertical-align: middle;
    }
    .main-title { font-size: 0.95rem; font-weight: 600; margin-top: 10px; margin-bottom: 2px; }
    hr { margin: 8px 0px; border: 0; border-top: 1px solid #f0f0f0; }
    div.stButton > button { border-radius: 12px; font-size: 11px; height: 26px; }
    </style>
    """, unsafe_allow_html=True)

# 3. [로직] 데이터 수집 및 분석 함수
@st.cache_data(ttl=600)
def fetch_refined_data(query_text, lang='ko'):
    final_query = f"{query_text} -양체험 -원장 -의사 -공무원 -모집"
    url = f"https://news.google.com/rss/search?q={quote(final_query)}&hl={lang}&gl=KR&ceid=KR:{lang}"
    feed = feedparser.parse(url)
    
    grouped = defaultdict(list)
    for entry in feed.entries:
        clean_t = re.sub(r" - .*$", "", entry.title).strip()
        unique_key = clean_t.replace(" ", "")[:12] # 기관/기관장 중복 방지
        grouped[unique_key].append(entry)
        
    final = []
    for key, items in grouped.items():
        items.sort(key=lambda x: x.published_parsed, reverse=True)
        rep = items[0]
        rep.count = len(items)
        rep.dt = datetime.datetime(*rep.published_parsed[:6])
        title_match = re.search(r" - (.*)$", rep.title)
        rep.media_name = title_match.group(1) if title_match else "뉴스"
        rep.clean_title = rep.title.replace(f" - {rep.media_name}", "").strip() if title_match else rep.title
        final.append(rep)
    return sorted(final, key=lambda x: x.dt, reverse=True)

def analyze_smart_report(title):
    # 따옴표 주제어 정밀 추출
    subject_match = re.search(r"['‘\"“](.*?)['’\"”]", title)
    extracted = subject_match.group(1) if subject_match else "보건의료 이슈"
    
    return {
        "topic": f"[{extracted}] 관련 보건/사회적 동향",
        "gov_rule": "의료기사법 및 보건의료 정책 가이드라인",
        "tip": f"**'{extracted}'**에 대한 배경을 분석하여, 변화하는 의료 환경에 능동적으로 대비하는 태도를 강조하세요."
    }

def bold_keywords(title):
    kws = ["Pathology", "Clinical", "Diagnostic", "Molecular", "Hematology", "EEG", "AI"]
    for kw in kws:
        title = re.sub(f"({kw})", r"**\1**", title, flags=re.IGNORECASE)
    return title

# --- 4. 메인 화면 ---
st.title("🔬 2026 임상병리 커리어 전략 마스터")

tab_news, tab_paper, tab_cal = st.tabs(["🗞️ 의료 뉴스 분석", "🧬 전공 분과 학술 자료", "📅 일정/링크"])

# [탭 1] 의료 뉴스 분석 (희진님이 요청한 그 기능!)
with tab_news:
    st.subheader("📰 보건의료 사회 이슈 및 정책 분석")
    news_data = fetch_refined_data("보건복지부 의료 정책 OR 임상병리 디지털 AI OR 의료계 사회 이슈")
    for e in news_data[:15]:
        strat = analyze_smart_report(e.clean_title)
        badge = f'<span class="news-badge">{e.count}건</span>' if e.count > 1 else ""
        st.markdown(f'<div class="main-title">📍 {e.clean_title} {badge}</div>', unsafe_allow_html=True)
        
        with st.expander("🔎 분석 리포트 확인"):
            st.success(f"**현안 주제**: {strat['topic']}")
            st.info(f"**📜 관련 지침/법령**: {strat['gov_rule']}")
            st.warning(f"**🎯 자소서 활용 팁**\n\n{strat['tip']}")
            st.divider()
            st.markdown(f"**출처**: [{e.media_name}]({e.link}) | **일자**: {e.dt.strftime('%Y-%m-%d')}")

# [탭 2] 전공 분과 학술 자료 (분과별 세분화)
with tab_paper:
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("🇰🇷 국내 분과별 동향")
        # 1. 진검
        with st.expander("🧪 진단검사 (혈액, 미생물, 분자유전 등)"):
            for e in fetch_refined_data("진단검사의학과 (혈액응고 OR 미생물 OR 분자유전 OR 요경검)")[:5]:
                st.write(f"🔹 {e.clean_title}")
                st.link_button(f"{e.media_name} 보기", e.link)
        # 2. 생리
        with st.expander("🧠 생리 기능 (EEG, 심초음파, NCS 등)"):
            for e in fetch_refined_data("임상병리사 (EEG OR NCS OR 심초음파 OR 순환기과)")[:5]:
                st.write(f"🔹 {e.clean_title}")
                st.link_button(f"{e.media_name} 보기", e.link)
        # 3. 병리/수상
        with st.expander("🔬 병리 및 학생 수상 실적"):
            for e in fetch_refined_data("병리과 (디지털병리 OR 면역병리) OR 임상병리학과 수상")[:5]:
                st.write(f"🏆 {e.clean_title}")
                st.link_button("상세 보기", e.link)

    with col_r:
        st.subheader("🌐 Global Journals (English)")
        foreign = fetch_refined_data("Pathology OR Clinical Diagnostic", lang='en')
        for fp in foreign[:12]:
            if not re.search('[가-힣]', fp.clean_title):
                st.markdown(f"📄 {bold_keywords(fp.clean_title)}")
                st.caption(f"Source: {fp.media_name}")
                st.link_button("Read Paper", fp.link)
                st.markdown("<hr>", unsafe_allow_html=True)

# [탭 3] 일정 및 링크
with tab_cal:
    st.success("🎯 제54회 임상병리사 국가고시: 2026-12-13 (일)")
    st.divider()
    l_cols = st.columns(len(ASSOC_LINKS))
    for i, (name, info) in enumerate(ASSOC_LINKS.items()):
        l_cols[i].link_button(f"{info['icon']} {name}", info['url'], use_container_width=True)
