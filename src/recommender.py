from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import csv

# --- Experiment: weight shift -------------------------------------------
# Original weights: genre 20, energy 20 (max score 100).
# Experiment: halve genre (20 -> 10) and double energy (20 -> 40).
# To undo, set GENRE_POINTS = 20 and ENERGY_WEIGHT = 20.
MOOD_POINTS = 30
MOOD_CLUSTER_POINTS = 15
GENRE_POINTS = 10
ENERGY_WEIGHT = 40
VALENCE_WEIGHT = 10
DANCEABILITY_WEIGHT = 8
ACOUSTICNESS_WEIGHT = 7
TEMPO_WEIGHT = 5

# Highest possible raw score. With the experiment weights this is 110,
# so scores are rescaled to stay on a 0-100 scale.
MAX_RAW_SCORE = (
    MOOD_POINTS
    + GENRE_POINTS
    + ENERGY_WEIGHT
    + VALENCE_WEIGHT
    + DANCEABILITY_WEIGHT
    + ACOUSTICNESS_WEIGHT
    + TEMPO_WEIGHT
)


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """

    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """

    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"


def load_songs(csv_path: str) -> List[Dict]:
    """Load song rows from a CSV file and convert numeric fields."""
    numeric_fields = (
        "energy",
        "tempo_bpm",
        "valence",
        "danceability",
        "acousticness",
    )
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as csv_file:
        for song in csv.DictReader(csv_file):
            song["id"] = int(song["id"])
            for field in numeric_fields:
                song[field] = float(song[field])
            songs.append(song)
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against the user's preferences and explain the points."""
    mood_clusters = {
        "Calm": {"chill", "relaxed", "peaceful", "focused", "dreamy", "reflective"},
        "Happy": {
            "happy",
            "uplifting",
            "euphoric",
            "celebratory",
            "carefree",
            "playful",
            "whimsical",
            "mischievous",
        },
        "Intense": {
            "intense",
            "angry",
            "aggressive",
            "anxious",
            "rebellious",
            "overwhelmed",
        },
        "Energetic": {"energetic", "confident", "determined", "adventurous"},
        "Romantic": {"romantic", "passionate"},
        "Longing": {"sad", "melancholic", "yearning", "nostalgic"},
        "Moody": {"moody", "mysterious", "uncertain"},
    }

    score = 0.0
    reasons = []
    favorite_mood = str(user_prefs["favorite_mood"]).strip().casefold()
    song_mood = str(song["mood"]).strip().casefold()

    if song_mood == favorite_mood:
        score += MOOD_POINTS
        reasons.append(f"mood match: {song['mood']} (+{MOOD_POINTS} points)")
    else:
        favorite_cluster = next(
            (name for name, moods in mood_clusters.items() if favorite_mood in moods),
            None,
        )
        song_cluster = next(
            (name for name, moods in mood_clusters.items() if song_mood in moods),
            None,
        )
        if favorite_cluster is not None and favorite_cluster == song_cluster:
            score += MOOD_CLUSTER_POINTS
            reasons.append(
                f"mood cluster match: {favorite_cluster} (+{MOOD_CLUSTER_POINTS} points)"
            )

    favorite_genre = str(user_prefs["favorite_genre"]).strip().casefold()
    song_genre = str(song["genre"]).strip().casefold()
    if song_genre == favorite_genre:
        score += GENRE_POINTS
        reasons.append(f"genre match: {song['genre']} (+{GENRE_POINTS} points)")

    numeric_features = (
        ("energy", "target_energy", ENERGY_WEIGHT, 1),
        ("valence", "target_valence", VALENCE_WEIGHT, 1),
        ("danceability", "target_danceability", DANCEABILITY_WEIGHT, 1),
        ("acousticness", "target_acousticness", ACOUSTICNESS_WEIGHT, 1),
        ("tempo_bpm", "target_tempo", TEMPO_WEIGHT, 120),
    )
    for song_key, target_key, weight, scale in numeric_features:
        song_value = float(song[song_key])
        target_value = float(user_prefs[target_key])
        closeness = max(0.0, 1.0 - abs(song_value - target_value) / scale)
        points = closeness * weight
        score += points
        feature_name = "tempo" if song_key == "tempo_bpm" else song_key
        reasons.append(f"{feature_name} closeness: {points:.2f}/{weight} points")

    # Rescale so the final score is always out of 100, whatever the weights.
    final_score = score / MAX_RAW_SCORE * 100
    return final_score, reasons


def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5
) -> List[Tuple[Dict, float, str]]:
    """Return the top k songs ranked by preference score."""
    scored_songs = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = "; ".join(reasons)
        scored_songs.append((song, score, explanation))

    return sorted(scored_songs, key=lambda result: result[1], reverse=True)[:k]
