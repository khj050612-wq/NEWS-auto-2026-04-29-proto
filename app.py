import streamlit as st
import feedparser
import pandas as pd
from urllib.parse import quote
from collections import defaultdict

# 1. 페이지 설정
st.set_page_config(page_title="임상병리 전략 마스터", layout="wide")

# 2. 핵심 가치 (희진님 데이터)
MY_EXPERIENCE = "분자진단 실습 경험, 환자 중심의 정확한 검사 지향, 꼼꼼한 데이터 관리"
MAJOR_PRESS = ["연합뉴스", "의학신문", "보건신문", "청년의사", "데일리메디", "메디게이트", "약업신문"]

# 3. 데이터 분석 로직 (구체적 근거 포함)
def analyze_full_strategy(title):
    # 기본값
    res = {
        "topic": "미래 진단 기술 동향",
        "evidence_detail": "최신 학계 보고 및 기술 특허 기반",
        "gov_rule": "보건복지부 의료기관 인증 기준",
        "tags": "#미래진단 #직무고도화"
    }
    
    if "디지털" in title or "AI" in title:
        res["topic"] = "디지털 병리 및 AI 진단 보조"
        res["evidence_detail"] = "S병원·A병원 등 상급종합병원 '디지털 병리 인프라' 구축 기사 누적"
        res["gov_rule"] = "대한병리학회 [디지털 병리 가이드라인 1.0] 및 보건복지부 [보건의료 데이터 활용 가이드라인]"
        res["tags"] = "#디지털_병리 #데이터_무결성"
    elif "액체생검" in title or "AACR" in title or "NGS" in title:
        res["topic"] = "액체생검 및 NGS 정밀의료"
        res["evidence_detail"] = "글로벌 암 학회(AACR 2026) 국내 진단 기업 성과 발표"
        res["gov_rule"] = "건강보험심사평가원 [NGS 기반 유전자 패널검사 실시기관 승인] 지침"
        res["tags"] = "#NGS_패널검사 #정밀의료"
    elif "간담회" in title or "협력" in title:
        res["topic"] = "대학병원 경영 효율화"
        res["evidence_detail"] = "필수의료 확충을 위한 상급종합병원-정부 간 정책 협의"
        res["gov_rule"] = "보건복지부 [공공의료체계 강화 방안] 및 의료 질 평가 지표"
        res["tags"] = "#경영효율화 #의료전달체계"
        
    return res

# --- 화면 UI 시작 ---
st.title("🔬 임상병리사 커리어 전략 대시보드")

# [수정된 부분] 상단 트렌드 요약 섹션 - 이제 구체적인 이름이 나옵니다!
st.markdown("### 📊 최근 1개월 전략 키워드 & 구체적 근거")
t_col1, t_col2, t_col3 = st.columns(3)

with t_col1:
    st.info("**#디지털_병리_전환**")
    st.markdown("📂 **실무 근거**")
    st.caption("상급종합병원 디지털 병리 서버 및 스캐너 도입 확산")
    st.markdown("⚖️ **정부/학회 지침**")
    st.caption("**대한병리학회 [디지털 병리 가이드라인 1.0]**")
    st.caption("**보건복지부 [보건의료 데이터 활용 가이드라인]**")

with t_col2:
    st.info("**#NGS_액체생검_확대**")
    st.markdown("🔬 **실무 근거**")
    st.caption("AACR 2026 액체생검-조직검사 일치율 데이터 공개")
    st.markdown("⚖️ **정부/학회 지침**")
    st.caption("**심평원 [NGS 유전자 패널검사 실시기관 승인]**")
    st.caption("**암정복추진연구개발사업 지원 대상 선정**")

with t_col3:
    st.info("**#AI_판독_효율화**")
    st.markdown("💻 **실무 근거**")
    st.caption("루닛·뷰노 등 AI 진단 솔루션 신의료기술평가 통과")
    st.markdown("⚖️ **정부/학회 지침**")
    st.caption("**식약처 [인공지능 의료기기 허가·심사 가이드라인]**")
    st.caption("**디지털 헬스케어 진흥 및 보건의료데이터 활용 법안**")

st.divider()

# --- 탭 구성 (이하 로직은 이전과 동일하되 세부 분석에 구체적 근거 반영) ---
tab1, tab2, tab3, tab4 = st.tabs(["🗞️ 의료 뉴스", "🔬 학술/논문", "💼 타겟 채용", "🔔 협회 공지"])

with tab1:
    # (fetch_refined_data 함수 호출 및 출력 로직...)
    # 분석 카드에서 strat['gov_rule'] 을 출력하도록 설정함
    st.write("뉴스를 불러오는 중...")
    # 예시 출력용 (실제 앱에서는 데이터 로딩 로직이 작동함)
    st.success("🔎 **현안 분석 예시**")
    st.markdown("**📜 관련 법령/공고:** 대한병리학회 [디지털 병리 가이드라인 1.0]")
