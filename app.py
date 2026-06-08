import sys
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

sys.path.insert(0, str(Path(__file__).parent))
from db import get_con, TYPE_COLORS, TYPE_ORDER

st.set_page_config(
    page_title="Pokédex",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CDN = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon"

# ── Game registry ─────────────────────────────────────────────────────────────
GAMES = {
    1: {"title": "Generation I",    "subtitle": "Red · Blue · Yellow",
        "starters": [1, 4, 7],      "legendary": 150,  "accent": "#C62828"},
    2: {"title": "Generation II",   "subtitle": "Gold · Silver · Crystal",
        "starters": [152, 155, 158], "legendary": 249,  "accent": "#F9A825"},
    3: {"title": "Generation III",  "subtitle": "Ruby · Sapphire · Emerald",
        "starters": [252, 255, 258], "legendary": 384,  "accent": "#2E7D32"},
    4: {"title": "Generation IV",   "subtitle": "Diamond · Pearl · Platinum",
        "starters": [387, 390, 393], "legendary": 483,  "accent": "#1565C0"},
    5: {"title": "Generation V",    "subtitle": "Black · White",
        "starters": [495, 498, 501], "legendary": 643,  "accent": "#37474F"},
    6: {"title": "Generation VI",   "subtitle": "X · Y",
        "starters": [650, 653, 656], "legendary": 716,  "accent": "#4527A0"},
    7: {"title": "Generation VII",  "subtitle": "Sun · Moon",
        "starters": [722, 725, 728], "legendary": 791,  "accent": "#E65100"},
    8: {"title": "Generation VIII", "subtitle": "Sword · Shield",
        "starters": [810, 813, 816], "legendary": 888,  "accent": "#0277BD"},
    9: {"title": "Generation IX",   "subtitle": "Scarlet · Violet",
        "starters": [906, 909, 912], "legendary": 1007, "accent": "#6A1B9A"},
}

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Game selection cards ── */
.game-card {
    position: relative;
    border-radius: 16px;
    overflow: hidden;
    padding: 18px 14px 14px;
    text-align: center;
    margin-bottom: 8px;
    transition: transform 0.18s, box-shadow 0.18s;
    border: 2px solid transparent;
    min-height: 220px;
    display: flex;
    flex-direction: column;
    align-items: center;
}
.game-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.5);
}
/* Legendary art — absolute-positioned behind everything */
.game-card .cover-art {
    position: absolute;
    right: -12px;
    bottom: -8px;
    width: 160px;
    height: 160px;
    background-size: contain;
    background-repeat: no-repeat;
    background-position: bottom right;
    opacity: 0.18;
    pointer-events: none;
}
/* Foreground content sits above the art */
.game-card .card-content {
    position: relative;
    z-index: 1;
    width: 100%;
}
.game-title {
    font-size: 1.05rem;
    font-weight: 800;
    letter-spacing: 0.03em;
    margin-bottom: 2px;
}
.game-subtitle {
    font-size: 0.75rem;
    color: #ccc;
    margin-bottom: 10px;
}
.game-count {
    display: inline-block;
    background: rgba(0,0,0,0.35);
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 0.75rem;
    color: #ddd;
    margin-top: 8px;
    backdrop-filter: blur(4px);
}
.starter-row { display: flex; justify-content: center; gap: 6px; }
.starter-row img { image-rendering: pixelated; }

/* ── Pokédex detail panel ── */
.type-badge {
    display: inline-block;
    padding: 4px 16px;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: 700;
    margin-right: 6px;
    color: white;
    text-shadow: 0 1px 2px rgba(0,0,0,0.4);
}
.stat-row { display: flex; align-items: center; margin-bottom: 5px; }
.stat-label {
    width: 52px; font-weight: 600; color: #aaa; font-size: 0.8rem;
    text-align: right; margin-right: 10px; flex-shrink: 0;
}
.stat-bar-bg {
    flex: 1; background: #2a2a2a; border-radius: 8px;
    height: 12px; overflow: hidden;
}
.stat-bar-fill { height: 100%; border-radius: 8px; }
.stat-val {
    width: 36px; text-align: right; font-size: 0.85rem;
    font-weight: 700; margin-left: 8px; flex-shrink: 0;
}
.flavor-text {
    font-size: 1.05rem; line-height: 1.6; color: #e8e8e8;
    border-left: 4px solid #EE8130;
    padding-left: 14px; margin: 12px 0 18px 0;
}
.physical-stat {
    display: inline-block; background: #1e2128;
    border-radius: 12px; padding: 6px 14px;
    margin-right: 8px; font-size: 0.9rem;
}

/* ── Card grid cells — uniform spreadsheet-style ── */
.poke-cell {
    background: #1a1d23;
    border: 1px solid #2e3038;
    border-radius: 8px;
    padding: 8px 4px 6px;
    text-align: center;
    /* Fixed height so every cell is identical */
    min-height: 148px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    gap: 3px;
    margin-bottom: 2px;
}
.poke-cell.selected {
    border-width: 2px;
    background: #1e2430;
}
/* Fixed-size image box — all sprites same visual footprint */
.poke-img-box {
    width: 68px;
    height: 68px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}
.poke-img-box img {
    max-width: 68px;
    max-height: 68px;
    image-rendering: pixelated;
}
.poke-num  { font-size: 0.62rem; color: #777; font-weight: 600; }
.poke-name { font-size: 0.7rem;  color: #eee; font-weight: 700; line-height: 1.2; }

/* Card buttons — visible on dark background */
div[data-testid="stVerticalBlock"] .stButton button {
    font-size: 0.7rem !important;
    padding: 3px 6px !important;
    border: 1px solid #3e4148 !important;
    background-color: #2a2d35 !important;
    color: #ccc !important;
    border-radius: 6px !important;
    width: 100% !important;
}
div[data-testid="stVerticalBlock"] .stButton button:hover {
    border-color: #EE8130 !important;
    color: #fff !important;
}
/* Primary (selected) card button — accent fill */
div[data-testid="stVerticalBlock"] .stButton button[kind="primary"] {
    background-color: var(--primary-color, #EE8130) !important;
    border-color: transparent !important;
    color: white !important;
    font-weight: 700 !important;
}
</style>
""", unsafe_allow_html=True)

con = get_con()


# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data
def load_all():
    df = con.sql("SELECT * FROM pokedex_full ORDER BY Number, Name").df()  # includes all columns incl. new traits fields
    df["_len"] = df["Name"].str.len()
    df = (df.sort_values(["Number", "_len"])
            .drop_duplicates(subset=["Number"])
            .drop(columns=["_len"])
            .reset_index(drop=True))
    return df

df_all = load_all()

# Pre-compute count per generation (post-dedup)
GEN_COUNTS = df_all.groupby("Generation").size().to_dict()


# ── Helpers ───────────────────────────────────────────────────────────────────
def type_badge(t: str) -> str:
    c = TYPE_COLORS.get(t, "#888")
    return f'<span class="type-badge" style="background:{c};">{t}</span>'

def stat_color(v: int) -> str:
    if v >= 100: return "#5bde7a"
    if v >= 70:  return "#f7d02c"
    if v >= 45:  return "#EE8130"
    return "#C22E28"

def stat_bar(label: str, val: int) -> str:
    pct = min(int(val / 255 * 100), 100)
    c = stat_color(val)
    return (
        f'<div class="stat-row">'
        f'<div class="stat-label">{label}</div>'
        f'<div class="stat-bar-bg"><div class="stat-bar-fill" style="width:{pct}%;background:{c};"></div></div>'
        f'<div class="stat-val" style="color:{c};">{val}</div>'
        f'</div>'
    )


# ── Physical Traits helpers ───────────────────────────────────────────────────

HEIGHT_COMPS = [
    (0.3,  "smaller than a house cat 🐱"),
    (0.6,  "about the size of a toddler 👶"),
    (1.0,  "about as tall as a 7-year-old 🧒"),
    (1.4,  "about as tall as a 10-year-old 🧑"),
    (1.7,  "about as tall as a grown-up 🧍"),
    (2.5,  "taller than a basketball hoop 🏀"),
    (5.0,  "as tall as a double-decker bus 🚌"),
    (10.0, "as tall as a 3-story building 🏢"),
    (float("inf"), "absolutely ENORMOUS 🌋"),
]
WEIGHT_COMPS = [
    (1,    "lighter than a water bottle 💧"),
    (5,    "about as heavy as a house cat 🐱"),
    (15,   "about as heavy as a big dog 🐕"),
    (40,   "about as heavy as a panda bear 🐼"),
    (100,  "about as heavy as a motorbike 🏍️"),
    (500,  "about as heavy as a horse 🐴"),
    (1000, "about as heavy as a car 🚗"),
    (float("inf"), "heavier than most things you know 🏔️"),
]
GROWTH_ICONS = {
    "Erratic": "⚡⚡ Very Fast", "Fast": "⚡ Fast",
    "Medium Fast": "➡️ Medium", "Medium Slow": "🐾 Medium Slow",
    "Slow": "🐢 Slow", "Fluctuating": "🔀 Fluctuating",
}
CATCH_LABELS = [
    (30,  "💀 Very Hard"),
    (75,  "⭐ Hard"),
    (150, "⭐⭐ Medium"),
    (200, "⭐⭐⭐ Easy"),
    (255, "⭐⭐⭐⭐⭐ Very Easy"),
]
HAPPINESS_LABELS = [
    (50,  "😤 Grumpy — needs lots of love to warm up"),
    (100, "😐 Neutral — fairly content from the start"),
    (256, "😊 Happy — loves its new trainer right away!"),
]
COLOR_SWATCHES = {
    "Black": "#333", "Blue": "#4a7fc1", "Brown": "#8B5E3C", "Gray": "#999",
    "Green": "#4CAF50", "Pink": "#F48FB1", "Purple": "#9C27B0", "Red": "#E53935",
    "White": "#eee", "Yellow": "#F9A825",
}


def _compare(val: float, table: list) -> str:
    for threshold, label in table:
        if val <= threshold:
            return label
    return table[-1][1]


def _catch_label(rate: int) -> str:
    pct = round(rate / 255 * 100, 1)
    for threshold, label in CATCH_LABELS:
        if rate <= threshold:
            return f"{label}  ({pct}% catch chance)"
    return f"💀 Very Hard  ({pct}% catch chance)"


def _happiness_label(val: int) -> str:
    for threshold, label in HAPPINESS_LABELS:
        if val < threshold:
            return label
    return HAPPINESS_LABELS[-1][1]


def _gender_html(rate: int) -> str:
    if rate == -1:
        return '<span style="color:#aaa;font-size:1rem;">⚲ Genderless</span>'
    f_pct = rate / 8 * 100
    m_pct = 100 - f_pct
    f_bar = f'<div style="height:10px;border-radius:4px 0 0 4px;background:#F48FB1;width:{f_pct}%;display:inline-block;"></div>'
    m_bar = f'<div style="height:10px;border-radius:0 4px 4px 0;background:#6390F0;width:{m_pct}%;display:inline-block;"></div>'
    return (
        f'<div style="margin:6px 0 2px;">{f_bar}{m_bar}</div>'
        f'<span style="color:#F48FB1;">♀ {f_pct:.0f}%</span>'
        f'&nbsp;&nbsp;'
        f'<span style="color:#6390F0;">♂ {m_pct:.0f}%</span>'
    )


def _type_badges_from_str(types_str: str | None) -> str:
    if not types_str:
        return '<span style="color:#666;">None</span>'
    return " ".join(type_badge(t.strip()) for t in types_str.split(";") if t.strip())


def _section(title: str) -> None:
    st.markdown(
        f'<div style="margin:20px 0 8px;font-size:1rem;font-weight:800;'
        f'color:#EE8130;border-bottom:1px solid #2a2d33;padding-bottom:4px;">'
        f'{title}</div>',
        unsafe_allow_html=True,
    )


def render_traits_tab(row, sel_num: int) -> None:
    """Render the full Physical Traits tab content."""
    con = get_con()

    # Determine up-front whether this Pokémon has any genuine wild encounters.
    # CaptureRate exists in PokéAPI for every species (it's an internal game formula
    # value), but it is only meaningful to show when the Pokémon can actually be
    # found and caught in the wild. If WildLocations == 0, hide the catch gauge.
    wild_count = con.sql(
        f"SELECT COUNT(*) FROM raw_locations WHERE Number = {sel_num}"
    ).fetchone()[0]
    has_wild = wild_count > 0

    # ── Section 1: Body Facts ─────────────────────────────────────────────────
    _section("🔬 Body Facts")
    col_a, col_b = st.columns(2)

    with col_a:
        # Color swatch
        color_name = str(row.get("Color") or "Gray")
        swatch_bg  = COLOR_SWATCHES.get(color_name, "#888")
        swatch_fg  = "#000" if color_name in ("White", "Yellow") else "#fff"
        shape_name = str(row.get("Shape") or "Unknown")
        st.markdown(
            f'<div style="display:flex;gap:10px;align-items:center;margin-bottom:10px;">'
            f'<span style="background:{swatch_bg};color:{swatch_fg};padding:3px 14px;'
            f'border-radius:20px;font-weight:700;">{color_name}</span>'
            f'<span style="color:#aaa;">Body shape: <strong style="color:#eee;">{shape_name}</strong></span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        h = float(row["HeightM"])
        st.markdown(
            f'**📏 Height:** {h:.1f} m — *{_compare(h, HEIGHT_COMPS)}*'
        )

    with col_b:
        w = float(row["WeightKg"])
        st.markdown(
            f'**⚖️ Weight:** {w:.1f} kg — *{_compare(w, WEIGHT_COMPS)}*'
        )
        # Gender bar
        rate = int(row.get("GenderRate") or -1)
        st.markdown("**⚤ Gender:**")
        st.markdown(_gender_html(rate), unsafe_allow_html=True)

    # ── Section 2: Trainer Facts ──────────────────────────────────────────────
    _section("🎮 Trainer Facts")
    col_c, col_d = st.columns(2)

    with col_c:
        # Catch difficulty — only shown for Pokémon that actually appear in the wild.
        # CaptureRate exists in PokéAPI for all species but has no meaning for
        # Pokémon that cannot be encountered (gifts, evolutions, legendaries obtained
        # through scripted events). Showing it for Charizard, e.g., would falsely
        # imply it can be caught, which it cannot.
        st.markdown("**🎯 Catch Difficulty:**")
        if has_wild:
            catch = int(row.get("CaptureRate") or 0)
            catch_pct = min(catch / 255, 1.0)
            catch_color = "#5bde7a" if catch > 180 else "#f7d02c" if catch > 90 else "#EE8130" if catch > 30 else "#C22E28"
            st.markdown(
                f'<div style="background:#2a2a2a;border-radius:8px;height:12px;margin:4px 0;">'
                f'<div style="width:{catch_pct*100:.0f}%;height:100%;border-radius:8px;background:{catch_color};"></div>'
                f'</div>'
                f'<div style="font-size:0.85rem;color:#aaa;">{_catch_label(catch)}</div>'
                f'<div style="font-size:0.75rem;color:#666;margin-top:2px;">Higher = easier to catch</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div style="font-size:0.88rem;color:#888;font-style:italic;margin-top:4px;">'
                '🚫 Not applicable — this Pokémon cannot be found in the wild.'
                '</div>',
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # Base experience
        xp = int(row.get("BaseExperience") or 0)
        xp_pct = min(xp / 608, 1.0)
        st.markdown("**✨ XP Reward when defeated:**")
        st.markdown(
            f'<div style="background:#2a2a2a;border-radius:8px;height:12px;margin:4px 0;">'
            f'<div style="width:{xp_pct*100:.0f}%;height:100%;border-radius:8px;background:#7C4DFF;"></div>'
            f'</div>'
            f'<div style="font-size:0.85rem;color:#aaa;">{xp} XP — '
            f'{"lots of XP! 🏆" if xp > 200 else "average XP" if xp > 80 else "low XP"}</div>'
            f'<div style="font-size:0.75rem;color:#666;margin-top:2px;">More XP = better reward for your team</div>',
            unsafe_allow_html=True,
        )

    with col_d:
        # Starting happiness
        happy = int(row.get("BaseHappiness") or 0)
        st.markdown("**😊 Starting Happiness:**")
        st.markdown(
            f'<div style="font-size:0.9rem;color:#eee;margin:4px 0;">{_happiness_label(happy)}</div>'
            f'<div style="font-size:0.75rem;color:#666;">Score: {happy}/255</div>',
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # Growth rate
        growth = str(row.get("GrowthRate") or "Medium Fast")
        growth_icon = GROWTH_ICONS.get(growth, f"➡️ {growth}")
        st.markdown("**📈 Growth Rate (how fast it levels up):**")
        st.markdown(
            f'<div style="font-size:0.9rem;color:#eee;margin:4px 0;">{growth_icon}</div>',
            unsafe_allow_html=True,
        )

        # Egg groups
        eg1 = str(row.get("EggGroup1") or "")
        eg2 = str(row.get("EggGroup2") or "")
        groups = eg1 + (f" / {eg2}" if eg2 else "")
        if groups:
            st.markdown(f"**🥚 Egg Groups:** {groups}")

    # ── Section 3: Abilities ──────────────────────────────────────────────────
    _section("⚡ Abilities")
    st.caption("Abilities are special powers that help Pokémon in battle!")

    abilities_df = con.sql(
        f"SELECT AbilityName, IsHidden FROM raw_abilities WHERE Number = {sel_num} ORDER BY IsHidden"
    ).df()

    if abilities_df.empty:
        st.markdown("*No ability data available.*")
    else:
        badges_html = ""
        for _, ab in abilities_df.iterrows():
            name = str(ab["AbilityName"])
            is_hidden = str(ab["IsHidden"]).lower() == "true"
            if is_hidden:
                badges_html += (
                    f'<span style="background:#F9A825;color:#000;padding:4px 16px;'
                    f'border-radius:20px;font-weight:700;margin-right:8px;margin-bottom:6px;'
                    f'display:inline-block;">✨ {name} (Hidden)</span>'
                )
            else:
                badges_html += (
                    f'<span style="background:#2E7D32;color:#fff;padding:4px 16px;'
                    f'border-radius:20px;font-weight:700;margin-right:8px;margin-bottom:6px;'
                    f'display:inline-block;">{name}</span>'
                )
        st.markdown(f'<div style="margin:6px 0;">{badges_html}</div>', unsafe_allow_html=True)

    # ── Section 4: Where to Find It ───────────────────────────────────────────
    _section("🗺️ Where to Find It")

    locs_df = con.sql(
        f"SELECT Region, AreaName, EncounterRate FROM raw_locations "
        f"WHERE Number = {sel_num} ORDER BY Region, EncounterRate DESC"
    ).df()

    if locs_df.empty:
        st.info("🚫 This Pokémon can't be found in the wild — it must be obtained another way! (Gift, trade, or evolution)")
    else:
        regions = locs_df["Region"].unique()
        region_cols = st.columns(min(len(regions), 3))
        for col, region in zip(region_cols, regions):
            with col:
                region_data = locs_df[locs_df["Region"] == region][["AreaName", "EncounterRate"]]
                with st.expander(f"📍 {region} ({len(region_data)} areas)"):
                    st.dataframe(
                        region_data.rename(columns={"AreaName": "Area", "EncounterRate": "Encounter %"}),
                        use_container_width=True, hide_index=True,
                    )

    # ── Section 5: Type Battle Info ───────────────────────────────────────────
    _section("⚔️ Type Battle Info")
    traits_row = con.sql(
        f"SELECT StrongAgainst, WeakAgainst, ResistantTo, ImmuneFrom "
        f"FROM pokemon_traits WHERE Number = {sel_num}"
    ).fetchone()

    type1 = str(row.get("Type1") or "")
    type2 = str(row.get("Type2") or "")
    type_desc = f"{type1}" + (f" / {type2}" if type2 else "")
    st.caption(f"How {row['Name']}'s **{type_desc}** type performs in battles:")

    if traits_row:
        strong, weak, resist, immune = traits_row
        col_e, col_f = st.columns(2)
        with col_e:
            st.markdown("🔴 **Strong against:**")
            st.markdown(_type_badges_from_str(strong), unsafe_allow_html=True)
            st.markdown("<br>🟡 **Resists hits from:**", unsafe_allow_html=True)
            st.markdown(_type_badges_from_str(resist), unsafe_allow_html=True)
        with col_f:
            st.markdown("🔵 **Weak to:**")
            st.markdown(_type_badges_from_str(weak), unsafe_allow_html=True)
            if immune:
                st.markdown("<br>⚫ **Immune to (no damage!):**", unsafe_allow_html=True)
                st.markdown(_type_badges_from_str(immune), unsafe_allow_html=True)
    else:
        st.markdown("*Type battle data not available.*")

def gif_url(pokemon_id: int) -> str:
    return f"{CDN}/other/showdown/{pokemon_id}.gif"

def artwork_url(pokemon_id: int) -> str:
    return f"{CDN}/other/official-artwork/{pokemon_id}.png"


# ── Evolution tab ─────────────────────────────────────────────────────────────

# Friendly emoji for evolution items so the trigger labels pop for kids.
_ITEM_EMOJI = {
    "thunder-stone": "⚡", "water-stone": "💧", "fire-stone": "🔥",
    "leaf-stone": "🍃", "moon-stone": "🌙", "sun-stone": "☀️",
    "shiny-stone": "✨", "dusk-stone": "🌑", "dawn-stone": "🌅",
    "ice-stone": "❄️", "oval-stone": "🥚", "black-augurite": "🪨",
    "kings-rock": "👑", "metal-coat": "⚙️", "dragon-scale": "🐉",
    "razor-claw": "🪝", "razor-fang": "🦷", "deep-sea-tooth": "🦈",
    "deep-sea-scale": "🐚", "protector": "🛡️", "electirizer": "🔌",
    "magmarizer": "🌋", "up-grade": "💾", "dubious-disc": "💿",
    "reaper-cloth": "🧵", "prism-scale": "🌈", "sachet": "🌸",
    "whipped-dream": "🍰", "tart-apple": "🍏", "sweet-apple": "🍎",
    "cracked-pot": "🫖", "chipped-pot": "🫖",
}


def _nice(slug: str) -> str:
    return slug.replace("-", " ").title()


def _evo_condition_label(e: dict) -> str:
    """Build a kid-readable trigger label for one evolution edge dict."""
    parts: list[str] = []

    if e["min_level"] is not None:
        parts.append(f"Lv {e['min_level']}")
    if e["trigger_item"]:
        parts.append(f"{_ITEM_EMOJI.get(e['trigger_item'], '💎')} {_nice(e['trigger_item'])}")
    if e["trigger"] == "trade":
        parts.append("🔄 Trade")
    if e["held_item"]:
        parts.append(f"💼 hold {_nice(e['held_item'])}")
    if e["known_move"]:
        parts.append(f"📘 knows {_nice(e['known_move'])}")
    if e["min_happiness"] is not None:
        parts.append("❤️ Friendship")
    if e["location"]:
        parts.append(f"📍 {_nice(e['location'])}")
    if e["time_of_day"] == "day":
        parts.append("☀️ Day")
    elif e["time_of_day"] == "night":
        parts.append("🌙 Night")

    if not parts:
        parts.append(_nice(e["trigger"]) if e["trigger"] else "Evolves")
    return " · ".join(parts)


def render_evolution_tab(row, sel_num: int) -> None:
    """Render the clickable, animated evolution family tree for sel_num."""
    from collections import defaultdict, deque

    con = get_con()
    _section("🔗 Evolution Family")

    cid_row = con.sql(
        f"SELECT chain_id FROM raw_evolution "
        f"WHERE species_id = {sel_num} OR evolves_into_id = {sel_num} LIMIT 1"
    ).fetchone()

    # No edge references this Pokémon → it doesn't evolve.
    if cid_row is None:
        st.markdown(
            f'<div style="text-align:center;margin:18px 0;">'
            f'<img src="{gif_url(sel_num)}" width="120" style="image-rendering:pixelated;"/>'
            f'<div style="margin-top:8px;color:#ccc;font-size:1.05rem;">'
            f'🚫 <strong>{row["Name"]}</strong> does not evolve.</div>'
            f'<div style="color:#777;font-size:0.85rem;">It stays just the way it is!</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        return

    cid = int(cid_row[0])
    raw = con.sql(
        "SELECT species_id, evolves_into_id, trigger, min_level, min_happiness, "
        "trigger_item, time_of_day, location, held_item, known_move "
        f"FROM raw_evolution WHERE chain_id = {cid}"
    ).df()

    def _s(v) -> str:
        return v if isinstance(v, str) else ""

    def _i(v):
        return int(v) if pd.notna(v) else None

    edges = [{
        "species_id":      int(r["species_id"]),
        "evolves_into_id": int(r["evolves_into_id"]),
        "trigger":         _s(r["trigger"]),
        "min_level":       _i(r["min_level"]),
        "min_happiness":   _i(r["min_happiness"]),
        "trigger_item":    _s(r["trigger_item"]),
        "time_of_day":     _s(r["time_of_day"]),
        "location":        _s(r["location"]),
        "held_item":       _s(r["held_item"]),
        "known_move":      _s(r["known_move"]),
    } for _, r in raw.iterrows()]

    # Build adjacency, find the root (a species never reached by evolution).
    children: dict[int, list[dict]] = defaultdict(list)
    parents, all_children = set(), set()
    for e in edges:
        children[e["species_id"]].append(e)
        parents.add(e["species_id"])
        all_children.add(e["evolves_into_id"])
    root = next((s for s in parents if s not in all_children), edges[0]["species_id"])

    # Breadth-first into depth levels; remember the edge that produced each node.
    level_nodes: dict[int, list[int]] = defaultdict(list)
    edge_into: dict[int, dict] = {}
    visited = {root}
    q = deque([(root, 0)])
    while q:
        nid, depth = q.popleft()
        level_nodes[depth].append(nid)
        for ce in children.get(nid, []):
            child = ce["evolves_into_id"]
            if child not in visited:
                visited.add(child)
                edge_into[child] = ce
                q.append((child, depth + 1))

    st.caption("Tap any Pokémon to jump to it in the Pokédex! ✨")

    HILITE = "#F7D02C"
    for depth in sorted(level_nodes):
        nodes = level_nodes[depth]
        for col, nid in zip(st.columns(len(nodes)), nodes):
            with col:
                m = df_all[df_all["Number"] == nid]
                name = str(m.iloc[0]["Name"]) if len(m) else f"#{nid:04d}"
                gen = int(m.iloc[0]["Generation"]) if len(m) else None

                if nid in edge_into:
                    st.markdown(
                        f'<div style="text-align:center;color:#7fbfff;font-size:0.78rem;'
                        f'font-weight:700;margin-bottom:2px;line-height:1.2;">'
                        f'⬇ {_evo_condition_label(edge_into[nid])}</div>',
                        unsafe_allow_html=True,
                    )

                is_cur = nid == sel_num
                ring = (f"box-shadow:0 0 0 3px {HILITE};border-radius:14px;background:#ffffff14;"
                        if is_cur else "")
                st.markdown(
                    f'<div style="text-align:center;">'
                    f'<img src="{gif_url(nid)}" width="104" '
                    f'style="image-rendering:pixelated;padding:6px;{ring}"/>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                if st.button(("⭐ " + name) if is_cur else name,
                             key=f"evo_{cid}_{nid}", use_container_width=True,
                             disabled=(is_cur or gen is None)):
                    st.session_state["selected_gen"] = gen
                    st.session_state["selected_number"] = nid
                    st.session_state["_scroll_top"] = True
                    st.rerun()


# ── Session state defaults ────────────────────────────────────────────────────
if "selected_gen" not in st.session_state:
    st.session_state["selected_gen"] = None
if "selected_number" not in st.session_state:
    st.session_state["selected_number"] = None


# ══════════════════════════════════════════════════════════════════════════════
# SCREEN 1 — Game selection
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state["selected_gen"] is None:

    st.markdown(
        "<h1 style='text-align:center;margin-bottom:4px;'>📖 Pokédex</h1>"
        "<p style='text-align:center;color:#aaa;font-size:1.1rem;margin-bottom:32px;'>"
        "Pick your Pokémon game to get started!</p>",
        unsafe_allow_html=True,
    )

    # 3 columns × 3 rows
    gen_items = list(GAMES.items())
    for row_i in range(3):
        cols = st.columns(3, gap="medium")
        for col_i, col in enumerate(cols):
            gen = row_i * 3 + col_i + 1
            info = GAMES[gen]
            count = GEN_COUNTS.get(gen, 0)
            starters = info["starters"]
            accent = info["accent"]

            starter_imgs = "".join(
                f'<img src="{gif_url(s)}" width="72" style="image-rendering:pixelated;"/>'
                for s in starters
            )

            with col:
                leg_id = info["legendary"]
                art_url = f"{CDN}/other/official-artwork/{leg_id}.png"
                # Gradient: accent colour fading to dark, with legendary art watermark
                gradient = f"linear-gradient(145deg, {accent}33 0%, #0e1117 65%)"
                st.markdown(
                    f'<div class="game-card" style="background:{gradient};border-color:{accent};">'
                    f'<div class="cover-art" style="background-image:url(\'{art_url}\');"></div>'
                    f'<div class="card-content">'
                    f'<div class="game-title" style="color:{accent};">{info["title"]}</div>'
                    f'<div class="game-subtitle">{info["subtitle"]}</div>'
                    f'<div class="starter-row">{starter_imgs}</div>'
                    f'<div class="game-count">✨ {count} new Pokémon</div>'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                if st.button(f"Explore {info['title']} →",
                             key=f"gen_{gen}",
                             use_container_width=True):
                    st.session_state["selected_gen"] = gen
                    st.session_state["selected_number"] = None
                    st.rerun()

    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# SCREEN 2 — Pokédex for selected generation
# ══════════════════════════════════════════════════════════════════════════════
gen = st.session_state["selected_gen"]
info = GAMES[gen]
accent = info["accent"]

# Filter to this generation only, sorted by Pokédex number
df = df_all[df_all["Generation"] == gen].sort_values("Number").reset_index(drop=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    if st.button("← All Games", use_container_width=True):
        st.session_state["selected_gen"] = None
        st.session_state["selected_number"] = None
        st.rerun()

    st.markdown(
        f'<div style="color:{accent};font-weight:800;font-size:1.1rem;margin:8px 0 2px;">'
        f'{info["title"]}</div>'
        f'<div style="color:#aaa;font-size:0.85rem;margin-bottom:16px;">{info["subtitle"]}</div>',
        unsafe_allow_html=True,
    )

    search = st.text_input("🔍 Search", placeholder="e.g. Charizard")
    show_legendary = st.radio("Show", ["All", "Non-Legendary", "Legendary only"])

    if st.button("🎲 Surprise me!", use_container_width=True):
        st.session_state["selected_number"] = int(df.sample(1).iloc[0]["Number"])
        st.session_state["_scroll_top"] = True
        st.rerun()

# Apply search/legendary filter (generation is already locked)
df_view = df.copy()
if search:
    df_view = df_view[df_view["Name"].str.contains(search, case=False, na=False)]
if show_legendary == "Non-Legendary":
    df_view = df_view[~df_view["Legendary"]]
elif show_legendary == "Legendary only":
    df_view = df_view[df_view["Legendary"]]

if df_view.empty:
    st.warning("No Pokémon match that search. Try something else!")
    st.stop()

# Resolve selected Pokémon (default to first of this gen)
default_num = int(df_view.iloc[0]["Number"])
sel_num = st.session_state.get("selected_number") or default_num
if sel_num not in df_view["Number"].values:
    sel_num = default_num
st.session_state["selected_number"] = sel_num
row = df_view[df_view["Number"] == sel_num].iloc[0]

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown(
    f'<h2 style="margin-bottom:4px;">'
    f'<span style="color:{accent};">{info["title"]}</span>'
    f'&nbsp;<span style="color:#888;font-size:1rem;font-weight:400;">{info["subtitle"]}</span>'
    f'</h2>'
    f'<p style="color:#aaa;margin-bottom:16px;">'
    f'#{int(df.iloc[0]["Number"]):04d} – #{int(df.iloc[-1]["Number"]):04d} · '
    f'{len(df_view):,} Pokémon shown</p>',
    unsafe_allow_html=True,
)

# Scroll to top whenever a new Pokémon is selected.
# Uses a counter token so the iframe content hash changes every click →
# Streamlit never reuses a cached iframe and the script always re-executes.
# Three firings (0 / 200 / 500 ms) catch any post-render DOM reflows.
# scrollTop = 0 (instant) instead of smooth — smooth can be interrupted.
if st.session_state.pop("_scroll_top", False):
    n = st.session_state.get("_scroll_n", 0) + 1
    st.session_state["_scroll_n"] = n
    components.html(
        f"<script>/* {n} */"
        "function _s(){{var e=window.parent.document.querySelector('[data-testid=\"stMain\"]');"
        "if(e)e.scrollTop=0;}}"
        "_s();setTimeout(_s,200);setTimeout(_s,500);"
        "</script>",
        height=0,
    )

# ── Detail panel — tabbed ────────────────────────────────────────────────────
with st.container(border=True):
    tab_overview, tab_traits, tab_evo = st.tabs(
        ["📋 Overview", "🏋️ Physical Traits", "🔗 Evolution"])

    # ── Overview tab (unchanged layout) ──────────────────────────────────────
    with tab_overview:
        art_col, info_col = st.columns([1, 1.7], gap="large")

        with art_col:
            st.image(row["ArtworkURL"], use_container_width=True)
            st.markdown(
                f'<div style="text-align:center;margin-top:6px;">'
                f'<img src="{row["AnimatedGifURL"]}" width="96" style="image-rendering:pixelated;"/>'
                f'<br><span style="font-size:0.75rem;color:#888;">Battle sprite</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

        with info_col:
            leg_star = " ⭐" if row["Legendary"] else ""
            st.markdown(
                f'<span style="color:#888;font-size:1.1rem;font-weight:700;">#{int(row["Number"]):04d}</span>'
                f'<span style="color:#888;font-size:0.85rem;"> Gen {gen}{leg_star}</span>',
                unsafe_allow_html=True,
            )
            st.markdown(f"## {row['Name']}")

            badges = type_badge(row["Type1"])
            if row["Type2"]:
                badges += type_badge(row["Type2"])
            genus = row.get("Genus", "") or ""
            st.markdown(
                f'<span style="color:#bbb;font-style:italic;font-size:0.95rem;">{genus}</span>'
                f'<br>{badges}',
                unsafe_allow_html=True,
            )

            flavor = row.get("FlavorText", "") or ""
            if flavor:
                st.markdown(
                    f'<div class="flavor-text">"{flavor}"</div>',
                    unsafe_allow_html=True,
                )

            egg2 = f" / {row['EggGroup2']}" if row.get("EggGroup2") else ""
            st.markdown(
                f'<div style="margin-bottom:14px;">'
                f'<span class="physical-stat">📏 {row["HeightM"]:.1f} m</span>'
                f'<span class="physical-stat">⚖️ {row["WeightKg"]:.1f} kg</span>'
                f'<span class="physical-stat">🥚 {row.get("EggGroup1","")}{egg2}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

            bars = "".join([
                stat_bar("HP",    int(row["HP"])),
                stat_bar("ATK",   int(row["Attack"])),
                stat_bar("DEF",   int(row["Defense"])),
                stat_bar("SpATK", int(row["SpAtk"])),
                stat_bar("SpDEF", int(row["SpDef"])),
                stat_bar("SPD",   int(row["Speed"])),
            ])
            tc = stat_color(int(row["TotalStats"]) // 6)
            bars += (f'<div style="margin-top:8px;font-size:0.82rem;color:#aaa;">'
                     f'Total: <strong style="color:{tc}">{int(row["TotalStats"])}</strong></div>')
            st.markdown(bars, unsafe_allow_html=True)

    # ── Physical Traits tab ───────────────────────────────────────────────────
    with tab_traits:
        render_traits_tab(row, int(row["Number"]))

    # ── Evolution tab ─────────────────────────────────────────────────────────
    with tab_evo:
        render_evolution_tab(row, int(row["Number"]))

# ── Card grid — uniform spreadsheet cells ─────────────────────────────────────
st.divider()
st.subheader(f"All {len(df_view):,} Pokémon — click any card to explore!")

COLS = 8
for chunk_start in range(0, len(df_view), COLS):
    chunk = df_view.iloc[chunk_start : chunk_start + COLS]
    cols = st.columns(COLS, gap="small")
    for col, (_, r) in zip(cols, chunk.iterrows()):
        with col:
            is_sel = int(r["Number"]) == sel_num
            cell_cls = "poke-cell selected" if is_sel else "poke-cell"
            border_color = accent if is_sel else "#2e3038"

            st.markdown(
                f'<div class="{cell_cls}" style="border-color:{border_color};">'
                f'<div class="poke-img-box">'
                f'<img src="{r["AnimatedGifURL"]}"/>'
                f'</div>'
                f'<div class="poke-num">#{int(r["Number"]):04d}</div>'
                f'<div class="poke-name">{r["Name"]}</div>'
                f'{type_badge(r["Type1"])}'
                f'</div>',
                unsafe_allow_html=True,
            )

            btn_label = "✓ Selected" if is_sel else "View →"
            btn_type  = "primary"    if is_sel else "secondary"
            if st.button(btn_label, key=f"c_{int(r['Number'])}", type=btn_type,
                         use_container_width=True):
                st.session_state["selected_number"] = int(r["Number"])
                st.session_state["_scroll_top"] = True
                st.rerun()
