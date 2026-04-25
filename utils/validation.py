from typing import List, Dict, Any, Tuple, Set

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


def validate_no_back_to_back_sits(lineup: List[Dict]) -> List[str]:
    """
    Walk the full ordered segment list and confirm no player appears in
    players_out for two consecutive segments.
    Returns list of violation description strings (empty = pass).
    """
    sorted_lineup = sorted(lineup, key=lambda p: p["seq_num"])
    violations = []
    for i in range(1, len(sorted_lineup)):
        prev = sorted_lineup[i - 1]
        curr = sorted_lineup[i]
        prev_out = set(prev.get("players_out", []))
        curr_out = set(curr.get("players_out", []))
        overlap = prev_out & curr_out
        if overlap:
            violations.append(
                f"Back-to-back sit: {', '.join(sorted(overlap))} "
                f"({prev['label']} → {curr['label']})"
            )
    return violations


def validate_offense_to_defense_no_repeat_sits(lineup: List[Dict]) -> List[str]:
    """
    Check each same-possession Offense→Defense pair (within each half):
      - Offense 1 Out vs Defense 1 Out
      - Offense 2 Out vs Defense 2 Out
      - Offense 3 Out vs Defense 3 Out
    Returns violation strings.
    """
    violations = []
    for half in (1, 2):
        for poss_num in range(1, 4):
            offense_seg = next(
                (p for p in lineup if p["half"] == half and p["possession"] == poss_num and p["type"] == "Offense"),
                None
            )
            defense_seg = next(
                (p for p in lineup if p["half"] == half and p["possession"] == poss_num and p["type"] == "Defense"),
                None
            )
            if offense_seg is None or defense_seg is None:
                continue
            out_off = set(offense_seg.get("players_out", []))
            out_def = set(defense_seg.get("players_out", []))
            overlap = out_off & out_def
            if overlap:
                violations.append(
                    f"Offense→Defense repeat sit: {', '.join(sorted(overlap))} "
                    f"({offense_seg['label']} → {defense_seg['label']})"
                )
    return violations


def validate_defense_to_next_offense_no_repeat_sits(lineup: List[Dict]) -> List[str]:
    """
    Check each Defense→next Offense transition:
      - Defense 1 Out vs Offense 2 Out (same half)
      - Defense 2 Out vs Offense 3 Out (same half)
      - Defense 3 Out vs next half's Offense 1 Out
    Returns violation strings.
    """
    violations = []
    # Within-half transitions
    for half in (1, 2):
        for def_poss_num in range(1, 3):
            defense_seg = next(
                (p for p in lineup if p["half"] == half and p["possession"] == def_poss_num and p["type"] == "Defense"),
                None
            )
            next_off_seg = next(
                (p for p in lineup if p["half"] == half and p["possession"] == def_poss_num + 1 and p["type"] == "Offense"),
                None
            )
            if defense_seg is None or next_off_seg is None:
                continue
            out_def = set(defense_seg.get("players_out", []))
            out_off = set(next_off_seg.get("players_out", []))
            overlap = out_def & out_off
            if overlap:
                violations.append(
                    f"Defense→Offense repeat sit: {', '.join(sorted(overlap))} "
                    f"({defense_seg['label']} → {next_off_seg['label']})"
                )
    # Half-boundary transition: 1H Defense 3 → 2H Offense 1
    def3_seg = next(
        (p for p in lineup if p["half"] == 1 and p["possession"] == 3 and p["type"] == "Defense"),
        None
    )
    off1_h2_seg = next(
        (p for p in lineup if p["half"] == 2 and p["possession"] == 1 and p["type"] == "Offense"),
        None
    )
    if def3_seg and off1_h2_seg:
        out_def3 = set(def3_seg.get("players_out", []))
        out_off1_h2 = set(off1_h2_seg.get("players_out", []))
        overlap = out_def3 & out_off1_h2
        if overlap:
            violations.append(
                f"Half-boundary repeat sit: {', '.join(sorted(overlap))} "
                f"({def3_seg['label']} → {off1_h2_seg['label']})"
            )
    return violations


def validate_full_sit_flow(lineup: List[Dict]) -> Tuple[bool, List[str]]:
    """
    Run all three checks and return (all_pass, all_violations).
    """
    all_violations: List[str] = []
    all_violations += validate_no_back_to_back_sits(lineup)
    all_violations += validate_offense_to_defense_no_repeat_sits(lineup)
    all_violations += validate_defense_to_next_offense_no_repeat_sits(lineup)
    # Deduplicate while preserving order
    seen: Set[str] = set()
    unique: List[str] = []
    for v in all_violations:
        if v not in seen:
            seen.add(v)
            unique.append(v)
    return len(unique) == 0, unique
