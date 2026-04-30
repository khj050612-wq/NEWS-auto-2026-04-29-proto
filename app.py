import streamlit as st
import feedparser
import pandas as pd
from urllib.parse import quote
from collections import defaultdict
import datetime

# 1. 페이지 설정
st.set_page_config(page_title="2026 임상병리 전략 마스터", layout="wide")

# 2. 고정 데이터
MY_EXPERIENCE = "분자진단 실습 경험, 환자 중심의 정확한 검사 지향, 꼼꼼한 데이터 관리"
MAJOR_PRESS = ["연합뉴스", "의학신문", "보건신문", "청년의사", "데일리메디", "메디게이트", "약업신문", "메디파나"]
ASSOC_LINKS = {"중앙회": "http://www.kamt.or.kr/", "정보학회": "http://www.ksclis.or.kr/", "미생물": "http://www.kscm.or.kr/", "혈액": "http://www.ksch.or.kr/", "진단검사": "https://www.kslm.org/"}

# 3. 날짜 포맷 함수 (Apr. 2026 스타일)
def format_date_eng(published_str):
    try:
        # GMT 시간 파싱
        dt = datetime.datetime.strptime(published_str, '%a, %d %b %Y %H:%M:%S %Z')
        now = datetime.datetime.now()
        
        # 이번 달 기사면 일자 포함: 23 Apr. 2026
        if dt.year == now.year and dt.month == now.month:
            return dt.strftime('%d %b. %Y')
        # 지난 기사면 월/년만: Apr. 2026
        else:
            return dt.strftime('%b. %Y')
    except:
        return published_str

# 4. 분석 로직
def analyze_full_strategy(title):
    res = {"topic": "보건의료 정책 동향", "gov_rule": "의료기사법 및 보건의료 데이터 지침", "tags": "#보건의료_트렌드"}
    if "디지털" in title or "AI" in title:
        res.update({"topic": "디지털 병리 및 스마트 진단", "gov_rule": "대한병리학회 [디지털 병리 가이드라인 1.0]", "tags": "#디지털_병리"})
    elif any(kw in title for kw in ["액체생검", "AACR", "NGS", "분자"]):
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
        items.sort(key=lambda x: (any(p in x.get('source', {}).get('text', '') for p in MAJOR_PRESS), x.published_parsed), reverse=True)
        rep = items[0]
        rep.count = len(items)
        final.append(rep)
    return sorted(final, key=lambda x: x.published_parsed, reverse=True)

# --- 화면 구성 ---
st.title("🔬 2026 임상병리사 커리어 전략 플랫폼")

# 상단 요약
st.markdown("### 📊 최근 1개월 전략 키워드 & 실증 근거")
t1, t2 = st.columns(2)
with t1:
    st.info("**#디지털_병리_품질관리**\n\n📜 대한병리학회 가이드라인 1.0")
with t2:
    st.info("**#NGS_액체생검_급여화**\n\n🔬 심평원 유전자 패널검사 승인 지침")

st.divider()

# 탭 시스템
tab_news, tab_paper, tab_jobs, tab_assoc = st.tabs(["🗞️ 의료 뉴스 분석", "🔬 전공 학술 자료", "💼 타겟 채용 정보", "🔔 협회 링크 & 이슈"])


# [탭 1] 뉴스 분석 부분 수정
with tab_news:
    with st.spinner("최신 이슈를 분석 중입니다..."):
        news_data = fetch_refined_data(["임상병리 디지털", "분자진단 기술", "액체생검 AACR"])
        st.markdown(f"### 📋 오늘 분석된 핵심 뉴스: 총 **{len(news_data)}**건")
        
        for i, entry in enumerate(news_data):
            strat = analyze_full_strategy(entry.title)
            press = entry.get('source', {}).get('text', '전문 매체')
            is_major = any(p in press for p in MAJOR_PRESS)
            
            # 날짜 형식 적용
            f_date = format_date_eng(entry.published)
            
            # --- [수정 포인트] 제목과 숫자 박스 레이아웃 ---
            title_col, count_col = st.columns([0.85, 0.15]) # 제목 8.5 : 숫자박스 1.5 비율
            
            with title_col:
                display_title = f"{'⭐' if is_major else '📍'} {entry.title} [{f_date}]"
                # expander를 제목 컬럼 안에 배치
                exp = st.expander(display_title)
            
            with count_col:
                # 관련 기사가 여러 건일 경우 주황색 박스 노출
                if entry.count > 1:
                    st.warning(f"**{entry.count}건**")
                else:
                    st.write("") # 1건일 때는 깔끔하게 비움

            with exp: # 익스팬더 내부 내용
                # 1. 상단 분석 리포트
                st.markdown(f"#### 🔍 분석 리포트")
                c1, c2 = st.columns(2)
                with c1:
                    st.success(f"**현안 주제**\n{strat['topic']}")
                with c2:
                    st.info(f"**📜 관련 지침/법령**\n{strat['gov_rule']}")
                
                st.markdown(f"**🔑 키워드:** `{strat['tags']}`")
                
                # 2. 중간 자소서 활용 (주황색 칸 강조)
                st.warning(f"**🎯 자소서 활용 팁**\n\n{MY_EXPERIENCE.split(',')[0]} 역량을 본 이슈와 연결하여 전문성을 어필하세요.")
                
                # 3. 하단 출처 정보
                st.divider()
                st.caption(f"출처: {press} | 원문 날짜: {entry.published}")
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
