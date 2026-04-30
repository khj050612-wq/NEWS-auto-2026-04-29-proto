import streamlit as st
import feedparser
import pandas as pd
from urllib.parse import quote
from collections import defaultdict
import datetime

# 1. 페이지 설정
st.set_page_config(page_title="2026 임상병리 전략 마스터", layout="wide")

# [CSS] 제목 옆 딥 레드 배지 스타일
st.markdown("""
    <style>
    .news-badge {
        background-color: #D32F2F; 
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: bold;
        margin-left: 8px;
        display: inline-block;
        vertical-align: middle;
    }
    .main-title { font-size: 1.1rem; font-weight: 600; margin-bottom: -10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 처리 함수들
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
        # 실제 매체명(source.text)이 있는 것을 우선순위로 정렬
        items.sort(key=lambda x: x.published_parsed, reverse=True)
        rep = items[0]
        rep.count = len(items)
        # 매체명 직접 추출
        rep.media_name = rep.get('source', {}).get('text', '뉴스 매체')
        final.append(rep)
    return sorted(final, key=lambda x: x.published_parsed, reverse=True)

# --- UI 시작 ---
st.title("🔬 2026 임상병리사 커리어 전략 플랫폼")
st.divider()

tab_news, tab_paper, tab_jobs, tab_assoc = st.tabs(["🗞️ 의료 뉴스 분석", "🔬 전공 학술 자료", "💼 타겟 채용 정보", "🔔 협회 링크 & 이슈"])

with tab_news:
    news_data = fetch_refined_data(["임상병리 디지털", "분자진단 기술", "액체생검 AACR"])
    st.markdown(f"### 📋 오늘 분석된 핵심 뉴스: 총 **{len(news_data)}**건")
    
    for i, entry in enumerate(news_data):
        strat = analyze_full_strategy(entry.title)
        f_date = format_date_eng(entry.published)
        badge = f'<span class="news-badge">{entry.count}건</span>' if entry.count > 1 else ""
        
        # [수정] 제목 라인: 제목 + 날짜 + 레드배지
        st.markdown(f'<div class="main-title">📍 {entry.title} <small>[{f_date}]</small> {badge}</div>', unsafe_allow_html=True)
        
        with st.expander("🔎 분석 리포트 확인"):
            # 분석 내용
            c1, c2 = st.columns(2)
            with c1:
                st.success(f"**현안 주제**\n{strat['topic']}")
            with c2:
                st.info(f"**📜 관련 지침/법령**\n{strat['gov_rule']}")
            
            # 자소서 팁 (주황색)
            st.warning(f"**🎯 자소서 활용 팁**\n\n{MY_EXPERIENCE.split(',')[0]} 역량을 본 이슈와 연결하여 실무 전문성을 어필하세요.")
            
            st.divider()
            # [수정] 출처: 매체명 정확하게 노출
            st.caption(f"**출처: {entry.media_name}** | 원문 날짜: {entry.published}")
            st.markdown(f"🔗 [기사 원문 읽기]({entry.link})")

# [탭 2] 전공 학술 자료 (2단 레이아웃)
with tab_paper:
    cl, cr = st.columns(2)
    with cl:
        st.subheader("🇰🇷 최신 학술 동향")
        academic = fetch_refined_data(["임상병리학회 학술대회"])
        for p in academic[:10]:
            with st.expander(f"📌 {p.title} [{format_date_eng(p.published)}]"):
                st.write(f"[자료 확인]({p.link})")
    with cr:
        st.subheader("🔬 Global Journals (English)")
        st.link_button("PubMed", "https://pubmed.ncbi.nlm.nih.gov/")
        foreign = fetch_refined_data(["site:nature.com pathology", "PubMed clinical laboratory"])
        for fp in foreign[:10]:
            st.markdown(f"📄 **{fp.title}** [{format_date_eng(fp.published)}]")
            st.caption(f"[Read Original]({fp.link})")

# [탭 4] 협회 링크
with tab_assoc:
    st.subheader("🔗 공식 사이트 퀵 링크")
    cols = st.columns(len(ASSOC_LINKS))
    for i, (name, link) in enumerate(ASSOC_LINKS.items()):
        cols[i].link_button(f"{name} ↗️", link)
