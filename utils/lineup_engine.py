from typing import List, Dict, Any, Optional
import random

OFFENSE_POSITION_RATINGS = {
    "QB": "qb_rating",
    "RB": "rb_rating",
    "Center": "center_rating",
    "WR1": "wr_rating",
    "WR2": "wr_rating",
    "Slot1": "slot_rating",
    "Slot2": "slot_rating",
}

DEFENSE_POSITION_RATINGS = {
    "OLB1": "olb_rating",
    "OLB2": "olb_rating",
    "MLB": "mlb_rating",
    "CB1": "cb_rating",
    "CB2": "cb_rating",
    "Safety": "safety_rating",
    "Blitzer": "blitzer_rating",
}

def select_qbs(available_players: List[Dict], qb_eligible_ids: List[int]) -> tuple:
    qb_pool = [p for p in available_players if p["id"] in qb_eligible_ids and p.get("qb_eligible", True)]
    if not qb_pool:
        return None, None
    qb_pool_sorted = sorted(qb_pool, key=lambda x: x.get("qb_rating", 0), reverse=True)
    if len(qb_pool_sorted) == 1:
        return qb_pool_sorted[0], qb_pool_sorted[0]
    else:
        return qb_pool_sorted[0], qb_pool_sorted[1]

def assign_positions(players: List[Dict], position_ratings: Dict[str, str], locked: Dict[str, Dict] = None) -> Dict[str, Dict]:
    assignment = {}
    if locked:
        assignment.update(locked)
    remaining_positions = [p for p in position_ratings if p not in assignment]
    remaining_players = [p for p in players if p not in assignment.values()]
    
    # Greedy assignment: best player for each position
    for pos in remaining_positions:
        rating_key = position_ratings[pos]
        best = max(remaining_players, key=lambda x: x.get(rating_key, 0), default=None)
        if best:
            assignment[pos] = best
            remaining_players.remove(best)
    
    return assignment

def compute_lineup_rank(assignment: Dict[str, Dict], position_ratings: Dict[str, str]) -> float:
    if not assignment:
        return 0.0
    total = sum(assignment[pos].get(position_ratings[pos], 0) for pos in assignment if pos in position_ratings)
    return round(total / max(len(assignment), 1), 2)

def generate_game_plan(
    available_players: List[Dict],
    qb_half1_id: int,
    qb_half2_id: int,
    settings: Dict[str, Any],
    mode: str = "Fair Rotation"
) -> List[Dict]:
    possessions_per_half = settings.get("possessions_per_half", 3)
    halves = settings.get("halves", 2)
    
    all_possessions = []
    possession_num = 0
    
    # Track play counts for fairness
    play_counts = {p["id"]: {"offense": 0, "defense": 0} for p in available_players}
    
    for half in range(1, halves + 1):
        qb_id = qb_half1_id if half == 1 else qb_half2_id
        qb = next((p for p in available_players if p["id"] == qb_id), None)
        
        for poss in range(1, possessions_per_half + 1):
            possession_num += 1
            
            # --- OFFENSE ---
            offense_players = _select_best_7(
                available_players, play_counts, "offense", qb, mode, 
                exclude_flags=["defense_only"]
            )
            offense_assignment = _assign_offense(offense_players, qb)
            offense_rank = compute_lineup_rank(offense_assignment, OFFENSE_POSITION_RATINGS)
            players_out_offense = [p["name"] for p in available_players if p not in offense_players and not p.get("defense_only")]
            
            all_possessions.append({
                "half": half,
                "possession": poss,
                "possession_num": possession_num,
                "type": "Offense",
                "label": f"{'1st' if half==1 else '2nd'} Half Possession {poss} Offense",
                "assignment": {pos: p["name"] for pos, p in offense_assignment.items()},
                "players": [p["name"] for p in offense_players],
                "players_out": players_out_offense,
                "lineup_rank": offense_rank,
                "notes": _lineup_notes(offense_players, offense_assignment, "offense"),
            })
            _update_counts(play_counts, offense_players, "offense")
            
            # --- DEFENSE ---
            defense_players = _select_best_7(
                available_players, play_counts, "defense", None, mode,
                exclude_flags=["offense_only"]
            )
            defense_assignment = _assign_defense(defense_players)
            defense_rank = compute_lineup_rank(defense_assignment, DEFENSE_POSITION_RATINGS)
            players_out_defense = [p["name"] for p in available_players if p not in defense_players and not p.get("offense_only")]
            
            all_possessions.append({
                "half": half,
                "possession": poss,
                "possession_num": possession_num,
                "type": "Defense",
                "label": f"{'1st' if half==1 else '2nd'} Half Possession {poss} Defense",
                "assignment": {pos: p["name"] for pos, p in defense_assignment.items()},
                "players": [p["name"] for p in defense_players],
                "players_out": players_out_defense,
                "lineup_rank": defense_rank,
                "notes": _lineup_notes(defense_players, defense_assignment, "defense"),
            })
            _update_counts(play_counts, defense_players, "defense")
    
    return all_possessions

def _select_best_7(players, play_counts, side, qb, mode, exclude_flags=None):
    eligible = [p for p in players if not any(p.get(f) for f in (exclude_flags or []))]
    if len(eligible) <= 7:
        return eligible
    
    rating_key = "offense_rating" if side == "offense" else "defense_rating"
    
    if mode == "Fair Rotation":
        # Sort by play count (ascending) then rating (descending)
        eligible_sorted = sorted(
            eligible,
            key=lambda p: (play_counts[p["id"]][side], -p.get(rating_key, 0))
        )
    elif mode == "Must-Win":
        eligible_sorted = sorted(eligible, key=lambda p: -p.get(rating_key, 0))
    else:  # Balanced
        eligible_sorted = sorted(
            eligible,
            key=lambda p: (play_counts[p["id"]][side] * 0.5, -p.get(rating_key, 0) * 0.5)
        )
    
    selected = []
    if qb and side == "offense":
        if qb in eligible_sorted:
            selected.append(qb)
            eligible_sorted.remove(qb)
    
    must_play = [p for p in eligible_sorted if p.get("must_play_more")]
    others = [p for p in eligible_sorted if not p.get("must_play_more")]
    
    for p in must_play:
        if len(selected) < 7:
            selected.append(p)
    for p in others:
        if len(selected) < 7:
            selected.append(p)
    
    return selected[:7]

def _assign_offense(players, qb):
    assignment = {}
    remaining = list(players)
    if qb and qb in remaining:
        assignment["QB"] = qb
        remaining.remove(qb)
    elif remaining:
        # assign best qb_rating as QB
        best_qb = max(remaining, key=lambda x: x.get("qb_rating", 0))
        assignment["QB"] = best_qb
        remaining.remove(best_qb)
    
    # RB: fastest
    if remaining:
        rb = max(remaining, key=lambda x: x.get("rb_rating", 0))
        assignment["RB"] = rb
        remaining.remove(rb)
    # Center: best center_rating
    if remaining:
        center = max(remaining, key=lambda x: x.get("center_rating", 0))
        assignment["Center"] = center
        remaining.remove(center)
    # WR1, WR2: best wr_rating
    for slot in ["WR1", "WR2"]:
        if remaining:
            wr = max(remaining, key=lambda x: x.get("wr_rating", 0))
            assignment[slot] = wr
            remaining.remove(wr)
    # Slot1, Slot2
    for slot in ["Slot1", "Slot2"]:
        if remaining:
            sl = max(remaining, key=lambda x: x.get("slot_rating", 0))
            assignment[slot] = sl
            remaining.remove(sl)
    return assignment

def _assign_defense(players):
    assignment = {}
    remaining = list(players)
    
    # Blitzer: best blitzer_rating
    if remaining:
        bl = max(remaining, key=lambda x: x.get("blitzer_rating", 0))
        assignment["Blitzer"] = bl
        remaining.remove(bl)
    # Safety
    if remaining:
        sf = max(remaining, key=lambda x: x.get("safety_rating", 0))
        assignment["Safety"] = sf
        remaining.remove(sf)
    # CB1, CB2
    for slot in ["CB1", "CB2"]:
        if remaining:
            cb = max(remaining, key=lambda x: x.get("cb_rating", 0))
            assignment[slot] = cb
            remaining.remove(cb)
    # MLB
    if remaining:
        mlb = max(remaining, key=lambda x: x.get("mlb_rating", 0))
        assignment["MLB"] = mlb
        remaining.remove(mlb)
    # OLB1, OLB2
    for slot in ["OLB1", "OLB2"]:
        if remaining:
            olb = max(remaining, key=lambda x: x.get("olb_rating", 0))
            assignment[slot] = olb
            remaining.remove(olb)
    return assignment

def _update_counts(play_counts, players, side):
    for p in players:
        if p["id"] in play_counts:
            play_counts[p["id"]][side] += 1

def _lineup_notes(players, assignment, side):
    notes = []
    if side == "offense":
        avg = sum(p.get("offense_rating", 5) for p in players) / max(len(players), 1)
    else:
        avg = sum(p.get("defense_rating", 5) for p in players) / max(len(players), 1)
    if avg >= 7.5:
        notes.append("Strong unit")
    elif avg < 5.0:
        notes.append("Developing unit")
    return "; ".join(notes) if notes else ""
