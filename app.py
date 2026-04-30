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

# 3. [업그레이드] 제목 내 따옴표 및 핵심 주제 추출 함수
def analyze_smart_report(title):
    res = {
        "topic": "보건의료 정책 동향",
        "gov_rule": "의료기사법 및 보건의료 데이터 지침",
        "tags": "#보건의료_트렌드",
        "tip": "본 이슈를 실무 역량과 연결하여 전문성을 어필하세요."
    }

    # [핵심 로직] 제목에서 '주제'나 '따옴표' 내용 추출
    subject_match = re.search(r"['‘](.*?)['’]", title)
    extracted_subject = subject_match.group(1) if subject_match else None

    # 1. 학술상/수상 소식일 때
    if any(kw in title for kw in ["학술상", "수상", "포럼", "대상"]):
        event_match = re.search(r"([가-힣]+학회|[가-힣]+사회|[가-힣]+포럼)", title)
        event_name = event_match.group(1) if event_match else "관련 학술 행사"
        
        # 따옴표로 추출된 구체적 주제가 있다면 그걸 현안으로 사용
        display_topic = f"[{extracted_subject}] 연구 및 {event_name} 성과" if extracted_subject else f"학술 역량 강화 및 {event_name} 최신 연구"
        
        res.update({
            "topic": display_topic,
            "gov_rule": "대한임상병리사협회 학술활동 지침 및 보수교육 관리규정",
            "tags": "#학술상 #연구주제분석 #임상연구역량",
            "tip": f"'{extracted_subject if extracted_subject else '수상 주제'}'에 대한 연구 배경을 분석하여, 변화하는 진단 환경에 대비하는 능동적인 자세를 강조하세요."
        })

    # 2. 신기술 발표/포트폴리오 관련
    elif any(kw in title for kw in ["기술", "발표", "강화", "도약"]):
        tech_name = extracted_subject if extracted_subject else "차세대 진단 기술"
        res.update({
            "topic": f"{tech_name} 도입 및 글로벌 진단 시장 동향",
            "gov_rule": "체외진단의료기기법 및 혁신의료기기 통합심사 지침",
            "tags": "#기술혁신 #글로벌트렌드",
            "tip": f"{tech_name}와 같은 최신 기술이 실제 검사실에 도입되었을 때 발생할 수 있는 변수와 품질관리 방안을 고민해보세요."
        })

    # 3. 디지털/AI/NGS (기존 유지)
    elif "디지털" in title or "AI" in title:
        res.update({"topic": "디지털 병리 시스템 구축", "gov_rule": "대한병리학회 디지털 병리 가이드라인 1.0", "tags": "#AI_진단"})
    
    return res

# 4. 데이터 수집 함수 (매체명/날짜 처리 동일)
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
        
        # 매체명 분리
        title_match = re.search(r" - (.*)$", rep.title)
        if title_match:
            rep.media_name = title_match.group(1)
            rep.clean_title = rep.title.replace(f" - {rep.media_name}", "").strip()
        else:
            rep.media_name = rep.get('source', {}).get('text', '뉴스 매체')
            rep.clean_title = rep.title
        final.append(rep)
    return sorted(final, key=lambda x: x.published_parsed, reverse=True)

# --- UI 부분 ---
st.title("🔬 2026 임상병리사 커리어 전략 플랫폼")
st.divider()

tab_news, = st.tabs(["🗞️ 의료 뉴스 분석"]) # 예시를 위해 탭 하나만 표시

with tab_news:
    # 검색 키워드에 '임상병리 주제' 추가
    news_data = fetch_refined_data(["임상병리 학술상 주제", "분자진단 기술 발표", "디지털병리 도입"])
    
    for i, entry in enumerate(news_data):
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
            
            st.warning(f"**🎯 자소서 활용 팁**\n\n{strat['tip']}")
            
            st.divider()
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
