import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime
import os
import re
import json

st.set_page_config(
    page_title="Calm Corner Check-In",
    page_icon="🌟",
    layout="centered"
)

st.markdown("""
<style>
    .stApp { background: linear-gradient(160deg, #fef6ff 0%, #e8f4ff 100%); }
    .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
    .big-title {
        font-size: 2.8rem;
        font-weight: 900;
        text-align: center;
        color: #2c3e50;
        padding: 10px 0 5px 0;
        line-height: 1.2;
        width: 100%;
        display: block;
    }
    .sub-title {
        font-size: 1.3rem;
        text-align: center;
        color: #555;
        margin-bottom: 25px;
    }
    .zone-card {
        border-radius: 18px;
        padding: 18px 12px;
        text-align: center;
        margin-bottom: 10px;
    }
    .affirm-box {
        border-radius: 20px;
        padding: 25px;
        text-align: center;
        border: 3px solid #27ae60;
        background: #d5f5e3;
        margin-bottom: 20px;
    }
    .referral-card {
        border-radius: 18px;
        padding: 22px 16px;
        text-align: center;
        margin-bottom: 12px;
        cursor: pointer;
    }
    div[data-testid="stButton"] button {
        border-radius: 14px !important;
        font-size: 1.05rem !important;
        padding: 10px 16px !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

CONFIG_PATH = "data_ai/template_config.json"

# No groups pre-loaded — set them up via the Staff Dashboard > Program Settings
_DEFAULT_GROUPS = []


def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"password": "changeme", "groups": _DEFAULT_GROUPS}


def save_config(cfg):
    os.makedirs("data_ai", exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


def build_grade_to_groups(groups):
    gtg = {}
    for g in groups:
        for grade in g.get("grades", []):
            gtg.setdefault(grade, []).append(g["name"])
    return gtg


def build_group_colors(groups):
    return {g["name"]: {"bg": g["bg_color"], "text": g["text_color"]} for g in groups}


_cfg = load_config()
EDUCATOR_PASSWORD = _cfg["password"]
GRADE_TO_GROUPS = build_grade_to_groups(_cfg["groups"])
GROUP_COLORS = build_group_colors(_cfg["groups"])


def rec_group_button(label, key):
    colors = GROUP_COLORS.get(label, {"bg": "#e0e0e0", "text": "#333333"})
    bg, text = colors["bg"], colors["text"]
    is_selected = st.session_state.rec_group == label
    border = f"3px solid #2c3e50" if is_selected else (
        "2px solid #cccccc" if bg.upper() in ("#FFFFFF", "#FFF") else f"2px solid {bg}"
    )
    shadow = "box-shadow: 0 0 0 2px #2c3e50 !important;" if is_selected else ""
    marker = "rgm-" + re.sub(r"[^a-zA-Z0-9]", "-", key)
    st.markdown(
        f'<div id="{marker}"></div>'
        f'<style>'
        f'  .element-container:has(#{marker}) + .element-container button {{'
        f'    background-color: {bg} !important;'
        f'    color: {text} !important;'
        f'    border: {border} !important;'
        f'    {shadow}'
        f'  }}'
        f'  .element-container:has(#{marker}) + .element-container button:hover {{'
        f'    background-color: {bg} !important; color: {text} !important; opacity: 0.85 !important;'
        f'  }}'
        f'</style>',
        unsafe_allow_html=True,
    )
    return st.button(label, key=key, use_container_width=True)

for key, default in [
    ("step", 0),
    ("selected_zone", None),
    ("selected_feeling", None),
    ("selected_strategy", None),
    ("student_name", ""),
    ("grade", None),
    ("rec_group", ""),
    ("referral_type", None),
    ("specialist_notes", ""),
    ("checkin_start_time", None),
    ("notes_open", False),
    ("educator_authenticated", False),
    ("selected_student", None),
    ("editing_group", None),
    ("welcome_shown", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default


@st.dialog("👋 Welcome — Staff Setup")
def show_welcome():
    cfg = load_config()
    st.markdown(
        "<div style='font-size:1.05rem;'>To access the <strong>Staff Dashboard</strong>, "
        "open the sidebar and enter the staff password:</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div style='font-size:2rem;font-weight:900;text-align:center;"
        f"letter-spacing:4px;padding:14px;background:#f0f4ff;border-radius:12px;"
        f"border:2px solid #3498db;margin:14px 0;color:#2c3e50;'>{cfg['password']}</div>",
        unsafe_allow_html=True,
    )
    st.caption("Change this anytime in Staff Dashboard → Program Settings → Password.")
    if st.button("Got it! ✓", use_container_width=True, type="primary"):
        st.session_state.welcome_shown = True
        st.rerun()


if not st.session_state.welcome_shown:
    show_welcome()

# Auto-reset after 60 s of inactivity — reloads page = fresh session
components.html("""
<script>
(function() {
    var IDLE_MS = 60000;
    var timer;
    function reload() { window.parent.location.reload(); }
    function resetTimer() { clearTimeout(timer); timer = setTimeout(reload, IDLE_MS); }
    ['mousedown','mousemove','keydown','keyup','touchstart','click','scroll','wheel'].forEach(function(e) {
        try { window.parent.document.addEventListener(e, resetTimer, true); } catch(err) {}
    });
    resetTimer();
})();
</script>
""", height=0)

ZONES = {
    "🔵 Blue Zone": {
        "color": "#2980b9", "bg": "#d6eaf8", "border": "#3498db",
        "label": "Blue Zone", "hint": "Sad · Tired · Bored",
        "description": "Your body moves slow and feels low on energy.",
        "feelings": {
            "😴 Tired": [
                "🙆 Do 5 slow arm circles to wake your body up",
                "💧 Get a drink of water from the fountain",
                "🚶 Take a slow walk outside in the sunlight",
                "🫁 Take 3 deep breaths and sit up tall",
                "✏️ Draw or doodle something you like",
            ],
            "😢 Sad": [
                "🧸 Hold the comfort pillow — it's okay to feel sad",
                "✏️ Draw a picture of something that makes you happy",
                "🫁 Breathe in slowly through your nose, out through your mouth",
                "📖 Look through the calm corner picture cards",
                "✨ Watch the glitter bottle until it settles",
            ],
            "😑 Bored": [
                "🧩 Pick a calm corner activity — puzzle, coloring, or fidget toy",
                "✏️ Doodle or draw whatever comes to mind",
                "🚶 Walk one slow lap around campus to reset",
                "🎯 Set a small goal for the next 10 minutes",
                "📖 Flip through a book or picture cards",
            ],
            "🤒 Sick": [
                "🪑 Sit quietly with the pillow — rest your body",
                "💧 Take slow sips of water from the fountain",
                "🫁 Take slow, gentle breaths to help your body rest",
                "📖 Rest quietly and look through picture cards",
                "✨ Watch the glitter bottle and breathe slowly",
            ],
            "😶 Empty": [
                "🧸 Hug the comfort pillow — you don't have to do anything",
                "✨ Watch the glitter bottle until it fully settles",
                "🫁 Try box breathing — in 4, hold 4, out 4, hold 4",
                "✏️ Write or draw one small thing — anything at all",
                "🚶 Take a slow, quiet walk outside",
            ],
        },
    },
    "🟢 Green Zone": {
        "color": "#1e8449", "bg": "#d5f5e3", "border": "#27ae60",
        "label": "Green Zone", "hint": "Happy · Calm · Ready",
        "description": "Your body feels calm and just right.",
        "feelings": {
            "😊 Happy": [
                "⭐ Keep going — you're in a great spot!",
                "📝 Write down one thing that made you feel good today",
                "🎯 Set a fun goal for the rest of the day",
                "🧩 Pick an activity at your favorite spot",
                "😊 Share your good energy — be a positive leader",
            ],
            "😌 Calm": [
                "📚 You're ready — head back to your activity!",
                "🎯 Set one goal and go for it",
                "✅ Make a simple plan for the rest of the day",
                "🧩 Choose an activity you enjoy",
                "📝 Write down something you're looking forward to",
            ],
            "🤗 Friendly": [
                "🤝 Be a buddy or helper when you get back",
                "📝 Write a kind note for a friend",
                "🎯 Think of one way to include someone today",
                "😊 Smile and greet someone who looks lonely",
                "⭐ Share your good mood — it's contagious!",
            ],
            "🧠 Focused": [
                "📚 You're in the zone — go dive into your work!",
                "✅ Make a to-do list and start checking things off",
                "🎯 Set a stretch goal for today",
                "🧩 Find your favorite spot to work",
                "⭐ Challenge yourself — see how much you can get done!",
            ],
            "😃 Good": [
                "⭐ Keep that good energy going!",
                "📝 Write one thing you're grateful for right now",
                "🎯 Set a goal and go for it",
                "🤝 Help a classmate who's having a harder day",
                "😊 Take that good feeling back with you!",
            ],
        },
    },
    "🟡 Yellow Zone": {
        "color": "#b7770d", "bg": "#fef9e7", "border": "#f1c40f",
        "label": "Yellow Zone", "hint": "Worried · Frustrated · Silly",
        "description": "Your body feels wound up and hard to slow down.",
        "feelings": {
            "😰 Worried": [
                "✏️ Write your worry on paper — then fold it up and set it aside",
                "⭐ Trace a star shape slowly while breathing at each point",
                "🫁 Belly breathe — in for 4 counts, out for 4 counts",
                "✨ Watch the glitter bottle until the worry feels smaller",
                "🧸 Hold the fidget toy while we talk about what's on your mind",
            ],
            "😤 Frustrated": [
                "🤜 Do 10 wall push-ups to push that energy out",
                "🧸 Squeeze the stress ball as hard as you can, then let go",
                "🚶 Walk one brisk lap around campus to reset",
                "✏️ Scribble out your feelings on paper — then crumple it up",
                "🫁 Take 5 big breaths — breathe in the calm, breathe out the frustration",
            ],
            "🤪 Silly": [
                "🪑 Sit in the calm corner and let your body settle down",
                "🫁 Take 3 slow deep breaths to calm your body",
                "🔢 Count slowly to 10 in your head",
                "🤜 Do 5 slow wall push-ups to refocus",
                "✏️ Channel the sillies into a quick doodle",
            ],
            "😠 Annoyed": [
                "🚶 Walk one lap — come back when you feel ready",
                "🧸 Squeeze the stress ball in the calm corner",
                "✏️ Write out what's bugging you, then put the paper face-down",
                "🫁 Take 5 slow breaths before thinking about next steps",
                "🤜 Do wall push-ups to get the annoyed energy out of your body",
            ],
            "😬 Nervous": [
                "✋ Trace your hand slowly — breathe in going up each finger, out going down",
                "⭐ Trace a star shape slowly while breathing at each point",
                "🧸 Hold the fidget toy and squeeze it slowly",
                "🫁 Take 5 slow belly breaths — in for 4 counts, out for 4 counts",
                "✨ Watch the glitter bottle until your heart feels steadier",
            ],
        },
    },
    "🔴 Red Zone": {
        "color": "#c0392b", "bg": "#fdedec", "border": "#e74c3c",
        "label": "Red Zone", "hint": "Angry · Scared · Overwhelmed",
        "description": "Your body feels like it's in overdrive — everything is intense.",
        "feelings": {
            "😡 Angry": [
                "🤜 Do jumping jacks or wall push-ups to release the big energy",
                "🧸 Squeeze the pillow or stress ball as hard as you can",
                "🚶 Walk fast — one full lap around the building",
                "🫁 Belly breathe — push your tummy out as you breathe in",
                "✏️ Scribble your feelings hard on paper — then crumple it up",
            ],
            "😱 Scared": [
                "🧸 Hold the comfort pillow — you are safe right here",
                "✋ Trace your hand slowly — breathe in going up, out going down",
                "🫁 Belly breathe — in for 4 counts, out for 4 counts",
                "✨ Watch the glitter bottle until your heart slows down",
                "🪑 Sit quietly in the calm corner — you don't have to do anything yet",
            ],
            "😭 Very Upset": [
                "🧸 Hold the comfort pillow — it's okay to feel this way",
                "🪑 Sit in the calm corner — take all the time you need",
                "✏️ Draw or scribble how you're feeling right now",
                "🫁 Breathe in slowly through your nose, out through your mouth",
                "✨ Watch the glitter bottle until things feel a little calmer",
            ],
            "🤯 Overwhelmed": [
                "🪑 Sit in the calm corner — nothing else right now, just breathe",
                "🫁 Box breathe — in for 4, hold for 4, out for 4, hold for 4",
                "✋ Trace your hand slowly — breathe at each finger",
                "✨ Watch the glitter bottle and let your thoughts settle",
                "✏️ Write down just ONE thing — we'll figure out the rest together",
            ],
            "💥 Out of control": [
                "🪑 Sit down in the calm corner right now",
                "🤜 Do jumping jacks outside to release the big energy",
                "🫁 Belly breathe — push your tummy out as you breathe in",
                "🧸 Squeeze the pillow or stress ball with both hands",
                "✨ Watch the glitter bottle — watch it slow down with you",
            ],
        },
    },
}


def save_checkin(name, grade, rec_group, referral, zone, feeling, strategy, notes, start_time):
    os.makedirs("data_ai", exist_ok=True)
    filepath = "data_ai/template_checkins.csv"
    end_time = datetime.now()
    duration = round((end_time - start_time).total_seconds() / 60, 1) if start_time else None
    clean_zone     = zone.split()[1] if zone else zone
    clean_feeling  = " ".join(feeling.split()[1:]) if feeling else feeling
    clean_strategy = " ".join(strategy.split()[1:]) if strategy else strategy
    clean_referral = referral.split()[0] if referral else referral
    new_row = pd.DataFrame([{
        "Date":             start_time.strftime("%Y-%m-%d") if start_time else None,
        "Start Time":       start_time.strftime("%H:%M") if start_time else None,
        "End Time":         end_time.strftime("%H:%M"),
        "Duration (min)":   duration,
        "Student Name":     name,
        "Grade":            grade,
        "Rec Group":        rec_group,
        "Referral Type":    clean_referral,
        "Zone":             clean_zone,
        "Feeling":          clean_feeling,
        "Strategy Used":    clean_strategy,
        "Specialist Notes": notes,
    }])
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        df = new_row
    df.to_csv(filepath, index=False)


def normalize_df(df):
    """Migrate old-format column names to current readable format, merging when both exist."""
    renames = {
        "student_name":    "Student Name",
        "grade":           "Grade",
        "rec_group":       "Rec Group",
        "referral_type":   "Referral Type",
        "zone":            "Zone",
        "feeling":         "Feeling",
        "strategy_chosen": "Strategy Used",
        "specialist_notes":"Specialist Notes",
        "duration_minutes":"Duration (min)",
        "checkin_end":     "End Time",
        "checkin_start":   "Start Time",
        "timestamp":       "End Time",
    }
    for old, new in renames.items():
        if old in df.columns:
            if new in df.columns:
                df[new] = df[new].fillna(df[old])
                df = df.drop(columns=[old])
            else:
                df = df.rename(columns={old: new})
    return df


def reset_app():
    for key in ("step", "selected_zone", "selected_feeling", "selected_strategy",
                "student_name", "grade", "rec_group", "referral_type", "specialist_notes", "checkin_start_time"):
        st.session_state[key] = 0 if key == "step" else None
    st.session_state.student_name = ""
    st.session_state.rec_group = ""
    st.session_state.specialist_notes = ""
    st.session_state.notes_open = False


# ──────────────────────────────────────────────
# STEP 0 — Welcome & Name
# ──────────────────────────────────────────────
if st.session_state.step == 0:
    st.markdown("<div class='big-title'>🌟 Welcome to the Calm Corner 🌟</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>Let's check in together!</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        name = st.text_input("👤 What's your name?", placeholder="Type your name here...")
        if name:
            if st.button("✨ Let's Start!", use_container_width=True, type="primary"):
                st.session_state.student_name = name
                st.session_state.checkin_start_time = datetime.now()
                st.session_state.step = 1
                st.rerun()

# ──────────────────────────────────────────────
# STEP 1 — Grade & Rec Group
# ──────────────────────────────────────────────
elif st.session_state.step == 1:
    name = st.session_state.student_name
    st.markdown(f"<div class='big-title'>Hi, {name}! 👋</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>Tell us a little about yourself.</div>", unsafe_allow_html=True)

    st.markdown("**What grade are you in?**")
    grade_rows = [["TK", "K", "1st", "2nd", "3rd"], ["4th", "5th", "6th", "7th", "8th"]]
    for row in grade_rows:
        cols = st.columns(len(row))
        for i, g in enumerate(row):
            with cols[i]:
                selected = st.session_state.grade == g
                if st.button(g, key=f"grade_{g}", use_container_width=True,
                             type="primary" if selected else "secondary"):
                    if st.session_state.grade != g:
                        st.session_state.grade = g
                        st.session_state.rec_group = None
                    st.rerun()

    st.write("")
    if st.session_state.grade:
        available = GRADE_TO_GROUPS.get(st.session_state.grade, [])

        if not available:
            st.info("No groups have been set up yet. A staff member needs to add groups in the Staff Dashboard → Program Settings.")
        else:
            if len(available) == 1 and st.session_state.rec_group != available[0]:
                st.session_state.rec_group = available[0]
                st.rerun()

            if st.session_state.rec_group and st.session_state.rec_group not in available:
                st.session_state.rec_group = None
                st.rerun()

            if len(available) > 1:
                st.markdown("**Which class or group are you in?**")
                rec_groups = [(g, g) for g in available]
                pairs = [rec_groups[i:i+2] for i in range(0, len(rec_groups), 2)]
                for pair in pairs:
                    cols = st.columns(2)
                    for j, (key, label) in enumerate(pair):
                        with cols[j]:
                            if rec_group_button(label, f"rg_{key}"):
                                st.session_state.rec_group = key
                                st.rerun()
            else:
                st.markdown(
                    f"<div style='text-align:center;font-size:1rem;color:#555;margin-top:8px;'>"
                    f"Group: <strong>{available[0]}</strong></div>",
                    unsafe_allow_html=True,
                )

    st.write("")
    if st.session_state.grade and st.session_state.rec_group:
        if st.button("Next ➡️", use_container_width=True, type="primary"):
            st.session_state.step = 2
            st.rerun()

    st.write("")
    if st.button("⬅️ Go Back", use_container_width=True):
        st.session_state.step = 0
        st.rerun()

# ──────────────────────────────────────────────
# STEP 2 — How did you get here?
# ──────────────────────────────────────────────
elif st.session_state.step == 2:
    name = st.session_state.student_name
    st.markdown(f"<div class='big-title'>Hi, {name}! 👋</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='sub-title'>How did you get to the calm corner today?</div>",
        unsafe_allow_html=True,
    )

    referral_cards = [
        ("ref_self",   "Self — asked to come",        "🙋",   "I asked to come",      "I knew I needed a break",         "#e8f8f5", "#1abc9c", "#148f77"),
        ("ref_leader", "Referred by staff",  "👨‍🏫",  "A staff member sent me", "Staff thought I needed a break", "#fef5e7", "#f39c12", "#b7770d"),
    ]

    cols = st.columns(2)
    for i, (key, referral_type, emoji, label, subtitle, bg, border, color) in enumerate(referral_cards):
        with cols[i]:
            marker = f"refcard-{key}"
            st.markdown(
                f'<div id="{marker}"></div>'
                f'<style>'
                f'  .element-container:has(#{marker}) + .element-container button {{'
                f'    background-color: {bg} !important;'
                f'    color: {color} !important;'
                f'    border: 3px solid {border} !important;'
                f'    border-radius: 18px !important;'
                f'    min-height: 160px !important;'
                f'    padding: 20px 16px !important;'
                f'    white-space: normal !important;'
                f'    line-height: 1.4 !important;'
                f'  }}'
                f'  .element-container:has(#{marker}) + .element-container button p {{'
                f'    text-align: center !important; margin: 0 0 4px 0 !important;'
                f'  }}'
                f'  .element-container:has(#{marker}) + .element-container button p:first-child {{'
                f'    font-size: 3rem !important; line-height: 1.1 !important; margin-bottom: 10px !important;'
                f'  }}'
                f'  .element-container:has(#{marker}) + .element-container button p:nth-child(2) {{'
                f'    font-size: 1.1rem !important; font-weight: bold !important; color: {color} !important;'
                f'  }}'
                f'  .element-container:has(#{marker}) + .element-container button p:last-child {{'
                f'    font-size: 0.85rem !important; font-weight: normal !important; color: #666 !important;'
                f'  }}'
                f'  .element-container:has(#{marker}) + .element-container button:hover {{'
                f'    opacity: 0.85 !important; background-color: {bg} !important;'
                f'  }}'
                f'</style>',
                unsafe_allow_html=True,
            )
            if st.button(f"{emoji}\n\n{label}\n\n{subtitle}", key=key, use_container_width=True):
                st.session_state.referral_type = referral_type
                st.session_state.step = 3
                st.rerun()

    st.write("")
    if st.button("⬅️ Go Back", use_container_width=True):
        st.session_state.step = 1
        st.rerun()

# ──────────────────────────────────────────────
# STEP 3 — Pick a Zone
# ──────────────────────────────────────────────
elif st.session_state.step == 3:
    name = st.session_state.student_name
    st.markdown(f"<div class='big-title'>How are you feeling, {name}?</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='sub-title'>Which color matches how you feel <strong>right now</strong>?</div>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    zone_keys = list(ZONES.keys())

    for i, key in enumerate(zone_keys):
        zd = ZONES[key]
        target_col = col1 if i % 2 == 0 else col2
        with target_col:
            zm = "zm-" + re.sub(r"[^a-zA-Z0-9]", "-", key)
            st.markdown(
                f'<div id="{zm}"></div>'
                f'<style>'
                f'  .element-container:has(#{zm}) + .element-container button {{'
                f'    background-color: {zd["bg"]} !important;'
                f'    color: #333 !important;'
                f'    border: 3px solid {zd["border"]} !important;'
                f'    border-radius: 18px !important;'
                f'    min-height: 175px !important;'
                f'    padding: 18px 14px !important;'
                f'    white-space: normal !important;'
                f'    line-height: 1.4 !important;'
                f'  }}'
                f'  .element-container:has(#{zm}) + .element-container button p {{'
                f'    text-align: center !important; margin: 0 0 4px 0 !important;'
                f'  }}'
                f'  .element-container:has(#{zm}) + .element-container button p:first-child {{'
                f'    font-size: 2.2rem !important; line-height: 1.1 !important; margin-bottom: 6px !important;'
                f'  }}'
                f'  .element-container:has(#{zm}) + .element-container button p:nth-child(2) {{'
                f'    font-size: 1.1rem !important; font-weight: bold !important; color: {zd["color"]} !important; margin-bottom: 6px !important;'
                f'  }}'
                f'  .element-container:has(#{zm}) + .element-container button p:nth-child(3) {{'
                f'    font-size: 0.9rem !important; font-weight: 700 !important; color: #333 !important;'
                f'  }}'
                f'  .element-container:has(#{zm}) + .element-container button p:last-child {{'
                f'    font-size: 0.82rem !important; font-weight: normal !important; color: #777 !important; font-style: italic !important;'
                f'  }}'
                f'  .element-container:has(#{zm}) + .element-container button:hover {{'
                f'    opacity: 0.85 !important; background-color: {zd["bg"]} !important;'
                f'  }}'
                f'</style>',
                unsafe_allow_html=True,
            )
            if st.button(
                f"{key.split()[0]}\n\n{zd['label']}\n\n{zd['description']}\n\n{zd['hint']}",
                key=f"zone_{key}", use_container_width=True
            ):
                st.session_state.selected_zone = key
                st.session_state.step = 4
                st.rerun()

    st.write("")
    if st.button("⬅️ Go Back", use_container_width=True):
        st.session_state.step = 2
        st.rerun()

# ──────────────────────────────────────────────
# STEP 4 — Pick a Feeling
# ──────────────────────────────────────────────
elif st.session_state.step == 4:
    zone = st.session_state.selected_zone
    zd = ZONES[zone]

    st.markdown(
        f"""<div class='zone-card' style='background:{zd["bg"]};border:3px solid {zd["border"]};margin-bottom:20px;'>
            <div style='font-size:1.6rem;font-weight:bold;color:{zd["color"]};'>{zone}</div>
        </div>""",
        unsafe_allow_html=True,
    )
    st.markdown("<div class='sub-title'>Can you pick the feeling that fits best?</div>", unsafe_allow_html=True)

    for feeling in zd["feelings"].keys():
        if st.button(feeling, key=f"f_{feeling}", use_container_width=True):
            st.session_state.selected_feeling = feeling
            st.session_state.step = 5
            st.rerun()

    st.write("")
    if st.button("⬅️ Go Back", use_container_width=True):
        st.session_state.step = 3
        st.rerun()

# ──────────────────────────────────────────────
# STEP 5 — Choose a Calm Corner Tool
# ──────────────────────────────────────────────
elif st.session_state.step == 5:
    zone = st.session_state.selected_zone
    feeling = st.session_state.selected_feeling
    zd = ZONES[zone]

    st.markdown(
        f"""<div style='text-align:center;font-size:1.4rem;color:#444;margin-bottom:18px;'>
            You're feeling <strong>{feeling}</strong> — and that's okay! 💙<br>
            <span style='font-size:1.1rem;color:#666;'>Which calm corner tool would you like to try?</span>
        </div>""",
        unsafe_allow_html=True,
    )

    for strategy in zd["feelings"][feeling]:
        if st.button(strategy, key=f"s_{strategy}", use_container_width=True):
            st.session_state.selected_strategy = strategy
            st.session_state.step = 6
            st.rerun()

    st.write("")
    if st.button("⬅️ Go Back", use_container_width=True):
        st.session_state.step = 4
        st.rerun()

# ──────────────────────────────────────────────
# STEP 6 — Affirmation + Specialist Notes
# ──────────────────────────────────────────────
elif st.session_state.step == 6:
    name = st.session_state.student_name
    grade = st.session_state.grade
    rec_group = st.session_state.rec_group
    feeling = st.session_state.selected_feeling
    strategy = st.session_state.selected_strategy
    zone = st.session_state.selected_zone
    referral = st.session_state.referral_type

    st.markdown("<div style='text-align:center;font-size:3rem;margin:15px 0;'>⭐ 🌈 ⭐</div>", unsafe_allow_html=True)
    st.markdown(
        f"<div style='text-align:center;font-size:2rem;font-weight:bold;color:#27ae60;margin-bottom:15px;'>Great job checking in, {name}!</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""<div class='affirm-box'>
            <div style='font-size:1.2rem;color:#555;'>
                You're feeling <strong>{feeling}</strong>.<br><br>
                Your calm corner tool:<br>
                <span style='font-size:1.3rem;color:#1e8449;font-weight:bold;'>{strategy}</span>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='text-align:center;font-size:1.1rem;color:#777;margin-bottom:25px;'>🌟 It takes courage to check in with your feelings. You're doing great! 🌟</div>",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 New Check-In", use_container_width=True, type="primary"):
            save_checkin(name, grade, rec_group, referral, zone, feeling, strategy, st.session_state.specialist_notes, st.session_state.checkin_start_time)
            reset_app()
            st.rerun()

    # Discreet specialist notes — toggled by a small + button
    st.write("")
    left, mid, right = st.columns([3, 1, 3])
    with mid:
        label = "✕" if st.session_state.notes_open else "+"
        if st.button(label, key="notes_toggle", help="Add a note"):
            st.session_state.notes_open = not st.session_state.notes_open
            st.rerun()

    if st.session_state.notes_open:
        notes = st.text_area(
            "notes_hidden",
            value=st.session_state.specialist_notes,
            placeholder="Observations, context, follow-up needed...",
            label_visibility="collapsed",
            height=90,
            key="notes_field",
        )
        st.session_state.specialist_notes = notes

# ──────────────────────────────────────────────
# Sidebar — Educator Dashboard (password protected)
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🍎 Staff Dashboard")

    if not st.session_state.educator_authenticated:
        st.markdown(
            "<div style='font-size:0.9rem;color:#888;margin-bottom:8px;'>🔒 Staff only</div>",
            unsafe_allow_html=True,
        )
        pw = st.text_input("Enter password", type="password", key="edu_pw_field",
                           label_visibility="collapsed", placeholder="Enter staff password...")
        if st.button("Unlock", use_container_width=True):
            if pw == EDUCATOR_PASSWORD:
                st.session_state.educator_authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password.")
    else:
        filepath = "data_ai/template_checkins.csv"

        if os.path.exists(filepath):
            df = normalize_df(pd.read_csv(filepath))
        else:
            df = pd.DataFrame()

        if df.empty:
            st.info("No check-ins yet.")
        elif st.session_state.selected_student:
            # ── Student detail view ──────────────────────
            student = st.session_state.selected_student
            sdf = df[df["Student Name"] == student].copy()

            if st.button("← All Students", use_container_width=True):
                st.session_state.selected_student = None
                st.rerun()

            st.markdown(f"### {student}")
            grade_val = sdf["Grade"].dropna().iloc[-1] if "Grade" in sdf.columns and not sdf["Grade"].dropna().empty else "—"
            rec_val = sdf["Rec Group"].dropna().iloc[-1] if "Rec Group" in sdf.columns and not sdf["Rec Group"].dropna().empty else "—"
            st.caption(f"Grade {grade_val}  ·  {rec_val}")
            st.metric("Total Check-Ins", len(sdf))

            if "Referral Type" in sdf.columns:
                self_count = (sdf["Referral Type"].str.startswith("Self")).sum()
                ref_count = len(sdf) - self_count
                c1, c2 = st.columns(2)
                c1.metric("🙋 Self", self_count)
                c2.metric("👨‍🏫 Referred", ref_count)

            st.markdown("**Zone history:**")
            zone_counts = sdf["Zone"].value_counts().rename("Visits")
            st.bar_chart(zone_counts)

            st.markdown("**All check-ins:**")
            for _, row in sdf.iloc[::-1].iterrows():
                date_str = str(row.get("Date", ""))
                time_str = str(row.get("Start Time", row.get("End Time", "")))
                ref_icon = "🙋" if str(row.get("Referral Type", "")).startswith("Self") else "👨‍🏫"
                with st.expander(f"{ref_icon} {date_str} {time_str} · {row.get('Zone', '')}"):
                    st.write(f"**Feeling:** {row.get('Feeling', '')}")
                    st.write(f"**Tool used:** {row.get('Strategy Used', '')}")
                    dur = row.get("Duration (min)")
                    if dur and str(dur) not in ("", "nan", "None"):
                        st.write(f"**Duration:** {dur} min")
                    notes_val = str(row.get("Specialist Notes", "")).strip()
                    if notes_val and notes_val != "nan":
                        st.write(f"**Notes:** {notes_val}")

            st.download_button(
                f"📥 Download {student}'s Data",
                sdf.to_csv(index=False),
                f"{student.replace(' ', '_')}_checkins.csv",
                "text/csv",
                use_container_width=True,
            )

        else:
            # ── Overview ─────────────────────────────────
            col1, col2 = st.columns(2)
            col1.metric("Total Check-Ins", len(df))
            self_ref = (df["Referral Type"].str.startswith("Self")).sum() if "Referral Type" in df.columns else 0
            col2.metric("Self-Referred", self_ref)

            st.markdown("**Recent Check-Ins — tap a name to view:**")
            recent = df.tail(8).iloc[::-1].reset_index(drop=True)
            for _, row in recent.iterrows():
                time_str = str(row.get("End Time", ""))
                ref_icon = "🙋" if str(row.get("Referral Type", "")).startswith("Self") else "👨‍🏫"
                grade_str = f"Gr.{row['Grade']}  ·  " if "Grade" in row.index and str(row.get("Grade", "")) not in ("", "nan", "None") else ""
                label = f"{ref_icon} {row['Student Name']}  ·  {grade_str}{row.get('Zone', '')}  ·  {time_str}"
                if st.button(label, key=f"stu_{_}_{row['Student Name']}", use_container_width=True):
                    st.session_state.selected_student = row["Student Name"]
                    st.rerun()

            st.markdown("**Zone Breakdown:**")
            st.bar_chart(df["Zone"].value_counts().rename("Count"))

            if "Referral Type" in df.columns:
                st.markdown("**Referral Type:**")
                st.bar_chart(df["Referral Type"].value_counts().rename("Count"))

            st.download_button(
                "📥 Download All Data",
                df.to_csv(index=False),
                "calm_corner_checkins.csv",
                "text/csv",
                use_container_width=True,
            )

        st.divider()
        with st.expander("⚙️ Program Settings"):
            ALL_GRADES = ["TK", "K", "1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th"]
            cfg = load_config()
            grps = cfg["groups"]

            tab_grps, tab_pw = st.tabs(["Groups", "Password"])

            with tab_grps:
                if not grps:
                    st.info("No groups yet. Add your first group below.")

                for i, grp in enumerate(grps):
                    c1, c2, c3 = st.columns([4, 1, 1])
                    with c1:
                        st.markdown(
                            f'<div style="display:inline-block;width:12px;height:12px;'
                            f'background:{grp["bg_color"]};border:1px solid #ccc;border-radius:3px;'
                            f'vertical-align:middle;margin-right:5px;"></div>'
                            f'<span style="font-size:0.88rem;font-weight:600;">{grp["name"]}</span> '
                            f'<span style="font-size:0.75rem;color:#999;">'
                            f'{", ".join(grp.get("grades", []))}</span>',
                            unsafe_allow_html=True,
                        )
                    with c2:
                        if st.button("✏️", key=f"edit_g_{i}", help="Edit"):
                            st.session_state.editing_group = i
                            st.rerun()
                    with c3:
                        if st.button("🗑️", key=f"del_g_{i}", help="Delete"):
                            grps.pop(i)
                            cfg["groups"] = grps
                            save_config(cfg)
                            if st.session_state.editing_group == i:
                                st.session_state.editing_group = None
                            st.rerun()

                st.divider()

                edit_idx = st.session_state.editing_group
                if edit_idx is not None:
                    is_new = edit_idx == -1
                    base = {} if is_new else grps[edit_idx]
                    st.markdown(f"**{'New Group' if is_new else 'Edit: ' + base.get('name', '')}**")
                    g_name   = st.text_input("Name", value=base.get("name", ""), key="eg_name")
                    g_bg     = st.color_picker("Background color", value=base.get("bg_color", "#e0e0e0"), key="eg_bg")
                    g_text   = st.color_picker("Text color", value=base.get("text_color", "#333333"), key="eg_text")
                    g_grades = st.multiselect("Grades", ALL_GRADES, default=base.get("grades", []), key="eg_grades")
                    ca, cb = st.columns(2)
                    with ca:
                        if st.button("💾 Save", key="eg_save", use_container_width=True):
                            if g_name.strip():
                                entry = {
                                    "name": g_name.strip(),
                                    "bg_color": g_bg,
                                    "text_color": g_text,
                                    "grades": g_grades,
                                }
                                if is_new:
                                    grps.append(entry)
                                else:
                                    grps[edit_idx] = entry
                                cfg["groups"] = grps
                                save_config(cfg)
                                st.session_state.editing_group = None
                                st.rerun()
                            else:
                                st.error("Group name is required.")
                    with cb:
                        if st.button("Cancel", key="eg_cancel", use_container_width=True):
                            st.session_state.editing_group = None
                            st.rerun()
                else:
                    if st.button("＋ Add New Group", key="add_new_grp", use_container_width=True):
                        st.session_state.editing_group = -1
                        st.rerun()

            with tab_pw:
                st.markdown("**Change Staff Password:**")
                new_pw  = st.text_input("New password", type="password", key="set_pw1")
                new_pw2 = st.text_input("Confirm password", type="password", key="set_pw2")
                if st.button("💾 Update Password", key="update_pw_btn", use_container_width=True):
                    if not new_pw:
                        st.error("Enter a new password.")
                    elif new_pw != new_pw2:
                        st.error("Passwords don't match.")
                    else:
                        cfg["password"] = new_pw
                        save_config(cfg)
                        st.success("Password updated! Use it next time you unlock.")

        if st.button("🔒 Lock Dashboard", use_container_width=True):
            st.session_state.educator_authenticated = False
            st.session_state.selected_student = None
            st.rerun()
