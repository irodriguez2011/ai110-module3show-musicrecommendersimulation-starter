# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeMatch 1.0**

---

## 2. Goal / Task

VibeMatch suggests songs a listener will probably enjoy.

- The user describes their taste: one favorite genre, one favorite mood, and target values for energy, tempo, valence, danceability, and acousticness.
- The system gives every song a score from 0 to 100.
- It returns the top 5 songs, with reasons showing where each song's points came from.

It does not predict a rating or a play. It ranks songs by how closely they match the user's stated taste.

---

## 3. Data Used

- **Size:** 53 songs in `data/songs.csv`.
- **Variety:** 41 genres and 33 moods.
- **Features per song:** title, artist, genre, mood, energy, tempo (BPM), valence, danceability, and acousticness.
- **Where the songs came from:**
  - Songs 1–10 came with the starter project.
  - Songs 11–45 are made-up songs I added to cover more genres and moods.
  - Songs 46–53 are real songs by artists I listen to. Their feature values are estimates, not official data.

**Limits of the data:**

- Most genres have only 1 or 2 songs. The biggest is bachata, with 4.
- Most songs are made up, so nobody can judge them by ear.
- The real songs' numbers are guesses about how they sound.
- There is no listening history, like plays, skips, or likes.
- There is no information about lyrics, language, or release year.

---

## 4. Algorithm Summary

Each song earns points in two ways.

**1. Label matches**

- **Mood:** 30 points for an exact match. 15 points if the mood is in the same group, like "chill" and "relaxed."
- **Genre:** 10 points for an exact match. There is no partial credit.

**2. Sound matches (closeness)**

A song earns more points the **closer** it is to the user's target. Being higher or lower than the target does not matter. Only the distance counts.

| Feature | Max points |
|---|---|
| Energy | 40 |
| Valence | 10 |
| Danceability | 8 |
| Acousticness | 7 |
| Tempo | 5 |

- Tempo is divided by 120 first, so it is on the same 0–1 scale as the other features.
- A feature can never give negative points.

**3. Final score and ranking**

- The points add up to a maximum of 110. The total is rescaled so every score is out of 100.
- The system scores every song, sorts them from highest to lowest, and returns the top 5.

**Note:** these are my experiment weights. My first version used genre 20 and energy 20. I halved genre and doubled energy to test how sensitive the rankings are (see Evaluation).

---

## 5. Observed Behavior / Biases

**What works well**

- When a song matches the genre, the mood, and the sound, it lands at the top. For a "chill lofi" listener, the top 3 are all calm lofi songs.
- Mood groups help. Calm songs from other genres, like ambient and jazz, still show up for a chill listener.
- Loud, intense songs (metal, punk) correctly sink to the bottom for calm listeners.

**Single-genre limit**

- The profile allows only one favorite genre, but I like five: hip-hop, r&b, afrobeats, reggaeton, and bachata.
- I had to pick r&b. The other four genres get no genre points.
- A real reggaeton song I like ranked only 10th.

**No concept of artist**

- The system doesn't know who made a song.
- Two songs by my favorite artist landed far apart: one ranked 8th and the other ranked 36th. The second one is slower and darker than my targets.
- I like everything by that artist, but the system can't learn that.

**Labels can beat sound**

- With my first weights (genre 20), a made-up r&b song ranked 1st for my profile. It beat real songs that matched my sound better.
- One label match was worth more than all the sound differences combined.

**Mood can override genre**

- For a "rock + sad" listener, the pop song "Heartbreak Disco" ranked 1st, above the rock song "Storm Runner."
- An exact mood match (30 points) is worth far more than a genre match (10 points).
- This could frustrate users who see genre as a must-have.

**Unbalanced catalog**

- Most genres have only one song. Listeners whose genre has more songs get more strong matches.

---

## 6. Evaluation Process

I tested the system in four ways.

**1. A simple "chill lofi" profile**

- Genre lofi, mood chill, low energy, acoustic.
- The top 5 were calm lofi, ambient, and jazz songs. This matched what I expected.

**2. My own music taste**

- I built a profile from my real taste: r&b, romantic, upbeat, and danceable.
- I added real songs by artists I like and checked where they ranked.
- With the first weights, 4 of the top 5 were artists I like. A made-up r&b song was 1st.
- After the weight change, a real afrobeats song I like moved to 1st.
- One song by my favorite artist stayed near the bottom (36th).

**3. Edge-case profiles**

I tried three tricky profiles to see where the system breaks.

**High energy + sad mood** (`rock`, `sad`; energy `0.9`, tempo `150`, valence `0.1`, danceability `0.8`, acousticness `0.1`):

```text
1. Heartbreak Disco | 84.16 / 100
2. Storm Runner | 67.82 / 100
3. Last Train to Vela | 60.91 / 100
4. Redline Reverie | 58.70 / 100
5. Velvet Static | 57.57 / 100
```

**Lofi + angry mood + conflicting numbers** (`lofi`, `angry`; energy `0.9`, tempo `60`, valence `0.9`, danceability `0.1`, acousticness `1.0`):

```text
1. Garage Riot | 71.78 / 100
2. Iron Furnace | 69.37 / 100
3. Gym Hero | 60.55 / 100
4. Sidewalk Static | 60.22 / 100
5. Storm Runner | 59.81 / 100
```

**Unknown labels + impossible numbers** (`unknown`, `unknown`; energy `1.5`, tempo `-100`, valence `-1.0`, danceability `2.0`, acousticness `2.0`):

```text
1. Iron Furnace | 17.09 / 100
2. Redline Reverie | 17.09 / 100
3. Velvet Static | 16.73 / 100
4. Garage Riot | 16.00 / 100
5. Canopy Run | 16.00 / 100
```

What I learned from these:

- **Mood wins.** In the angry profile, the exact "angry" mood pushed punk and metal above lofi, even though lofi was the chosen genre.
- **Gym Hero was a surprise.** It is pop, and it fits that profile's numbers poorly. It still reached 3rd, because its "intense" mood is grouped with "angry" and its energy is high.
- **Bad inputs give low scores, not errors.** With impossible targets, almost every feature earned 0. Only energy still mattered, so the loudest songs won with very low scores.
- **Ties are not handled.** Iron Furnace and Redline Reverie tied at 17.09. Their order just came from their order in the CSV.

**4. Weight-shift experiment**

- I halved genre (20 → 10) and doubled energy (20 → 40).
- The max score became 110, so I rescaled scores back to 100. I checked that a perfect song scores 100 and the worst scores 0.
- **Chill lofi profile:** the top 5 stayed in the same order. Only the scores changed.
- **My profile:** a real afrobeats song that sounds more like my taste moved from 2nd to 1st.
- **Verdict:** a little more accurate for me, but mostly just different. It did not fix the single-genre problem or the favorite-artist problem.

---

## 7. Intended Use and Non-Intended Use

**Intended use**

- A classroom project to learn how recommender systems work.
- Exploring how scoring weights change rankings.
- Small tests with a short, hand-made song list.

**Not intended for**

- Real users or a real music app.
- Large catalogs. It checks every song one by one.
- Judging the quality of an artist or song. The numbers are estimates and labels.
- Any decision that affects people, like which artists get promoted or paid.

---

## 8. Ideas for Improvement

1. **Allow several favorite genres and moods.** For example, `["hip-hop", "r&b", "afrobeats", "reggaeton", "bachata"]`. This would fix the single-genre problem.
   - Right now the code compares the song's genre to one string with `==`. Passing a list would quietly give every song 0 genre points.
   - The fix: accept a string or a list, then check `if song_genre in favorite_genres`. A single genre would still work, so old profiles and tests keep working.
2. **Add artist preferences.** Let users name favorite artists and give those songs bonus points, so every song by a favorite artist gets credit, not just the ones that match the numbers.
3. **Learn from behavior.** Use likes and skips to adjust the targets over time. This would move the system toward collaborative filtering, like Spotify and YouTube use.

Smaller fixes:

- Add a tie-break rule, such as "closer energy wins."
- Check that numeric targets are in a valid range before scoring.

---

## 9. Personal Reflection

**My biggest learning moment**

My biggest moment came when I tested the system on my own taste. At first I judged songs that were made up. I didn't know any of them, so I was just guessing. My "intuition" test meant nothing.

Then I added real songs by artists I actually listen to. That changed everything. Right away I saw real problems. I like five genres, but the profile only lets me pick one. Two songs by my favorite artist landed at 8th and 36th. The system had no idea they were by the same artist.

I learned that you can only test a recommender with data you actually understand.

**How AI tools helped, and when I double-checked them**

AI helped me:

- Research how Spotify and YouTube make recommendations.
- Turn my ideas into clear prompts.
- Design and compare scoring rules.
- Add songs to the dataset and write up results.

I still had to check its work:

- I asked two AI tools for a scoring design and compared them. One had an energy formula missing parentheses. Read literally, it could give negative points.
- Its suggested mood groups didn't cover all the moods in my dataset.
- I checked the math in another AI's critique before trusting it.
- When I changed the weights, the max score became 110, not 100. I had to rescale it and test that a perfect song still scored 100.
- Some of my written "expected results" went out of date after each change, so I had to keep them in sync.

AI was fast, but I needed to verify the numbers myself.

**What surprised me**

I was surprised how "smart" a few simple rules can feel. The system just adds up points. But for a chill lofi listener, it picked calm songs that really fit together. The printed reasons, like "mood match (+30 points)," made it feel even more thoughtful.

It also fooled me in the other direction. Some results looked reasonable but happened for the wrong reason. A song once ranked first just because of its genre label, not because it sounded right.

**What I would try next**

- Let users pick several genres and favorite artists.
- Use likes and skips to learn what someone really enjoys, like real apps do.
- Use real song data instead of estimates.
- Add a tie-break rule and check for bad inputs.
- Try mixing in a little variety, so the top 5 isn't always the same type of song.
