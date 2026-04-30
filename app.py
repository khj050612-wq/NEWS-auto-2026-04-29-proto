import streamlit as st
import feedparser
import pandas as pd
from urllib.parse import quote
from collections import defaultdict, Counter
import datetime
import re

# 1. [데이터] 전역 변수 및 퀵 링크
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
    .news-badge { background-color: #D32F2F; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; margin-left: 8px; display: inline-block; vertical-align: middle; }
    .main-title { font-size: 0.95rem; font-weight: 600; margin-top: 10px; margin-bottom: 2px; }
    hr { margin: 8px 0px; border: 0; border-top: 1px solid #f0f0f0; }
    .part-label { background-color: #e3f2fd; color: #1565c0; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: bold; margin-right: 5px; }
    .archive-box { background-color: #f9f9f9; padding: 15px; border-radius: 10px; border-left: 5px solid #D32F2F; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 3. [로직] 데이터 수집 함수
@st.cache_data(ttl=600)
def fetch_refined_data(query_text, filter_type="news", lang='ko'):
    base_filter = "-양체험 -원장 -의사 -수의사 -공무원 -모집 -구병원 -에스포항병원"
    if filter_type == "major":
        base_filter += " -획득 -인증 -수상(단순) -보유 -기념"
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
        rep = items[0]; rep.count = len(items); rep.dt = datetime.datetime(*rep.published_parsed[:6])
        title_match = re.search(r" - (.*)$", rep.title)
        rep.media_name = title_match.group(1) if title_match else "뉴스"
        rep.clean_title = rep.title.replace(f" - {rep.media_name}", "").strip() if title_match else rep.title
        final.append(rep)
    return sorted(final, key=lambda x: x.dt, reverse=True), titles_for_analysis

def get_top_keywords(titles):
    words = []
    for t in titles:
        extracted = re.findall(r'[가-힣A-Z]{2,}', t)
        words.extend(extracted)
    stop_words = ["뉴스", "개최", "발표", "참여", "진행", "올해", "출시", "지원", "확대"]
    return Counter([w for w in words if w not in stop_words]).most_common(10)

# --- 4. 메인 화면 ---
st.title("🔬 2026 임상병리 커리어 전략 마스터")

# [수정] 네 번째 탭 '경험 아카이브' 추가
tab_news, tab_paper, tab_archive, tab_cal = st.tabs(["🗞️ 의료 뉴스", "🧪 전공 분과", "📓 경험 아카이브", "📅 일정/링크"])

# [탭 1] 의료 뉴스 (거시적)
with tab_news:
    st.subheader("📊 의료계 실시간 화제 키워드")
    news_data, all_titles = fetch_refined_data("임상병리사 OR 보건복지부 정책 OR 의료 이슈", filter_type="news")
    top_kws = get_top_keywords(all_titles)
    kw_cols = st.columns(5)
    for i, (word, count) in enumerate(top_kws):
        with kw_cols[i % 5]:
            st.markdown(f'<div style="text-align: center; border: 1px solid #eee; padding: 5px; border-radius: 8px; background-color: #fbfbfb;"><span style="font-size: 0.8rem; font-weight: 600;">{word}</span></div>', unsafe_allow_html=True)
    st.divider()
    for e in news_data[:10]:
        badge = f'<span class="news-badge">{e.count}건</span>' if e.count > 1 else ""
        st.markdown(f'<div class="main-title">📍 {e.clean_title} {badge}</div>', unsafe_allow_html=True)
        with st.expander("🔎 분석 및 원문"):
            st.info(f"출처: {e.media_name} | {e.dt.strftime('%Y-%m-%d')}")
            st.link_button("원문 읽기", e.link)

# [탭 2] 전공 분과 (미시적 - 실무 역량 강화용)
with tab_paper:
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("🧬 전공 파트별 실무/기술 현안")
        
        # 1. 진단검사 (실무 기술 위주)
        with st.expander("🧪 진단검사 (분자유전/NGS/특수혈액)", expanded=True):
            jin_query = "(진단검사의학과 NGS) OR (분자유전 검사 기술) OR (혈액은행 지침)"
            data, _ = fetch_refined_data(jin_query, filter_type="major")
            for e in data[:5]:
                st.markdown(f'<span class="part-label">진검</span> **{e.clean_title}**', unsafe_allow_html=True)
                st.link_button("기술 확인", e.link)
                st.markdown("<hr>", unsafe_allow_html=True)

        # 2. 생리 기능 (검사법 위주)
        with st.expander("🧠 생리 기능 (심초음파/EEG/TCD/NCS)"):
            sang_query = "(심초음파 기술) OR (EEG 검사 지침) OR (NCS TCD 판독)"
            data, _ = fetch_refined_data(sang_query, filter_type="major")
            for e in data[:5]:
                st.markdown(f'<span class="part-label">생리</span> **{e.clean_title}**', unsafe_allow_html=True)
                st.link_button("검사법 확인", e.link)
                st.markdown("<hr>", unsafe_allow_html=True)

        # 3. 병리 파트 (완전 독립: 전문 기술 위주)
        with st.expander("🔬 병리 파트 (조직/세포/면역/디지털병리)"):
            # '수상', '포럼' 등을 제외하고 병리 기술 키워드만 집중
            byung_query = "(디지털병리 AI 분석) OR (면역조직화학염색 기술) OR (동결절편 검사) OR (세포병리 액상세포검사)"
            data, _ = fetch_refined_data(byung_query, filter_type="major")
            for e in data[:5]:
                st.markdown(f'<span class="part-label">병리</span> **{e.clean_title}**', unsafe_allow_html=True)
                st.link_button("전문 기술 확인", e.link)
                st.markdown("<hr>", unsafe_allow_html=True)
# [탭 3] 경험 아카이브 (희진님의 일기장/경험 정리함)
with tab_archive:
    st.subheader("📓 희진님의 실무 경험 & 인사이트 기록")
    
    # 세션 상태를 이용한 간단한 메모장 기능 (임시 저장용)
    if 'my_notes' not in st.session_state:
        st.session_state.my_notes = []

    with st.form("archive_form", clear_on_submit=True):
        note_type = st.selectbox("카테고리", ["🩸 실습 기록", "📜 자소서 소스", "💬 면접 대비", "🔬 공부 노트"])
        note_content = st.text_area("오늘의 전공 지식이나 경험을 한 줄로 요약해 보세요.", placeholder="예: 오늘 EEG 실습 때 전극 부착 부위(10-20 system) 재확인함. 자소서에 꼼꼼함 강조 포인트로 활용 예정.")
        submitted = st.form_submit_button("기록 저장하기")
        
        if submitted and note_content:
            st.session_state.my_notes.insert(0, {"date": datetime.datetime.now().strftime("%Y-%m-%d"), "type": note_type, "content": note_content})

    st.divider()
    
    # 저장된 기록 리스트 표시
    if st.session_state.my_notes:
        for n in st.session_state.my_notes:
            st.markdown(f"""
            <div class="archive-box">
                <small>{n['date']} | <b>{n['type']}</b></small><br>
                <div style="margin-top:5px;">{n['content']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("아직 기록된 내용이 없습니다. 오늘의 공부나 실습 내용을 아카이브 해보세요!")

# [탭 4] 일정 및 링크
with tab_cal:
    st.success("🎯 제54회 임상병리사 국가고시: 2026-12-13 (일)")
    l_cols = st.columns(len(ASSOC_LINKS))
    for i, (name, info) in enumerate(ASSOC_LINKS.items()):
        l_cols[i].link_button(f"{info['icon']} {name}", info['url'], use_container_width=True)
