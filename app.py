"""
VibeMatch web UI for the Music Recommender Simulation.

Run it with:
    streamlit run app.py

The scoring logic lives in src/recommender.py. This file only collects
preferences from sliders and dropdowns and shows the ranked results.
"""

import html
import random

import streamlit as st

from src.explain import heads_up, match_label, song_summary
from src.recommender import load_songs, recommend_songs

# --- Style guide -----------------------------------------------------------
# Core colors (the page colors are set in .streamlit/config.toml).
STAGE = "#1E1A2E"
RAISED = "#2A2540"
VIOLET = "#7C3AED"
LILAC = "#A78BFA"
MAGENTA = "#EC4899"
TEXT = "#F4F1FA"
MUTED_TEXT = "#A9A3BD"

# One-click vibes that set every slider at once.
PRESETS = {
    "Late-night R&B": {
        "genre": "r&b/soul", "mood": "moody", "energy": 0.50, "tempo": 85,
        "valence": 0.40, "danceability": 0.65, "acousticness": 0.25,
    },
    "Perreo party": {
        "genre": "urbano latino", "mood": "celebratory", "energy": 0.80, "tempo": 95,
        "valence": 0.80, "danceability": 0.85, "acousticness": 0.12,
    },
    "Bachata night": {
        "genre": "bachata", "mood": "romantic", "energy": 0.65, "tempo": 125,
        "valence": 0.60, "danceability": 0.78, "acousticness": 0.40,
    },
    "Afrobeats vibes": {
        "genre": "afrobeats", "mood": "uplifting", "energy": 0.70, "tempo": 102,
        "valence": 0.70, "danceability": 0.80, "acousticness": 0.15,
    },
    "Rock throwback": {
        "genre": "rock", "mood": "energetic", "energy": 0.90, "tempo": 140,
        "valence": 0.40, "danceability": 0.40, "acousticness": 0.02,
    },
    "Sad hours": {
        "genre": "pop", "mood": "sad", "energy": 0.35, "tempo": 90,
        "valence": 0.20, "danceability": 0.45, "acousticness": 0.65,
    },
}

# Starting profile, same as src/main.py.
DEFAULT_PROFILE = {
    "genre": "r&b/soul", "mood": "romantic", "energy": 0.55, "tempo": 90,
    "valence": 0.55, "danceability": 0.70, "acousticness": 0.25,
}

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500&family=Space+Grotesk:wght@500;700&display=swap');
html, body, [class*="css"], .stMarkdown, p, label {{ font-family: 'Inter', sans-serif; }}
h1, h2, h3 {{ font-family: 'Space Grotesk', sans-serif !important; }}
.vm-title {{ font-family: 'Space Grotesk', sans-serif; font-size: 2.6rem !important; font-weight: 700; line-height: 1.1;
  margin: 0; color: {TEXT}; }}
.vm-title span {{ color: {MAGENTA}; }}
.vm-tagline {{ color: {MUTED_TEXT}; margin: 0 0 1.5rem; }}
.vm-card {{ background: {STAGE}; border-radius: 14px; padding: 1rem 1.25rem; margin-bottom: 0.75rem; }}
.vm-row {{ display: flex; align-items: center; gap: 14px; }}
.vm-rank {{ width: 46px; height: 46px; border-radius: 10px; background: {RAISED}; color: {LILAC};
  display: flex; align-items: center; justify-content: center;
  font-family: 'Space Grotesk', sans-serif; font-size: 1.2rem; font-weight: 700; }}
.vm-rank.top {{ background: {MAGENTA}; color: #FFFFFF; }}
.vm-info {{ flex: 1; min-width: 0; }}
.vm-song {{ color: {TEXT}; font-size: 1.05rem; font-weight: 500; margin: 0; }}
.vm-meta {{ color: {MUTED_TEXT}; font-size: 0.88rem; margin: 0; }}
.vm-bar {{ flex: 1; height: 8px; border-radius: 4px; background: {RAISED}; }}
.vm-fill {{ height: 8px; border-radius: 4px; background: {VIOLET}; }}
.vm-summary {{ color: {MUTED_TEXT}; font-size: 0.9rem; margin: 12px 0 0; }}
.vm-warn {{ color: {LILAC}; font-size: 0.85rem; margin: 4px 0 0; }}
.vm-score {{ color: {TEXT}; font-weight: 500; font-size: 0.95rem; min-width: 110px; text-align: right; }}
</style>
"""


def get_songs():
    """Load the catalog (small enough to reread on every rerun)."""
    return load_songs("data/songs.csv")


def apply_settings(settings):
    """Copy a preset into the sidebar widgets (runs before they render)."""
    for key, value in settings.items():
        st.session_state[key] = value


def random_settings(genres, moods):
    """Build a random profile for the 'Surprise me' button."""
    return {
        "genre": random.choice(genres),
        "mood": random.choice(moods),
        "energy": round(random.random(), 2),
        "tempo": random.randint(60, 180),
        "valence": round(random.random(), 2),
        "danceability": round(random.random(), 2),
        "acousticness": round(random.random(), 2),
    }


def song_card(rank, song, score, user_prefs):
    """Return the HTML for one result card."""
    top_class = " top" if rank == 1 else ""
    warning = heads_up(user_prefs, song)
    warning_html = f'<p class="vm-warn">{html.escape(warning)}</p>' if warning else ""
    return f"""
<div class="vm-card">
  <div class="vm-row">
    <div class="vm-rank{top_class}">{rank}</div>
    <div class="vm-info">
      <p class="vm-song">{html.escape(song['title'])}</p>
      <p class="vm-meta">{html.escape(song['artist'])} · {html.escape(song['genre'])}</p>
    </div>
  </div>
  <div class="vm-row" style="margin-top:14px">
    <div class="vm-bar"><div class="vm-fill" style="width:{score:.0f}%"></div></div>
    <span class="vm-score">{match_label(score)}</span>
  </div>
  <p class="vm-summary">{html.escape(song_summary(song))}</p>
  {warning_html}
</div>
"""


def main():
    st.set_page_config(page_title="VibeMatch", page_icon="🎧", layout="centered")
    st.markdown(CSS, unsafe_allow_html=True)

    songs = get_songs()
    genres = sorted({song["genre"] for song in songs})
    moods = sorted({song["mood"] for song in songs})

    if "genre" not in st.session_state:
        apply_settings(DEFAULT_PROFILE)

    with st.sidebar:
        st.caption("Pick a vibe or move any slider. Your songs update right away, so there's no submit button.")
        st.header("Pick a vibe")
        preset_cols = st.columns(2)
        for index, (name, settings) in enumerate(PRESETS.items()):
            preset_cols[index % 2].button(
                name, on_click=apply_settings, args=(settings,), use_container_width=True
            )
        st.button(
            "Surprise me",
            on_click=lambda: apply_settings(random_settings(genres, moods)),
            type="primary",
            use_container_width=True,
        )

        st.header("Or tune it yourself")
        st.selectbox("Favorite genre", genres, key="genre")
        st.selectbox("Favorite mood", moods, key="mood")
        st.slider("Energy", 0.0, 1.0, step=0.01, key="energy",
                  help="0 = sleepy, 1 = full power")
        st.slider("Tempo (BPM)", 60, 180, step=1, key="tempo")
        st.slider("Happiness (valence)", 0.0, 1.0, step=0.01, key="valence",
                  help="0 = sad, 1 = joyful")
        st.slider("Danceability", 0.0, 1.0, step=0.01, key="danceability")
        st.slider("Acousticness", 0.0, 1.0, step=0.01, key="acousticness",
                  help="0 = electronic, 1 = unplugged")
        count = st.slider("How many songs", 1, 10, 5)

    user_prefs = {
        "favorite_genre": st.session_state.genre,
        "favorite_mood": st.session_state.mood,
        "target_energy": st.session_state.energy,
        "target_tempo": st.session_state.tempo,
        "target_valence": st.session_state.valence,
        "target_danceability": st.session_state.danceability,
        "target_acousticness": st.session_state.acousticness,
    }

    st.markdown('<div class="vm-title">Vibe<span>Match</span></div>', unsafe_allow_html=True)
    st.markdown(
        f'<p class="vm-tagline">Your top {count} matches for '
        f'<b>{html.escape(user_prefs["favorite_mood"])}</b> '
        f'<b>{html.escape(user_prefs["favorite_genre"])}</b>, '
        f'out of {len(songs)} songs.</p>',
        unsafe_allow_html=True,
    )

    for rank, (song, score, _points) in enumerate(
        recommend_songs(user_prefs, songs, k=count), start=1
    ):
        st.markdown(song_card(rank, song, score, user_prefs), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
