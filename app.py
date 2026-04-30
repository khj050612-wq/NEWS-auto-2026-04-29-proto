import streamlit as st
import feedparser
import pandas as pd
from urllib.parse import quote
from datetime import datetime

# 1. 페이지 기본 설정
st.set_page_config(page_title="JINI 취업 전략 보드", layout="wide")

# 2. 임시 데이터 (저녁에 구글 시트 연동 시 이 부분이 자동으로 대체됩니다)
if 'news_basket' not in st.session_state:
    st.session_state.news_basket = []

# 희진님의 핵심 경험/가치관 (자소서 매칭용)
MY_EXPERIENCE = "분자진단 실습 경험, 환자 중심의 정확한 검사 지향, 꼼꼼한 데이터 관리"

# 3. 뉴스 수집 로직 (엄격한 필터링 버전)
@st.cache_data(ttl=3600)
def fetch_news():
    # 진짜 임상병리 전공/병원 이슈만 가져오기 위한 키워드
    STRICT_KEYWORDS = [
        "임상병리 디지털", "분자진단 기술", "NGS 검사", 
        "액체생검", "디지털 병리 시스템", "대학병원 의료 질 향상"
    ]
    
    all_entries = []
    for kw in STRICT_KEYWORDS:
        # 노이즈(공무원, 채용공고, 부동산 등)를 확실히 제거하는 검색식
        query = f"{kw} -공무원 -모집 -수당 -공고 -부동산 -토지 -블로그 -실종"
        url = f"https://news.google.com/rss/search?q={quote(query)}&hl=ko&gl=KR&ceid=KR:ko"
        feed = feedparser.parse(url)
        all_entries.extend(feed.entries)
        
    # 중복 제거 및 최신순 정렬
    unique_news = {e.link: e for e in all_entries}.values()
    return sorted(unique_news, key=lambda x: x.published_parsed, reverse=True)

# 4. 현안 및 자소서 전략 분석 함수
def analyze_strategy(title, my_exp):
    # (1) 현안 주제 정밀 분석
    topic = "보건의료 정책 동향"
    if "디지털" in title or "AI" in title:
        topic = "미래형 스마트 진단 시스템 구축"
    elif "간담회" in title or "협력" in title or "병원장" in title:
        topic = "대학병원 경영 효율화 및 의료 전달 체계"
    elif "진단" in title or "검사" in title:
        topic = "정밀 의료 기반 고부가가치 검사 확대"
    
    # (2) 자소서 키워드 추출
    if "디지털" in topic:
        tags = "#스마트_직무역량 #디지털_적응력"
    elif "경영" in topic:
        tags = "#비용절감_전문가 #협업_커뮤니케이션"
    else:
        tags = "#검사_무결성 #환자_신뢰_보호"
        
    # (3) 임상병리 연결 전략
    connection = f"{topic} 상황에서 오진 없는 검사로 병원의 신뢰도를 높이는 역할"
    
    # (4) 내 경험 매칭 (희진님 텍스트 기반)
    matching = f"나의 '{my_exp.split(',')[0]}'을(를) 활용해 {topic}에 기여할 방안 제시"
    
    return {"topic": topic, "tags": tags, "connection": connection, "matching": matching}

# --- 메인 화면 시작 ---
st.title("🔬 임상병리사 취업 전략 & 자소서 마스터")
st.markdown(f"**💡 현재 내 경험 소스:** `{MY_EXPERIENCE}`")
st.divider()

with st.spinner("최신 의료 전공 소식 분석 중..."):
    news_list = fetch_news()

if not news_list:
    st.warning("조건에 맞는 최신 뉴스가 없습니다. 키워드를 조절해보세요.")

for entry in news_list[:15]:
    # AI 전략 분석 실행
    strategy = analyze_strategy(entry.title, MY_EXPERIENCE)
    
    with st.container():
        # 기사 제목 및 출처
        source = getattr(entry, 'source', {}).get('text', '전문 매체')
        st.markdown(f"### 📍 {entry.title}")
        st.caption(f"출처: {source} | 날짜: {entry.published} | [원문보기]({entry.link})")
        
        # 현안 분석 결과 (눈에 띄게 표시)
        st.success(f"🔎 **현안 주제:** {strategy['topic']}")
        
        # 4개 영역 상세 분석
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**📝 기사 요약:** {entry.title[:40]}...")
            st.markdown(f"**🔑 핵심 키워드:** `{strategy['tags']}`")
        with col2:
            st.markdown(f"**🧬 임상병리 연결:** {strategy['connection']}")
            st.markdown(f"**🎯 자소서 연결:** {strategy['matching']}")
            
        # 선택적 메모 및 저장
        user_note = st.text_input("면접 대비 메모 (선택사항)", key=f"note_{entry.link}", placeholder="여기에 적은 내용도 함께 저장됩니다.")
        
        if st.button("📌 자소서/면접 소스로 저장", key=f"btn_{entry.link}"):
            st.session_state.news_basket.append({
                "날짜": entry.published,
                "제목": entry.title,
                "현안": strategy['topic'],
                "연결": strategy['connection'],
                "매칭": strategy['matching'],
                "메모": user_note
            })
            st.toast("전략 정보가 저장되었습니다!")
        st.write("---")

# 사이드바: 저장된 데이터 확인 및 관리
st.sidebar.header("🧺 나의 면접/자소서 바구니")
if st.session_state.news_basket:
    df = pd.DataFrame(st.session_state.news_basket)
    st.sidebar.write(f"현재 {len(df)}개의 전략 저장됨")
    
    if st.sidebar.button("🗑️ 바구니 비우기"):
        st.session_state.news_basket = []
        st.rerun()
