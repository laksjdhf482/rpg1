import streamlit as st
import time
import math
import io
import wave
import base64
import streamlit.components.v1 as components

st.set_page_config(
    page_title="거지 탈출 RPG",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ============================================================
# 게임 설정
# ============================================================

STAGES = [
    ("시골 탈출", "시골", 1_000_000, "🌾"),
    ("길거리 탈출", "길거리 인도", 5_000_000, "🚶"),
    ("서울역 탈출", "서울역", 50_000_000, "🚉"),
    ("반지하 탈출", "반지하", 250_000_000, "🏠"),
    ("1층집 탈출", "지방 도시의 아파트", 1_250_000_000, "🏢"),
]

# 상점은 딱 2개만 사용
SHOP_ITEMS = [
    ("돈 증가", "클릭당 수입 +1,000원", "money"),
    ("클릭 더블", "한 번 클릭하면 2번 클릭한 것으로 적용", "double"),
]

# ============================================================
# 효과음
# ============================================================

def make_coin_sound():
    sample_rate = 44100
    duration = 0.16
    frames = bytearray()

    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        f1 = 880 * (1 - 0.15 * t / duration)
        f2 = 1320 * (1 - 0.20 * t / duration)
        envelope = math.exp(-16 * t)

        sample = int(
            0.24 * 32767 * envelope *
            (
                math.sin(2 * math.pi * f1 * t)
                + 0.45 * math.sin(2 * math.pi * f2 * t)
            )
        )
        sample = max(-32768, min(32767, sample))
        frames += int(sample).to_bytes(2, "little", signed=True)

    output = io.BytesIO()
    with wave.open(output, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(frames)

    return output.getvalue()


SOUND = make_coin_sound()
SOUND_B64 = base64.b64encode(SOUND).decode()

# ============================================================
# 상태
# ============================================================

def init_game():
    defaults = {
        "money": 0,
        "stage": 0,
        "click_power": 1_000,
        "double_click": False,
        "shop_levels": [0, 0],
        "shop_open": False,
        "notice": "",
        "floating_text": "",
        "sound": False,
        "clear": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_game():
    st.session_state.money = 0
    st.session_state.stage = 0
    st.session_state.click_power = 1_000
    st.session_state.double_click = False
    st.session_state.shop_levels = [0, 0]
    st.session_state.shop_open = False
    st.session_state.notice = ""
    st.session_state.floating_text = ""
    st.session_state.sound = False
    st.session_state.clear = False


init_game()

# ============================================================
# 계산
# ============================================================

def money_text(value):
    return f"{value:,}원"


def upgrade_cost(level):
    return int(1000 * (1.5 ** level))


def click_income():
    multiplier = 2 if st.session_state.double_click else 1
    return st.session_state.click_power * multiplier


def do_click():
    earned = click_income()
    st.session_state.money += earned
    st.session_state.floating_text = f"+{money_text(earned)}"
    st.session_state.sound = True
    st.session_state.notice = ""

    goal = STAGES[st.session_state.stage][2]

    if st.session_state.money >= goal:
        if st.session_state.stage < len(STAGES) - 1:
            st.session_state.stage += 1
            next_name = STAGES[st.session_state.stage][0]
            st.session_state.notice = f"STAGE CLEAR! → {next_name}"
        else:
            st.session_state.clear = True
            st.session_state.notice = "최종 탈출 성공!"


def buy_upgrade(index):
    level = st.session_state.shop_levels[index]
    cost = upgrade_cost(level)

    if st.session_state.money < cost:
        st.session_state.notice = "돈이 부족합니다"
        return

    st.session_state.money -= cost
    st.session_state.shop_levels[index] += 1

    if index == 0:
        st.session_state.click_power += 1_000
        st.session_state.notice = "돈 증가 업그레이드 완료!"
    else:
        st.session_state.double_click = True
        st.session_state.notice = "클릭 더블 업그레이드 완료!"


# ============================================================
# 모바일 최적화 CSS
# ============================================================

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Jua&display=swap');

html, body, [class*="css"] {
    font-family: 'Jua', sans-serif;
}

#MainMenu, footer, header {
    visibility: hidden;
}

.stApp {
    background: linear-gradient(#f5e7c8, #e5cfa3);
    min-height: 100vh;
}

.block-container {
    max-width: 600px !important;
    padding: 10px 12px 18px !important;
}

/* 전체 화면에서 세로 공간 절약 */
.game-title {
    text-align: center;
    font-size: clamp(28px, 8vw, 42px);
    line-height: 1;
    font-weight: 900;
    color: #3b3025;
    margin: 2px 0 3px;
}

.game-subtitle {
    text-align: center;
    font-size: clamp(11px, 3vw, 15px);
    color: #756451;
    margin-bottom: 7px;
}

.location-card {
    background: #fff9e9;
    border: 3px solid #44372b;
    border-radius: 15px;
    padding: 8px 10px;
    box-shadow: 3px 3px 0 #44372b;
    margin-bottom: 8px;
    text-align: center;
}

.location-name {
    font-size: clamp(18px, 5vw, 25px);
    font-weight: 900;
    color: #44372b;
}

.location-desc {
    font-size: clamp(10px, 2.8vw, 13px);
    color: #756451;
    line-height: 1.25;
}

.money-card {
    background: #fff9e9;
    border: 3px solid #44372b;
    border-radius: 15px;
    padding: 7px 10px;
    text-align: center;
    box-shadow: 3px 3px 0 #44372b;
    margin-bottom: 6px;
}

.money-label {
    font-size: 11px;
    color: #776752;
}

.money-value {
    font-size: clamp(27px, 8vw, 42px);
    line-height: 1.05;
    font-weight: 900;
    color: #3b3025;
}

.stat-row {
    display: flex;
    gap: 6px;
    margin: 6px 0;
}

.stat {
    flex: 1;
    background: #fff9e9;
    border: 2px solid #554536;
    border-radius: 10px;
    padding: 5px;
    text-align: center;
}

.stat-title {
    font-size: 9px;
    color: #806f5c;
}

.stat-value {
    font-size: clamp(12px, 3.5vw, 17px);
    font-weight: 900;
    color: #3d3025;
}

.click-area {
    background: #d5b98c;
    border: 3px solid #44372b;
    border-radius: 17px;
    padding: 7px 10px 10px;
    box-shadow: 3px 3px 0 #44372b;
    margin: 7px 0;
}

.floating {
    text-align: center;
    height: 26px;
    font-size: clamp(17px, 5vw, 25px);
    font-weight: 900;
    color: #b46a10;
    animation: fadeUp .9s ease-out forwards;
}

@keyframes fadeUp {
    0% { opacity: 1; transform: translateY(0); }
    100% { opacity: 0; transform: translateY(-18px); }
}

.click-guide {
    text-align: center;
    font-size: 10px;
    color: #5f4f3d;
    margin-bottom: 4px;
}

div.stButton > button {
    border: 2px solid #44372b;
    border-radius: 11px;
    font-family: 'Jua', sans-serif;
    font-weight: 900;
    min-height: 38px;
    padding: 4px 6px;
}

.click-button button {
    min-height: clamp(70px, 18vw, 105px) !important;
    font-size: clamp(22px, 7vw, 32px) !important;
    background: #f7c65d !important;
    box-shadow: 3px 3px 0 #44372b;
}

.click-button button:active {
    transform: translate(2px, 2px);
    box-shadow: 1px 1px 0 #44372b;
}

/* 오른쪽 하단 상점 버튼 */
.shop-floating {
    position: fixed;
    right: 14px;
    bottom: 14px;
    z-index: 999;
}

.shop-floating button {
    background: #f7c65d !important;
    border: 3px solid #44372b !important;
    border-radius: 50% !important;
    width: 68px !important;
    height: 68px !important;
    min-height: 68px !important;
    box-shadow: 4px 4px 0 #44372b !important;
    font-size: 15px !important;
}

.shop-panel {
    background: #fff9e9;
    border: 3px solid #44372b;
    border-radius: 16px;
    padding: 9px;
    margin-top: 7px;
    box-shadow: 3px 3px 0 #44372b;
}

.shop-panel-title {
    text-align: center;
    font-size: 20px;
    font-weight: 900;
    margin-bottom: 5px;
}

.shop-card {
    background: #f5e7c8;
    border: 2px solid #554536;
    border-radius: 11px;
    padding: 7px;
    margin: 5px 0;
}

.shop-name {
    font-size: 15px;
    font-weight: 900;
}

.shop-desc {
    font-size: 10px;
    color: #756451;
}

.notice {
    text-align: center;
    height: 22px;
    font-size: 12px;
    font-weight: 900;
    color: #a55708;
}

.clear-box {
    background: #fff2a8;
    border: 3px solid #44372b;
    border-radius: 15px;
    padding: 12px;
    text-align: center;
    font-size: 21px;
    font-weight: 900;
    margin: 7px 0;
}

.reset-area {
    margin-top: 5px;
}

/* 좁은 휴대전화 화면 */
@media (max-width: 420px) {
    .block-container {
        padding: 7px 8px 12px !important;
    }

    .game-subtitle {
        display: none;
    }

    .location-card {
        padding: 6px;
    }

    .click-area {
        margin: 5px 0;
    }

    .shop-floating {
        right: 9px;
        bottom: 9px;
    }

    .shop-floating button {
        width: 60px !important;
        height: 60px !important;
        min-height: 60px !important;
    }
}
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# 화면
# ============================================================

stage_name, place, goal, emoji = STAGES[st.session_state.stage]

st.markdown(
    '<div class="game-title">거지 탈출 RPG</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="game-subtitle">클릭해서 돈을 모으고 다음 장소로 탈출하자</div>',
    unsafe_allow_html=True,
)

st.markdown(
    f"""
<div class="location-card">
    <div class="location-name">
        {emoji} STAGE {st.session_state.stage + 1} · {stage_name}
    </div>
    <div class="location-desc">
        {place} · 목표 {money_text(goal)}
    </div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
<div class="money-card">
    <div class="money-label">현재 보유 금액</div>
    <div class="money-value">{money_text(st.session_state.money)}</div>
</div>
""",
    unsafe_allow_html=True,
)

progress = min(st.session_state.money / goal, 1.0)
st.progress(progress)

# 능력치
st.markdown(
    f"""
<div class="stat-row">
    <div class="stat">
        <div class="stat-title">클릭당 수입</div>
        <div class="stat-value">{money_text(st.session_state.click_power)}</div>
    </div>
    <div class="stat">
        <div class="stat-title">클릭 효과</div>
        <div class="stat-value">
            {"×2" if st.session_state.double_click else "×1"}
        </div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# 클릭 영역
st.markdown('<div class="click-area">', unsafe_allow_html=True)

if st.session_state.floating_text:
    st.markdown(
        f'<div class="floating">{st.session_state.floating_text}</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown('<div class="floating"></div>', unsafe_allow_html=True)

st.markdown(
    '<div class="click-guide">버튼을 누를 때마다 돈을 벌 수 있습니다</div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="click-button">', unsafe_allow_html=True)

if st.button(
    f"돈 벌기  +{money_text(click_income())}",
    use_container_width=True,
):
    do_click()
    st.rerun()

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# 효과음
if st.session_state.sound:
    st.audio(SOUND, format="audio/wav", autoplay=True)
    st.session_state.sound = False

# 안내
if st.session_state.notice:
    st.markdown(
        f'<div class="notice">{st.session_state.notice}</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown('<div class="notice"></div>', unsafe_allow_html=True)

# ============================================================
# 상점 버튼
# ============================================================

# Streamlit 기본 버튼을 고정 위치처럼 보이게 하기 위한 wrapper
st.markdown('<div class="shop-floating">', unsafe_allow_html=True)

if st.button("상점", key="shop_open_button"):
    st.session_state.shop_open = not st.session_state.shop_open
    st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# 상점
# ============================================================

if st.session_state.shop_open:
    st.markdown(
        """
<div class="shop-panel">
    <div class="shop-panel-title">상점</div>
</div>
""",
        unsafe_allow_html=True,
    )

    for i, (name, desc, item_type) in enumerate(SHOP_ITEMS):
        level = st.session_state.shop_levels[i]
        cost = upgrade_cost(level)

        # 클릭 더블은 한 번만 구매 가능
        if item_type == "double" and st.session_state.double_click:
            button_text = "구매 완료"
            disabled = True
        else:
            button_text = f"업그레이드 · {money_text(cost)}"
            disabled = False

        st.markdown(
            f"""
<div class="shop-card">
    <div class="shop-name">{name} · Lv.{level}</div>
    <div class="shop-desc">{desc}</div>
    <div class="shop-desc">다음 비용: <b>{money_text(cost)}</b></div>
</div>
""",
            unsafe_allow_html=True,
        )

        if st.button(
            button_text,
            key=f"upgrade_{i}",
            use_container_width=True,
            disabled=disabled,
        ):
            buy_upgrade(i)
            st.rerun()

# 초기화는 아주 작게
st.markdown('<div class="reset-area">', unsafe_allow_html=True)

if st.button("게임 초기화", use_container_width=True):
    reset_game()
    st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# 최종 클리어
if st.session_state.clear:
    st.markdown(
        """
<div class="clear-box">
    최종 탈출 성공!<br>
    12억 5천만 원 달성
</div>
""",
        unsafe_allow_html=True,
    )
