"""Streamlit app for the Music Recommender Simulation.

Run with:
    streamlit run app.py
"""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent
from typing import Dict, List

import streamlit.components.v1 as components
import streamlit as st

from src.recommender import load_songs, recommend_songs


APP_TITLE = "Magic Jukebox"
DATA_PATH = Path("data/songs.csv")

PROFILE_PRESETS = {
    "Custom": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "tempo": 118,
        "valence": 0.75,
        "danceability": 0.78,
        "acousticness": 0.2,
    },
    "Gym Hype": {
        "genre": "pop",
        "mood": "intense",
        "energy": 0.95,
        "tempo": 132,
        "valence": 0.7,
        "danceability": 0.9,
        "acousticness": 0.05,
    },
    "Chill Study": {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.4,
        "tempo": 80,
        "valence": 0.55,
        "danceability": 0.6,
        "acousticness": 0.85,
    },
    "Late Night Drive": {
        "genre": "synthwave",
        "mood": "moody",
        "energy": 0.72,
        "tempo": 110,
        "valence": 0.5,
        "danceability": 0.74,
        "acousticness": 0.2,
    },
    "Sunset Warmup": {
        "genre": "indie pop",
        "mood": "happy",
        "energy": 0.68,
        "tempo": 124,
        "valence": 0.82,
        "danceability": 0.8,
        "acousticness": 0.3,
    },
}


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def get_songs() -> List[Dict]:
    return load_songs(str(DATA_PATH))


def build_preferences(
    favorite_genre: str,
    favorite_mood: str,
    target_energy: float,
    target_tempo: float,
    target_valence: float,
    target_danceability: float,
    acoustic_preference: float,
) -> Dict:
    return {
        "genre": favorite_genre,
        "mood": favorite_mood,
        "energy": target_energy,
        "targetTempo": target_tempo,
        "targetValence": target_valence,
        "targetDanceability": target_danceability,
        "targetAcousticness": acoustic_preference,
    }


def resolve_profile(profile_name: str) -> Dict[str, float | str]:
    return PROFILE_PRESETS.get(profile_name, PROFILE_PRESETS["Custom"])


def pretty_score(score: float) -> str:
    return f"{score:.2f}"


def build_phone_html(recommendations: List[tuple], fallback_profile: str) -> str:
    if recommendations:
        top_song, top_score, top_reasons = recommendations[0]
        top_match_html = f"""
            <div class="section-label">Top Match</div>
            <div class="top-match">{top_song.get('title', 'Untitled')} by {top_song.get('artist', 'Unknown Artist')}</div>
            <p class="utility">{top_reasons}</p>
            <div class="chip-row">
                <span class="chip">{top_song.get('genre', '')}</span>
                <span class="chip">{top_song.get('mood', '')}</span>
                <span class="chip">Score {pretty_score(top_score)}</span>
            </div>
        """
        cards_html = "".join(
            render_receipt_card(song, score, reasons, rank)
            for rank, (song, score, reasons) in enumerate(recommendations, start=1)
        )
    else:
        top_match_html = f"""
            <div class="section-label">Top Match</div>
            <div class="top-match">No recommendations yet</div>
            <p class="utility">Try changing the {fallback_profile} profile in the sidebar.</p>
        """
        cards_html = """
            <div class="receipt-card">
                <p class="receipt-reasons">No recommendations were generated for the current profile.</p>
            </div>
        """

    return dedent(
        f"""
        <style>
        html, body {{
            margin: 0;
            padding: 0;
            background: transparent;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }}

        * {{ box-sizing: border-box; }}

        .phone-shell {{
            max-width: 430px;
            margin: 0 auto;
            padding: 0.9rem;
            border-radius: 2rem;
            background: linear-gradient(180deg, rgba(255,255,255,0.12), rgba(255,255,255,0.04));
            box-shadow: 0 30px 80px rgba(0, 0, 0, 0.38);
            border: 1px solid rgba(255,255,255,0.10);
        }}

        .phone-screen {{
            background: linear-gradient(180deg, rgba(15, 20, 31, 0.95), rgba(8, 10, 17, 0.96));
            border-radius: 1.5rem;
            padding: 0.8rem;
            max-height: 760px;
            overflow-y: auto;
            border: 1px solid rgba(255,255,255,0.06);
            color: #f4f7fb;
        }}

        .phone-notch {{
            width: 38%;
            height: 0.45rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.14);
            margin: 0 auto 1rem auto;
        }}

        .now-playing {{
            border-radius: 1.3rem;
            padding: 0.85rem;
            background: linear-gradient(135deg, rgba(124,228,255,0.18), rgba(255,139,212,0.14));
            border: 1px solid rgba(255,255,255,0.08);
            margin-bottom: 0.75rem;
        }}

        .section-label {{
            color: #a7b0c0;
            text-transform: uppercase;
            letter-spacing: 0.14em;
            font-size: 0.72rem;
            font-weight: 700;
            margin-bottom: 0.65rem;
        }}

        .now-playing h2,
        .receipt-card h3 {{
            margin: 0.25rem 0 0.1rem 0;
            color: #f4f7fb;
        }}

        .now-playing .subtle,
        .receipt-artist,
        .receipt-reasons,
        .utility {{
            color: #a7b0c0;
        }}

        .chip-row, .receipt-tags, .receipt-meta, .receipt-topline {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
            align-items: center;
        }}

        .chip, .receipt-tags span, .receipt-topline span, .receipt-meta span {{
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 0.28rem 0.58rem;
            font-size: 0.72rem;
            border: 1px solid rgba(255,255,255,0.09);
            background: rgba(255,255,255,0.06);
            color: #f4f7fb;
        }}

        .top-match {{
            font-size: 1rem;
            font-weight: 700;
            color: #ffd36e;
        }}

        .receipt-card {{
            position: relative;
            overflow: hidden;
            border-radius: 1.2rem;
            padding: 0.85rem;
            background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.04));
            border: 1px solid rgba(255,255,255,0.08);
            margin-bottom: 0.65rem;
        }}

        .receipt-card h3 {{
            font-size: 1.02rem;
            line-height: 1.1;
        }}

        .receipt-artist,
        .receipt-reasons {{
            font-size: 0.86rem;
            line-height: 1.35;
        }}

        .receipt-tags {{ margin-top: 0.7rem; }}

        .receipt-meter {{
            height: 0.48rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.08);
            overflow: hidden;
            margin: 0.8rem 0 0.55rem 0;
        }}

        .receipt-meter-fill {{
            height: 100%;
            border-radius: inherit;
            background: linear-gradient(90deg, #7ce4ff, #ff8bd4);
        }}

        .receipt-cutout {{
            position: absolute;
            top: 50%;
            width: 0.7rem;
            height: 0.7rem;
            border-radius: 999px;
            transform: translateY(-50%);
            background: #080b12;
            border: 1px solid rgba(255,255,255,0.08);
        }}

        .receipt-cutout-left {{ left: -0.35rem; }}
        .receipt-cutout-right {{ right: -0.35rem; }}

        .receipt-topline {{
            justify-content: space-between;
            margin-bottom: 0.35rem;
        }}

        .receipt-rank {{ color: #7ce4ff; font-weight: 700; }}
        .receipt-score {{ color: #ffd36e; font-weight: 700; }}
        </style>

        <div class="phone-shell">
            <div class="phone-screen">
                <div class="phone-notch"></div>
                <div class="now-playing">
                    <div class="section-label">Now playing</div>
                    <h2>Magic Jukebox</h2>
                    <div class="subtle">A polished, mobile-style reveal of your top matches.</div>
                    <div class="chip-row" style="margin-top: 0.85rem;">
                        <span class="chip">Genre first</span>
                        <span class="chip">Energy aware</span>
                        <span class="chip">Receipt view</span>
                    </div>
                </div>
                {top_match_html}
                {cards_html}
            </div>
        </div>
        """
    ).strip()


def render_receipt_card(song: Dict, score: float, reasons: str, rank: int) -> str:
    genre = song.get("genre", "")
    mood = song.get("mood", "")
    energy = float(song.get("energy", 0.0))
    tempo = int(round(float(song.get("tempo_bpm", 0.0))))

    return f"""
        <div class="receipt-card">
            <div class="receipt-cutout receipt-cutout-left"></div>
            <div class="receipt-cutout receipt-cutout-right"></div>
            <div class="receipt-topline">
                <span class="receipt-rank">#{rank}</span>
                <span class="receipt-score">Match {pretty_score(score)}</span>
            </div>
            <h3>{song.get('title', 'Untitled')}</h3>
            <p class="receipt-artist">{song.get('artist', 'Unknown Artist')}</p>
            <div class="receipt-tags">
                <span>{genre}</span>
                <span>{mood}</span>
                <span>{tempo} BPM</span>
            </div>
            <div class="receipt-meter">
                <div class="receipt-meter-fill" style="width: {max(8.0, min(score * 7.0, 100.0)):.1f}%"></div>
            </div>
            <div class="receipt-meta">
                <span>Energy {energy:.2f}</span>
                <span>{song.get('acousticness', 0.0):.2f} acoustic</span>
            </div>
            <p class="receipt-reasons">{reasons}</p>
        </div>
        """


def main() -> None:
    songs = get_songs()
    genres = sorted({song["genre"] for song in songs})
    moods = sorted({song["mood"] for song in songs})

    st.markdown(
        """
        <style>
        :root {
            --bg: #0d1117;
            --panel: rgba(18, 22, 32, 0.86);
            --panel-strong: #121826;
            --text: #f4f7fb;
            --muted: #a7b0c0;
            --accent: #7ce4ff;
            --accent-2: #ff8bd4;
            --gold: #ffd36e;
            --card: rgba(255, 255, 255, 0.07);
            --border: rgba(255, 255, 255, 0.12);
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(124, 228, 255, 0.16), transparent 28%),
                radial-gradient(circle at top right, rgba(255, 139, 212, 0.14), transparent 26%),
                linear-gradient(180deg, #070a10 0%, #0d1117 35%, #101723 100%);
            color: var(--text);
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(15, 20, 31, 0.96), rgba(11, 15, 24, 0.96));
            border-right: 1px solid rgba(255, 255, 255, 0.06);
            color: var(--text);
        }

        section[data-testid="stSidebar"] * {
            color: var(--text);
        }

        section[data-testid="stSidebar"] .stSelectbox label,
        section[data-testid="stSidebar"] .stSlider label,
        section[data-testid="stSidebar"] .stNumberInput label,
        section[data-testid="stSidebar"] .stTextInput label,
        section[data-testid="stSidebar"] .stRadio label,
        section[data-testid="stSidebar"] .stMultiSelect label {
            color: #f8fbff !important;
            font-weight: 600;
        }

        section[data-testid="stSidebar"] .stMarkdown,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] div,
        section[data-testid="stSidebar"] label {
            color: #f4f7fb;
        }

        section[data-testid="stSidebar"] [data-baseweb="select"] > div,
        section[data-testid="stSidebar"] [data-baseweb="input"] > div,
        section[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] {
            background: rgba(255, 255, 255, 0.06);
            border-color: rgba(124, 228, 255, 0.22);
        }

        section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div,
        section[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] [role="slider"] {
            color: #ffffff;
        }

        .hero {
            max-width: 980px;
            margin: 0 auto 1rem auto;
            padding: 1rem 0 0 0;
        }

        .eyebrow {
            color: var(--accent);
            letter-spacing: 0.18em;
            text-transform: uppercase;
            font-size: 0.72rem;
            font-weight: 700;
            margin-bottom: 0.35rem;
        }

        .hero h1 {
            font-size: clamp(2.3rem, 5vw, 4.8rem);
            line-height: 0.95;
            margin: 0;
            color: var(--text);
        }

        .hero p {
            max-width: 58ch;
            color: var(--muted);
            font-size: 1.02rem;
            margin-top: 0.75rem;
        }

        .phone-shell {
            max-width: min(430px, 100%);
            margin: 0 auto;
            padding: 0.9rem;
            border-radius: 2rem;
            background: linear-gradient(180deg, rgba(255,255,255,0.12), rgba(255,255,255,0.04));
            box-shadow: 0 30px 80px rgba(0, 0, 0, 0.38);
            border: 1px solid rgba(255,255,255,0.10);
        }

        .phone-screen {
            background: linear-gradient(180deg, rgba(15, 20, 31, 0.95), rgba(8, 10, 17, 0.96));
            border-radius: 1.5rem;
            padding: 0.8rem;
            max-height: calc(100vh - 6rem);
            overflow-y: auto;
            border: 1px solid rgba(255,255,255,0.06);
        }

        .phone-notch {
            width: 38%;
            height: 0.45rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.14);
            margin: 0 auto 1rem auto;
        }

        .now-playing {
            border-radius: 1.3rem;
            padding: 0.85rem;
            background: linear-gradient(135deg, rgba(124,228,255,0.18), rgba(255,139,212,0.14));
            border: 1px solid rgba(255,255,255,0.08);
            margin-bottom: 0.75rem;
        }

        .now-playing h2,
        .receipt-card h3 {
            margin: 0.25rem 0 0.1rem 0;
            color: var(--text);
        }

        .now-playing .subtle,
        .receipt-artist,
        .receipt-reasons,
        .utility {
            color: var(--muted);
        }

        .chip-row, .receipt-tags, .receipt-meta, .receipt-topline {
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
            align-items: center;
        }

        .chip, .receipt-tags span, .receipt-topline span, .receipt-meta span {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 0.34rem 0.7rem;
            font-size: 0.78rem;
            border: 1px solid rgba(255,255,255,0.09);
            background: rgba(255,255,255,0.06);
            color: var(--text);
        }

        .top-match {
            font-size: 1.05rem;
            font-weight: 700;
            color: var(--gold);
        }

        .receipt-card {
            position: relative;
            overflow: hidden;
            border-radius: 1.2rem;
            padding: 0.85rem 0.85rem 0.8rem 0.85rem;
            background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.04));
            border: 1px solid rgba(255,255,255,0.08);
            margin-bottom: 0.65rem;
        }

        .receipt-card::before {
            content: "";
            position: absolute;
            inset: 0;
            background: radial-gradient(circle at top right, rgba(124,228,255,0.10), transparent 35%);
            pointer-events: none;
        }

        .receipt-cutout {
            position: absolute;
            top: 50%;
            width: 0.7rem;
            height: 0.7rem;
            border-radius: 999px;
            transform: translateY(-50%);
            background: #080b12;
            border: 1px solid rgba(255,255,255,0.08);
        }

        .receipt-cutout-left { left: -0.35rem; }
        .receipt-cutout-right { right: -0.35rem; }

        .receipt-topline {
            justify-content: space-between;
            margin-bottom: 0.35rem;
        }

        .receipt-rank {
            color: var(--accent);
            font-weight: 700;
        }

        .receipt-score {
            color: var(--gold);
            font-weight: 700;
        }

        .receipt-tags { margin-top: 0.7rem; }

        .receipt-card h3 {
            font-size: 1.02rem;
            line-height: 1.1;
        }

        .receipt-artist,
        .receipt-reasons {
            font-size: 0.86rem;
            line-height: 1.35;
        }

        .receipt-tags span,
        .receipt-meta span,
        .chip {
            padding: 0.28rem 0.58rem;
            font-size: 0.72rem;
        }

        .phone-screen .section-label {
            margin-bottom: 0.5rem;
        }

        .phone-screen .top-match {
            font-size: 1rem;
        }

        @media (max-width: 900px) {
            .hero {
                max-width: 100%;
                padding-left: 0.25rem;
                padding-right: 0.25rem;
            }

            .phone-screen {
                max-height: none;
            }
        }

        .receipt-meter {
            height: 0.48rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.08);
            overflow: hidden;
            margin: 0.8rem 0 0.55rem 0;
        }

        .receipt-meter-fill {
            height: 100%;
            border-radius: inherit;
            background: linear-gradient(90deg, var(--accent), var(--accent-2));
        }

        .section-label {
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.14em;
            font-size: 0.72rem;
            font-weight: 700;
            margin-bottom: 0.65rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">Magic Jukebox</div>
            <h1>A recommendation app that feels like a polished phone screen.</h1>
            <p>
                Tune the vibe in the sidebar, then explore the highest-scoring songs in a tall, mobile-style
                layout with score chips, explanation snippets, and a receipt-like rhythm to the cards.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.title("Control Panel")
        st.caption("Adjust the vibe and let the harnessed recommender rank the catalog.")
        profile_name = st.selectbox("User profile", list(PROFILE_PRESETS.keys()), index=0)
        preset = resolve_profile(profile_name)

        favorite_genre = st.selectbox(
            "Favorite genre",
            genres,
            index=genres.index(str(preset["genre"])) if str(preset["genre"]) in genres else 0,
        )
        favorite_mood = st.selectbox(
            "Favorite mood",
            moods,
            index=moods.index(str(preset["mood"])) if str(preset["mood"]) in moods else 0,
        )
        target_energy = st.slider("Target energy", 0.0, 1.0, float(preset["energy"]), 0.01)
        target_tempo = st.slider("Target tempo (BPM)", 50, 180, int(preset["tempo"]), 1)
        target_valence = st.slider("Target valence", 0.0, 1.0, float(preset["valence"]), 0.01)
        target_danceability = st.slider("Target danceability", 0.0, 1.0, float(preset["danceability"]), 0.01)
        acoustic_preference = st.slider("Target acousticness", 0.0, 1.0, float(preset["acousticness"]), 0.01)
        k = st.slider("How many recommendations?", 3, 10, 5, 1)

        prefs = build_preferences(
            favorite_genre=favorite_genre,
            favorite_mood=favorite_mood,
            target_energy=target_energy,
            target_tempo=target_tempo,
            target_valence=target_valence,
            target_danceability=target_danceability,
            acoustic_preference=acoustic_preference,
        )

        st.markdown("<div class='section-label'>Selected profile</div>", unsafe_allow_html=True)
        st.json({"profile": profile_name, **prefs})

    recommendations = recommend_songs(prefs, songs, k=k)

    left, right = st.columns([0.92, 1.08], gap="large")

    with left:
        phone_html = build_phone_html(recommendations, profile_name)
        components.html(phone_html, height=820, scrolling=True)

    with right:
        st.markdown("<div class='section-label'>Why this works</div>", unsafe_allow_html=True)
        st.write(
            "The UI is intentionally built to feel like a modern phone app: a focused hero, a compact top-match strip, and receipt-style cards that make the reasons easy to scan."
        )
        st.write(
            "Because the data and scoring live in src/recommender.py, the visual layer stays thin. That makes it easy to keep the design pretty without hiding how the recommendations are computed."
        )
        st.markdown(
            """
            <div class="receipt-card">
                <div class="section-label">Profile Snapshot</div>
                <p class="receipt-reasons">
                    Genre, mood, energy, tempo, valence, danceability, and acousticness all influence the ranking.
                    That makes the results feel more like a curated set instead of a plain list.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div class='section-label'>Current preferences</div>", unsafe_allow_html=True)
        st.json(prefs)


if __name__ == "__main__":
    main()