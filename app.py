import streamlit as st
import pandas as pd
import heapq
import re
import os
import json
import base64

# --- 1. 기본 페이지 설정 ---
st.set_page_config(
    page_title="DIGIMON STORY: CYBER SLEUTH // EVOLUTION ROUTER",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- 2. 다국어 사전 파일 분리 로드 (locales.json & digimon_names_ko.json) ---
KO_JSON_PATH = os.path.join(BASE_DIR, "digimon_names_ko.json")
if os.path.exists(KO_JSON_PATH):
    with open(KO_JSON_PATH, "r", encoding="utf-8") as f:
        KO_NAME_DICT = json.load(f)
else:
    KO_NAME_DICT = {}

LOCALES_PATH = os.path.join(BASE_DIR, "locales.json")
if os.path.exists(LOCALES_PATH):
    with open(LOCALES_PATH, "r", encoding="utf-8") as f:
        LOCALE_TEXT = json.load(f)
else:
    LOCALE_TEXT = {
        "KO": {"sys_title": "DIGIMON STORY: CYBER SLEUTH", "sys_sub": "최적 진화/퇴화 경로 탐색기", "start_label": "출발 디지몬", "target_label": "목표 디지몬"},
        "EN": {"sys_title": "DIGIMON STORY: CYBER SLEUTH", "sys_sub": "Evolution Route Solver", "start_label": "START DIGIMON", "target_label": "TARGET DIGIMON"}
    }

# --- 3. UI/CSS 디자인 시스템 ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700&family=Pretendard:wght@400;500;600;700;800&display=swap');

    /* 기본 레이아웃 & 사이버 배경 그리드 */
    .stApp {
        background-color: #030712 !important;
        background-image: 
            linear-gradient(rgba(56, 189, 248, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(56, 189, 248, 0.03) 1px, transparent 1px),
            radial-gradient(circle at 50% 0%, rgba(30, 58, 138, 0.18) 0%, transparent 70%);
        background-size: 32px 32px, 32px 32px, 100% 100%;
        color: #f1f5f9;
        font-family: 'Pretendard', -apple-system, sans-serif;
    }

    /* 상단 헤더 & 메뉴 설정 */
    header[data-testid="stHeader"] {
        background: transparent !important;
        z-index: 100 !important;
    }
    #MainMenu, [data-testid="stToolbarActions"], [data-testid="stDecoration"], footer {
        display: none !important;
    }

    /* 사이드바 열기/닫기 토글 버튼 */
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stExpandSidebarButton"] {
        display: inline-flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        color: #38bdf8 !important;
        background-color: #090e1a !important;
        border: 1px solid rgba(56, 189, 248, 0.4) !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.5) !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        z-index: 999999 !important;
    }
    [data-testid="stSidebarCollapsedControl"] svg,
    [data-testid="stSidebarCollapseButton"] svg,
    [data-testid="stExpandSidebarButton"] svg {
        fill: #38bdf8 !important;
        color: #38bdf8 !important;
    }
    [data-testid="stSidebarCollapsedControl"]:hover,
    [data-testid="stSidebarCollapseButton"]:hover,
    [data-testid="stExpandSidebarButton"]:hover {
        background-color: #111c33 !important;
        border-color: #38bdf8 !important;
        box-shadow: 0 0 16px rgba(56, 189, 248, 0.6) !important;
    }

    /* 사이드바 */
    [data-testid="stSidebar"] {
        background: #060a14 !important;
        border-right: 1px solid rgba(56, 189, 248, 0.12) !important;
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.5) !important;
    }

    .main .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 4rem !important;
        max-width: 960px;
    }

    /* 사이버 HUD 헤더 배너 */
    .cyber-banner {
        position: relative;
        background: rgba(10, 16, 30, 0.75);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(56, 189, 248, 0.22);
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 18px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45);
        overflow: hidden;
    }
    .cyber-banner::before {
        content: '';
        position: absolute;
        top: 0; left: 0; width: 4px; height: 100%;
        background: linear-gradient(180deg, #38bdf8, #818cf8);
    }
    .cyber-title {
        font-family: 'Orbitron', monospace;
        font-weight: 800;
        font-size: 1.45rem;
        letter-spacing: 2px;
        background: linear-gradient(90deg, #38bdf8 0%, #cbd5e1 60%, #94a3b8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2;
    }
    .cyber-sub {
        color: #94a3b8;
        font-size: 0.82rem;
        margin-top: 5px;
        font-family: 'Space Grotesk', 'Pretendard', sans-serif;
        letter-spacing: 0.5px;
    }
    .cyber-tag {
        display: inline-block;
        font-family: 'Orbitron', monospace;
        font-size: 0.68rem;
        color: #38bdf8;
        background: rgba(56, 189, 248, 0.1);
        border: 1px solid rgba(56, 189, 248, 0.3);
        padding: 3px 8px;
        border-radius: 4px;
        letter-spacing: 1px;
    }

    /* 선택창 라벨 */
    div[data-testid="stSelectbox"] label p {
        font-family: 'Orbitron', monospace !important;
        font-size: 0.72rem !important;
        color: #38bdf8 !important;
        letter-spacing: 1px !important;
        font-weight: 700 !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #070c18 !important;
        border: 1px solid rgba(56, 189, 248, 0.25) !important;
        border-radius: 8px !important;
        color: #f1f5f9 !important;
        font-weight: 600 !important;
    }
    div[data-baseweb="select"] > div:hover {
        border-color: #38bdf8 !important;
    }

    /* Swap 버튼 */
    .swap-btn-wrap button {
        height: 42px !important;
        margin-top: 24px !important;
        background-color: #0b1324 !important;
        border: 1px solid rgba(56, 189, 248, 0.4) !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
    }

    /* 텔레메트리 대시보드 (요약 바) */
    .telemetry-board {
        background: rgba(8, 14, 26, 0.85);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 10px;
        padding: 12px 18px;
        margin: 16px 0 24px 0;
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: 16px;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);
    }
    .tele-item {
        border-left: 2px solid rgba(56, 189, 248, 0.3);
        padding-left: 12px;
    }
    .tele-title {
        font-family: 'Orbitron', monospace;
        font-size: 0.68rem;
        color: #64748b;
        letter-spacing: 1px;
    }
    .tele-val {
        font-family: 'Orbitron', monospace;
        font-size: 1.25rem;
        font-weight: 800;
        color: #38bdf8;
        margin-top: 2px;
    }
    .tele-sub {
        font-size: 0.75rem;
        color: #94a3b8;
        margin-top: 2px;
    }

    /* 타임라인 노드 카드 */
    .node-card {
        background: rgba(11, 18, 33, 0.75);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(56, 189, 248, 0.15);
        border-radius: 10px;
        padding: 12px 16px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35);
        display: flex;
        align-items: center;
        gap: 14px;
        position: relative;
        transition: transform 0.15s ease, border-color 0.15s ease;
    }
    .node-card:hover {
        border-color: rgba(56, 189, 248, 0.4);
        background: rgba(15, 23, 42, 0.85);
    }
    .node-start {
        border-left: 4px solid #38bdf8 !important;
        background: linear-gradient(90deg, rgba(56, 189, 248, 0.07) 0%, rgba(11, 18, 33, 0.75) 100%);
    }
    .node-evo {
        border-left: 4px solid #10b981 !important;
        background: linear-gradient(90deg, rgba(16, 185, 129, 0.06) 0%, rgba(11, 18, 33, 0.75) 100%);
    }
    .node-dev {
        border-left: 4px solid #3b82f6 !important;
        background: linear-gradient(90deg, rgba(59, 130, 246, 0.06) 0%, rgba(11, 18, 33, 0.75) 100%);
    }

    /* 노드 인덱스 번호 */
    .node-idx {
        font-family: 'Orbitron', monospace;
        font-size: 0.85rem;
        font-weight: 800;
        color: #64748b;
        letter-spacing: 1px;
        width: 28px;
        text-align: center;
        flex-shrink: 0;
    }

    /* 썸네일 포트레이트 */
    .digi-thumb-wrap {
        position: relative;
        width: 50px;
        height: 50px;
        border-radius: 10px;
        background: #090e1c;
        border: 1px solid rgba(56, 189, 248, 0.25);
        padding: 2px;
        flex-shrink: 0;
    }
    .digi-thumb-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        border-radius: 7px;
    }

    /* 디지몬 이름 및 태그 */
    .mon-name-main {
        font-size: 1.12rem;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: -0.2px;
    }
    .mon-name-en {
        font-size: 0.8rem;
        color: #94a3b8;
        margin-left: 6px;
        font-weight: 500;
    }

    /* 정밀 스탯 칩 (노 아이콘, 미니멀 HUD 스타일) */
    .stat-bar {
        display: flex;
        flex-wrap: wrap;
        gap: 5px;
        margin-top: 6px;
    }
    .stat-pill {
        display: inline-flex;
        align-items: center;
        background: #080d19;
        border: 1px solid #1e293b;
        border-radius: 4px;
        padding: 2px 7px;
        font-family: 'Orbitron', monospace;
        font-size: 0.7rem;
        font-weight: 600;
        color: #cbd5e1;
    }
    .stat-pill .stat-k {
        color: #64748b;
        margin-right: 4px;
        font-size: 0.65rem;
    }
    .stat-pill .stat-v {
        color: #38bdf8;
    }
    .stat-extra {
        background: rgba(244, 63, 94, 0.08);
        border-color: rgba(244, 63, 94, 0.3);
    }
    .stat-extra .stat-k { color: #f43f5e; }
    .stat-extra .stat-v { color: #fca5a5; font-family: 'Pretendard', sans-serif; }

    /* 세대 및 속성 뱃지 */
    .hud-badge {
        font-size: 0.68rem;
        font-weight: 700;
        padding: 2px 6px;
        border-radius: 4px;
        display: inline-block;
        letter-spacing: 0.3px;
    }
    .stg-baby { background: rgba(56, 189, 248, 0.15); color: #7dd3fc; border: 1px solid rgba(56, 189, 248, 0.3); }
    .stg-rookie { background: rgba(16, 185, 129, 0.15); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.3); }
    .stg-champion { background: rgba(59, 130, 246, 0.15); color: #93c5fd; border: 1px solid rgba(59, 130, 246, 0.3); }
    .stg-ultimate { background: rgba(168, 85, 247, 0.15); color: #d8b4fe; border: 1px solid rgba(168, 85, 247, 0.3); }
    .stg-mega { background: rgba(244, 63, 94, 0.15); color: #fda4af; border: 1px solid rgba(244, 63, 94, 0.3); }
    .stg-ultra { background: rgba(245, 158, 11, 0.18); color: #fcd34d; border: 1px solid rgba(245, 158, 11, 0.4); }
    .stg-unknown { background: #1e293b; color: #94a3b8; }

    .attr-vac { background: rgba(245, 158, 11, 0.12); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.25); }
    .attr-data { background: rgba(6, 182, 212, 0.12); color: #67e8f9; border: 1px solid rgba(6, 182, 212, 0.25); }
    .attr-vir { background: rgba(239, 68, 68, 0.12); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.25); }
    .attr-free { background: rgba(148, 163, 184, 0.12); color: #cbd5e1; border: 1px solid rgba(148, 163, 184, 0.25); }

    /* 타임라인 연결선 */
    .circuit-link {
        display: flex;
        flex-direction: column;
        align-items: center;
        height: 24px;
        position: relative;
        justify-content: center;
    }
    .circuit-beam {
        width: 2px;
        height: 100%;
        background: linear-gradient(180deg, #38bdf8 0%, rgba(56, 189, 248, 0.15) 100%);
    }
    .circuit-dot {
        position: absolute;
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #38bdf8;
        box-shadow: 0 0 8px #38bdf8;
    }

    /* 액션 뱃지 */
    .action-tag {
        font-family: 'Orbitron', monospace;
        font-size: 0.7rem;
        font-weight: 800;
        letter-spacing: 0.5px;
        display: inline-block;
        margin-right: 6px;
    }
    .action-evo { color: #10b981; }
    .action-dev { color: #60a5fa; }
    .action-origin { color: #38bdf8; }

    /* 일반 버튼 스타일링 */
    .stButton > button {
        background-color: #0d1527 !important;
        color: #f1f5f9 !important;
        border: 1px solid rgba(56, 189, 248, 0.25) !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
        transition: all 0.15s ease;
    }
    .stButton > button:hover {
        background-color: #1e293b !important;
        border-color: #38bdf8 !important;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.3) !important;
    }

    /* 차단 미니 카드 (사이드바) */
    .ban-item-card {
        background: #090e1c;
        border: 1px solid rgba(244, 63, 94, 0.25);
        border-radius: 6px;
        padding: 6px 10px;
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 6px;
    }

    /* Expander 커스텀 스타일링 (사이버 HUD 드롭다운) */
    [data-testid="stExpander"] {
        background: rgba(6, 10, 20, 0.6) !important;
        border: 1px solid rgba(56, 189, 248, 0.18) !important;
        border-radius: 8px !important;
        margin-top: 6px !important;
        margin-bottom: 10px !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35) !important;
    }
    [data-testid="stExpander"] summary {
        color: #7dd3fc !important;
        font-family: 'Space Grotesk', 'Pretendard', sans-serif !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        padding: 8px 14px !important;
    }
    [data-testid="stExpander"] summary:hover {
        color: #38bdf8 !important;
    }

    /* 스펙 & 스킬 정보 그리드 */
    .spec-meta-wrap {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
        gap: 8px;
        margin-bottom: 12px;
    }
    .spec-meta-chip {
        background: #090e1c;
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 6px;
        padding: 6px 10px;
        text-align: center;
    }
    .spec-meta-label {
        font-size: 0.65rem;
        color: #64748b;
        font-family: 'Orbitron', monospace;
        letter-spacing: 0.5px;
    }
    .spec-meta-val {
        font-size: 0.95rem;
        font-weight: 700;
        color: #38bdf8;
        font-family: 'Orbitron', monospace;
        margin-top: 2px;
    }

    .stat-matrix-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Orbitron', monospace;
        font-size: 0.74rem;
        margin-bottom: 14px;
    }
    .stat-matrix-table th {
        background: rgba(15, 23, 42, 0.85);
        color: #94a3b8;
        padding: 6px 8px;
        border: 1px solid rgba(56, 189, 248, 0.15);
        text-align: center;
        font-weight: 700;
    }
    .stat-matrix-table td {
        padding: 6px 8px;
        border: 1px solid rgba(56, 189, 248, 0.1);
        text-align: center;
        color: #e2e8f0;
        background: rgba(9, 14, 28, 0.5);
    }
    .stat-matrix-table tr:hover td {
        background: rgba(56, 189, 248, 0.08);
    }
    .stat-hl {
        color: #38bdf8 !important;
        font-weight: 700;
    }

    /* 스킬 카드 디자인 */
    .skill-card-sig {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.08) 0%, rgba(11, 18, 33, 0.85) 100%);
        border: 1px solid rgba(245, 158, 11, 0.35);
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 10px;
    }
    .skill-card-inherit {
        background: rgba(9, 14, 28, 0.7);
        border: 1px solid rgba(56, 189, 248, 0.15);
        border-radius: 6px;
        padding: 8px 12px;
        margin-bottom: 6px;
    }
    .skill-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 4px;
        flex-wrap: wrap;
        gap: 6px;
    }
    .skill-name {
        font-size: 0.9rem;
        font-weight: 700;
        color: #ffffff;
    }
    .skill-desc {
        font-size: 0.76rem;
        color: #cbd5e1;
        line-height: 1.45;
    }
    .skill-badge-sig {
        background: rgba(245, 158, 11, 0.2);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.4);
        font-size: 0.65rem;
        font-family: 'Orbitron', monospace;
        padding: 2px 6px;
        border-radius: 4px;
    }
    .skill-badge-lv {
        background: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.3);
        font-size: 0.68rem;
        font-family: 'Orbitron', monospace;
        font-weight: 700;
        padding: 2px 6px;
        border-radius: 4px;
    }
    .skill-props {
        display: inline-flex;
        gap: 6px;
        font-family: 'Orbitron', monospace;
        font-size: 0.68rem;
        color: #94a3b8;
    }

    .mech-guide-box {
        background: rgba(30, 41, 59, 0.35);
        border-left: 3px solid #38bdf8;
        border-radius: 0 6px 6px 0;
        padding: 10px 14px;
        margin-top: 12px;
        font-size: 0.74rem;
        color: #94a3b8;
        line-height: 1.55;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. 세션 상태 기본값 초기화 (기본 언어: EN) ---
if 'lang' not in st.session_state:
    st.session_state.lang = "EN"
if 'blocked_list' not in st.session_state:
    st.session_state.blocked_list = []
if 'exclude_hm' not in st.session_state:
    st.session_state.exclude_hm = False
if 'exclude_nx' not in st.session_state:
    st.session_state.exclude_nx = False

# --- 5. 초상화 이미지 캐시 로더 ---
@st.cache_data
def get_digimon_img_data(name):
    slug = name.lower()
    slug = re.sub(r'\(blk\)', 'black', slug)
    slug = re.sub(r'\(blue\)', 'blue', slug)
    slug = re.sub(r'[^a-z0-9]+', '-', slug).strip('-')
    
    local_path = os.path.join(BASE_DIR, "assets", "portraits", f"{slug}.png")
    if os.path.exists(local_path):
        with open(local_path, "rb") as img_f:
            b64 = base64.b64encode(img_f.read()).decode('utf-8')
            return f"data:image/png;base64,{b64}"
            
    return f"https://www.grindosaur.com/img/games/digimon-story-cyber-sleuth/icons/{slug}-icon.png"

def safe_int(val):
    if pd.isna(val) or val is None: return 0
    val_str = str(val).replace('%', '').strip()
    try: return int(float(val_str))
    except ValueError: return 0

# --- 6. 엑셀 데이터 로딩 & 공식 진화 필요 레벨, 스펙, 스킬 매핑 ---
@st.cache_data
def load_all_data():
    df_evo = pd.read_csv(os.path.join(BASE_DIR, 'Digivolutions.xls'), sep=';').dropna(subset=['Digivolves from', 'Digivolves to'])
    df_digimon = pd.read_csv(os.path.join(BASE_DIR, 'Digimon.xls'), sep=';')
    df_req = pd.read_csv(os.path.join(BASE_DIR, 'Digivolution Requirements.xls'), sep=';')
    df_skills = pd.read_csv(os.path.join(BASE_DIR, 'Skills.xls'), sep=';')
    df_sbd = pd.read_csv(os.path.join(BASE_DIR, 'Skills by Digimon.xls'), sep=';')
    
    stage_map = dict(zip(df_digimon['Digimon'], df_digimon['Stage']))
    attr_map = dict(zip(df_digimon['Digimon'], df_digimon['Attribute']))
    
    req_map = {}
    hm_mon_set = set()
    for _, row in df_req.iterrows():
        digimon_name = str(row['Digimon']).strip()
        cond = str(row.get('Extra Condition', '')).strip() if pd.notna(row.get('Extra Condition')) and str(row.get('Extra Condition')).strip() != 'nan' else None
        if cond and 'hacker' in cond.lower():
            hm_mon_set.add(digimon_name)
            
        req_map[digimon_name] = {
            'Level': safe_int(row.get('Level')),
            'HP': safe_int(row.get('HP')),
            'SP': safe_int(row.get('SP')),
            'ATK': safe_int(row.get('ATK')),
            'DEF': safe_int(row.get('DEF')),
            'INT': safe_int(row.get('INT')),
            'SPD': safe_int(row.get('SPD')),
            'ABI': safe_int(row.get('ABI')),
            'CAM': safe_int(row.get('CAM')),
            'Extra': cond
        }
        
    nx_mon_set = set()
    digimon_stats = {}
    for _, row in df_digimon.iterrows():
        mon = str(row['Digimon']).strip()
        if 'nx' in mon.lower():
            nx_mon_set.add(mon)
            
        digimon_stats[mon] = {
            'Number': safe_int(row.get('Number')),
            'Stage': str(row.get('Stage', '')).strip(),
            'Type': str(row.get('Type', '')).strip(),
            'Attribute': str(row.get('Attribute', '')).strip(),
            'Memory': safe_int(row.get('Memory')),
            'Equip Slots': safe_int(row.get('Equip Slots')),
            'lv1': {
                'HP': safe_int(row.get('HP lvl 1')), 'SP': safe_int(row.get('SP lvl 1')),
                'ATK': safe_int(row.get('ATK lvl 1')), 'DEF': safe_int(row.get('DEF lvl 1')),
                'INT': safe_int(row.get('INT lvl 1')), 'SPD': safe_int(row.get('SPD lvl 1'))
            },
            'lv50': {
                'HP': safe_int(row.get('HP lvl 50')), 'SP': safe_int(row.get('SP lvl 50')),
                'ATK': safe_int(row.get('ATK lvl 50')), 'DEF': safe_int(row.get('DEF lvl 50')),
                'INT': safe_int(row.get('INT lvl 50')), 'SPD': safe_int(row.get('SPD lvl 50'))
            },
            'lv99': {
                'HP': safe_int(row.get('HP lvl 99')), 'SP': safe_int(row.get('SP lvl 99')),
                'ATK': safe_int(row.get('ATK lvl 99')), 'DEF': safe_int(row.get('DEF lvl 99')),
                'INT': safe_int(row.get('INT lvl 99')), 'SPD': safe_int(row.get('SPD lvl 99'))
            }
        }
    
    skills_dict = {}
    for _, row in df_skills.iterrows():
        s_clean = str(row['Skill']).strip().replace("'", "").replace('"', '')
        skills_dict[s_clean.lower()] = {
            'name': s_clean,
            'sp': safe_int(row.get('SP Cost')),
            'type': str(row.get('Type', '')).strip(),
            'power': safe_int(row.get('Power')),
            'attr': str(row.get('Attribute', '')).strip(),
            'inheritable': str(row.get('Inheritable', '')).strip().lower() == 'yes',
            'desc': str(row.get('Description', '')).strip()
        }

    typo_map = {
        'commet hammer ii': 'comet hammer ii',
        'chronobreaker': 'chrono breaker'
    }

    digimon_skills = {}
    for _, row in df_sbd.iterrows():
        mon = str(row['Digimon']).strip()
        raw_sname = str(row['Skill']).strip().replace("'", "").replace('"', '').lower()
        clean_sname = typo_map.get(raw_sname, raw_sname)
        sk_info = skills_dict.get(clean_sname, {
            'name': str(row['Skill']).strip(), 'sp': 0, 'type': 'Unknown', 'power': 0,
            'attr': 'Neutral', 'inheritable': False, 'desc': ''
        })
        lv = safe_int(row.get('Level'))
        if mon not in digimon_skills:
            digimon_skills[mon] = {'signature': [], 'inheritable': []}
        if sk_info['inheritable']:
            digimon_skills[mon]['inheritable'].append((lv, sk_info))
        else:
            digimon_skills[mon]['signature'].append((lv, sk_info))
    
    g_undirected = {}
    digimon_set = set()
    for _, row in df_evo.iterrows():
        src = str(row['Digivolves from']).strip()
        dst = str(row['Digivolves to']).strip()
        digimon_set.update([src, dst])
        if src not in g_undirected: g_undirected[src] = []
        if dst not in g_undirected: g_undirected[dst] = []
        g_undirected[src].append((dst, 'Evolve'))
        g_undirected[dst].append((src, 'Devolve'))
        
    return sorted(list(digimon_set)), stage_map, attr_map, req_map, g_undirected, digimon_stats, digimon_skills, hm_mon_set, nx_mon_set

all_digimon_list, stage_map, attr_map, req_map, g_undirected, digimon_stats, digimon_skills, hm_mon_set, nx_mon_set = load_all_data()

STAGE_MIN_LEVELS = {
    'Baby': 1, 'In-Training': 5, 'Rookie': 9, 'Champion': 15,
    'Ultimate': 28, 'Mega': 50, 'Ultra': 65, 'Armor': 14
}

def get_evolution_level_cost(mon, stage_map, req_map):
    req = req_map.get(mon, {})
    lv = req.get('Level', 0)
    if lv > 0:
        return lv
    stg = stage_map.get(mon, 'Rookie')
    return STAGE_MIN_LEVELS.get(stg, 10)

def find_optimal_path(graph, start, target, stage_map, req_map, blocked_total_set=set()):
    pq = [(0, start, [(start, 'Start', 0)])]
    visited = {}
    while pq:
        cost, curr, path = heapq.heappop(pq)
        if curr in visited and visited[curr] <= cost: continue
        visited[curr] = cost
        if curr == target: return cost, path
        for nxt, move_type in graph.get(curr, []):
            if nxt in blocked_total_set and nxt != target: continue
            edge_cost = 1 if move_type == 'Devolve' else get_evolution_level_cost(nxt, stage_map, req_map)
            new_cost = cost + edge_cost
            if nxt not in visited or new_cost < visited[nxt]:
                heapq.heappush(pq, (new_cost, nxt, path + [(nxt, move_type, edge_cost)]))
    return None, None

def ban_digimon(mon_name):
    if mon_name not in st.session_state.blocked_list:
        st.session_state.blocked_list.append(mon_name)

def unban_digimon(mon_name):
    if mon_name in st.session_state.blocked_list:
        st.session_state.blocked_list.remove(mon_name)

def reset_blocked():
    st.session_state.blocked_list = []

# --- 7. 사이드바 구성 ---
def on_lang_change():
    val = st.session_state.get("lang_radio_widget", "English (EN)")
    st.session_state.lang = "KO" if "KO" in val else "EN"
    sync_selectboxes()

cur_lang_idx = 0 if st.session_state.lang == "KO" else 1
st.sidebar.radio(
    "🌐 LANGUAGE",
    ["한국어 (KO)", "English (EN)"],
    index=cur_lang_idx,
    key="lang_radio_widget",
    on_change=on_lang_change
)
st.session_state.lang = "KO" if "KO" in st.session_state.get("lang_radio_widget", "English (EN)") else "EN"
L = LOCALE_TEXT.get(st.session_state.lang, LOCALE_TEXT["EN"])

# 필터 옵션 (Hacker's Memory & NX Digimon)
st.sidebar.markdown(f"<div style='font-family:Orbitron; font-size:0.85rem; font-weight:800; color:#38bdf8; letter-spacing:1px; margin-top:16px;'>{L['filter_title']}</div>", unsafe_allow_html=True)
exclude_hm = st.sidebar.checkbox(L['filter_exclude_hm'], value=st.session_state.exclude_hm, key='exclude_hm_cb')
exclude_nx = st.sidebar.checkbox(L['filter_exclude_nx'], value=st.session_state.exclude_nx, key='exclude_nx_cb')
st.session_state.exclude_hm = exclude_hm
st.session_state.exclude_nx = exclude_nx

# 필터 적용된 디지몬 목록 계산
excluded_filter_set = set()
if exclude_hm:
    excluded_filter_set.update(hm_mon_set)
if exclude_nx:
    excluded_filter_set.update(nx_mon_set)

digimon_list = [m for m in all_digimon_list if m not in excluded_filter_set]

# 출발 / 목표 디지몬 영속 세션 상태 관리
if "start_mon" not in st.session_state or st.session_state.start_mon not in digimon_list:
    st.session_state.start_mon = "Keramon" if "Keramon" in digimon_list else digimon_list[0]
if "target_mon" not in st.session_state or st.session_state.target_mon not in digimon_list:
    st.session_state.target_mon = "Angewomon" if "Angewomon" in digimon_list else digimon_list[1]

def sync_selectboxes():
    s = st.session_state.start_mon
    t = st.session_state.target_mon
    for lg in ["KO", "EN"]:
        st.session_state[f"sb_start_{lg}"] = s
        st.session_state[f"sb_target_{lg}"] = t

def on_start_change():
    k = f"sb_start_{st.session_state.lang}"
    if k in st.session_state:
        st.session_state.start_mon = st.session_state[k]
        sync_selectboxes()

def on_target_change():
    k = f"sb_target_{st.session_state.lang}"
    if k in st.session_state:
        st.session_state.target_mon = st.session_state[k]
        sync_selectboxes()

def swap_selected_mon():
    s = st.session_state.start_mon
    t = st.session_state.target_mon
    st.session_state.start_mon = t
    st.session_state.target_mon = s
    sync_selectboxes()

# 차단 목록 (사이드바)
st.sidebar.markdown(f"<div style='font-family:Orbitron; font-size:0.85rem; font-weight:800; color:#38bdf8; letter-spacing:1px; margin-top:20px;'>{L['sidebar_title']}</div>", unsafe_allow_html=True)
st.sidebar.markdown(f"<div style='font-size:0.75rem; color:#64748b; margin-bottom:12px;'>{L['sidebar_desc']}</div>", unsafe_allow_html=True)

if st.session_state.blocked_list:
    for b_mon in list(st.session_state.blocked_list):
        b_name = f"{KO_NAME_DICT.get(b_mon, b_mon)}" if st.session_state.lang == "KO" else b_mon
        b_img = get_digimon_img_data(b_mon)
        
        sb1, sb2 = st.sidebar.columns([4, 2])
        with sb1:
            st.markdown(
                f"<div class='ban-item-card'>"
                f"<img src='{b_img}' style='width:24px; height:24px; border-radius:4px;'>"
                f"<div style='font-size:0.8rem; font-weight:600; color:#e2e8f0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;'>{b_name}</div>"
                f"</div>",
                unsafe_allow_html=True
            )
        with sb2:
            st.button(L["unban_btn"], key=f"unban_sb_{b_mon}", on_click=unban_digimon, args=(b_mon,), use_container_width=True)
            
    st.sidebar.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    st.sidebar.button(L["reset_btn"], on_click=reset_blocked, use_container_width=True)
else:
    st.sidebar.info(L["sidebar_empty"])

# --- 8. 메인 헤더 배너 (동적 유닛 개수 표기) ---
online_tag_text = L['status_online'].format(count=len(digimon_list))
st.markdown(f"""
<div class="cyber-banner">
    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
        <div>
            <div class="cyber-title">{L['sys_title']}</div>
            <div class="cyber-sub">{L['sys_sub']}</div>
        </div>
        <div class="cyber-tag">{online_tag_text}</div>
    </div>
</div>
""", unsafe_allow_html=True)

def format_mon_display(mon):
    if st.session_state.lang == "KO":
        ko = KO_NAME_DICT.get(mon, mon)
        return f"{ko} ({mon})" if ko != mon else mon
    else:
        return mon

# --- 9. 검색 및 선택 덱 (Search Deck) ---
sync_selectboxes()
col_start, col_swap, col_target = st.columns([10, 1.8, 10], vertical_alignment="center")

start_idx = digimon_list.index(st.session_state.start_mon) if st.session_state.start_mon in digimon_list else 0
target_idx = digimon_list.index(st.session_state.target_mon) if st.session_state.target_mon in digimon_list else 1

with col_start:
    st.selectbox(
        L["start_label"],
        digimon_list,
        index=start_idx,
        format_func=format_mon_display,
        key=f"sb_start_{st.session_state.lang}",
        on_change=on_start_change
    )

with col_swap:
    st.markdown('<div class="swap-btn-wrap">', unsafe_allow_html=True)
    st.button("⇄", on_click=swap_selected_mon, help=L["swap_tooltip"], use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_target:
    st.selectbox(
        L["target_label"],
        digimon_list,
        index=target_idx,
        format_func=format_mon_display,
        key=f"sb_target_{st.session_state.lang}",
        on_change=on_target_change
    )

# --- 10. 유닛 스펙 & 스킬 정보 렌더러 ---
def render_digimon_details(mon):
    stats = digimon_stats.get(mon, {})
    skills = digimon_skills.get(mon, {'signature': [], 'inheritable': []})
    
    stg_raw = stats.get('Stage', stage_map.get(mon, 'Unknown'))
    attr_raw = stats.get('Attribute', attr_map.get(mon, 'Neutral'))
    type_raw = stats.get('Type', 'Unknown')
    
    stg_text = L['stage'].get(stg_raw, stg_raw)
    attr_text = L['attr'].get(attr_raw, attr_raw)
    mem = stats.get('Memory', 0)
    slots = stats.get('Equip Slots', 0)
    
    # 1. 메타 태그 바
    meta_html = (
        f'<div class="spec-meta-wrap">'
        f'<div class="spec-meta-chip"><div class="spec-meta-label">{L["type_label"]}</div><div class="spec-meta-val">{type_raw}</div></div>'
        f'<div class="spec-meta-chip"><div class="spec-meta-label">{L["memory_label"]}</div><div class="spec-meta-val">{mem} <span style="font-size:0.65rem; color:#64748b;">MEM</span></div></div>'
        f'<div class="spec-meta-chip"><div class="spec-meta-label">{L["equip_label"]}</div><div class="spec-meta-val">{slots} <span style="font-size:0.65rem; color:#64748b;">SLOTS</span></div></div>'
        f'</div>'
    )
    
    # 2. 기본 스탯 매트릭스 (Lv 1, 50, 99)
    lv1 = stats.get('lv1', {})
    lv50 = stats.get('lv50', {})
    lv99 = stats.get('lv99', {})
    
    stats_table_html = (
        f'<div style="font-family:Orbitron; font-size:0.75rem; font-weight:700; color:#38bdf8; margin:10px 0 6px 0;">{L["stats_title"]}</div>'
        f'<table class="stat-matrix-table">'
        f'<thead><tr><th>LEVEL</th><th>HP</th><th>SP</th><th>ATK</th><th>DEF</th><th>INT</th><th>SPD</th></tr></thead>'
        f'<tbody>'
        f'<tr><td>Lv. 01</td><td>{lv1.get("HP", 0)}</td><td>{lv1.get("SP", 0)}</td><td>{lv1.get("ATK", 0)}</td><td>{lv1.get("DEF", 0)}</td><td>{lv1.get("INT", 0)}</td><td>{lv1.get("SPD", 0)}</td></tr>'
        f'<tr><td>Lv. 50</td><td class="stat-hl">{lv50.get("HP", 0)}</td><td class="stat-hl">{lv50.get("SP", 0)}</td><td class="stat-hl">{lv50.get("ATK", 0)}</td><td class="stat-hl">{lv50.get("DEF", 0)}</td><td class="stat-hl">{lv50.get("INT", 0)}</td><td class="stat-hl">{lv50.get("SPD", 0)}</td></tr>'
        f'<tr><td>Lv. 99</td><td class="stat-hl" style="color:#67e8f9 !important;">{lv99.get("HP", 0)}</td><td class="stat-hl" style="color:#67e8f9 !important;">{lv99.get("SP", 0)}</td><td class="stat-hl" style="color:#67e8f9 !important;">{lv99.get("ATK", 0)}</td><td class="stat-hl" style="color:#67e8f9 !important;">{lv99.get("DEF", 0)}</td><td class="stat-hl" style="color:#67e8f9 !important;">{lv99.get("INT", 0)}</td><td class="stat-hl" style="color:#67e8f9 !important;">{lv99.get("SPD", 0)}</td></tr>'
        f'</tbody></table>'
    )
    
    # 3. 고유 필살기 (Signature Special Skill)
    sig_html = ""
    if skills['signature']:
        sig_items = []
        for lv, s in skills['signature']:
            pwr_str = f"PWR {s['power']}" if s['power'] > 0 else "SUPPORT"
            sp_str = f"SP {s['sp']}" if s['sp'] > 0 else "SP 0"
            attr_elem = L['attr'].get(s['attr'], s['attr'])
            sig_items.append(
                f'<div class="skill-card-sig">'
                f'<div class="skill-header">'
                f'<div><span class="skill-name">{s["name"]}</span> <span class="skill-badge-sig">{L["sig_skill_badge"]}</span></div>'
                f'<div class="skill-props"><span>{s["type"]}</span> • <span>{attr_elem}</span> • <span>{pwr_str}</span> • <span>{sp_str}</span></div>'
                f'</div>'
                f'<div class="skill-desc">{s["desc"]}</div>'
                f'</div>'
            )
        sig_html = f'<div style="font-family:Orbitron; font-size:0.75rem; font-weight:700; color:#fbbf24; margin:10px 0 6px 0;">{L["sig_skill_title"]}</div>' + "".join(sig_items)
    
    # 4. 레벨별 습득 계승기 (Inheritable Skills by Level)
    inherit_html = ""
    if skills['inheritable']:
        inh_items = []
        sorted_inh = sorted(skills['inheritable'], key=lambda x: x[0])
        for lv, s in sorted_inh:
            pwr_str = f"PWR {s['power']}" if s['power'] > 0 else "SUPPORT"
            sp_str = f"SP {s['sp']}" if s['sp'] > 0 else "SP 0"
            attr_elem = L['attr'].get(s['attr'], s['attr'])
            inh_items.append(
                f'<div class="skill-card-inherit">'
                f'<div class="skill-header">'
                f'<div><span class="skill-badge-lv">Lv.{lv:02d}</span> <span class="skill-name" style="font-size:0.85rem;">{s["name"]}</span> <span class="hud-badge" style="background:rgba(56,189,248,0.1); color:#7dd3fc; font-size:0.65rem;">{s["type"]}</span> <span class="hud-badge" style="background:rgba(148,163,184,0.1); color:#94a3b8; font-size:0.65rem;">{attr_elem}</span></div>'
                f'<div class="skill-props"><span>{pwr_str}</span> • <span>{sp_str}</span></div>'
                f'</div>'
                f'<div class="skill-desc">{s["desc"]}</div>'
                f'</div>'
            )
        inherit_html = f'<div style="font-family:Orbitron; font-size:0.75rem; font-weight:700; color:#38bdf8; margin:12px 0 6px 0;">{L["inherit_skills_title"]}</div>' + "".join(inh_items)
    
    # 5. 스킬 계승 메커니즘 안내
    guide_html = (
        f'<div class="mech-guide-box">'
        f'<div style="font-weight:700; color:#38bdf8; margin-bottom:3px;">{L["skill_mech_title"]}</div>'
        f'{L["skill_mech_desc"]}'
        f'</div>'
    )
    
    full_html = f'<div style="padding:4px 2px;">{meta_html}{stats_table_html}{sig_html}{inherit_html}{guide_html}</div>'
    st.markdown(full_html, unsafe_allow_html=True)

# --- 11. 경로 연산 및 렌더링 ---
start_mon = st.session_state.start_mon
target_mon = st.session_state.target_mon

if start_mon == target_mon:
    st.warning(L["same_alert"])
else:
    blocked_total_set = set(st.session_state.blocked_list).union(excluded_filter_set)
    cost_opt, path_opt = find_optimal_path(g_undirected, start_mon, target_mon, stage_map, req_map, blocked_total_set)
    
    if path_opt:
        evo_count = sum(1 for _, move, _ in path_opt if move == "Evolve")
        dev_count = sum(1 for _, move, _ in path_opt if move == "Devolve")
        total_steps = len(path_opt) - 1

        # 텔레메트리 요약 바
        st.markdown(f"""
        <div class="telemetry-board">
            <div class="tele-item">
                <div class="tele-title">{L['total_steps'].upper()}</div>
                <div class="tele-val">{total_steps:02d} <span style="font-size:0.8rem; color:#64748b;">{L['steps_unit']}</span></div>
            </div>
            <div class="tele-item">
                <div class="tele-title">{L['effort_score'].upper()}</div>
                <div class="tele-val">{cost_opt:02d} <span style="font-size:0.8rem; color:#64748b;">{L['score_unit']}</span></div>
            </div>
            <div class="tele-item">
                <div class="tele-title">{L['flow_breakdown'].upper()}</div>
                <div class="tele-sub" style="font-family:'Orbitron', monospace; font-size:0.85rem; font-weight:700; color:#e2e8f0; margin-top:5px;">
                    {L['flow_fmt'].format(evo=evo_count, dev=dev_count)}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        def get_stage_cls(stg):
            if stg in ['Baby', 'In-Training']: return 'stg-baby'
            if stg == 'Rookie': return 'stg-rookie'
            if stg == 'Champion': return 'stg-champion'
            if stg == 'Ultimate': return 'stg-ultimate'
            if stg == 'Mega': return 'stg-mega'
            if stg in ['Ultra', 'Armor']: return 'stg-ultra'
            return 'stg-unknown'

        def get_attr_cls(attr):
            if attr == 'Vaccine': return 'attr-vac'
            if attr == 'Data': return 'attr-data'
            if attr == 'Virus': return 'attr-vir'
            return 'attr-free'

        fallback_svg = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='48' height='48' viewBox='0 0 24 24' fill='none' stroke='%2338bdf8' stroke-width='2'%3E%3Crect width='18' height='18' x='3' y='3' rx='2'/%3E%3Ccircle cx='9' cy='9' r='2'/%3E%3Cpath d='m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21'/%3E%3C/svg%3E"

        # 타임라인 카드 및 스펙/스킬 확장 렌더링
        for idx, (mon, move, c) in enumerate(path_opt):
            raw_stg = stage_map.get(mon, 'Unknown')
            raw_attr = attr_map.get(mon, 'Neutral')
            stg = L["stage"].get(raw_stg, raw_stg)
            attr = L["attr"].get(raw_attr, raw_attr)
            
            d_name = KO_NAME_DICT.get(mon, mon) if st.session_state.lang == "KO" else mon
            sub_name = f"{mon}" if st.session_state.lang == "KO" and mon in KO_NAME_DICT else ""
            img_url = get_digimon_img_data(mon)
            
            stage_cls = get_stage_cls(raw_stg)
            attr_cls = get_attr_cls(raw_attr)

            # 연결선
            if idx > 0:
                st.markdown('<div class="circuit-link"><div class="circuit-beam"></div><div class="circuit-dot"></div></div>', unsafe_allow_html=True)

            # 스탯 요구치 칩
            req_pills_html = ""
            if move == "Evolve":
                req = req_map.get(mon, {})
                stat_pills = []
                for k in ['Level', 'HP', 'SP', 'ATK', 'DEF', 'INT', 'SPD', 'ABI']:
                    if req.get(k, 0) > 0:
                        stat_pills.append(f'<span class="stat-pill"><span class="stat-k">{k.upper()}</span><span class="stat-v">{req[k]}</span></span>')
                if req.get('CAM', 0) > 0:
                    stat_pills.append(f'<span class="stat-pill"><span class="stat-k">CAM</span><span class="stat-v">{req["CAM"]}%</span></span>')
                
                req_pills_html = "".join(stat_pills)
                if req.get('Extra'):
                    req_pills_html += f'<span class="stat-pill stat-extra"><span class="stat-k">REQ</span><span class="stat-v">{req["Extra"]}</span></span>'
                if req_pills_html:
                    req_pills_html = f'<div class="stat-bar">{req_pills_html}</div>'

            cost_label = f"+{c} LV" if move == "Evolve" else "+1 STEP"

            # 0번: 시작 지점 카드
            if idx == 0:
                card_html = (
                    f'<div class="node-card node-start">'
                    f'<div class="node-idx">00</div>'
                    f'<div class="digi-thumb-wrap">'
                    f'<img src="{img_url}" class="digi-thumb-img" onerror="this.onerror=null;this.src=\'{fallback_svg}\';">'
                    f'</div>'
                    f'<div style="flex-grow:1;">'
                    f'<div>'
                    f'<span class="action-tag action-origin">{L["start_point"]}</span>'
                    f'<span class="mon-name-main">{d_name}</span>'
                    f'<span class="mon-name-en">{sub_name}</span>'
                    f'<span class="hud-badge {stage_cls}">{stg}</span> '
                    f'<span class="hud-badge {attr_cls}">{attr}</span>'
                    f'</div>'
                    f'</div>'
                    f'<div style="font-family:\'Orbitron\', monospace; font-size:0.75rem; color:#38bdf8; font-weight:700;">START</div>'
                    f'</div>'
                )
                st.markdown(card_html, unsafe_allow_html=True)
                with st.expander(f"📊 {d_name} // {L['specs_expander']}"):
                    render_digimon_details(mon)

            # 1번 이후: 진화 / 퇴화 카드
            else:
                action_label = L["evolve"] if move == "Evolve" else L["devolve"]
                action_cls = "action-evo" if move == "Evolve" else "action-dev"
                node_cls = "node-evo" if move == "Evolve" else "node-dev"

                if move == "Devolve":
                    card_col, btn_col = st.columns([6.2, 1.2])
                    with card_col:
                        card_html = (
                            f'<div class="node-card {node_cls}">'
                            f'<div class="node-idx">{idx:02d}</div>'
                            f'<div class="digi-thumb-wrap">'
                            f'<img src="{img_url}" class="digi-thumb-img" onerror="this.onerror=null;this.src=\'{fallback_svg}\';">'
                            f'</div>'
                            f'<div style="flex-grow:1;">'
                            f'<div>'
                            f'<span class="action-tag {action_cls}">{action_label}</span>'
                            f'<span class="mon-name-main">{d_name}</span>'
                            f'<span class="mon-name-en">{sub_name}</span>'
                            f'<span class="hud-badge {stage_cls}">{stg}</span> '
                            f'<span class="hud-badge {attr_cls}">{attr}</span>'
                            f'</div>'
                            f'{req_pills_html}'
                            f'</div>'
                            f'<div style="font-family:\'Orbitron\', monospace; font-size:0.75rem; color:#64748b; font-weight:700;">{cost_label}</div>'
                            f'</div>'
                        )
                        st.markdown(card_html, unsafe_allow_html=True)

                    with btn_col:
                        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
                        st.button(L["ban_btn"], key=f"ban_{mon}_{idx}", on_click=ban_digimon, args=(mon,), use_container_width=True)

                else:
                    card_html = (
                        f'<div class="node-card {node_cls}">'
                        f'<div class="node-idx">{idx:02d}</div>'
                        f'<div class="digi-thumb-wrap">'
                        f'<img src="{img_url}" class="digi-thumb-img" onerror="this.onerror=null;this.src=\'{fallback_svg}\';">'
                        f'</div>'
                        f'<div style="flex-grow:1;">'
                        f'<div>'
                        f'<span class="action-tag {action_cls}">{action_label}</span>'
                        f'<span class="mon-name-main">{d_name}</span>'
                        f'<span class="mon-name-en">{sub_name}</span>'
                        f'<span class="hud-badge {stage_cls}">{stg}</span> '
                        f'<span class="hud-badge {attr_cls}">{attr}</span>'
                        f'</div>'
                        f'{req_pills_html}'
                        f'</div>'
                        f'<div style="font-family:\'Orbitron\', monospace; font-size:0.75rem; color:#64748b; font-weight:700;">{cost_label}</div>'
                        f'</div>'
                    )
                    st.markdown(card_html, unsafe_allow_html=True)

                with st.expander(f"📊 {d_name} // {L['specs_expander']}"):
                    render_digimon_details(mon)

    else:
        st.error(L["no_path"])