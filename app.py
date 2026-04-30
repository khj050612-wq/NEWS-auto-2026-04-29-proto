import streamlit as st
import feedparser
import pandas as pd
from urllib.parse import quote
from collections import defaultdict, Counter
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
    .news-badge { background-color: #D32F2F; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; margin-left: 8px; display: inline-block; vertical-align: middle; }
    .main-title { font-size: 0.95rem; font-weight: 600; margin-top: 10px; margin-bottom: 2px; }
    hr { margin: 8px 0px; border: 0; border-top: 1px solid #f0f0f0; }
    div.stButton > button { border-radius: 12px; font-size: 11px; height: 26px; }
    .part-label { background-color: #e3f2fd; color: #1565c0; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: bold; margin-right: 5px; }
    .kw-card { text-align: center; border: 1px solid #e6e9ef; padding: 10px; border-radius: 10px; background: linear-gradient(145deg, #ffffff, #f5f7fa); }
    </style>
    """, unsafe_allow_html=True)

# 3. [로직] 데이터 수집 및 분석 함수
@st.cache_data(ttl=600)
def fetch_refined_data(query_text, filter_type="news", lang='ko'):
    base_filter = "-양체험 -원장 -의사 -수의사 -공무원 -모집 -구병원 -에스포항병원"
    if filter_type == "major":
        base_filter += " -획득 -인증 -수상 -보유 -기념"
    
    final_query = f"{query_text} {base_filter}"
    url = f"https://news.google.com/rss/search?q={quote(final_query)}&hl={lang}&gl=KR&ceid=KR:{lang}"
    feed = feedparser.parse(url)
    
    grouped = defaultdict(list)
    titles_for_analysis = []
    for entry in feed.entries:
        clean_t = re.sub(r" - .*$", "", entry.title).strip()
        titles_for_analysis.append(clean_t)
        unique_key = clean_t.replace(" ", "")[:12]
        grouped[unique_key].append(entry)
        
    final = []
    for key, items in grouped.items():
        items.sort(key=lambda x: x.published_parsed, reverse=True)
        rep = items[0]
        rep.count = len(items); rep.dt = datetime.datetime(*rep.published_parsed[:6])
        title_match = re.search(r" - (.*)$", rep.title)
        rep.media_name = title_match.group(1) if title_match else "뉴스"
        rep.clean_title = rep.title.replace(f" - {rep.media_name}", "").strip() if title_match else rep.title
        final.append(rep)
    return sorted(final, key=lambda x: x.dt, reverse=True), titles_for_analysis

# [핵심] 분석 리포트 생성 로직 복구
def generate_smart_report(title):
    # 따옴표나 핵심 명사 추출
    subject_match = re.search(r"['‘\"“](.*?)['’\"”]", title)
    subject = subject_match.group(1) if subject_match else "보건의료 현안"
    
    return {
        "topic": f"🔥 {subject} 중심의 의료 환경 변화",
        "gov_rule": "의료법 및 임상병리사 직무 표준 지침",
        "tip": f"자소서 작성 시 **'{subject}'** 기술 도입에 따른 환자 안전과 검사 정확도 향상을 본인의 **'데이터 관리 능력'**과 연결해 보세요."
    }

def get_top_keywords(titles):
    words = []
    for t in titles:
        t = re.sub(r'[^\w\s]', '', t) 
        extracted = re.findall(r'[가-힣A-Z]{2,}', t)
        words.extend(extracted)
    stop_words = ["뉴스", "추진", "강화", "이용", "시대", "지원", "확대", "개최", "참여", "진행", "올해", "출시", "서비스", "정부", "복지부", "보건", "의료", "대통령", "정책", "방안"]
    return Counter([w for w in words if w not in stop_words and len(w) > 1]).most_common(10)

# --- 4. 메인 화면 ---
st.title("🔬 2026 임상병리 커리어 전략 마스터")

tab_news, tab_paper, tab_archive, tab_cal = st.tabs(["🗞️ 의료 뉴스 분석", "🧪 전공 분과", "📓 경험 아카이브", "📅 일정/링크"])

# [탭 1] 의료 뉴스 분석 (리포트 기능 복구!)
with tab_news:
    news_data, all_titles = fetch_refined_data("임상병리사 OR 디지털 헬스케어 OR 의료 AI", filter_type="news")
    
    st.subheader("📊 지금 화제인 전공 키워드 TOP 10")
    top_kws = get_top_keywords(all_titles)
    kw_cols = st.columns(5)
    for i, (word, count) in enumerate(top_kws):
        with kw_cols[i % 5]:
            st.markdown(f'<div class="kw-card"><small>RANK {i+1}</small><br><b>{word}</b></div>', unsafe_allow_html=True)
    st.divider()
    
    for e in news_data[:12]:
        badge = f'<span class="news-badge">{e.count}건</span>' if e.count > 1 else ""
        st.markdown(f'<div class="main-title">📍 {e.clean_title} {badge}</div>', unsafe_allow_html=True)
        
        # [수정] 분석 리포트 내용 상세화
        with st.expander("🔎 분석 리포트 & 자소서 팁 확인"):
            report = generate_smart_report(e.clean_title)
            st.success(f"**📌 핵심 주제**: {report['topic']}")
            st.info(f"**📜 관련 근거**: {report['gov_rule']}")
            st.warning(f"**🎯 자소서/면접 공략**\n\n{report['tip']}")
            st.divider()
            st.caption(f"출처: {e.media_name} | 발행일: {e.dt.strftime('%Y-%m-%d')}")
            st.link_button("뉴스 원문 보기", e.link, use_container_width=True)

# [탭 2] 전공 분과 (진검/생리/병리 전문 필터링)
with tab_paper:
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("🧬 분과별 실무 기술 현안")
        with st.expander("🧪 진단검사 (분자유전/NGS/특수혈액)", expanded=True):
            data, _ = fetch_refined_data("(진단검사의학과 NGS) OR (분자유전 검사 기술)", filter_type="major")
            for e in data[:5]:
                st.markdown(f'<span class="part-label">진검</span> **{e.clean_title}**', unsafe_allow_html=True)
                st.link_button("기술 확인", e.link); st.markdown("<hr>", unsafe_allow_html=True)
        
        with st.expander("🧠 생리 기능 (심초음파/EEG/TCD/NCS)"):
            data, _ = fetch_refined_data("(심초음파 기술) OR (EEG 검사 지침) OR (TCD NCS)", filter_type="major")
            for e in data[:5]:
                st.markdown(f'<span class="part-label">생리</span> **{e.clean_title}**', unsafe_allow_html=True)
                st.link_button("검사법 확인", e.link); st.markdown("<hr>", unsafe_allow_html=True)

        with st.expander("🔬 병리 파트 (조직/세포/면역/디지털병리)"):
            data, _ = fetch_refined_data("(디지털병리 AI) OR (면역조직화학) OR (동결절편)", filter_type="major")
            for e in data[:5]:
                st.markdown(f'<span class="part-label">병리</span> **{e.clean_title}**', unsafe_allow_html=True)
                st.link_button("기술 확인", e.link); st.markdown("<hr>", unsafe_allow_html=True)
    with col_r:
        st.subheader("🌐 Global Technical Journals")
        data, _ = fetch_refined_data("Clinical Pathology OR Molecular Diagnostic", lang='en')
        for fp in data[:10]:
            if not re.search('[가-힣]', fp.clean_title):
                st.markdown(f"📄 **{fp.clean_title}**"); st.link_button("Read Paper", fp.link); st.markdown("<hr>", unsafe_allow_html=True)

# [탭 3] 경험 아카이브 (세션 유지 메모장)
with tab_archive:
    st.subheader("📓 희진님의 실무 경험 기록")
    if 'my_notes' not in st.session_state: st.session_state.my_notes = []
    with st.form("archive_form", clear_on_submit=True):
        cat = st.selectbox("구분", ["🩸 실습", "📜 자소서", "💬 면접", "🔬 공부"])
        txt = st.text_area("메모를 남겨주세요.")
        if st.form_submit_button("기록 저장") and txt:
            st.session_state.my_notes.insert(0, {"date": datetime.datetime.now().strftime("%Y-%m-%d"), "type": cat, "content": txt})
    for n in st.session_state.my_notes:
        st.info(f"{n['date']} [{n['type']}] {n['content']}")

# [탭 4] 일정 및 링크
with tab_cal:
    st.success("🎯 제54회 임상병리사 국가고시: 2026-12-13")
    l_cols = st.columns(len(ASSOC_LINKS))
    for i, (name, info) in enumerate(ASSOC_LINKS.items()):
        l_cols[i].link_button(f"{info['icon']} {name}", info['url'], use_container_width=True)
