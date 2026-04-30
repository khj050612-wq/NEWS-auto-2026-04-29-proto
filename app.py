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
ASSOC_LINKS = {"중앙회": "http://www.kamt.or.kr/", "정보학회": "http://www.ksclis.or.kr/", "미생물": "http://www.kscm.or.kr/", "혈액": "http://www.ksch.or.kr/", "진단검사": "https://www.kslm.org/"}

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

# 3. 데이터 처리 함수 (매체명 추출 강화)
def format_date_eng(published_str):
    try:
        dt = datetime.datetime.strptime(published_str, '%a, %d %b %Y %H:%M:%S %Z')
        now = datetime.datetime.now()
        return dt.strftime('%d %b. %Y') if (dt.year == now.year and dt.month == now.month) else dt.strftime('%b. %Y')
    except: return published_str

def analyze_full_strategy(title):
    res = {"topic": "보건의료 정책 동향", "gov_rule": "의료기사법 및 보건의료 데이터 지침", "tags": "#보건의료_트렌드"}
    if "디지털" in title or "AI" in title:
        res.update({"topic": "디지털 병리 및 스마트 진단", "gov_rule": "대한병리학회 [디지털 병리 가이드라인 1.0]", "tags": "#디지털_병리"})
    elif any(kw in title for kw in ["액체생검", "AACR", "NGS", "분자", "젠큐릭스", "씨젠"]):
        res.update({"topic": "정밀의료 및 분자진단 고도화", "gov_rule": "심평원 [NGS 기반 유전자 패널검사 실시기관 승인]", "tags": "#NGS_패널검사"})
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
        
        # [핵심 수정] 매체명 추출 로직 강화: 제목의 " - 매체명" 부분을 정규식으로 추출
        title_match = re.search(r" - (.*)$", rep.title)
        if title_match:
            rep.media_name = title_match.group(1)
            # 제목에서 매체명 제거하여 깔끔하게 표시
            rep.clean_title = rep.title.replace(f" - {rep.media_name}", "").strip()
        else:
            rep.media_name = rep.get('source', {}).get('text', '뉴스 매체')
            rep.clean_title = rep.title

        final.append(rep)
    return sorted(final, key=lambda x: x.published_parsed, reverse=True)

# --- 메인 UI ---
st.title("🔬 2026 임상병리사 커리어 전략 플랫폼")
st.divider()

tab_news, tab_paper, tab_jobs, tab_assoc = st.tabs(["🗞️ 의료 뉴스 분석", "🔬 전공 학술 자료", "💼 타겟 채용 정보", "🔔 협회 링크 & 이슈"])

# [탭 1] 의료 뉴스 분석
with tab_news:
    with st.spinner("최신 뉴스 분석 중..."):
        news_data = fetch_refined_data(["임상병리 디지털", "분자진단 기술", "액체생검 AACR"])
        st.markdown(f"### 📋 오늘 분석된 핵심 뉴스: 총 **{len(news_data)}**건")
        
        for i, entry in enumerate(news_data):
            strat = analyze_full_strategy(entry.clean_title)
            f_date = format_date_eng(entry.published)
            badge = f'<span class="news-badge">{entry.count}건</span>' if entry.count > 1 else ""
            
            # 제목 라인 (깔끔한 제목 + 날짜 + 배지)
            st.markdown(f'<div class="main-title">📍 {entry.clean_title} <small>[{f_date}]</small> {badge}</div>', unsafe_allow_html=True)
            
            with st.expander("🔎 분석 리포트 확인"):
                c1, c2 = st.columns(2)
                with c1:
                    st.success(f"**현안 주제**\n{strat['topic']}")
                with c2:
                    st.info(f"**📜 관련 지침/법령**\n{strat['gov_rule']}")
                
                st.warning(f"**🎯 자소서 활용 팁**\n\n{MY_EXPERIENCE.split(',')[0]} 역량을 본 이슈와 연결하여 실무 전문성을 어필하세요.")
                
                st.divider()
                # 출처 매체명을 이제 확실하게 출력 (예: 출처: 핀포인트뉴스)
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
