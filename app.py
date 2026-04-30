import streamlit as st
import feedparser
import pandas as pd
from urllib.parse import quote

# 1. 페이지 설정
st.set_page_config(page_title="임상병리 2026 전략 플랫폼", layout="wide")

# 2. 고정 데이터: 각 분과별 공식 사이트 링크 (허브용)
ASSOC_LINKS = {
    "중앙회": "http://www.kamt.or.kr/", # 대한임상병리사협회
    "정보학회": "http://www.ksclis.or.kr/", # 대한임상검사정보학회
    "미생물": "http://www.kscm.or.kr/", # 대한임상미생물검사학회
    "혈액": "http://www.ksch.or.kr/", # 대한임상혈액검사학회
    "조직세포": "http://www.kscct.or.kr/", # 대한임상조직세포검사학회
    "진단검사": "https://www.kslm.org/" # 대한진단검사의학회
}

# 3. 데이터 수집 함수 (개별 로딩용)
@st.cache_data(ttl=600)
def fetch_news(keywords):
    all_entries = []
    for kw in keywords:
        query = f"{kw} -공무원 -모집"
        url = f"https://news.google.com/rss/search?q={quote(query)}&hl=ko&gl=KR&ceid=KR:ko"
        feed = feedparser.parse(url)
        all_entries.extend(feed.entries)
    return all_entries[:10]

# --- 화면 UI 시작 ---
st.title("🔬 2026 임상병리사 취업 전략 플랫폼")

# [상단 요약] 1개월 전략 키워드 & 구체적 근거
st.markdown("### 📊 최근 1개월 전략 키워드 & 실증 근거")
t_col1, t_col2 = st.columns(2)
with t_col1:
    st.info("**#디지털_병리_품질관리**")
    st.caption("📂 **실무 근거:** 주요 상급종합병원 LIS(실험실정보시스템) 연동 기사 누적")
    st.caption("⚖️ **지침:** 대한병리학회 [디지털 병리 가이드라인 1.0] 내 이미지 표준화 지침")
with t_col2:
    st.info("**#NGS_액체생검_급여화**")
    st.caption("🔬 **실무 근거:** 2026 AACR 국내 진단기업 일치율 데이터(80% 이상) 보도")
    st.caption("⚖️ **지침:** 심평원 [NGS 기반 유전자 패널검사 실시기관 승인] 지침")

st.divider()

# [모듈형 탭]
tab_news, tab_paper, tab_jobs, tab_assoc = st.tabs([
    "🗞️ 의료 뉴스 분석", "🔬 전공 학술 자료", "💼 타겟 채용 정보", "🔔 협회 링크 & 이슈"
])

# --- [탭 4] 협회 링크 & 이슈 정리 (희진님 요청사항 집중 반영) ---
with tab_assoc:
    st.subheader("🔔 협회별 공식 사이트 & 실시간 이슈 리포트")
    
    # 1. 분과별 퀵 링크 (로그인 편의성)
    st.markdown("#### 🔗 공식 사이트 퀵 링크 (로그인 필요)")
    link_cols = st.columns(len(ASSOC_LINKS))
    for i, (name, link) in enumerate(ASSOC_LINKS.items()):
        link_cols[i].link_button(f"{name} ↗️", link)
    
    st.write("")
    
    # 2. 뉴스 기반 협회 관련 이슈 정리
    st.markdown("#### 📰 뉴스에 언급된 협회/학회 관련 이슈")
    with st.spinner("협회 관련 최신 언급을 정리 중입니다..."):
        # 협회 명칭들로 뉴스 검색
        assoc_news = fetch_news(["대한임상병리사협회", "임상검사정보학회 이슈", "진단검사의학회 가이드라인"])
        
        if not assoc_news:
            st.write("최근 협회 관련 대외 뉴스가 없습니다.")
        else:
            for n in assoc_news:
                with st.expander(f"📍 {n.title}"):
                    st.caption(f"출처: {n.get('source', {}).get('text', '전문매체')} | {n.published}")
                    st.write(f"🔗 [이슈 자세히 보기]({n.link})")
                    # 협회 관련성 요약
                    if "학술" in n.title or "대회" in n.title:
                        st.success("💡 **분석:** 협회 차원의 대규모 학술 행사가 예정되어 있습니다. 주요 세션을 확인하세요.")
                    elif "가이드라인" in n.title or "권고" in n.title:
                        st.warning("💡 **분석:** 실무 지침이 업데이트되었습니다. 면접 전 핵심 내용을 반드시 숙지하세요.")

# --- 나머지 탭은 기능 유지 ---
with tab_news:
    with st.spinner("트렌드 분석 중..."):
        news = fetch_news(["임상병리 디지털", "액체생검 기술"])
        for n in news:
            st.markdown(f"**{n.title}**")
            st.caption(f"[원문보기]({n.link})")
            st.write("---")

with tab_paper:
    st.subheader("🔬 최신 학술 동향")
    papers = fetch_news(["진단검사의학 학술논문", "임상병리 신기술"])
    for p in papers:
        st.write(f"📄 {p.title} ([링크]({p.link}))")

with tab_jobs:
    st.subheader("💼 타겟 병원/기관 공고")
    jobs = fetch_news(["대학병원 임상병리사 채용", "씨젠 채용", "녹십자 의료재단"])
    for j in jobs:
        st.warning(f"💼 {j.title}")
        st.caption(f"[공고확인]({j.link})")
