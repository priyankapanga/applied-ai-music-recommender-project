from src.recommender import Song, UserProfile, Recommender
from src.reliability_harness import HarnessCase, run_reliability_harness

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


def test_reliability_harness_passes_on_representative_profiles():
    rec = make_small_recommender()
    cases = [
        HarnessCase(
            name="pop_happy",
            user=UserProfile(
                favorite_genre="pop",
                favorite_mood="happy",
                target_energy=0.8,
                likes_acoustic=False,
            ),
            expected_top_genre="pop",
            expected_top_mood="happy",
        ),
        HarnessCase(
            name="lofi_chill",
            user=UserProfile(
                favorite_genre="lofi",
                favorite_mood="chill",
                target_energy=0.4,
                likes_acoustic=True,
            ),
            expected_top_genre="lofi",
            expected_top_mood="chill",
        ),
    ]

    result = run_reliability_harness(rec, cases=cases, k=2)

    assert result["passed"] is True
    assert result["passed_cases"] == 2
    assert result["issues"] == []
