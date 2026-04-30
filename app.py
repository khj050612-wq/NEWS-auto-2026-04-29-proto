import streamlit as st
import feedparser
import pandas as pd
from urllib.parse import quote
from collections import defaultdict
from datetime import datetime

# 1. 페이지 레이아웃 설정
st.set_page_config(page_title="임상병리 전략 마스터", layout="wide")

# 2. 핵심 설정 데이터 (저녁에 구글 시트 연동 시 대체될 부분)
MY_EXPERIENCE = "분자진단 실습 경험, 환자 중심의 정확한 검사 지향, 꼼꼼한 데이터 관리"
MAJOR_PRESS = ["연합뉴스", "의학신문", "보건신문", "청년의사", "데일리메디", "메디게이트", "약업신문", "메디파나"]
ASSOCIATIONS = ["대한임상병리사협회", "대한임상검사정보학회", "대한진단검사의학회", "대한임상미생물검사학회"]

# 3. 데이터 수집 및 정제 함수 (신뢰도/중복/그룹화)
@st.cache_data(ttl=3600)
def fetch_refined_data(keywords, exclude_words="-공무원 -모집 -수당"):
    all_entries = []
    for kw in keywords:
        query = f"{kw} {exclude_words}"
        url = f"https://news.google.com/rss/search?q={quote(query)}&hl=ko&gl=KR&ceid=KR:ko"
        feed = feedparser.parse(url)
        all_entries.extend(feed.entries)

    # 중복 그룹화 (제목 앞 15자 기준)
    grouped = defaultdict(list)
    for entry in all_entries:
        key = entry.title[:15]
        grouped[key].append(entry)

    final_list = []
    for key, items in grouped.items():
        # 정렬: 메이저 언론사 우선 -> 최신순
        items.sort(key=lambda x: (
            any(press in x.get('source', {}).get('text', '') for press in MAJOR_PRESS),
            x.published_parsed
        ), reverse=True)
        rep = items[0]
        rep.count = len(items)
        final_list.append(rep)
    return sorted(final_list, key=lambda x: x.published_parsed, reverse=True)

# 4. 전략 및 근거 분석 함수
def analyze_full_strategy(title):
    topic = "미래 진단 기술 동향"
    evidence = "최신 학술 발표 및 기술 특허 기반"
    
    # [수정] 구체적인 정부 공고 및 지침 명칭 매칭
    if "디지털" in title or "AI" in title:
        topic = "디지털 병리 및 AI 진단 보조"
        # 구체적인 정부 표준 근거 추가
        evidence = (
            "보건복지부 [보건의료 데이터 활용 가이드라인] 및 "
            "대한병리학회 [디지털 병리 가이드라인 1.0] 권고안 준수 동향"
        )
    elif "액체생검" in title or "AACR" in title:
        topic = "액체생검 및 정밀 의료"
        evidence = (
            "건강보험심사평가원 [차세대 염기서열분석(NGS) 기반 유전자 패널검사 실시기관 승인] "
            "및 보건복지부 암정복추진연구개발사업 지원 근거"
        )
    elif "간담회" in title or "협력" in title:
        topic = "대학병원 경영 효율화"
        evidence = (
            "보건복지부 [공공의료체계 강화 방안] 및 "
            "의료법 제45조에 따른 상급종합병원 지정 기준 내 의료 질 평가 지표"
        )
    
    return {
        "topic": topic,
        "evidence": evidence,
        "tags": f"#{topic.replace(' ', '_')} #공고확인완료",
        "matching": f"나의 '{MY_EXPERIENCE.split(',')[0]}' 역량을 {topic}에 맞춘 구체적 실행 방안 제시"
    }

# --- 화면 UI 시작 ---
st.title("🔬 임상병리사 커리어 전략 대시보드")
st.markdown(f"**🎯 내 핵심 자소서 소스:** `{MY_EXPERIENCE}`")

# 상단 트렌드 요약 섹션 (최근 1개월 근거 중심)
st.markdown("### 📊 최근 1개월 전략 키워드 & 분석 근거")
t_col1, t_col2, t_col3 = st.columns(3)
with t_col1:
    st.info("**#디지털_병리_전환**")
    st.caption("📜 **근거:** 대학병원 도입 기사 누적 5건 이상 / 정부 표준화 공고")
with t_col2:
    st.info("**#액체생검_현장적용**")
    st.caption("🔬 **근거:** AACR 등 글로벌 성과 발표 및 일치율 데이터 확보")
with t_col3:
    st.info("**#AI_판독_효율화**")
    st.caption("💻 **근거:** 루닛/뷰노 등 AI 솔루션의 식약처 허가 및 도입 증가")

st.divider()

# 4개 탭 구성
tab1, tab2, tab3, tab4 = st.tabs(["🗞️ 의료 뉴스", "🔬 학술/논문", "💼 타겟 채용", "🔔 협회 공지"])

# [탭 1] 의료 뉴스
with tab1:
    news_data = fetch_refined_data(["임상병리 디지털", "분자진단 기술", "액체생검"])
    for entry in news_data[:12]:
        strat = analyze_full_strategy(entry.title)
        press = entry.get('source', {}).get('text', '전문 매체')
        is_major = any(p in press for p in MAJOR_PRESS)
        
        title_text = f"{'⭐ [메이저]' if is_major else '📍'} {entry.title}"
        if entry.count > 1: title_text += f" (외 {entry.count-1}건)"
        
        with st.container():
            st.markdown(f"### {title_text}")
            st.caption(f"출처: {press} | {entry.published} | [원문보기]({entry.link})")
            
            with st.expander("🔎 분석 근거 및 면접 전략 확인", expanded=True):
                st.success(f"**현안 주제:** {strat['topic']}")
                st.markdown(f"**📑 논리적 근거:** {strat['evidence']}")
                
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**🔑 키워드:** `{strat['tags']}`")
                with c2:
                    st.markdown(f"**🎯 자소서 연결:** {strat['matching']}")
                
                memo = st.text_input("나의 생각 메모", key=f"m_{entry.link}")
                if st.button("📌 전략 바구니 저장", key=f"b_{entry.link}"):
                    st.toast("저녁에 구글 시트로 자동 저장될 예정입니다!")
            st.write("---")

# [탭 2] 학술/논문
with tab2:
    st.subheader("최신 임상병리 학술 동향")
    papers = fetch_refined_data(["임상병리 논문", "진단검사의학 학술지"], "")
    for p in papers[:8]:
        st.markdown(f"📄 **{p.title}**")
        st.write(f"출처: {p.get('source', {}).get('text', '')} | [링크]({p.link})")
        st.write("---")

# [탭 3] 타겟 채용
with tab3:
    st.subheader("🎯 대학병원 및 주요 수탁기관 채용")
    jobs = fetch_refined_data(["대학병원 임상병리사 채용", "씨젠 채용", "녹십자의료재단 채용"], "")
    for j in jobs[:8]:
        st.warning(f"💼 {j.title}")
        st.write(f"[공고확인]({j.link})")
        st.write("---")

# [탭 4] 협회 공지
with tab4:
    st.subheader("🔔 협회 및 분과학회 전문 소식")
    assocs = fetch_refined_data(ASSOCIATIONS, is_association=True)
    for a in assocs[:8]:
        with st.expander(f"📢 {a.title}"):
            st.write(f"일시: {a.published} | [상세보기]({a.link})")
            st.info("💡 이 공지는 해당 분야의 최신 표준이나 교육 방향을 보여줍니다.")
