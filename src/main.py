"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs


def main() -> None:
    """Load songs and print the top personalized recommendations."""
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    user_prefs = {
        "favorite_genre": "lofi",
        "favorite_mood": "chill",
        "target_energy": 0.4,
        "target_tempo": 78,
        "target_valence": 0.58,
        "target_danceability": 0.60,
        "target_acousticness": 0.78,
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print(f"\nTop {len(recommendations)} recommendations")
    print("=" * 60)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{rank}. {song['title']}")
        print(f"   Final score: {score:.2f} / 100")
        print("   Reasons:")
        for reason in explanation.split("; "):
            print(f"   - {reason}")
        print("-" * 60)


if __name__ == "__main__":
    main()
