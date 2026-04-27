from dataclasses import asdict, dataclass
from typing import Dict, List, Optional, Sequence

from src.recommender import Recommender, Song, UserProfile, score_song


@dataclass(frozen=True)
class HarnessCase:
    name: str
    user: UserProfile
    expected_top_genre: Optional[str] = None
    expected_top_mood: Optional[str] = None


def default_harness_cases() -> List[HarnessCase]:
    return [
        HarnessCase(
            name="upbeat_pop",
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
            name="chill_lofi",
            user=UserProfile(
                favorite_genre="lofi",
                favorite_mood="chill",
                target_energy=0.4,
                likes_acoustic=True,
            ),
            expected_top_genre="lofi",
            expected_top_mood="chill",
        ),
        HarnessCase(
            name="high_energy_rock",
            user=UserProfile(
                favorite_genre="rock",
                favorite_mood="intense",
                target_energy=0.95,
                likes_acoustic=False,
            ),
            expected_top_genre="rock",
            expected_top_mood="intense",
        ),
    ]


def _score_ranked_songs(recommender: Recommender, user: UserProfile) -> List[Song]:
    user_prefs = recommender._user_profile_to_preferences(user)
    ranked_pairs = sorted(
        ((song, score_song(user_prefs, asdict(song))[0]) for song in recommender.songs),
        key=lambda item: item[1],
        reverse=True,
    )
    return [song for song, _ in ranked_pairs]


def run_reliability_harness(
    recommender: Recommender,
    cases: Optional[Sequence[HarnessCase]] = None,
    k: int = 5,
) -> Dict[str, object]:
    """Run deterministic checks over representative user profiles.

    The harness verifies that the recommender returns songs in score order,
    produces non-empty explanations, and puts the expected genre/mood at the
    top when the catalog contains a clear match.
    """

    cases_to_run = list(cases) if cases is not None else default_harness_cases()
    issues: List[str] = []
    passed_cases = 0

    for case in cases_to_run:
        ranked_songs = _score_ranked_songs(recommender, case.user)
        recommendations = recommender.recommend(case.user, k=k)
        expected_top = ranked_songs[0] if ranked_songs else None

        case_issues: List[str] = []
        if not recommendations:
            case_issues.append("returned no recommendations")
        else:
            if len({song.id for song in recommendations}) != len(recommendations):
                case_issues.append("returned duplicate songs")

            expected_order = ranked_songs[: len(recommendations)]
            if [song.id for song in recommendations] != [song.id for song in expected_order]:
                case_issues.append("ranking order does not match score order")

            top_song = recommendations[0]
            explanation = recommender.explain_recommendation(case.user, top_song)
            if not explanation.strip():
                case_issues.append("top recommendation explanation was empty")

            if case.expected_top_genre and top_song.genre != case.expected_top_genre:
                case_issues.append(
                    f"expected top genre {case.expected_top_genre!r}, got {top_song.genre!r}"
                )
            if case.expected_top_mood and top_song.mood != case.expected_top_mood:
                case_issues.append(
                    f"expected top mood {case.expected_top_mood!r}, got {top_song.mood!r}"
                )

            if expected_top is not None and top_song.id != expected_top.id:
                case_issues.append(
                    f"top recommendation {top_song.id} did not match highest-scoring song {expected_top.id}"
                )

        if case_issues:
            issues.append(f"{case.name}: " + "; ".join(case_issues))
        else:
            passed_cases += 1

    return {
        "passed": not issues,
        "passed_cases": passed_cases,
        "total_cases": len(cases_to_run),
        "issues": issues,
    }