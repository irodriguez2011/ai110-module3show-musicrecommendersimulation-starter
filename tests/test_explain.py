from src.explain import heads_up, match_label, song_summary

PREFS = {
    "favorite_genre": "afrobeats",
    "favorite_mood": "uplifting",
    "target_energy": 0.70,
    "target_tempo": 102,
    "target_valence": 0.70,
    "target_danceability": 0.80,
    "target_acousticness": 0.15,
}


def make_song(**changes):
    song = {
        "title": "Test Song", "artist": "Test Artist", "genre": "afrobeats",
        "mood": "uplifting", "energy": 0.70, "tempo_bpm": 104, "valence": 0.70,
        "danceability": 0.80, "acousticness": 0.12,
    }
    song.update(changes)
    return song


def test_summary_is_one_plain_sentence():
    assert song_summary(make_song()) == "An upbeat afrobeats song made for dancing."
    assert song_summary(make_song(mood="sad", genre="pop", danceability=0.3,
                                  acousticness=0.9)) == "A wistful pop song with a soft, acoustic sound."


def test_summary_never_shows_mood_labels():
    summary = song_summary(make_song(mood="confident"))
    assert "confident" not in summary
    assert summary.startswith("A high-energy")


def test_heads_up_only_when_energy_is_far_off():
    assert heads_up(PREFS, make_song()) is None
    assert heads_up(PREFS, make_song(energy=0.95)) == "Heads up: it's more hype than you asked for."
    assert heads_up(PREFS, make_song(energy=0.30)) == "Heads up: it's more chill than you asked for."


def test_match_label_bands():
    assert match_label(95) == "Perfect match"
    assert match_label(80) == "Great match"
    assert match_label(65) == "Good match"
    assert match_label(40) == "Worth a try"
