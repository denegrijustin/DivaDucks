from typing import List, Dict, Any

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
