import streamlit as st
import feedparser
import pandas as pd
from urllib.parse import quote
from collections import defaultdict
import datetime
import re

# 1. 전역 변수 설정
MY_EXPERIENCE = "분자진단 실습 경험, 환자 중심의 정확한 검사 지향, 꼼꼼한 데이터 관리"
MAJOR_PRESS = ["연합뉴스", "의학신문", "보건신문", "청년의사", "데일리메디", "메디게이트", "약업신문", "메디파나"]

# 2. 페이지 설정 및 CSS
st.set_page_config(page_title="2026 임상병리 전략 마스터", layout="wide")
st.markdown("""
    <style>
    .news-badge {
        background-color: #D32F2F; color: white; padding: 2px 8px; border-radius: 4px;
        font-size: 0.75rem; font-weight: bold; margin-left: 8px; display: inline-block; vertical-align: middle;
    }
    .main-title { font-size: 1.1rem; font-weight: 600; margin-top: 10px; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 3. [핵심 수정] 기사 제목 맞춤형 정밀 분석 함수
def analyze_smart_report(title):
    # 기본값
    res = {
        "topic": "보건의료 정책 동향",
        "gov_rule": "의료기사법 및 보건의료 데이터 지침",
        "tags": "#보건의료_트렌드",
        "tip": "본 이슈를 실무 역량과 연결하여 전문성을 어필하세요."
    }

    # 1. 학술대회/학술상 관련 분석 (희진님 요청사항)
    if any(kw in title for kw in ["학술상", "수상", "포럼", "학술대회"]):
        # 제목에서 학술대회 명칭 추출 시도
        event_match = re.search(r"([가-힣]+학회|[가-힣]+사회|[가-힣]+포럼)", title)
        event_name = event_match.group(1) if event_match else "관련 학술 행사"
        res.update({
            "topic": f"학술 역량 강화 및 {event_name} 최신 연구",
            "gov_rule": "대한임상병리사협회 보수교육 및 학술활동 지침",
            "tags": "#학술상 #연구역량 #임상연구",
            "tip": f"해당 학술대회의 주요 주제를 파악하여, 최신 연구에 대한 본인의 관심도와 탐구 정신을 강조하세요."
        })

    # 2. 디지털 병리 관련
    elif "디지털" in title or "AI" in title:
        res.update({
            "topic": "디지털 병리 및 스마트 진단 인프라",
            "gov_rule": "대한병리학회 [디지털 병리 가이드라인 1.0]",
            "tags": "#디지털_병리 #LIS_연동",
            "tip": "장비 디지털화에 따른 데이터 무결성 관리 능력을 강조하세요."
        })

    # 3. NGS/분자진단 관련
    elif any(kw in title for kw in ["액체생검", "AACR", "NGS", "분자", "검사"]):
        res.update({
            "topic": "정밀의료 및 분자진단 기술 고도화",
            "gov_rule": "심평원 [NGS 기반 유전자 패널검사 실시기관 승인]",
            "tags": "#분자진단 #정밀의학",
            "tip": "분자진단 실습 경험을 바탕으로 정밀 검사 역량을 어필하세요."
        })
        
    return res

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
        items.sort(key=lambda x: x.published_parsed, reverse=True)
        rep = items[0]
        rep.count = len(items)
        
        # 제목에서 매체명 정밀 분리
        title_match = re.search(r" - (.*)$", rep.title)
        if title_match:
            rep.media_name = title_match.group(1)
            rep.clean_title = rep.title.replace(f" - {rep.media_name}", "").strip()
        else:
            rep.media_name = rep.get('source', {}).get('text', '뉴스 매체')
            rep.clean_title = rep.title
        final.append(rep)
    return sorted(final, key=lambda x: x.published_parsed, reverse=True)

# --- 메인 화면 ---
st.title("🔬 2026 임상병리사 커리어 전략 플랫폼")
st.divider()

tab_news, tab_paper, tab_jobs, tab_assoc = st.tabs(["🗞️ 의료 뉴스 분석", "🔬 전공 학술 자료", "💼 타겟 채용 정보", "🔔 협회 링크 & 이슈"])

# [탭 1] 의료 뉴스 분석
with tab_news:
    news_data = fetch_refined_data(["임상병리 디지털", "분자진단 기술", "액체생검 AACR", "임상병리학과 학술상"])
    st.markdown(f"### 📋 오늘 분석된 핵심 뉴스: 총 **{len(news_data)}**건")
    
    for i, entry in enumerate(news_data):
        # [수정] 똑똑해진 분석 함수 호출
        strat = analyze_smart_report(entry.clean_title)
        f_date = datetime.datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %Z').strftime('%d %b. %Y')
        badge = f'<span class="news-badge">{entry.count}건</span>' if entry.count > 1 else ""
        
        st.markdown(f'<div class="main-title">📍 {entry.clean_title} <small>[{f_date}]</small> {badge}</div>', unsafe_allow_html=True)
        
        with st.expander("🔎 분석 리포트 확인"):
            c1, c2 = st.columns(2)
            with c1:
                st.success(f"**현안 주제**\n{strat['topic']}")
            with c2:
                st.info(f"**📜 관련 지침/법령**\n{strat['gov_rule']}")
            
            # 주황색 자소서 팁도 기사 내용에 따라 가변적으로 변경
            st.warning(f"**🎯 자소서 활용 팁**\n\n{strat['tip']}")
            
            st.divider()
            # 매체명 정확히 출력
            st.caption(f"**출처: {entry.media_name}** | 원문 날짜: {entry.published}")
            st.markdown(f"🔗 [기사 원문 읽기]({entry.link})")

# [탭 2] 전공 학술 자료 (국내/해외 2단)
with tab_paper:
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("🇰🇷 최신 학술 동향")
        academic = fetch_refined_data(["임상병리학회 학술대회"])
        for p in academic[:10]:
            st.write(f"📌 {p.title} ([링크]({p.link}))")
    with col_r:
        st.subheader("🔬 Global Journals (English)")
        st.link_button("PubMed 이동", "https://pubmed.ncbi.nlm.nih.gov/")
        foreign = fetch_refined_data(["site:nature.com pathology", "PubMed diagnostic"])
        for fp in foreign[:10]:
            st.write(f"📄 {fp.title} ([Read]({fp.link}))")

# [탭 4] 협회 링크
with tab_assoc:
    st.subheader("🔗 공식 사이트 퀵 링크")
    l_cols = st.columns(len(ASSOC_LINKS))
    for i, (name, link) in enumerate(ASSOC_LINKS.items()):
        l_cols[i].link_button(f"{name} ↗️", link)
