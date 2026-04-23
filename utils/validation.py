from typing import List, Dict, Any, Tuple

def validate_game_plan_inputs(
    available_players: List[Dict],
    qb_eligible_ids: List[int],
    settings: Dict
) -> Tuple[bool, List[str]]:
    errors = []
    
    offense_eligible = [p for p in available_players if not p.get("defense_only")]
    defense_eligible = [p for p in available_players if not p.get("offense_only")]
    
    offense_size = settings.get("offense_size", 7)
    defense_size = settings.get("defense_size", 7)
    
    if len(offense_eligible) < offense_size:
        errors.append(f"Need at least {offense_size} players available for offense. Have {len(offense_eligible)}.")
    if len(defense_eligible) < defense_size:
        errors.append(f"Need at least {defense_size} players available for defense. Have {len(defense_eligible)}.")
    if not qb_eligible_ids:
        errors.append("No QB selected. Please select at least one QB.")
    
    qb_players = [p for p in available_players if p["id"] in qb_eligible_ids]
    if not qb_players and qb_eligible_ids:
        errors.append("Selected QB is not in the available players list.")
    
    if len(available_players) < 7:
        errors.append(f"Need at least 7 available players. Currently {len(available_players)}.")
    
    return len(errors) == 0, errors

def validate_players(players: List[Dict]) -> List[str]:
    warnings = []
    names = [p["name"] for p in players if not p.get("archived")]
    if len(names) < 7:
        warnings.append(f"Only {len(names)} active players. Need at least 7 for a game.")
    
    qb_eligible = [p for p in players if p.get("qb_eligible") and not p.get("archived")]
    if not qb_eligible:
        warnings.append("No QB-eligible players. Mark at least one player as QB eligible.")
    elif len(qb_eligible) == 1:
        warnings.append(f"Only one QB eligible ({qb_eligible[0]['name']}). Consider a backup QB.")
    
    injured = [p["name"] for p in players if p.get("injured")]
    if injured:
        warnings.append(f"Injured players: {', '.join(injured)}")
    
    unavailable = [p["name"] for p in players if not p.get("available") and not p.get("archived") and not p.get("injured")]
    if unavailable:
        warnings.append(f"Marked unavailable: {', '.join(unavailable)}")
    
    return warnings
