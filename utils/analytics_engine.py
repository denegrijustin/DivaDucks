from typing import List, Dict, Any, Tuple

def compute_usage(game_plan: List[Dict], available_players: List[Dict]) -> Dict[str, Any]:
    total_possessions = len(game_plan)
    offense_possessions = [p for p in game_plan if p["type"] == "Offense"]
    defense_possessions = [p for p in game_plan if p["type"] == "Defense"]
    
    usage = {}
    for player in available_players:
        name = player["name"]
        offense_count = sum(1 for p in offense_possessions if name in p["players"])
        defense_count = sum(1 for p in defense_possessions if name in p["players"])
        total_count = offense_count + defense_count
        total_possible = len(offense_possessions) + len(defense_possessions)
        usage[name] = {
            "offense_possessions": offense_count,
            "defense_possessions": defense_count,
            "total_possessions": total_count,
            "offense_pct": round(offense_count / max(len(offense_possessions), 1) * 100, 1),
            "defense_pct": round(defense_count / max(len(defense_possessions), 1) * 100, 1),
            "total_pct": round(total_count / max(total_possible, 1) * 100, 1),
        }
    
    return usage

def compute_qb_usage(game_plan: List[Dict]) -> Dict[str, int]:
    qb_counts = {}
    for poss in game_plan:
        if poss["type"] == "Offense":
            qb = poss["assignment"].get("QB", "Unknown")
            qb_counts[qb] = qb_counts.get(qb, 0) + 1
    return qb_counts

def find_strongest_weakest(game_plan: List[Dict]):
    if not game_plan:
        return None, None
    sorted_plan = sorted(game_plan, key=lambda x: x["lineup_rank"], reverse=True)
    return sorted_plan[0], sorted_plan[-1]

def player_role_fit(player: Dict) -> str:
    offense_r = player.get("offense_rating", 5)
    defense_r = player.get("defense_rating", 5)
    if offense_r > 7 and defense_r > 7:
        return "Two-Way Star"
    elif offense_r > 7:
        return "Offensive Specialist"
    elif defense_r > 7:
        return "Defensive Specialist"
    elif player.get("qb_rating", 0) > 7:
        return "QB Leader"
    else:
        return "Versatile Player"


def compute_bench_patterns(game_plan: List[Dict], available_players: List[Dict]) -> Dict[str, Any]:
    """
    For each player, compute bench streak statistics from the live game sequence.

    Returns a dict keyed by player name with:
        bench_sequence: list of bools (True = benched that possession)
        total_bench: int
        consecutive_violations: int  (times sat two in a row)
        max_consecutive_bench: int
        bench_pct: float
    """
    result = {}
    for player in available_players:
        name = player["name"]

        # Build the bench sequence for eligible possessions only
        bench_sequence: List[bool] = []
        for poss in game_plan:
            is_off = poss["type"] == "Offense"
            # Skip possessions this player is not eligible for
            if is_off and player.get("defense_only"):
                continue
            if not is_off and player.get("offense_only"):
                continue
            bench_sequence.append(name not in poss["players"])

        # Compute statistics
        total_poss = len(bench_sequence)
        total_bench = sum(bench_sequence)

        consecutive_violations = 0
        max_streak = 0
        current_streak = 0
        for i, benched in enumerate(bench_sequence):
            if benched:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
                if i > 0 and bench_sequence[i - 1]:
                    consecutive_violations += 1
            else:
                current_streak = 0

        result[name] = {
            "bench_sequence": bench_sequence,
            "total_bench": total_bench,
            "total_eligible": total_poss,
            "consecutive_violations": consecutive_violations,
            "max_consecutive_bench": max_streak,
            "bench_pct": round(total_bench / max(total_poss, 1) * 100, 1),
        }

    return result


def check_no_sit_twice_violations(game_plan: List[Dict], available_players: List[Dict]) -> List[str]:
    """Return a list of violation strings if any player sat twice in a row."""
    patterns = compute_bench_patterns(game_plan, available_players)
    violations = []
    for name, data in patterns.items():
        v = data["consecutive_violations"]
        if v > 0:
            violations.append(
                f"{name} sat twice in a row {v} time(s) "
                f"(max bench streak: {data['max_consecutive_bench']})"
            )
    return violations
