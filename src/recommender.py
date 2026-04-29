import csv
from dataclasses import asdict, dataclass
from typing import List, Dict, Tuple, Optional

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
        """Initialize recommender with a list of songs."""
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return top k songs recommended for the user."""
        user_prefs = self._user_profile_to_preferences(user)
        scored_songs = [
            (song, score_song(user_prefs, asdict(song))[0])
            for song in self.songs
        ]
        ranked_songs = sorted(scored_songs, key=lambda item: item[1], reverse=True)
        return [song for song, _ in ranked_songs[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Explain why a song was recommended to the user."""
        user_prefs = self._user_profile_to_preferences(user)
        _, reasons = score_song(user_prefs, asdict(song))
        if reasons:
            return f"Recommended because it matches your preferences: {', '.join(reasons)}."
        return "Recommended because it is a reasonable fit for your taste profile."

    @staticmethod
    def _user_profile_to_preferences(user: UserProfile) -> Dict[str, object]:
        """Convert a typed profile into the dictionary shape used by score_song()."""
        return {
            "favorite_genre": user.favorite_genre,
            "favorite_mood": user.favorite_mood,
            "target_energy": user.target_energy,
            "targetAcousticness": 0.85 if user.likes_acoustic else 0.15,
        }

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    songs: List[Dict] = []

    with open(csv_path, newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            song: Dict = {}
            for key, value in row.items():
                if value is None:
                    song[key] = value
                    continue

                value = value.strip()
                if key == "id":
                    song[key] = int(value)
                elif key in {
                    "energy",
                    "tempo_bpm",
                    "valence",
                    "danceability",
                    "acousticness",
                }:
                    song[key] = float(value)
                else:
                    song[key] = value

            songs.append(song)

    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """
    reasons: List[str] = []
    score = 0.0

    preferred_genre = user_prefs.get("genre") or user_prefs.get("favorite_genre")
    preferred_mood = user_prefs.get("mood") or user_prefs.get("favorite_mood")
    target_energy = user_prefs.get("targetEnergy", user_prefs.get("energy", user_prefs.get("target_energy", 0.0)))
    target_tempo = user_prefs.get("targetTempo", user_prefs.get("tempo_bpm", user_prefs.get("target_tempo")))
    target_valence = user_prefs.get("targetValence", user_prefs.get("valence", user_prefs.get("target_valence")))
    target_danceability = user_prefs.get(
        "targetDanceability",
        user_prefs.get("danceability", user_prefs.get("target_danceability")),
    )
    target_acousticness = user_prefs.get(
        "targetAcousticness",
        user_prefs.get("acousticness", user_prefs.get("target_acousticness")),
    )
    preferred_artist = user_prefs.get("artist") or user_prefs.get("preferred_artist")

    genre = str(song.get("genre", "")).strip().lower()
    mood = str(song.get("mood", "")).strip().lower()

    if preferred_genre and genre == str(preferred_genre).strip().lower():
        score += 2.0
        reasons.append("genre match (+2)")

    if preferred_mood and mood == str(preferred_mood).strip().lower():
        score += 1.0
        reasons.append("mood match (+1)")

    if preferred_artist and str(song.get("artist", "")).strip().lower() == str(preferred_artist).strip().lower():
        score += 0.5
        reasons.append("artist match (+0.5)")

    energy = float(song.get("energy", 0.0))
    energy_score = 3.0 * (1.0 - min(abs(energy - float(target_energy)), 1.0))
    score += energy_score
    reasons.append(f"energy closeness (+{energy_score:.2f})")

    if target_tempo is not None:
        tempo = float(song.get("tempo_bpm", 0.0))
        tempo_score = 1.5 * (1.0 - min(abs(tempo - float(target_tempo)) / 80.0, 1.0))
        score += tempo_score
        reasons.append(f"tempo closeness (+{tempo_score:.2f})")

    if target_valence is not None:
        valence = float(song.get("valence", 0.0))
        valence_score = 1.0 * (1.0 - min(abs(valence - float(target_valence)), 1.0))
        score += valence_score
        reasons.append(f"valence closeness (+{valence_score:.2f})")

    if target_danceability is not None:
        danceability = float(song.get("danceability", 0.0))
        danceability_score = 1.0 * (1.0 - min(abs(danceability - float(target_danceability)), 1.0))
        score += danceability_score
        reasons.append(f"danceability closeness (+{danceability_score:.2f})")

    if target_acousticness is not None:
        acousticness = float(song.get("acousticness", 0.0))
        acousticness_score = 1.0 * (1.0 - min(abs(acousticness - float(target_acousticness)), 1.0))
        score += acousticness_score
        reasons.append(f"acousticness closeness (+{acousticness_score:.2f})")

    return score, reasons

# Sum of all weights: genre(2) + mood(1) + energy(3) + tempo(1.5) + valence(1) + danceability(1) + acousticness(1)
_MAX_SCORE = 10.5


def confidence_pct(score: float) -> int:
    """Return recommendation confidence as a 0–100 integer percentage."""
    return round(min(score / _MAX_SCORE, 1.0) * 100)


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    scored_songs = [
        (
            song,
            score,
            ", ".join(reasons) if reasons else "no matching preference signals",
        )
        for song in songs
        for score, reasons in [score_song(user_prefs, song)]
    ]

    return sorted(scored_songs, key=lambda item: item[1], reverse=True)[:k]
