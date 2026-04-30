import streamlit as st
import feedparser
import pandas as pd
from urllib.parse import quote
from collections import defaultdict

# 1. 페이지 설정
st.set_page_config(page_title="2026 임상병리 전략 마스터", layout="wide")

# 2. 고정 데이터 설정
MY_EXPERIENCE = "분자진단 실습 경험, 환자 중심의 정확한 검사 지향, 꼼꼼한 데이터 관리"
MAJOR_PRESS = ["연합뉴스", "의학신문", "보건신문", "청년의사", "데일리메디", "메디게이트", "약업신문", "메디파나"]
ASSOC_LINKS = {
    "중앙회": "http://www.kamt.or.kr/",
    "정보학회": "http://www.ksclis.or.kr/",
    "미생물": "http://www.kscm.or.kr/",
    "혈액": "http://www.ksch.or.kr/",
    "진단검사": "https://www.kslm.org/"
}

# 3. 데이터 분석 로직 (구체적 지침 근거 반영)
def analyze_full_strategy(title):
    res = {
        "topic": "보건의료 정책 동향",
        "gov_rule": "의료기사법 및 보건의료 데이터 지침",
        "evidence": "최신 학술 발표 및 정책 가이드라인 기반",
        "tags": "#보건의료_트렌드"
    }
    if "디지털" in title or "AI" in title:
        res.update({
            "topic": "디지털 병리 및 스마트 진단",
            "gov_rule": "대한병리학회 [디지털 병리 가이드라인 1.0]",
            "evidence": "상급종합병원 인프라 도입 및 LIS 데이터 표준화 동향",
            "tags": "#디지털_병리 #무결성_보호"
        })
    elif any(kw in title for kw in ["액체생검", "AACR", "NGS", "분자"]):
        res.update({
            "topic": "정밀의료 및 분자진단 고도화",
            "gov_rule": "심평원 [NGS 기반 유전자 패널검사 실시기관 승인]",
            "evidence": "2026 AACR 국내 진단기업 일치율 데이터 보도 기반",
            "tags": "#NGS_패널검사 #액체생검"
        })
    return res

# 4. 데이터 수집 함수 (캐싱 적용)
@st.cache_data(ttl=600)
def fetch_refined_data(keywords):
    all_entries = []
    for kw in keywords:
        query = f"{kw} -공무원 -모집"
        url = f"https://news.google.com/rss/search?q={quote(query)}&hl=ko&gl=KR&ceid=KR:ko"
        feed = feedparser.parse(url)
        all_entries.extend(feed.entries)
    
    grouped = defaultdict(list)
    for entry in all_entries:
        key = entry.title[:15]
        grouped[key].append(entry)
        
    final = []
    for key, items in grouped.items():
        items.sort(key=lambda x: (any(p in x.get('source', {}).get('text', '') for p in MAJOR_PRESS), x.published_parsed), reverse=True)
        rep = items[0]
        rep.count = len(items)
        final.append(rep)
    return sorted(final, key=lambda x: x.published_parsed, reverse=True)

# --- 메인 화면 UI 시작 ---
st.title("🔬 2026 임상병리사 커리어 전략 플랫폼")
st.caption("2026년 4월 30일 실시간 트렌드 및 학술/채용 데이터 반영")

# 📊 상단 전략 대시보드
st.markdown("### 📊 최근 1개월 전략 키워드 & 실증 근거")
t1, t2 = st.columns(2)
with t1:
    st.info("**#디지털_병리_품질관리**\n\n📜 대한병리학회 가이드라인 1.0 이미지 표준화 지침 기반")
with t2:
    st.info("**#NGS_액체생검_급여화**\n\n🔬 심평원 유전자 패널검사 승인 지침 기반")

st.divider()

# 탭 시스템 구성
tab_news, tab_paper, tab_jobs, tab_assoc = st.tabs([
    "🗞️ 의료 뉴스 분석", "🔬 전공 학술 자료", "💼 타겟 채용 정보", "🔔 협회 링크 & 이슈"
])

# [탭 1] 의료 뉴스 분석 (카운트 표시 + 클릭형 분석박스)
with tab_news:
    with st.spinner("최신 이슈를 분석 중입니다..."):
        news_data = fetch_refined_data(["임상병리 디지털", "분자진단 기술", "액체생검 AACR"])
        st.markdown(f"### 📋 오늘 분석된 핵심 뉴스: 총 **{len(news_data)}**건")
        
        for i, entry in enumerate(news_data):
            strat = analyze_full_strategy(entry.title)
            press = entry.get('source', {}).get('text', '전문 매체')
            is_major = any(p in press for p in MAJOR_PRESS)
            display_title = f"{'⭐ [메이저]' if is_major else '📍'} {entry.title}"
            if entry.count > 1: display_title += f" (+{entry.count-1})"

            with st.expander(display_title):
                st.caption(f"출처: {press} | 발행일: {entry.published} | [기사원문]({entry.link})")
                st.divider()
                c1, c2 = st.columns(2)
                with c1:
                    st.success(f"**현안 주제:** {strat['topic']}")
                    st.info(f"**📜 관련 지침/법령:** {strat['gov_rule']}")
                with c2:
                    st.warning(f"**🔑 키워드:** `{strat['tags']}`")
                    st.markdown(f"**🎯 자소서 활용:** {MY_EXPERIENCE.split(',')[0]} 역량과 연결")

# [탭 2] 전공 학술 자료 (2단 레이아웃: 국내외 동향 vs 해외 NSC/PubMed 원문)
with tab_paper:
    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("🇰🇷/🌐 최신 학술 동향 분석")
        academic = fetch_refined_data(["임상병리학회 학술대회", "Diagnostic Laboratory Trends 2026"])
        for p in academic[:10]:
            with st.expander(f"📌 {p.title}"):
                st.write(f"[자료 확인]({p.link})")
    
    with col_right:
        st.subheader("🔬 Global Top Journals (English Original)")
        c1, c2, c3, c4 = st.columns(4)
        c1.link_button("Nature", "https://www.nature.com/")
        c2.link_button("Science", "https://www.science.org/")
        c3.link_button("Cell", "https://www.cell.com/")
        c4.link_button("PubMed", "https://pubmed.ncbi.nlm.nih.gov/")
        st.divider()
        foreign = fetch_refined_data(["site:nature.com clinical pathology", "site:science.org diagnostic", "site:cell.com pathology", "PubMed diagnostic"])
        for fp in foreign[:12]:
            st.markdown(f"📄 **{fp.title}**")
            st.caption(f"Source: {fp.get('source', {}).get('text', 'International Journal')} | [Read]({fp.link})")

# [탭 3] 타겟 채용 정보
with tab_jobs:
    st.subheader("💼 주요 기관 채용 공고")
    jobs = fetch_refined_data(["대학병원 임상병리사 채용", "씨젠 채용", "녹십자의료재단 채용"])
    for j in jobs:
        st.warning(f"💼 {j.title}")
        st.caption(f"[공고상세]({j.link})")

# [탭 4] 협회 링크 & 이슈 (허브 기능)
with tab_assoc:
    st.subheader("🔗 공식 사이트 퀵 링크 (로그인용)")
    l_cols = st.columns(len(ASSOC_LINKS))
    for i, (name, link) in enumerate(ASSOC_LINKS.items()):
        l_cols[i].link_button(f"{name} ↗️", link)
    st.markdown("#### 📰 뉴스 속 협회/학회 동향")
    a_news = fetch_refined_data(["대한임상병리사협회", "대한진단검사의학회"])
    for n in a_news:
        st.write(f"📍 {n.title} ([링크]({n.link}))")
