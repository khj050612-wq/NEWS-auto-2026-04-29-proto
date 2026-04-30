import streamlit as st
import feedparser
import pandas as pd
from urllib.parse import quote
from collections import defaultdict
import datetime
import re

# 1. [데이터] 전역 변수 및 설정
MY_EXPERIENCE = "분자진단 실습 경험, 환자 중심의 정확한 검사 지향, 꼼꼼한 데이터 관리"
MAJOR_PRESS = ["연합뉴스", "의학신문", "보건신문", "청년의사", "데일리메디", "메디게이트", "약업신문", "메디파나"]
ASSOC_LINKS = {
    "중앙회": "http://www.kamt.or.kr/", 
    "정보학회": "http://www.ksclis.or.kr/", 
    "미생물": "http://www.kscm.or.kr/", 
    "혈액": "http://www.ksch.or.kr/", 
    "진단검사": "https://www.kslm.org/"
}

# 2. [UI] 페이지 설정 및 맞춤형 CSS
st.set_page_config(page_title="2026 임상병리 전략 마스터", layout="wide")

st.markdown("""
    <style>
    .news-badge {
        background-color: #D32F2F; color: white; padding: 2px 8px; border-radius: 4px;
        font-size: 0.75rem; font-weight: bold; margin-left: 8px; display: inline-block; vertical-align: middle;
    }
    .main-title { font-size: 1.1rem; font-weight: 600; margin-top: 15px; margin-bottom: 5px; }
    .stExpander { border: 1px solid #f0f2f6; border-radius: 8px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 3. [로직] 지능형 분석 및 데이터 처리 함수
def analyze_smart_report(title):
    # 제목 내 따옴표(' ', “ ”) 추출 로직
    subject_match = re.search(r"['‘\"“](.*?)['’\"”]", title)
    extracted = subject_match.group(1) if subject_match else None

    res = {
        "topic": "보건의료 정책 및 진단 트렌드",
        "gov_rule": "의료기사법 및 보건의료 데이터 활용 가이드라인",
        "tip": "본 기사의 핵심 내용을 실무 역량과 연결하여 전문성을 강조하세요."
    }

    # 학술상/수상/대회 관련
    if any(kw in title for kw in ["학술", "상", "수상", "포럼", "대상"]):
        topic_text = f"[{extracted}] 연구 성과 및 학술 동향" if extracted else "임상병리 학술 역량 강화"
        res.update({
            "topic": topic_topic if 'topic_topic' in locals() else topic_text,
            "gov_rule": "대한임상병리사협회 학술활동 및 보수교육 지침",
            "tip": f"**'{extracted if extracted else '수상 주제'}'**의 연구 배경을 분석하여, 변화하는 진단 환경에 선제적으로 대응하는 의과학자적 자질을 어필하세요."
        })
    # 디지털 병리/AI 관련
    elif any(kw in title for kw in ["디지털", "AI", "인공지능"]):
        res.update({
            "topic": f"[{extracted if extracted else '디지털 병리'}] 시스템 고도화 및 AI 진단 도입",
            "gov_rule": "대한병리학회 [디지털 병리 가이드라인 1.0]",
            "tip": f"AI 분석 도입에 따른 검사 효율 개선과 데이터 무결성(Integrity) 유지 역량을 실무 강점으로 내세우세요."
        })
    # 기술 발표/분자진단
    elif any(kw in title for kw in ["진단", "기술", "발표", "분자", "성공", "개발"]):
        res.update({
            "topic": f"[{extracted if extracted else '차세대 진단기술'}] 상용화 및 글로벌 진단 시장 점유",
            "gov_rule": "체외진단의료기기법 및 혁신의료기기 통합심사 지침",
            "tip": f"신기술 도입 시 검사실에서 발생할 수 있는 품질 표준화(Standardization) 방안을 본인의 꼼꼼함과 연결하세요."
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
    
    # [중복 제거 로직] 기관명(병원/기업)이 다르면 다른 뉴스로 인정
    grouped = defaultdict(list)
    for entry in all_entries:
        # 매체명 제외한 순수 제목
        clean_t = re.sub(r" - .*$", "", entry.title).strip()
        # 제목 앞 12글자(기관명 포함 확률 높음)를 키로 설정
        unique_key = clean_t.replace(" ", "")[:12]
        grouped[unique_key].append(entry)
        
    final = []
    for key, items in grouped.items():
        items.sort(key=lambda x: x.published_parsed, reverse=True)
        rep = items[0]
        rep.count = len(items)
        
        # 매체명(출처) 정밀 추출
        title_match = re.search(r" - (.*)$", rep.title)
        if title_match:
            rep.media_name = title_match.group(1)
            rep.clean_title = rep.title.replace(f" - {rep.media_name}", "").strip()
        else:
            rep.media_name = rep.get('source', {}).get('text', '뉴스 매체')
            rep.clean_title = rep.title
        final.append(rep)
    return sorted(final, key=lambda x: x.published_parsed, reverse=True)

# --- 4. 메인 UI 화면 ---
st.title("🔬 2026 임상병리 커리어 전략 마스터")
st.caption("실시간 의료 트렌드 기반 자소서/면접 대응 플랫폼")
st.divider()

# 탭 시스템
tab_news, tab_paper, tab_assoc = st.tabs(["🗞️ 의료 뉴스 분석", "🔬 전공 학술 자료", "🔔 협회 퀵 링크"])

# [탭 1] 뉴스 분석 (핵심 기능)
with tab_news:
    with st.spinner("최신 임상병리 이슈 분석 중..."):
        news_data = fetch_refined_data(["임상병리 디지털 AI", "임상병리학과 학술상 수상", "분자진단 기술 발표"])
        st.markdown(f"### 📋 오늘 분석된 핵심 뉴스: 총 **{len(news_data)}**건")
        
        for i, entry in enumerate(news_data):
            strat = analyze_smart_report(entry.clean_title)
            # 날짜 포맷 (Apr. 2026 스타일)
            f_date = datetime.datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %Z').strftime('%d %b. %Y')
            # 딥 레드 배지
            badge = f'<span class="news-badge">{entry.count}건</span>' if entry.count > 1 else ""
            
            # 제목 라인 출력
            st.markdown(f'<div class="main-title">📍 {entry.clean_title} <small>[{f_date}]</small> {badge}</div>', unsafe_allow_html=True)
            
            with st.expander("🔎 분석 리포트 확인"):
                c1, c2 = st.columns(2)
                with c1:
                    st.success(f"**현안 주제**\n{strat['topic']}")
                with c2:
                    st.info(f"**📜 관련 지침/법령**\n{strat['gov_rule']}")
                
                # 자소서 활용 팁 (주황색 강조)
                st.warning(f"**🎯 자소서 활용 팁**\n\n{strat['tip']}")
                
                st.divider()
                # 출처 매체명 정확하게 표시
                st.caption(f"**출처: {entry.media_name}** | 원문 날짜: {entry.published}")
                st.markdown(f"🔗 [기사 원문 읽기]({entry.link})")

# [탭 2] 전공 학술 자료 (수정된 로직)
with tab_paper:
    cl, cr = st.columns(2)
    with cl:
        st.subheader("🇰🇷 국내 학술 동향")
        # 국내 학술대회 소식 위주
        academic = fetch_refined_data(["임상병리학회 학술대회", "진단검사의학회 초록"])
        for p in academic[:10]:
            st.write(f"📌 {p.clean_title} ([링크]({p.link}))")
            
    with cr:
        st.subheader("🔬 Global Journals (English)")
        st.link_button("PubMed 바로가기", "https://pubmed.ncbi.nlm.nih.gov/")
        
        # [수정 포인트] 해외 저널만 나오도록 사이트 제한 및 언어 필터 강화
        # 한글 뉴스가 섞이지 않게 -site:kr 등을 추가함
        foreign_query = [
            "site:nature.com clinical pathology", 
            "site:sciencedirect.com medical laboratory",
            "site:academic.oup.com clinical chemistry",
            "PubMed diagnostic technology"
        ]
        
        # 영어 기사만 가져오도록 키워드 조합
        foreign = fetch_refined_data(foreign_query)
        
        for fp in foreign[:12]:
            # 제목에 한글이 포함된 기사는 필터링해서 제외
            if not re.search('[가-힣]', fp.clean_title):
                st.markdown(f"📄 **{fp.clean_title}**")
                st.caption(f"Source: {fp.media_name} | [Read Original]({fp.link})")

# [탭 3] 협회 링크
with tab_assoc:
    st.subheader("🔗 공식 사이트 퀵 링크")
    cols = st.columns(len(ASSOC_LINKS))
    for i, (name, link) in enumerate(ASSOC_LINKS.items()):
        cols[i].link_button(f"{name} ↗️", link)
