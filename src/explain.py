"""
Plain-language text for the web UI.

score_song() returns point-by-point reasons, which are useful for testing
but mean nothing to a listener. These helpers describe each song in one
short sentence and add a heads-up only when the energy is noticeably off.
"""

from typing import Dict, Optional

from src.recommender import MOOD_CLUSTERS

# How each mood cluster sounds, as one everyday adjective.
CLUSTER_WORDS = {
    "Calm": "laid-back",
    "Happy": "upbeat",
    "Intense": "intense",
    "Energetic": "high-energy",
    "Romantic": "romantic",
    "Longing": "wistful",
    "Moody": "moody",
}

NOTICEABLE = 0.20  # Energy gap big enough to warn about.


def mood_cluster(mood: str) -> Optional[str]:
    """Return the cluster name for a mood, or None if it has no cluster."""
    mood = mood.strip().casefold()
    return next((name for name, moods in MOOD_CLUSTERS.items() if mood in moods), None)


def match_label(score: float) -> str:
    """Turn a 0-100 score into a short label a listener understands."""
    if score >= 90:
        return "Perfect match"
    if score >= 75:
        return "Great match"
    if score >= 60:
        return "Good match"
    return "Worth a try"


def song_summary(song: Dict) -> str:
    """Describe the song in one sentence, e.g. 'A romantic r&b/soul song made for dancing.'"""
    feel = CLUSTER_WORDS.get(mood_cluster(str(song["mood"])), "")
    words = f"{feel} {song['genre']}".strip()
    article = "An" if words[0].lower() in "aeiou" else "A"

    # Add the one trait that stands out most, if any.
    if float(song["danceability"]) >= 0.75:
        detail = " made for dancing"
    elif float(song["acousticness"]) >= 0.6:
        detail = " with a soft, acoustic sound"
    elif float(song["energy"]) >= 0.85 and feel != "high-energy":
        detail = " with nonstop energy"
    elif float(song["tempo_bpm"]) < 80:
        detail = " with a slow, easy pace"
    else:
        detail = ""
    return f"{article} {words} song{detail}."


def heads_up(user_prefs: Dict, song: Dict) -> Optional[str]:
    """Warn only when the song's energy is far from what the listener asked for."""
    gap = float(song["energy"]) - float(user_prefs["target_energy"])
    if gap >= NOTICEABLE:
        return "Heads up: it's more hype than you asked for."
    if gap <= -NOTICEABLE:
        return "Heads up: it's more chill than you asked for."
    return None
