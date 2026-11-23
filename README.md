# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real-world music recommenders often combine song attributes with listening behavior, such as plays, skips, and saves, to predict what a listener may enjoy and rank those options. This project uses a simpler content-based approach: it compares each song's genre and mood with the user's preferences, and scores how close each numeric feature (energy, tempo, valence, danceability, acousticness) is to the user's target. A weighted score prioritizes the closest matches; unlike larger systems, this version does not learn from listening history or other users.

Each `Song` stores `id`, `title`, `artist`, `genre`, `mood`, `energy`, `tempo_bpm`, `valence`, `danceability`, and `acousticness`. The user's taste profile is a dictionary with a favorite genre, a favorite mood, and a target value for each numeric feature. The scoring rule uses all of these features: genre and mood are matched as labels, and every numeric feature is scored by how close it is to the user's target value.

### Implementation Plan

1. **Load the data.** `load_songs()` reads `data/songs.csv` with `csv.DictReader` and converts the numeric columns (`energy`, `tempo_bpm`, `valence`, `danceability`, `acousticness`) from text to numbers.
2. **Define the taste profile.** Store the user's preferences as a `user_prefs` dictionary (see below).
3. **Score one song.** `score_song(user_prefs, song)` applies the Algorithm Recipe and returns `(score, reasons)`.
4. **Score and rank every song.** `recommend_songs(user_prefs, songs, k)` loops over all songs, scores each one, sorts the results, and returns the top `k` as `(song, score, explanation)`.
5. **Connect the class version.** `Recommender.recommend()` and `Recommender.explain_recommendation()` reuse the same scoring logic so the tests in `tests/test_recommender.py` pass.
6. **Test and compare.** Check the results against the expected top 5 below, then run 3–4 different profiles (for example "late-night r&b", "rock throwback", "perreo party") to see whether the rankings make sense for each one.

### Taste Profile

The recommender compares every song against a user profile stored as a dictionary. The example profile is a "romantic R&B" listener: mid-tempo, smooth, and danceable, close to how my favorite r&b/soul songs sound.

```python
user_prefs = {
    "favorite_genre": "r&b/soul",
    "favorite_mood": "romantic",
    "target_energy": 0.55,
    "target_tempo": 90,
    "target_valence": 0.55,
    "target_danceability": 0.70,
    "target_acousticness": 0.25,
}
```

### Algorithm Recipe

**Scoring rule (one song, 0–100 points)**

| Feature | Max points | How it is scored |
|---|---|---|
| Mood | 30 | 30 for an exact match, 15 for a mood in the same cluster, 0 otherwise |
| Genre | 10 | 10 for an exact match, 0 otherwise |
| Energy | 40 | `(1 - abs(song - target)) * 40` |
| Valence | 10 | `(1 - abs(song - target)) * 10` |
| Danceability | 8 | `(1 - abs(song - target)) * 8` |
| Acousticness | 7 | `(1 - abs(song - target)) * 7` |
| Tempo | 5 | `(1 - abs(song_bpm - target_bpm) / 120) * 5` |

The points add up to 110, so the total is rescaled to a 0–100 score. (My first version used genre 20 and energy 20; see the model card for that experiment.)

Rules that apply to every numeric feature:

- **Closeness, not size.** A song scores highest when it is near the target, whether it is above or below it.
- **Tempo is normalized.** BPM is divided by 120 so it is on the same 0–1 scale as the other features.
- **No negative points.** Any closeness value below 0 is set to 0.
- **Reasons are recorded.** Each rule that awards points adds a short reason, such as `"mood match: focused"`, to explain the recommendation.

**Mood clusters (partial credit)**

Most moods appear only once or twice in the dataset, so exact matching alone would give almost every song 0 mood points. Similar moods are grouped so a near match earns half credit:

| Cluster | Moods |
|---|---|
| Calm | chill, relaxed, peaceful, focused, dreamy, reflective |
| Happy | happy, uplifting, euphoric, celebratory, carefree, playful, whimsical, mischievous |
| Intense | intense, angry, aggressive, anxious, rebellious, overwhelmed |
| Energetic | energetic, confident, determined, adventurous |
| Romantic | romantic, passionate |
| Longing | sad, melancholic, yearning, nostalgic |
| Moody | moody, mysterious, uncertain |

Mood (30) is weighted above genre (10) because mood describes how the listener wants to feel, and listeners cross genre lines more often than mood lines. Genre gets no partial credit for now.

**Ranking rule (all songs)**

1. Score every song in `songs.csv` with the scoring rule.
2. Sort from highest to lowest score.
3. Break ties by putting the song whose energy is closer to the target first.
4. Return the top `k` songs (default 5), each with its score and explanation.

### Data Flow

```mermaid
flowchart TD
    A["Input: user_prefs dictionary"] --> B["Load songs.csv"]
    B --> C{"For each song"}
    C --> D["score_song(user_prefs, song)<br/>returns score + reasons"]
    D --> E["Add (song, score, reasons) to results"]
    E --> C
    C -- "all songs scored" --> F["Rank: sort high to low, break ties"]
    F --> G["Output: top k recommendations"]
```

### Sample Recommendation Output

Output from running `python -m src.main` with the current profile in `src/main.py`:

```text
Loaded songs: 60

Top 5 recommendations
============================================================
1. StreetLove
   Final score: 99.01 / 100
   Reasons:
   - mood match: romantic (+30 points)
   - genre match: r&b/soul (+10 points)
   - energy closeness: 40.00/40 points
   - valence closeness: 9.50/10 points
   - danceability closeness: 7.84/8 points
   - acousticness closeness: 6.65/7 points
   - tempo closeness: 4.92/5 points
------------------------------------------------------------
2. True Colors
   Final score: 98.47 / 100
   Reasons:
   - mood match: romantic (+30 points)
   - genre match: r&b/soul (+10 points)
   - energy closeness: 40.00/40 points
   - valence closeness: 9.50/10 points
   - danceability closeness: 8.00/8 points
   - acousticness closeness: 6.65/7 points
   - tempo closeness: 4.17/5 points
------------------------------------------------------------
3. Twisted
   Final score: 97.80 / 100
   Reasons:
   - mood match: romantic (+30 points)
   - genre match: r&b/soul (+10 points)
   - energy closeness: 40.00/40 points
   - valence closeness: 9.00/10 points
   - danceability closeness: 7.36/8 points
   - acousticness closeness: 6.30/7 points
   - tempo closeness: 4.92/5 points
------------------------------------------------------------
4. Si El Mundo Se Acabara
   Final score: 85.56 / 100
   Reasons:
   - mood match: romantic (+30 points)
   - energy closeness: 36.00/40 points
   - valence closeness: 9.50/10 points
   - danceability closeness: 7.36/8 points
   - acousticness closeness: 6.51/7 points
   - tempo closeness: 4.75/5 points
------------------------------------------------------------
5. Ibiza (feat. Romeo Santos)
   Final score: 83.83 / 100
   Reasons:
   - mood match: romantic (+30 points)
   - energy closeness: 34.80/40 points
   - valence closeness: 8.90/10 points
   - danceability closeness: 7.20/8 points
   - acousticness closeness: 6.65/7 points
   - tempo closeness: 4.67/5 points
------------------------------------------------------------
```

### Expected Results for the Example Profile

Running the current recipe on the 60-song dataset gives:

| Rank | Song | Genre / Mood | Score |
|---|---|---|---|
| 1 | StreetLove | r&b/soul / romantic | 99.0 |
| 2 | True Colors | r&b/soul / romantic | 98.5 |
| 3 | Twisted | r&b/soul / romantic | 97.8 |
| 4 | Si El Mundo Se Acabara | urbano latino / romantic | 85.6 |
| 5 | Ibiza (feat. Romeo Santos) | urbano latino / romantic | 83.8 |

The lowest-scoring songs are Split in De Middle (soca / celebratory, 42.0) and Mr. Brightside (rock / anxious, 41.1). These numbers are a target for testing the implementation.

### Potential Biases

- **Labels can outweigh sound.** Mood and genre together are worth 40 of the 110 raw points. A song with matching labels but a poor numeric fit can beat a song that sounds right but has different labels.
- **Mood is favored over genre.** Mood is weighted 30 and genre 10, so a song in the user's favorite genre with an unrelated mood may be ranked below songs from other genres. For the example profile, romantic bachata and afrobeats songs rank 6th–11th, while the confident urbano latino song *Se Preparó* ranks 35th.
- **Exact genre matching ignores close neighbors.** An r&b/soul fan gets no genre credit for pop songs like *off the table* (Ariana Grande and The Weeknd), so great songs in similar genres can be buried.
- **The catalog is unbalanced.** It follows my own library: r&b/soul has 16 songs, urbano latino and pop have 10 each, and house, soca, j-pop, jazz, and hip-hop/rap have only 1. Users whose favorite genre has more songs get more strong matches to choose from.
- **The example profile leans toward r&b/soul.** Its numeric targets describe smooth, mid-tempo r&b, so it naturally favors that sound over other music.
- **The mood clusters reflect personal judgment.** Grouping moods like "nostalgic" with "sad" is a subjective choice. Another person might group them differently and get different recommendations.

### Known Limitations

- Genre is exact-match only, so similar genres (for example r&b/soul and pop) get no credit for being close.
- Mood clusters are hand-made and reflect one person's judgment.
- Labels (mood + genre) can still be worth 40 of the 110 raw points, so a song with matching labels but poor numeric fit can rank high.
- The system does not learn from listening history or other users, so it cannot do collaborative filtering.
- The profile allows only one favorite genre and one favorite mood. Real listeners often like several. For example, a listener who enjoys hip-hop/rap, r&b/soul, afrobeats, urbano latino, and bachata has to pick just one (r&b/soul). With the example profile, the urbano latino song *Se Preparó* ranks 35th of 60 because the other four favorite genres earn no genre points. A list such as `"favorite_genres": ["hip-hop/rap", "r&b/soul", "afrobeats", "urbano latino", "bachata"]` would fix this.
- There is no way to mark a feature as "I don't care," so every feature always counts toward the score.
- Distance is treated the same on both sides of a target. With a target energy of 0.55, songs at 0.45 and 0.65 score the same, even though a late-night listener might prefer the quieter one.


---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app in the terminal:

```bash
python -m src.main
```

4. Or run the web UI (VibeMatch):

```bash
streamlit run app.py
```

It opens at http://localhost:8502. (It uses port 8502 so it can run at the same time as my Project 4 app, which uses 8501.) Pick a preset vibe in the sidebar (Late-night R&B, Perreo party, Bachata night, Afrobeats vibes, Rock throwback, Sad hours), press "Surprise me", or move the sliders, and the top songs update right away. Each card shows a match label (Perfect, Great, Good, or Worth a try) and a one-sentence summary, such as "A wistful pop song with a soft, acoustic sound." If a song's energy is far from what you asked for, the card adds a short heads-up, such as "Heads up: it's more hype than you asked for." Press `Ctrl+C` in the terminal to stop it.

The web UI hides point totals and mood labels on purpose; the terminal version (`python -m src.main`) still prints the point-by-point breakdown for testing. The plain-language text comes from `src/explain.py`, the theme colors are in `.streamlit/config.toml`, and the card styles are in `app.py`.

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
# e.g.:
# User profile: genre=indie, mood=chill, energy=low
# Recommendations:
#   1. ...
#   2. ...
#   3. ...
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



