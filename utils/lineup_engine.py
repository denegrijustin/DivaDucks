from typing import List, Dict, Any, Optional, Tuple, Set

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


def friendly_rank_label(rank: float) -> str:
    """Return a human-readable label for a lineup rank (1-10 scale)."""
    if rank >= 8.0:
        return "Elite"
    elif rank >= 6.5:
        return "Strong"
    elif rank >= 5.0:
        return "Solid"
    elif rank >= 3.5:
        return "Average"
    else:
        return "Developing"


def select_qbs(available_players: List[Dict], qb_eligible_ids: List[int]) -> tuple:
    """Return (qb_half1, qb_half2). If 1 QB, she plays both halves. If >2, pick top 2 by rating."""
    qb_pool = [p for p in available_players if p["id"] in qb_eligible_ids and p.get("qb_eligible", True)]
    if not qb_pool:
        return None, None
    qb_pool_sorted = sorted(qb_pool, key=lambda x: x.get("qb_rating", 0), reverse=True)
    if len(qb_pool_sorted) == 1:
        return qb_pool_sorted[0], qb_pool_sorted[0]
    return qb_pool_sorted[0], qb_pool_sorted[1]


def compute_lineup_rank(assignment: Dict[str, Dict], position_ratings: Dict[str, str]) -> float:
    if not assignment:
        return 0.0
    total = sum(
        assignment[pos].get(position_ratings[pos], 0)
        for pos in assignment
        if pos in position_ratings
    )
    return round(total / max(len(assignment), 1), 2)


def generate_game_plans(
    available_players: List[Dict],
    qb_half1_id: int,
    qb_half2_id: int,
    settings: Dict[str, Any],
    mode: str = "Fair Rotation",
) -> Dict[str, List[Dict]]:
    """
    Generate both game-flow versions.

    Returns:
        {
            "offense_first": [...possessions in O,D,O,D order...],
            "defense_first": [...possessions in D,O,D,O order...],
        }
    """
    return {
        "offense_first": _generate_sequence(
            available_players, qb_half1_id, qb_half2_id, settings, mode,
            start_on_offense=True
        ),
        "defense_first": _generate_sequence(
            available_players, qb_half1_id, qb_half2_id, settings, mode,
            start_on_offense=False
        ),
    }


def _generate_sequence(
    available_players: List[Dict],
    qb_half1_id: int,
    qb_half2_id: int,
    settings: Dict[str, Any],
    mode: str,
    start_on_offense: bool,
) -> List[Dict]:
    """
    Generate one interleaved possession sequence enforcing the no-sit-twice hard rule.

    The no-sit-twice rule:
    - Two-way players who sit at possession N must play at possession N+1 in the live sequence.
    - offense_only players who sit at an offense possession must play at the next offense possession.
    - defense_only players who sit at a defense possession must play at the next defense possession.
    """
    possessions_per_half = settings.get("possessions_per_half", 3)
    halves = settings.get("halves", 2)

    play_counts: Dict[int, Dict[str, int]] = {
        p["id"]: {"offense": 0, "defense": 0} for p in available_players
    }

    # No-sit-twice tracking per phase
    must_next_offense: Set[int] = set()  # IDs who MUST be in next offense possession
    must_next_defense: Set[int] = set()  # IDs who MUST be in next defense possession

    all_possessions: List[Dict] = []
    seq_num = 0

    for half in range(1, halves + 1):
        qb_id = qb_half1_id if half == 1 else qb_half2_id
        qb = next((p for p in available_players if p["id"] == qb_id), None)

        for poss_num in range(1, possessions_per_half + 1):
            phases = ["offense", "defense"] if start_on_offense else ["defense", "offense"]

            for phase in phases:
                seq_num += 1
                half_label = "1st" if half == 1 else "2nd"
                poss_type = "Offense" if phase == "offense" else "Defense"

                must_ids = must_next_offense if phase == "offense" else must_next_defense

                selected, bench = _select_for_phase(
                    available_players, play_counts, phase,
                    qb if phase == "offense" else None,
                    mode, must_ids, 7
                )

                if phase == "offense":
                    assignment = _assign_offense(selected, qb)
                    rank = compute_lineup_rank(assignment, OFFENSE_POSITION_RATINGS)
                else:
                    assignment = _assign_defense(selected)
                    rank = compute_lineup_rank(assignment, DEFENSE_POSITION_RATINGS)

                rank_label = friendly_rank_label(rank)
                notes = _lineup_notes(selected, phase, rank_label)

                all_possessions.append({
                    "half": half,
                    "possession": poss_num,
                    "seq_num": seq_num,
                    "type": poss_type,
                    "label": f"{half_label} Half · Possession {poss_num} · {poss_type}",
                    "assignment": {pos: p["name"] for pos, p in assignment.items()},
                    "players": [p["name"] for p in selected],
                    "players_out": [p["name"] for p in bench],
                    "lineup_rank": rank,
                    "rank_label": rank_label,
                    "notes": notes,
                })

                # Update play counts
                for p in selected:
                    play_counts[p["id"]][phase] += 1

                # Update no-sit-twice tracking
                if phase == "offense":
                    must_next_offense = set()  # consumed; reset
                    for p in bench:
                        if p.get("offense_only"):
                            # Only plays offense → carry to next offense
                            must_next_offense.add(p["id"])
                        else:
                            # Two-way: must play the very next live possession (defense)
                            must_next_defense.add(p["id"])
                else:
                    must_next_defense = set()  # consumed; reset
                    for p in bench:
                        if p.get("defense_only"):
                            # Only plays defense → carry to next defense
                            must_next_defense.add(p["id"])
                        else:
                            # Two-way: must play the very next live possession (offense)
                            must_next_offense.add(p["id"])

    return all_possessions


def _select_for_phase(
    available_players: List[Dict],
    play_counts: Dict[int, Dict[str, int]],
    phase: str,
    qb: Optional[Dict],
    mode: str,
    must_include_ids: Set[int],
    size: int = 7,
) -> Tuple[List[Dict], List[Dict]]:
    """
    Select `size` players for a possession phase, enforcing must_include_ids (no-sit-twice).

    Returns: (selected, bench) — bench are eligible players who didn't play.
    """
    if phase == "offense":
        eligible = [p for p in available_players if not p.get("defense_only")]
    else:
        eligible = [p for p in available_players if not p.get("offense_only")]

    if len(eligible) <= size:
        return eligible, []

    # Must-include bucket (no-sit-twice forced players)
    must_play = [p for p in eligible if p["id"] in must_include_ids]

    # QB is always locked in for offense
    if phase == "offense" and qb and qb in eligible and qb not in must_play:
        must_play.insert(0, qb)

    # Safety: if must_play exceeds size, trim (this should never happen with default 10-player roster)
    if len(must_play) > size:
        must_play = must_play[:size]

    remaining_slots = size - len(must_play)
    other_eligible = [p for p in eligible if p not in must_play]

    rating_key = "offense_rating" if phase == "offense" else "defense_rating"

    def _sort_key(p: Dict):
        must_more = -1000 if p.get("must_play_more") else 0
        count = play_counts[p["id"]][phase]
        rating = p.get(rating_key, 0)
        if mode == "Fair Rotation":
            return (must_more + count, -rating)
        elif mode == "Must-Win":
            return (must_more, -rating)
        else:  # Balanced
            return (must_more + count * 0.5, -rating * 0.5)

    other_eligible.sort(key=_sort_key)

    selected = must_play + other_eligible[:remaining_slots]
    bench = [p for p in eligible if p not in selected]
    return selected, bench


def _assign_offense(players: List[Dict], qb: Optional[Dict]) -> Dict[str, Dict]:
    assignment: Dict[str, Dict] = {}
    remaining = list(players)

    # QB
    if qb and qb in remaining:
        assignment["QB"] = qb
        remaining.remove(qb)
    elif remaining:
        best_qb = max(remaining, key=lambda x: x.get("qb_rating", 0))
        assignment["QB"] = best_qb
        remaining.remove(best_qb)

    # RB: best rb_rating
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

    # Slot1, Slot2: best slot_rating
    for slot in ["Slot1", "Slot2"]:
        if remaining:
            sl = max(remaining, key=lambda x: x.get("slot_rating", 0))
            assignment[slot] = sl
            remaining.remove(sl)

    return assignment


def _assign_defense(players: List[Dict]) -> Dict[str, Dict]:
    assignment: Dict[str, Dict] = {}
    remaining = list(players)

    # Blitzer: best blitzer_rating
    if remaining:
        bl = max(remaining, key=lambda x: x.get("blitzer_rating", 0))
        assignment["Blitzer"] = bl
        remaining.remove(bl)

    # Safety: best safety_rating
    if remaining:
        sf = max(remaining, key=lambda x: x.get("safety_rating", 0))
        assignment["Safety"] = sf
        remaining.remove(sf)

    # CB1, CB2: best cb_rating
    for slot in ["CB1", "CB2"]:
        if remaining:
            cb = max(remaining, key=lambda x: x.get("cb_rating", 0))
            assignment[slot] = cb
            remaining.remove(cb)

    # MLB: best mlb_rating
    if remaining:
        mlb = max(remaining, key=lambda x: x.get("mlb_rating", 0))
        assignment["MLB"] = mlb
        remaining.remove(mlb)

    # OLB1, OLB2: best olb_rating
    for slot in ["OLB1", "OLB2"]:
        if remaining:
            olb = max(remaining, key=lambda x: x.get("olb_rating", 0))
            assignment[slot] = olb
            remaining.remove(olb)

    return assignment


def _lineup_notes(players: List[Dict], phase: str, rank_label: str) -> str:
    notes = []
    rating_key = "offense_rating" if phase == "offense" else "defense_rating"
    avg = sum(p.get(rating_key, 5) for p in players) / max(len(players), 1)

    if avg >= 7.5:
        notes.append("Strong unit")
    elif avg < 4.0:
        notes.append("Developing unit — give extra coaching attention")

    must_more = [p["name"] for p in players if p.get("must_play_more")]
    if must_more:
        notes.append(f"Must-play: {', '.join(must_more)}")

    return "; ".join(notes) if notes else rank_label


def repair_segment_from_previous(
    previous_out: List[str],
    current_segment: Dict,
    roster: List[Dict],
    position_rules: Dict[str, str],
) -> Dict:
    """
    Given that `previous_out` contains players who sat in the previous segment,
    repair `current_segment` so that none of those players appear in its
    players_out list.

    Strategy:
    1. Identify conflict players (in both previous_out and current players_out).
    2. For each conflict player, swap them back in by benching another player
       who was NOT in previous_out.
    3. Rebuild the assignment with the new selected set.
    4. Return the repaired segment dict (or original if no conflicts).
    """
    segment = dict(current_segment)
    is_offense = segment["type"] == "Offense"
    prev_out_set = set(previous_out)

    current_out_names = set(segment.get("players_out", []))
    conflicts = prev_out_set & current_out_names
    if not conflicts:
        return segment  # No repair needed

    # Build sets from current assignment (playing) and bench
    current_playing_names = set(segment.get("players", []))

    # Players that must come off the bench (were in previous_out and current bench)
    must_play_in = list(conflicts)

    # Candidates to bench: currently playing, NOT in previous_out
    can_bench = [
        name for name in current_playing_names
        if name not in prev_out_set
    ]

    # Swap: bring in conflict players, bench can_bench players (as many as needed)
    new_playing = set(current_playing_names)
    new_out = set(current_out_names)

    for conflict_player in must_play_in:
        if can_bench:
            swap_out = can_bench.pop(0)
            new_playing.discard(swap_out)
            new_out.discard(conflict_player)
            new_playing.add(conflict_player)
            new_out.add(swap_out)
        else:
            # Cannot repair — mark as unresolved, keep original
            segment.setdefault("repair_warnings", [])
            segment["repair_warnings"].append(
                f"Could not remove {conflict_player} from bench "
                f"(no eligible swap found)"
            )

    # Rebuild assignment from new_playing set using roster + position rules
    player_map = {p["name"]: p for p in roster}
    playing_players = [player_map[n] for n in new_playing if n in player_map]

    if is_offense:
        # Find QB (kept from original assignment if still playing)
        qb_name = segment.get("assignment", {}).get("QB")
        qb = player_map.get(qb_name) if qb_name else None
        if qb and qb not in playing_players:
            qb = None
        new_assignment = _assign_offense(playing_players, qb)
    else:
        new_assignment = _assign_defense(playing_players)

    segment["players"] = sorted(new_playing)
    segment["players_out"] = sorted(new_out)
    segment["assignment"] = {pos: p["name"] for pos, p in new_assignment.items()}

    # Recompute rank
    pos_ratings = OFFENSE_POSITION_RATINGS if is_offense else DEFENSE_POSITION_RATINGS
    segment["lineup_rank"] = compute_lineup_rank(new_assignment, pos_ratings)
    segment["rank_label"] = friendly_rank_label(segment["lineup_rank"])

    return segment


def repair_defense_outs_for_possession(
    previous_out: List[str],
    defense_lineup: Dict,
    roster: List[Dict],
    position_rules: Dict[str, str],
) -> Dict:
    """Repair a defense segment so no player from previous_out sits again."""
    return repair_segment_from_previous(previous_out, defense_lineup, roster, position_rules)


def repair_offense_outs_for_possession(
    previous_out: List[str],
    offense_lineup: Dict,
    roster: List[Dict],
    position_rules: Dict[str, str],
) -> Dict:
    """Repair an offense segment so no player from previous_out sits again."""
    return repair_segment_from_previous(previous_out, offense_lineup, roster, position_rules)


def repair_game_plan(
    game_plan: List[Dict],
    roster: List[Dict],
) -> Tuple[List[Dict], List[str]]:
    """
    Walk the full sequential game plan and repair any back-to-back sit violations.
    Returns (repaired_plan, warnings).
    """
    if not game_plan:
        return game_plan, []

    sorted_plan = sorted(game_plan, key=lambda p: p["seq_num"])
    repaired: List[Dict] = [dict(sorted_plan[0])]
    warnings: List[str] = []

    for i in range(1, len(sorted_plan)):
        prev = repaired[i - 1]
        curr = dict(sorted_plan[i])
        prev_out = prev.get("players_out", [])
        curr_out = set(curr.get("players_out", []))
        conflicts = set(prev_out) & curr_out
        if conflicts:
            repaired_seg = repair_segment_from_previous(prev_out, curr, roster, {})
            repair_warns = repaired_seg.pop("repair_warnings", [])
            if repair_warns:
                warnings += repair_warns
            # Check if repair succeeded
            still_conflicts = set(prev_out) & set(repaired_seg.get("players_out", []))
            if still_conflicts:
                warnings.append(
                    f"Could not fully repair {repaired_seg['label']}: "
                    f"players still back-to-back: {', '.join(sorted(still_conflicts))}"
                )
            repaired.append(repaired_seg)
        else:
            repaired.append(curr)

    return repaired, warnings


# ---------------------------------------------------------------------------
# Legacy single-plan generator kept for backward compat (wraps new engine)
# ---------------------------------------------------------------------------
def generate_game_plan(
    available_players: List[Dict],
    qb_half1_id: int,
    qb_half2_id: int,
    settings: Dict[str, Any],
    mode: str = "Fair Rotation",
) -> List[Dict]:
    """Backward-compatible wrapper — returns offense-first sequence."""
    plans = generate_game_plans(available_players, qb_half1_id, qb_half2_id, settings, mode)
    return plans["offense_first"]
