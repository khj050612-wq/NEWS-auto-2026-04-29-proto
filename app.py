import streamlit as st
import feedparser
import pandas as pd
from urllib.parse import quote
from collections import defaultdict
import datetime
import re

# 1. 전역 변수 및 대학생용 교육 일정 데이터
MY_EXPERIENCE = "분자진단 실습 경험, 환자 중심의 정확한 검사 지향, 꼼꼼한 데이터 관리"

# [수정] 학회 링크 - 임티 교체 및 공식 명칭 정립
ASSOC_LINKS = {
    "대한임상병리사협회": {"url": "http://www.kamt.or.kr/", "icon": "🏠"}, 
    "임상검사정보학회": {"url": "http://www.ksclis.or.kr/", "icon": "💻"}, 
    "대한임상미생물검사학회": {"url": "http://www.kscm.or.kr/", "icon": "🧫"}, 
    "대한임상혈액검사학회": {"url": "http://www.ksch.or.kr/", "icon": "🩸"}, 
    "대한진단검사의학회": {"url": "https://www.kslm.org/", "icon": "🔬"}
}

# [신규] 대학생 맞춤형 주요 일정 (수료증, 교육, 시험 등)
CALENDAR_EVENTS = [
    {"날짜": "2026-05-15", "항목": "📌 경기도임상병리사회 학생포럼 (두원공대 등)"},
    {"날짜": "2026-06-20", "항목": "📜 분자진단 전문가 교육 수료 (대학생 가능)"},
    {"날짜": "2026-09-10", "항목": "📝 임상병리사 국가고시 원서 접수 시작"},
    {"날짜": "2026-10-15", "항목": "🔬 추계 종합학술대회 (학생 세션 참여)"},
    {"날짜": "2026-12-13", "항목": "🔥 제54회 임상병리사 국가고시 필기/실기"}
]

# 2. 페이지 설정 및 CSS
st.set_page_config(page_title="2026 임상병리 전략 마스터", layout="wide")
st.markdown("""
    <style>
    .news-badge { background-color: #D32F2F; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; margin-left: 8px; display: inline-block; }
    .month-header { background-color: #f1f3f6; padding: 8px 15px; border-radius: 6px; color: #2c3e50; font-weight: bold; margin-top: 25px; border-left: 6px solid #D32F2F; }
    .cal-card { background-color: #ffffff; padding: 10px; border-radius: 8px; border: 1px solid #e0e0e0; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 3. 데이터 처리 함수 (이전과 동일)
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
        rep.dt = datetime.datetime(*rep.published_parsed[:6])
        title_match = re.search(r" - (.*)$", rep.title)
        rep.media_name = title_match.group(1) if title_match else "뉴스 매체"
        rep.clean_title = rep.title.replace(f" - {rep.media_name}", "").strip() if title_match else rep.title
        final.append(rep)
    return sorted(final, key=lambda x: x.dt, reverse=True)

# --- UI 화면 구성 ---
st.title("🔬 2026 임상병리 커리어 전략 마스터")
st.divider()

# 탭 구성
t1, t2, t3 = st.tabs(["🗞️ 의료 뉴스 분석", "🔬 전공 학술 자료", "📅 학사/교육 일정"])

# [탭 1] 뉴스 분석
with t1:
    news_data = fetch_refined_data(["임상병리 디지털 AI", "임상병리 분자진단"])
    for entry in news_data:
        st.markdown(f'**📍 {entry.clean_title}**')
        with st.expander("🔎 분석 리포트 확인"):
            st.info(f"**출처: [{entry.media_name}]({entry.link})**")

# [탭 2] 전공 학술 자료 (월별 정렬)
with t2:
    cl, cr = st.columns(2)
    with cl:
        st.subheader("🇰🇷 국내 학술 동향")
        academic = fetch_refined_data(["임상병리학회 학술대회", "임상병리 학생포럼"])
        curr_month = ""
        for p in academic:
            month_str = p.dt.strftime('%B %Y')
            if month_str != curr_month:
                st.markdown(f'<div class="month-header">{month_str}</div>', unsafe_allow_html=True)
                curr_month = month_str
            st.write(f"📌 [{p.clean_title}]({p.link})")
    with cr:
        st.subheader("🌐 Global Journals")
        foreign = fetch_refined_data(["site:nature.com pathology"], lang='en')
        for fp in foreign[:8]:
            if not re.search('[가-힣]', fp.clean_title):
                st.write(f"📄 [{fp.clean_title}]({fp.link})")

# [탭 3] 대학생 전용 일정 및 퀵 링크 (요청사항 집중 반영)
with t3:
    st.subheader("📅 임상병리학과 대학생 필수 일정")
    cal_df = pd.DataFrame(CALENDAR_EVENTS)
    
    # 달력 형태로 시각화 (데이터프레임 활용)
    st.dataframe(cal_df, use_container_width=True, hide_index=True)
    
    st.info("💡 위 일정은 대학생이 수료 가능한 교육 및 국가고시 일정 위주로 업데이트됩니다.")
    
    st.divider()
    
    # [수정] 퀵 링크 - 화살표 제거, 이름 정교화, 임티 추가
    st.subheader("🔗 공식 사이트 퀵 링크")
    link_cols = st.columns(len(ASSOC_LINKS))
    for i, (name, info) in enumerate(ASSOC_LINKS.items()):
        with link_cols[i]:
            st.link_button(f"{info['icon']} {name}", info['url'], use_container_width=True)
