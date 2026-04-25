# app.py — DivaDucks Lineup Optimizer
# Single-file, production-ready Streamlit app

import copy
import math
import random
import itertools
from io import BytesIO

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors as rl_colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

# ============================================================
# APP CONFIG  (must be first Streamlit call)
# ============================================================
st.set_page_config(
    page_title="DivaDucks Lineup Optimizer",
    page_icon="🦆",
    layout="wide",
)

# ============================================================
# CONSTANTS
# ============================================================
SAMPLE_ROSTER = [
    {"name": "Katrina",  "speed": 3, "hands": 3, "flag_pulling": 3, "route_running": 3, "blocking": 3, "snapping": 3, "qb_ability": 3, "football_iq": 3, "effort": 3, "confidence": 3, "notes": ""},
    {"name": "Isla",     "speed": 3, "hands": 3, "flag_pulling": 3, "route_running": 3, "blocking": 3, "snapping": 3, "qb_ability": 3, "football_iq": 3, "effort": 3, "confidence": 3, "notes": ""},
    {"name": "Timber",   "speed": 3, "hands": 3, "flag_pulling": 3, "route_running": 3, "blocking": 3, "snapping": 3, "qb_ability": 3, "football_iq": 3, "effort": 3, "confidence": 3, "notes": ""},
    {"name": "Francie",  "speed": 3, "hands": 3, "flag_pulling": 3, "route_running": 3, "blocking": 3, "snapping": 3, "qb_ability": 3, "football_iq": 3, "effort": 3, "confidence": 3, "notes": ""},
    {"name": "Felicity", "speed": 3, "hands": 3, "flag_pulling": 3, "route_running": 3, "blocking": 3, "snapping": 3, "qb_ability": 3, "football_iq": 3, "effort": 3, "confidence": 3, "notes": ""},
    {"name": "Sophia",   "speed": 3, "hands": 3, "flag_pulling": 3, "route_running": 3, "blocking": 3, "snapping": 3, "qb_ability": 3, "football_iq": 3, "effort": 3, "confidence": 3, "notes": ""},
    {"name": "Quinn",    "speed": 3, "hands": 3, "flag_pulling": 3, "route_running": 3, "blocking": 3, "snapping": 3, "qb_ability": 3, "football_iq": 3, "effort": 3, "confidence": 3, "notes": ""},
    {"name": "Adriana",  "speed": 3, "hands": 3, "flag_pulling": 3, "route_running": 3, "blocking": 3, "snapping": 3, "qb_ability": 3, "football_iq": 3, "effort": 3, "confidence": 3, "notes": ""},
    {"name": "Olivia",   "speed": 3, "hands": 3, "flag_pulling": 3, "route_running": 3, "blocking": 3, "snapping": 3, "qb_ability": 3, "football_iq": 3, "effort": 3, "confidence": 3, "notes": ""},
    {"name": "Maya",     "speed": 3, "hands": 3, "flag_pulling": 3, "route_running": 3, "blocking": 3, "snapping": 3, "qb_ability": 3, "football_iq": 3, "effort": 3, "confidence": 3, "notes": ""},
]

ATTRIBUTES = [
    "speed", "hands", "flag_pulling", "route_running", "blocking",
    "snapping", "qb_ability", "football_iq", "effort", "confidence",
]
ATTR_LABELS = [
    "Speed", "Hands", "Flag Pulling", "Route Running", "Blocking",
    "Snapping", "QB Ability", "Football IQ", "Effort", "Confidence",
]

OFFENSE_POSITIONS = ["QB", "RB", "Center", "WR1", "WR2", "Slot1", "Slot2"]
DEFENSE_POSITIONS = ["Blitzer", "MLB", "Safety", "CB1", "CB2", "OLB1", "OLB2"]

POSITION_FIT_MAP = {
    "QB":      "qb_fit",
    "RB":      "rb_fit",
    "Center":  "center_fit",
    "WR1":     "wr_fit",
    "WR2":     "wr_fit",
    "Slot1":   "slot_fit",
    "Slot2":   "slot_fit",
    "Blitzer": "blitzer_fit",
    "MLB":     "mlb_fit",
    "Safety":  "safety_fit",
    "CB1":     "cb_fit",
    "CB2":     "cb_fit",
    "OLB1":    "olb_fit",
    "OLB2":    "olb_fit",
}

ROLE_FIT_KEYS = [
    "qb_fit", "rb_fit", "wr_fit", "slot_fit", "center_fit",
    "blitzer_fit", "mlb_fit", "safety_fit", "cb_fit", "olb_fit",
]
ROLE_FIT_LABELS = {
    "qb_fit": "QB", "rb_fit": "RB", "wr_fit": "WR", "slot_fit": "Slot",
    "center_fit": "Center", "blitzer_fit": "Blitzer", "mlb_fit": "MLB",
    "safety_fit": "Safety", "cb_fit": "CB", "olb_fit": "OLB",
}

# ============================================================
# SESSION STATE
# ============================================================

def init_session_state():
    defaults = {
        "roster":                copy.deepcopy(SAMPLE_ROSTER),
        "ratings":               {},
        "lineup":                None,
        "qb_mode":               "locked",
        "locked_qb":             None,
        "qb_group":              [],
        "coaching_mode":         "balanced",
        "possessions_per_half":  3,
        "validation_results":    [],
        "optimizer_score":       None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

# ============================================================
# ROLE FIT CALCULATION
# ============================================================

def calc_role_fits(p):
    s  = p["speed"]
    h  = p["hands"]
    fp = p["flag_pulling"]
    rr = p["route_running"]
    bl = p["blocking"]
    sn = p["snapping"]
    qb = p["qb_ability"]
    iq = p["football_iq"]
    ef = p["effort"]
    cf = p["confidence"]
    return {
        "qb_fit":      (qb*2 + iq + cf) / 4,
        "rb_fit":      (s*2  + h  + iq) / 4,
        "wr_fit":      (s    + rr + h*2) / 4,
        "slot_fit":    (rr   + h  + iq + s) / 4,
        "center_fit":  (sn*2 + iq + bl) / 4,
        "blitzer_fit": (s    + fp + iq + ef) / 4,
        "mlb_fit":     (fp*2 + iq + ef) / 4,
        "safety_fit":  (s    + fp + iq + h) / 4,
        "cb_fit":      (s*2  + fp + iq) / 4,
        "olb_fit":     (fp   + ef + s  + iq) / 4,
    }

def fits_for_roster(roster):
    return {p["name"]: calc_role_fits(p) for p in roster}

def overall_fit(fits_dict):
    vals = list(fits_dict.values())
    return sum(vals) / len(vals) if vals else 3.0

def stoplight_color(score):
    if score >= 4.0:
        return "#27ae60"
    elif score >= 3.0:
        return "#f39c12"
    return "#c0392b"

# ============================================================
# SEGMENT UTILITIES
# ============================================================

def get_segments(possessions_per_half):
    segs = []
    for half in ["1H", "2H"]:
        for poss in range(1, possessions_per_half + 1):
            segs.append((half, "Offense", poss))
            segs.append((half, "Defense", poss))
    return segs

def seg_label(half, phase, poss):
    return f"{half} {phase} #{poss}"

def get_entry(lineup, half, phase, poss):
    for e in lineup[half][phase]:
        if e["possession"] == poss:
            return e
    return None

# ============================================================
# POSITION ASSIGNMENT
# ============================================================

def assign_positions(on_field, phase, fits, qb_mode="rotating",
                     locked_qb=None, qb_group=None, qb_rotation_idx=0):
    remaining = list(on_field)
    positions = {}

    if phase == "Offense":
        if qb_mode == "locked" and locked_qb and locked_qb in remaining:
            qb_player = locked_qb
        elif qb_mode == "group" and qb_group:
            available = [p for p in (qb_group or []) if p in remaining]
            qb_player = (available[qb_rotation_idx % len(available)]
                         if available
                         else max(remaining, key=lambda n: fits.get(n, {}).get("qb_fit", 0)))
        else:
            qb_player = max(remaining, key=lambda n: fits.get(n, {}).get("qb_fit", 0))

        positions["QB"] = qb_player
        remaining.remove(qb_player)

        center = max(remaining, key=lambda n: fits.get(n, {}).get("center_fit", 0))
        positions["Center"] = center
        remaining.remove(center)

        rb = max(remaining, key=lambda n: fits.get(n, {}).get("rb_fit", 0))
        positions["RB"] = rb
        remaining.remove(rb)

        wr1 = max(remaining, key=lambda n: fits.get(n, {}).get("wr_fit", 0))
        positions["WR1"] = wr1
        remaining.remove(wr1)

        wr2 = max(remaining, key=lambda n: fits.get(n, {}).get("wr_fit", 0))
        positions["WR2"] = wr2
        remaining.remove(wr2)

        slot1 = max(remaining, key=lambda n: fits.get(n, {}).get("slot_fit", 0))
        positions["Slot1"] = slot1
        remaining.remove(slot1)

        positions["Slot2"] = remaining[0]

    else:
        mlb = max(remaining, key=lambda n: fits.get(n, {}).get("mlb_fit", 0))
        positions["MLB"] = mlb
        remaining.remove(mlb)

        safety = max(remaining, key=lambda n: fits.get(n, {}).get("safety_fit", 0))
        positions["Safety"] = safety
        remaining.remove(safety)

        blitzer = max(remaining, key=lambda n: fits.get(n, {}).get("blitzer_fit", 0))
        positions["Blitzer"] = blitzer
        remaining.remove(blitzer)

        cb1 = max(remaining, key=lambda n: fits.get(n, {}).get("cb_fit", 0))
        positions["CB1"] = cb1
        remaining.remove(cb1)

        cb2 = max(remaining, key=lambda n: fits.get(n, {}).get("cb_fit", 0))
        positions["CB2"] = cb2
        remaining.remove(cb2)

        olb1 = max(remaining, key=lambda n: fits.get(n, {}).get("olb_fit", 0))
        positions["OLB1"] = olb1
        remaining.remove(olb1)

        positions["OLB2"] = remaining[0]

    return positions

# ============================================================
# LINEUP GENERATION
# ============================================================

def choose_sitters(eligible, n_sits, sit_counts, max_sits, mode, fits):
    if n_sits <= 0:
        return []
    under = [p for p in eligible if sit_counts[p] < max_sits]
    pool = under if len(under) >= n_sits else eligible
    if len(pool) <= n_sits:
        return list(pool[:n_sits])

    def sort_key(name):
        sits = sit_counts[name]
        ov = overall_fit(fits[name]) if name in fits else 3.0
        # Use name as deterministic tiebreaker to ensure reproducible results
        if mode in ("balanced", "equal_pt"):
            return (sits, name)
        elif mode == "strongest":
            return (ov, name)
        elif mode == "development":
            return (-ov, name)
        return (sits, name)

    return sorted(pool, key=sort_key)[:n_sits]


def generate_lineup(roster, qb_mode, locked_qb, qb_group,
                    possessions_per_half, mode):
    n = len(roster)
    if n == 0:
        return None

    on_field_count = min(7, n)
    sits_per_seg = max(0, n - on_field_count)
    segments = get_segments(possessions_per_half)
    total_sits = len(segments) * sits_per_seg
    target = total_sits / n if n else 0
    max_sits_val = math.ceil(target)

    all_names = [p["name"] for p in roster]
    fits = fits_for_roster(roster)
    sit_counts = {name: 0 for name in all_names}
    prev_out = set()

    lineup = {"1H": {"Offense": [], "Defense": []},
              "2H": {"Offense": [], "Defense": []}}
    qb_rotation_idx = 0

    for half, phase, poss in segments:
        eligible = [nm for nm in all_names if nm not in prev_out]
        out = choose_sitters(eligible, sits_per_seg, sit_counts,
                             max_sits_val, mode, fits)
        on_field = [nm for nm in all_names if nm not in out]

        positions = assign_positions(
            on_field, phase, fits,
            qb_mode=qb_mode,
            locked_qb=locked_qb,
            qb_group=qb_group,
            qb_rotation_idx=qb_rotation_idx,
        )

        if phase == "Offense":
            qb_rotation_idx += 1

        lineup[half][phase].append({
            "possession": poss,
            "on_field":   on_field,
            "out":        out,
            "positions":  positions,
        })

        for nm in out:
            sit_counts[nm] += 1
        prev_out = set(out)

    return lineup

# ============================================================
# VALIDATION
# ============================================================

def validate_no_back_to_back_sits(lineup, possessions_per_half):
    segments = get_segments(possessions_per_half)
    prev_out = None
    violations = []

    for idx, (half, phase, poss) in enumerate(segments):
        entry = get_entry(lineup, half, phase, poss)
        if entry is None:
            prev_out = None
            continue
        curr_out = set(entry["out"])

        if prev_out is not None:
            for player in curr_out & prev_out:
                ph, pp, pr = segments[idx - 1]
                violations.append({
                    "player": player,
                    "seg1": seg_label(ph, pp, pr),
                    "seg2": seg_label(half, phase, poss),
                })
        prev_out = curr_out

    if violations:
        detail = "; ".join(
            f"{v['player']} ({v['seg1']} -> {v['seg2']})" for v in violations
        )
        return {
            "rule": "No Back-to-Back Sits",
            "status": "fail",
            "detail": detail,
            "offending_players": list({v["player"] for v in violations}),
            "offending_segment": violations[0]["seg2"],
        }
    return {
        "rule": "No Back-to-Back Sits",
        "status": "pass",
        "detail": "No back-to-back sit violations detected.",
        "offending_players": [],
        "offending_segment": None,
    }


def validate_sit_balance(lineup, roster, possessions_per_half):
    n = len(roster)
    if n == 0:
        return {"rule": "Sit Balance", "status": "pass",
                "detail": "Empty roster.", "offending_players": [],
                "offending_segment": None}

    on_field_count = min(7, n)
    sits_per_seg = max(0, n - on_field_count)
    total_sits = len(get_segments(possessions_per_half)) * sits_per_seg
    target = total_sits / n
    min_sits_val = math.floor(target)
    max_sits_val = math.ceil(target)

    counts = {p["name"]: 0 for p in roster}
    for half in ["1H", "2H"]:
        for phase in ["Offense", "Defense"]:
            for entry in lineup[half][phase]:
                for nm in entry["out"]:
                    if nm in counts:
                        counts[nm] += 1

    over_max = [nm for nm, c in counts.items() if c > max_sits_val]
    spread = (max(counts.values()) - min(counts.values())) if counts else 0

    if over_max:
        detail = (f"Players exceeding max sits ({max_sits_val}): "
                  f"{', '.join(over_max)}. "
                  f"Counts: {dict(sorted(counts.items()))}")
        return {"rule": "Sit Balance", "status": "fail", "detail": detail,
                "offending_players": over_max, "offending_segment": None}
    if spread > 1:
        detail = (f"Sit spread of {spread} "
                  f"(min={min(counts.values())}, max={max(counts.values())}). "
                  "Consider regenerating.")
        return {"rule": "Sit Balance", "status": "warn", "detail": detail,
                "offending_players": [], "offending_segment": None}

    return {"rule": "Sit Balance", "status": "pass",
            "detail": f"All players have {min_sits_val}-{max_sits_val} sits. Balanced.",
            "offending_players": [], "offending_segment": None}


def validate_offense_defense_sit_balance(lineup, roster):
    off_sits = {p["name"]: 0 for p in roster}
    def_sits = {p["name"]: 0 for p in roster}

    for half in ["1H", "2H"]:
        for e in lineup[half]["Offense"]:
            for nm in e["out"]:
                if nm in off_sits:
                    off_sits[nm] += 1
        for e in lineup[half]["Defense"]:
            for nm in e["out"]:
                if nm in def_sits:
                    def_sits[nm] += 1

    one_sided = []
    for p in roster:
        nm = p["name"]
        o, d = off_sits[nm], def_sits[nm]
        if o >= 2 and d == 0:
            one_sided.append(f"{nm} (all {o} sits on Offense)")
        elif d >= 2 and o == 0:
            one_sided.append(f"{nm} (all {d} sits on Defense)")

    if one_sided:
        return {
            "rule": "Offense/Defense Sit Balance",
            "status": "warn",
            "detail": "One-sided sits: " + "; ".join(one_sided),
            "offending_players": [s.split(" ")[0] for s in one_sided],
            "offending_segment": None,
        }
    return {
        "rule": "Offense/Defense Sit Balance",
        "status": "pass",
        "detail": "Sit distribution across Offense/Defense is balanced.",
        "offending_players": [],
        "offending_segment": None,
    }


def validate_sit_pairing_balance(lineup, possessions_per_half):
    pair_counts = {}
    trio_counts = {}

    for half, phase, poss in get_segments(possessions_per_half):
        entry = get_entry(lineup, half, phase, poss)
        if entry is None:
            continue
        out = sorted(entry["out"])
        for pair in itertools.combinations(out, 2):
            pair_counts[pair] = pair_counts.get(pair, 0) + 1
        if len(out) >= 3:
            for trio in itertools.combinations(out, 3):
                trio_counts[trio] = trio_counts.get(trio, 0) + 1

    issues = []
    for pair, cnt in pair_counts.items():
        if cnt > 2:
            issues.append(f"Pair ({pair[0]} & {pair[1]}) sit together {cnt}x (max 2)")
    for trio, cnt in trio_counts.items():
        if cnt > 2:
            issues.append(
                f"Trio ({trio[0]}, {trio[1]}, {trio[2]}) sit together {cnt}x (max 2)"
            )

    if issues:
        return {"rule": "Sit Pairing Balance", "status": "warn",
                "detail": "; ".join(issues),
                "offending_players": [], "offending_segment": None}
    return {"rule": "Sit Pairing Balance", "status": "pass",
            "detail": "No repeated sit-group patterns detected.",
            "offending_players": [], "offending_segment": None}


def validate_qb_rules(lineup, possessions_per_half, qb_mode, locked_qb):
    if qb_mode != "locked" or not locked_qb:
        return {"rule": "QB Rules", "status": "pass",
                "detail": "No locked-QB constraints active.",
                "offending_players": [], "offending_segment": None}

    violations = []
    for half, phase, poss in get_segments(possessions_per_half):
        if phase != "Offense":
            continue
        entry = get_entry(lineup, half, phase, poss)
        if entry is None:
            continue
        if (locked_qb in entry["out"]
                and entry["positions"].get("QB") == locked_qb):
            violations.append(seg_label(half, phase, poss))

    if violations:
        return {
            "rule": "QB Rules",
            "status": "fail",
            "detail": (f"Locked QB '{locked_qb}' is in out-list but also assigned "
                       f"QB in: {', '.join(violations)}"),
            "offending_players": [locked_qb],
            "offending_segment": violations[0],
        }
    return {"rule": "QB Rules", "status": "pass",
            "detail": "QB assignment is valid.",
            "offending_players": [], "offending_segment": None}


def validate_position_counts(lineup, possessions_per_half):
    violations = []
    for half, phase, poss in get_segments(possessions_per_half):
        entry = get_entry(lineup, half, phase, poss)
        lbl = seg_label(half, phase, poss)
        if entry is None:
            violations.append(f"{lbl}: missing entry")
            continue
        if len(entry["on_field"]) != 7:
            violations.append(
                f"{lbl}: {len(entry['on_field'])} on field (expected 7)"
            )
        expected = OFFENSE_POSITIONS if phase == "Offense" else DEFENSE_POSITIONS
        for pos in expected:
            if pos not in entry["positions"]:
                violations.append(f"{lbl}: missing position '{pos}'")

    if violations:
        return {"rule": "Position Counts", "status": "fail",
                "detail": "; ".join(violations),
                "offending_players": [], "offending_segment": None}
    return {"rule": "Position Counts", "status": "pass",
            "detail": "All segments have correct counts and positions.",
            "offending_players": [], "offending_segment": None}


def validate_no_duplicate_players(lineup, possessions_per_half):
    violations = []
    for half, phase, poss in get_segments(possessions_per_half):
        entry = get_entry(lineup, half, phase, poss)
        if entry is None:
            continue
        seen = {}
        for nm in entry["on_field"]:
            seen[nm] = seen.get(nm, 0) + 1
        dupes = [nm for nm, cnt in seen.items() if cnt > 1]
        if dupes:
            violations.append(
                f"{seg_label(half, phase, poss)}: duplicates {dupes}"
            )

    if violations:
        return {"rule": "No Duplicate Players", "status": "fail",
                "detail": "; ".join(violations),
                "offending_players": [], "offending_segment": None}
    return {"rule": "No Duplicate Players", "status": "pass",
            "detail": "No duplicate players in any segment.",
            "offending_players": [], "offending_segment": None}


def run_all_validations(lineup, roster, possessions_per_half,
                        qb_mode="locked", locked_qb=None):
    return [
        validate_no_back_to_back_sits(lineup, possessions_per_half),
        validate_sit_balance(lineup, roster, possessions_per_half),
        validate_offense_defense_sit_balance(lineup, roster),
        validate_sit_pairing_balance(lineup, possessions_per_half),
        validate_qb_rules(lineup, possessions_per_half, qb_mode, locked_qb),
        validate_position_counts(lineup, possessions_per_half),
        validate_no_duplicate_players(lineup, possessions_per_half),
    ]

# ============================================================
# AUTO-FIX
# ============================================================

def auto_fix_lineup(lineup, roster, possessions_per_half):
    fixed = copy.deepcopy(lineup)
    fits = fits_for_roster(roster)
    segments = get_segments(possessions_per_half)
    issues_fixed = 0

    for iteration in range(20):
        changed = False
        for idx in range(1, len(segments)):
            ph, pp, pr = segments[idx - 1]
            ch, cp, cr = segments[idx]

            prev_entry = get_entry(fixed, ph, pp, pr)
            curr_entry = get_entry(fixed, ch, cp, cr)
            if prev_entry is None or curr_entry is None:
                continue

            overlap = set(curr_entry["out"]) & set(prev_entry["out"])
            if not overlap:
                continue

            next_out = set()
            if idx + 1 < len(segments):
                nh, next_phase, nr = segments[idx + 1]
                ne = get_entry(fixed, nh, next_phase, nr)
                if ne:
                    next_out = set(ne["out"])

            for offender in sorted(overlap):
                candidates = [
                    nm for nm in curr_entry["on_field"]
                    if nm not in set(prev_entry["out"]) and nm not in next_out
                ]
                if not candidates:
                    candidates = [
                        nm for nm in curr_entry["on_field"]
                        if nm not in set(prev_entry["out"])
                    ]
                if not candidates:
                    continue

                swap_in = candidates[0]
                curr_entry["out"] = [
                    swap_in if nm == offender else nm
                    for nm in curr_entry["out"]
                ]
                curr_entry["on_field"] = [
                    offender if nm == swap_in else nm
                    for nm in curr_entry["on_field"]
                ]
                curr_entry["positions"] = assign_positions(
                    curr_entry["on_field"], cp, fits, qb_mode="rotating",
                )
                issues_fixed += 1
                changed = True
                break

        if not changed:
            break

    result = validate_no_back_to_back_sits(fixed, possessions_per_half)
    issues_remaining = len(result["offending_players"])
    return fixed, issues_fixed, issues_remaining

# ============================================================
# OPTIMIZER SCORE
# ============================================================

def score_lineup_quality(lineup, roster, possessions_per_half,
                         qb_mode="locked", locked_qb=None):
    validations = run_all_validations(
        lineup, roster, possessions_per_half, qb_mode, locked_qb
    )
    score = 100.0
    for v in validations:
        if v["status"] == "fail":
            score -= 20.0
        elif v["status"] == "warn":
            score -= 5.0

    fits = fits_for_roster(roster)
    total_fit = 0.0
    total_pos = 0

    for half, phase, poss in get_segments(possessions_per_half):
        entry = get_entry(lineup, half, phase, poss)
        if entry is None:
            continue
        pos_list = OFFENSE_POSITIONS if phase == "Offense" else DEFENSE_POSITIONS
        for pos in pos_list:
            player = entry["positions"].get(pos)
            if player and player in fits:
                fit_key = POSITION_FIT_MAP.get(pos)
                if fit_key:
                    total_fit += fits[player][fit_key]
                    total_pos += 1

    if total_pos > 0:
        avg_fit = total_fit / total_pos
        score += (avg_fit - 3.0) * 5.0

    return round(max(0.0, min(100.0, score)), 1)

# ============================================================
# QA TESTS
# ============================================================

def _build_fixture_lineup(outs_list, roster, pph=3):
    all_names = [p["name"] for p in roster]
    fits = fits_for_roster(roster)
    segments = get_segments(pph)
    lineup = {"1H": {"Offense": [], "Defense": []},
              "2H": {"Offense": [], "Defense": []}}

    for idx, (half, phase, poss) in enumerate(segments):
        out = list(outs_list[idx]) if idx < len(outs_list) else []
        on_field = [nm for nm in all_names if nm not in out]
        while len(on_field) < 7 and out:
            on_field.append(out.pop())

        positions = assign_positions(on_field, phase, fits, qb_mode="rotating")
        lineup[half][phase].append({
            "possession": poss,
            "on_field":   on_field,
            "out":        out,
            "positions":  positions,
        })
    return lineup


def run_qa_tests():
    roster = copy.deepcopy(SAMPLE_ROSTER)
    pph = 3

    K  = "Katrina"
    I  = "Isla"
    T  = "Timber"
    Fr = "Francie"
    Fe = "Felicity"
    S  = "Sophia"
    Q  = "Quinn"
    A  = "Adriana"
    O  = "Olivia"
    M  = "Maya"

    # Segment order (pph=3, 12 total):
    # 0=(1H,Off,1) 1=(1H,Def,1) 2=(1H,Off,2) 3=(1H,Def,2)
    # 4=(1H,Off,3) 5=(1H,Def,3) 6=(2H,Off,1) 7=(2H,Def,1)
    # 8=(2H,Off,2) 9=(2H,Def,2) 10=(2H,Off,3) 11=(2H,Def,3)

    # Test 1: Katrina back-to-back seg0->seg1  FAIL
    t1 = [
        [K, I, T],   [K, Fr, Fe],  [Q, A, O],   [M, I, T],
        [Fr, S, Q],  [A, O, M],    [I, T, Fe],   [K, S, Q],
        [Fr, A, O],  [I, T, M],    [Fe, S, K],   [Q, A, O],
    ]

    # Test 2: Francie back-to-back seg1->seg2  FAIL
    t2 = [
        [K, I, S],   [Fr, O, Fe],  [Fr, A, T],   [K, I, S],
        [O, M, Fe],  [Q, A, T],    [K, I, S],    [Fr, O, M],
        [T, Q, A],   [K, I, Fe],   [S, M, Fr],   [O, Q, A],
    ]

    # Test 3: Quinn back-to-back across halftime seg5->seg6  FAIL
    t3 = [
        [K, I, T],   [Fr, Fe, S],  [Q, A, O],    [M, I, T],
        [Fr, Fe, K], [S, Q, A],    [K, Q, T],    [Fr, Fe, O],
        [I, S, M],   [A, K, T],    [Fr, Q, O],   [I, S, M],
    ]

    # Test 4: Clean lineup  PASS
    t4 = [
        [K, I, T],   [Fr, Fe, S],  [Q, A, O],    [M, K, I],
        [T, Fr, Fe], [S, Q, A],    [O, M, K],    [I, T, Fr],
        [Fe, S, Q],  [A, O, M],    [K, I, T],    [Fr, Fe, S],
    ]

    # Test 5: Katrina has 6 sits -> FAIL sit balance
    t5 = [
        [K, I, T],   [Fr, Fe, S],  [K, Q, A],    [I, O, M],
        [K, Fr, Fe], [T, S, Q],    [K, A, O],    [I, Fr, M],
        [K, T, S],   [Fe, Q, A],   [K, O, M],    [I, T, Fr],
    ]

    # Test 6: Katrina 4 sits all on Offense -> WARNING
    t6 = [
        [K, I, T],   [Fr, Fe, S],  [K, Q, A],    [I, O, M],
        [Fr, Fe, T], [S, Q, A],    [K, O, M],    [I, T, Fr],
        [K, Fe, S],  [Q, A, O],    [M, I, T],    [Fr, Fe, S],
    ]

    # Test 7: Trio (K,I,T) sits together 4x -> WARNING
    t7 = [
        [K, I, T],   [Fr, Fe, S],  [K, I, T],    [Q, A, O],
        [K, I, T],   [M, Fr, Fe],  [K, I, T],    [S, Q, A],
        [O, M, Fr],  [Fe, S, Q],   [A, O, M],    [Fr, Fe, S],
    ]

    fixtures = [
        ("Test 1", t1, "fail", "No Back-to-Back Sits",
         "Katrina sits back-to-back: 1H Offense #1 -> 1H Defense #1"),
        ("Test 2", t2, "fail", "No Back-to-Back Sits",
         "Francie sits back-to-back: 1H Defense #1 -> 1H Offense #2"),
        ("Test 3", t3, "fail", "No Back-to-Back Sits",
         "Quinn sits back-to-back across halftime: 1H Defense #3 -> 2H Offense #1"),
        ("Test 4", t4, "pass", "No Back-to-Back Sits",
         "Clean lineup -- no back-to-back sits"),
        ("Test 5", t5, "fail", "Sit Balance",
         "Katrina has 6 sits, exceeding max_sits=4"),
        ("Test 6", t6, "warn", "Offense/Defense Sit Balance",
         "Katrina has 4 sits all on Offense"),
        ("Test 7", t7, "warn", "Sit Pairing Balance",
         "Trio (Katrina, Isla, Timber) sits together 4 times"),
    ]

    results = []
    for name, outs, expected_status, expected_rule, description in fixtures:
        lineup = _build_fixture_lineup(outs, roster, pph)
        validations = run_all_validations(lineup, roster, pph)
        val_map = {v["rule"]: v for v in validations}

        target_val = val_map.get(expected_rule, {})
        actual_status = target_val.get("status", "pass")

        if expected_status == "pass":
            passed = actual_status == "pass"
        elif expected_status == "fail":
            passed = actual_status == "fail"
        else:
            passed = actual_status in ("warn", "fail")

        results.append({
            "name":        name,
            "description": description,
            "expected":    expected_status,
            "actual":      actual_status,
            "rule":        expected_rule,
            "detail":      target_val.get("detail", ""),
            "passed":      passed,
        })
    return results

# ============================================================
# PDF CONSTANTS
# ============================================================

_PDF_RED   = rl_colors.HexColor("#C0392B")
_PDF_BLACK = rl_colors.black
_PDF_WHITE = rl_colors.white
_PDF_LGREY = rl_colors.HexColor("#F5F5F5")

# ============================================================
# PDF — FULL
# ============================================================

def _make_full_pdf(lineup, roster, possessions_per_half, validations, optimizer_score):
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=letter,
        leftMargin=0.5*inch, rightMargin=0.5*inch,
        topMargin=0.5*inch,  bottomMargin=0.5*inch,
    )
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(
        "🦆 DivaDucks -- Game Lineup", styles["Title"]
    ))
    elements.append(Spacer(1, 0.1*inch))

    score_txt = (f"Optimizer Score: {optimizer_score}/100"
                 if optimizer_score is not None else "Optimizer Score: N/A")
    elements.append(Paragraph(score_txt, styles["Heading2"]))
    elements.append(Spacer(1, 0.1*inch))

    for half, phase, poss in get_segments(possessions_per_half):
        entry = get_entry(lineup, half, phase, poss)
        if entry is None:
            continue

        elements.append(Paragraph(seg_label(half, phase, poss), styles["Heading3"]))
        pos_list = OFFENSE_POSITIONS if phase == "Offense" else DEFENSE_POSITIONS
        data = [["Position", "Player"]]
        for pos in pos_list:
            data.append([pos, entry["positions"].get(pos, "--")])
        data.append(["Sitting Out", ", ".join(entry["out"]) or "--"])

        tbl = Table(data, colWidths=[1.8*inch, 3.5*inch])
        tbl.setStyle(TableStyle([
            ("BACKGROUND",     (0, 0), (-1, 0),  _PDF_RED),
            ("TEXTCOLOR",      (0, 0), (-1, 0),  _PDF_WHITE),
            ("FONTNAME",       (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",       (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [_PDF_WHITE, _PDF_LGREY]),
            ("GRID",           (0, 0), (-1, -1), 0.5, _PDF_RED),
            ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING",    (0, 0), (-1, -1), 4),
        ]))
        elements.append(tbl)
        elements.append(Spacer(1, 0.08*inch))

    elements.append(Paragraph("Rules Check", styles["Heading2"]))
    val_data = [["Rule", "Status", "Detail"]]
    for v in validations:
        icon = ("PASS" if v["status"] == "pass"
                else ("WARN" if v["status"] == "warn" else "FAIL"))
        val_data.append([v["rule"], icon, v["detail"][:90]])

    vtbl = Table(val_data, colWidths=[2.0*inch, 0.8*inch, 4.5*inch])
    vtbl.setStyle(TableStyle([
        ("BACKGROUND",     (0, 0), (-1, 0),  _PDF_RED),
        ("TEXTCOLOR",      (0, 0), (-1, 0),  _PDF_WHITE),
        ("FONTNAME",       (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",       (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [_PDF_WHITE, _PDF_LGREY]),
        ("GRID",           (0, 0), (-1, -1), 0.5, _PDF_RED),
        ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",    (0, 0), (-1, -1), 4),
    ]))
    elements.append(vtbl)
    elements.append(Spacer(1, 0.1*inch))

    elements.append(Paragraph("Player Usage Summary", styles["Heading2"]))
    usage = _build_usage_data(lineup, roster, possessions_per_half)
    u_data = [["Player", "Off", "Def", "Total", "O-Sits", "D-Sits", "Sits", "Sit%"]]
    for r in usage:
        u_data.append([
            r["name"], r["off_apps"], r["def_apps"], r["total_apps"],
            r["off_sits"], r["def_sits"], r["total_sits"],
            f"{r['sit_pct']:.1f}%",
        ])
    utbl = Table(u_data, colWidths=[1.3*inch] + [0.7*inch]*7)
    utbl.setStyle(TableStyle([
        ("BACKGROUND",     (0, 0), (-1, 0),  _PDF_RED),
        ("TEXTCOLOR",      (0, 0), (-1, 0),  _PDF_WHITE),
        ("FONTNAME",       (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",       (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [_PDF_WHITE, _PDF_LGREY]),
        ("GRID",           (0, 0), (-1, -1), 0.5, _PDF_RED),
        ("ALIGN",          (1, 0), (-1, -1), "CENTER"),
        ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",    (0, 0), (-1, -1), 3),
    ]))
    elements.append(utbl)

    doc.build(elements)
    buf.seek(0)
    return buf

# ============================================================
# PDF — FIELD CARD
# ============================================================

def _make_field_card_pdf(lineup, roster, possessions_per_half):
    buf = BytesIO()
    page_w, page_h = landscape(letter)
    c = rl_canvas.Canvas(buf, pagesize=(page_w, page_h))

    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(_PDF_RED)
    c.drawString(0.4*inch, page_h - 0.35*inch,
                 "DivaDucks -- Field Card")

    segments = get_segments(possessions_per_half)
    n_cols = len(segments)
    left_margin = 0.4*inch
    label_col_w = 0.85*inch
    avail_w = page_w - left_margin*2 - label_col_w
    col_w = avail_w / max(n_cols, 1)
    row_h = 14
    header_y = page_h - 0.65*inch

    # Column headers
    c.setFont("Helvetica-Bold", 7)
    for ci, (half, phase, poss) in enumerate(segments):
        x = left_margin + label_col_w + ci * col_w
        c.setFillColor(_PDF_RED)
        c.rect(x, header_y - row_h, col_w - 1, row_h, fill=1, stroke=0)
        c.setFillColor(_PDF_WHITE)
        c.drawString(x + 2, header_y - row_h + 3,
                     f"{half} {phase[:3]} #{poss}")

    all_pos = list(dict.fromkeys(OFFENSE_POSITIONS + DEFENSE_POSITIONS))
    c.setFont("Helvetica", 7)

    for ri, pos in enumerate(all_pos):
        y = header_y - row_h * (ri + 2)
        if y < 0.35*inch:
            break
        bg = _PDF_LGREY if ri % 2 == 0 else _PDF_WHITE
        c.setFillColor(bg)
        c.rect(left_margin, y, page_w - left_margin*2, row_h, fill=1, stroke=0)
        c.setFillColor(_PDF_BLACK)
        c.setFont("Helvetica-Bold", 7)
        c.drawString(left_margin + 2, y + 3, pos)
        c.setFont("Helvetica", 7)
        for ci, (half, phase, poss) in enumerate(segments):
            x = left_margin + label_col_w + ci * col_w
            entry = get_entry(lineup, half, phase, poss)
            player = (entry["positions"].get(pos, "") or "") if entry else ""
            if player:
                c.drawString(x + 2, y + 3, player[:13])

    # Sitting-out row
    sit_y = header_y - row_h * (len(all_pos) + 2)
    if sit_y > 0.35*inch:
        c.setFillColor(_PDF_RED)
        c.rect(left_margin, sit_y - row_h,
               page_w - left_margin*2, row_h, fill=1, stroke=0)
        c.setFillColor(_PDF_WHITE)
        c.setFont("Helvetica-Bold", 7)
        c.drawString(left_margin + 2, sit_y - row_h + 3, "OUT:")
        c.setFont("Helvetica", 7)
        for ci, (half, phase, poss) in enumerate(segments):
            x = left_margin + label_col_w + ci * col_w
            entry = get_entry(lineup, half, phase, poss)
            out_str = (", ".join(entry["out"][:3])) if entry else ""
            c.setFillColor(_PDF_WHITE)
            c.drawString(x + 2, sit_y - row_h + 3, out_str[:20])

    c.save()
    buf.seek(0)
    return buf

# ============================================================
# USAGE DATA HELPER
# ============================================================

def _build_usage_data(lineup, roster, possessions_per_half):
    segments = get_segments(possessions_per_half)
    off_segs = [(h, ph, pr) for h, ph, pr in segments if ph == "Offense"]
    def_segs = [(h, ph, pr) for h, ph, pr in segments if ph == "Defense"]

    all_outs = []
    for h, ph, pr in segments:
        e = get_entry(lineup, h, ph, pr)
        if e:
            all_outs.append(frozenset(e["out"]))

    pair_counter = {}
    for out_set in all_outs:
        for pair in itertools.combinations(sorted(out_set), 2):
            pair_counter[pair] = pair_counter.get(pair, 0) + 1

    n_total = len(segments)
    rows = []
    for p in roster:
        nm = p["name"]
        off_apps = sum(
            1 for h, ph, pr in off_segs
            if nm in (get_entry(lineup, h, ph, pr) or {}).get("on_field", [])
        )
        def_apps = sum(
            1 for h, ph, pr in def_segs
            if nm in (get_entry(lineup, h, ph, pr) or {}).get("on_field", [])
        )
        off_sits = sum(
            1 for h, ph, pr in off_segs
            if nm in (get_entry(lineup, h, ph, pr) or {}).get("out", [])
        )
        def_sits = sum(
            1 for h, ph, pr in def_segs
            if nm in (get_entry(lineup, h, ph, pr) or {}).get("out", [])
        )
        total_sits = off_sits + def_sits
        sit_pct = (total_sits / n_total * 100) if n_total else 0.0

        partners = {}
        for pair, cnt in pair_counter.items():
            if nm in pair:
                other = pair[0] if pair[1] == nm else pair[1]
                partners[other] = cnt
        top = sorted(partners.items(), key=lambda x: -x[1])[:3]
        partner_str = ", ".join(f"{o}({c})" for o, c in top)

        rows.append({
            "name":         nm,
            "off_apps":     off_apps,
            "def_apps":     def_apps,
            "total_apps":   off_apps + def_apps,
            "off_sits":     off_sits,
            "def_sits":     def_sits,
            "total_sits":   total_sits,
            "sit_pct":      sit_pct,
            "top_partners": partner_str,
        })
    return rows

# ============================================================
# TAB 1 -- ROSTER AND RATINGS
# ============================================================

def render_tab_roster():
    st.subheader("Player Roster & Ratings")
    roster = st.session_state.roster

    c1, c2, _spacer = st.columns([1, 1, 3])
    with c1:
        if st.button("Load Sample Roster", use_container_width=True):
            st.session_state.roster = copy.deepcopy(SAMPLE_ROSTER)
            st.session_state.lineup = None
            st.session_state.optimizer_score = None
            st.rerun()
    with c2:
        if st.button("Reset Session", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

    st.markdown("---")

    # Names & notes
    st.markdown("#### Player Names & Notes")
    name_df = pd.DataFrame([{"Name": p["name"], "Notes": p["notes"]} for p in roster])
    edited_names = st.data_editor(
        name_df,
        use_container_width=True,
        num_rows="dynamic",
        key="name_editor",
        column_config={
            "Name":  st.column_config.TextColumn("Name",  required=True),
            "Notes": st.column_config.TextColumn("Notes", required=False),
        },
    )

    # Attributes
    st.markdown("#### Attribute Ratings (1-5)")
    attr_df = pd.DataFrame([
        {"Name": p["name"],
         **{lbl: p[attr] for attr, lbl in zip(ATTRIBUTES, ATTR_LABELS)}}
        for p in roster
    ])
    col_cfg = {"Name": st.column_config.TextColumn("Name", disabled=True)}
    for lbl in ATTR_LABELS:
        col_cfg[lbl] = st.column_config.NumberColumn(
            lbl, min_value=1, max_value=5, step=1
        )
    edited_attrs = st.data_editor(
        attr_df,
        use_container_width=True,
        num_rows="fixed",
        key="attr_editor",
        column_config=col_cfg,
    )

    if st.button("Save Roster Changes", use_container_width=True):
        new_roster = []
        old_lookup = {p["name"]: p for p in roster}
        for i, nrow in edited_names.iterrows():
            nm = str(nrow.get("Name", "")).strip()
            if not nm:
                continue
            notes = str(nrow.get("Notes", ""))
            attrs = {}
            if i < len(edited_attrs):
                arow = edited_attrs.iloc[i]
                attrs = {attr: int(arow.get(lbl, 3))
                         for attr, lbl in zip(ATTRIBUTES, ATTR_LABELS)}
            else:
                old = old_lookup.get(nm, {})
                attrs = {attr: old.get(attr, 3) for attr in ATTRIBUTES}
            new_roster.append({"name": nm, "notes": notes, **attrs})
        st.session_state.roster = new_roster
        st.session_state.lineup = None
        st.session_state.optimizer_score = None
        st.success(f"Roster saved -- {len(new_roster)} players.")
        st.rerun()

    st.markdown("---")

    # Role fit stoplight
    st.markdown("#### Role Fit Scores (green>=4.0 | amber>=3.0 | red<3.0)")
    fits = fits_for_roster(roster)
    role_keys = ROLE_FIT_KEYS
    role_lbls = [ROLE_FIT_LABELS[k] for k in role_keys]

    rows_html = []
    for p in roster:
        nm = p["name"]
        pf = fits.get(nm, {})
        cells = [f"<td style='padding:4px 8px;font-weight:bold'>{nm}</td>"]
        for k in role_keys:
            score = pf.get(k, 0)
            bg = stoplight_color(score)
            tc = "#000" if bg == "#f39c12" else "#fff"
            cells.append(
                f"<td style='background:{bg};color:{tc};"
                f"text-align:center;padding:4px 8px;border-radius:3px'>"
                f"{score:.2f}</td>"
            )
        rows_html.append("<tr>" + "".join(cells) + "</tr>")

    hdr = "<th style='padding:4px 8px'>Player</th>" + "".join(
        f"<th style='padding:4px 8px;text-align:center'>{l}</th>"
        for l in role_lbls
    )
    table_html = (
        "<div style='overflow-x:auto'>"
        "<table style='border-collapse:collapse;width:100%;font-size:13px'>"
        f"<thead><tr style='background:#C0392B;color:white'>{hdr}</tr></thead>"
        "<tbody>" + "".join(rows_html) + "</tbody>"
        "</table></div>"
    )
    st.markdown(table_html, unsafe_allow_html=True)

    st.markdown("---")

    # QB Configuration
    st.markdown("#### QB Configuration")
    qb_opts = ["Locked QB", "Rotating QB", "Group QB"]
    mode_map = {"Locked QB": "locked", "Rotating QB": "rotating", "Group QB": "group"}
    rev_map  = {v: k for k, v in mode_map.items()}
    current_label = rev_map.get(st.session_state.qb_mode, "Locked QB")
    sel = st.radio("QB Mode", qb_opts,
                   index=qb_opts.index(current_label),
                   horizontal=True, key="qb_mode_radio")
    st.session_state.qb_mode = mode_map[sel]

    player_names = [p["name"] for p in roster]
    if st.session_state.qb_mode == "locked":
        default_idx = 0
        if st.session_state.locked_qb in player_names:
            default_idx = player_names.index(st.session_state.locked_qb)
        st.session_state.locked_qb = st.selectbox(
            "Locked QB", player_names, index=default_idx, key="locked_qb_sel"
        )
    elif st.session_state.qb_mode == "group":
        existing = [p for p in (st.session_state.qb_group or []) if p in player_names]
        st.session_state.qb_group = st.multiselect(
            "QB Group (rotates)", player_names, default=existing, key="qb_group_sel"
        )

    st.markdown("---")
    st.markdown("#### Quick Rating Presets")
    pa, pb, pc = st.columns(3)
    with pa:
        if st.button("All Ratings -> 3", use_container_width=True):
            for p in st.session_state.roster:
                for attr in ATTRIBUTES:
                    p[attr] = 3
            st.session_state.lineup = None
            st.rerun()
    with pb:
        if st.button("All Ratings -> 4", use_container_width=True):
            for p in st.session_state.roster:
                for attr in ATTRIBUTES:
                    p[attr] = 4
            st.session_state.lineup = None
            st.rerun()
    with pc:
        if st.button("All Ratings -> 2", use_container_width=True):
            for p in st.session_state.roster:
                for attr in ATTRIBUTES:
                    p[attr] = 2
            st.session_state.lineup = None
            st.rerun()

# ============================================================
# TAB 2 -- GENERATE LINEUP
# ============================================================

def _run_generation(mode):
    roster = st.session_state.roster
    lu = generate_lineup(
        roster,
        st.session_state.qb_mode,
        st.session_state.locked_qb,
        st.session_state.qb_group,
        st.session_state.possessions_per_half,
        mode,
    )
    pph = st.session_state.possessions_per_half
    st.session_state.lineup = lu
    st.session_state.validation_results = run_all_validations(
        lu, roster, pph,
        st.session_state.qb_mode,
        st.session_state.locked_qb,
    )
    st.session_state.optimizer_score = score_lineup_quality(
        lu, roster, pph,
        st.session_state.qb_mode,
        st.session_state.locked_qb,
    )
    return st.session_state.optimizer_score


def render_tab_generate():
    st.subheader("Generate Lineup")

    roster = st.session_state.roster
    if not roster:
        st.warning("No players in roster. Load a roster in the Roster & Ratings tab.")
        return

    col1, col2 = st.columns(2)
    with col1:
        coaching_opts = ["Balanced", "Equal PT", "Development"]
        cm_map = {"Balanced": "balanced", "Equal PT": "equal_pt",
                  "Development": "development"}
        rev_cm = {v: k for k, v in cm_map.items()}
        sel_cm = st.radio(
            "Coaching Mode", coaching_opts,
            index=coaching_opts.index(rev_cm.get(st.session_state.coaching_mode, "Balanced")),
            horizontal=True, key="coaching_radio",
        )
        st.session_state.coaching_mode = cm_map[sel_cm]
    with col2:
        st.session_state.possessions_per_half = st.slider(
            "Possessions per Half", 1, 5,
            st.session_state.possessions_per_half,
            key="pph_slider",
        )

    st.markdown("---")
    st.markdown("#### Generation")

    g1, g2 = st.columns(2)
    with g1:
        if st.button("Generate Best Balanced Lineup", use_container_width=True):
            with st.spinner("Generating..."):
                sc = _run_generation("balanced")
            st.success(f"Balanced lineup generated! Score: {sc}/100")

        if st.button("Generate Strongest Lineup", use_container_width=True):
            with st.spinner("Generating..."):
                sc = _run_generation("strongest")
            st.success(f"Strongest lineup generated! Score: {sc}/100")

    with g2:
        if st.button("Generate Equal Playing Time Lineup", use_container_width=True):
            with st.spinner("Generating..."):
                sc = _run_generation("equal_pt")
            st.success(f"Equal PT lineup generated! Score: {sc}/100")

        if st.button("Generate Development Lineup", use_container_width=True):
            with st.spinner("Generating..."):
                sc = _run_generation("development")
            st.success(f"Development lineup generated! Score: {sc}/100")

    st.markdown("---")

    if st.button("Auto-Fix Lineup", use_container_width=True):
        if st.session_state.lineup is None:
            st.warning("Generate a lineup first.")
        else:
            with st.spinner("Applying auto-fix..."):
                fixed, fixed_count, remaining = auto_fix_lineup(
                    st.session_state.lineup,
                    roster,
                    st.session_state.possessions_per_half,
                )
            st.session_state.lineup = fixed
            pph = st.session_state.possessions_per_half
            st.session_state.validation_results = run_all_validations(
                fixed, roster, pph,
                st.session_state.qb_mode,
                st.session_state.locked_qb,
            )
            st.session_state.optimizer_score = score_lineup_quality(
                fixed, roster, pph,
                st.session_state.qb_mode,
                st.session_state.locked_qb,
            )
            if remaining == 0:
                st.success(
                    f"Auto-fix complete! Fixed {fixed_count} issue(s). "
                    f"No violations remain. Score: {st.session_state.optimizer_score}/100"
                )
            else:
                st.warning(
                    f"Fixed {fixed_count} issue(s), but {remaining} violation(s) "
                    "could not be resolved automatically. Try regenerating."
                )

    st.markdown("---")

    if st.button("Run QA Tests", use_container_width=True):
        with st.spinner("Running QA tests..."):
            qa_results = run_qa_tests()
        passed = sum(1 for r in qa_results if r["passed"])
        failed = len(qa_results) - passed
        if failed == 0:
            st.success(f"All {len(qa_results)} QA tests passed!")
        else:
            st.error(f"{failed} of {len(qa_results)} QA tests failed.")

        with st.expander("QA Test Results", expanded=True):
            for r in qa_results:
                icon = "PASS" if r["passed"] else "FAIL"
                st.markdown(f"**[{icon}] {r['name']}** -- _{r['description']}_")
                st.markdown(
                    f"&nbsp;&nbsp;Expected: `{r['expected'].upper()}` | "
                    f"Actual: `{r['actual'].upper()}` | Rule: _{r['rule']}_"
                )
                if r["detail"]:
                    st.caption(f"Detail: {r['detail']}")
                st.markdown("---")

# ============================================================
# TAB 3 -- LINEUP VIEW
# ============================================================

def render_tab_lineup():
    st.subheader("Lineup View")

    lineup = st.session_state.lineup
    if lineup is None:
        st.info("No lineup generated yet. Use the Generate Lineup tab.")
        return

    roster = st.session_state.roster
    pph    = st.session_state.possessions_per_half

    if st.session_state.optimizer_score is not None:
        st.metric("Optimizer Score", f"{st.session_state.optimizer_score} / 100")

    st.markdown("---")
    fits = fits_for_roster(roster)
    name_to_player = {p["name"]: p for p in roster}

    for half in ["1H", "2H"]:
        st.markdown(f"### {half}")
        for poss in range(1, pph + 1):
            col_off, col_def = st.columns(2)

            with col_off:
                entry = get_entry(lineup, half, "Offense", poss)
                if entry:
                    st.markdown(f"**Offense -- Possession {poss}**")
                    rows = []
                    for pos in OFFENSE_POSITIONS:
                        player = entry["positions"].get(pos, "--")
                        fit_key = POSITION_FIT_MAP.get(pos, "")
                        fit_score = fits.get(player, {}).get(fit_key, 0) if player != "--" else 0
                        rows.append({"Position": pos, "Player": player,
                                     "Fit": f"{fit_score:.2f}"})
                    rows.append({"Position": "Sitting Out",
                                 "Player": ", ".join(entry["out"]) or "--",
                                 "Fit": ""})
                    st.dataframe(pd.DataFrame(rows),
                                 use_container_width=True, hide_index=True)

            with col_def:
                entry = get_entry(lineup, half, "Defense", poss)
                if entry:
                    st.markdown(f"**Defense -- Possession {poss}**")
                    rows = []
                    for pos in DEFENSE_POSITIONS:
                        player = entry["positions"].get(pos, "--")
                        fit_key = POSITION_FIT_MAP.get(pos, "")
                        fit_score = fits.get(player, {}).get(fit_key, 0) if player != "--" else 0
                        rows.append({"Position": pos, "Player": player,
                                     "Fit": f"{fit_score:.2f}"})
                    rows.append({"Position": "Sitting Out",
                                 "Player": ", ".join(entry["out"]) or "--",
                                 "Fit": ""})
                    st.dataframe(pd.DataFrame(rows),
                                 use_container_width=True, hide_index=True)

        st.markdown("---")

    st.markdown("### Rules Check")
    val_results = st.session_state.validation_results
    if not val_results:
        val_results = run_all_validations(
            lineup, roster, pph,
            st.session_state.qb_mode,
            st.session_state.locked_qb,
        )

    for v in val_results:
        if v["status"] == "pass":
            st.success(f"PASS  **{v['rule']}** -- {v['detail']}")
        elif v["status"] == "warn":
            st.warning(f"WARN  **{v['rule']}** -- {v['detail']}")
        else:
            st.error(f"FAIL  **{v['rule']}** -- {v['detail']}")

# ============================================================
# TAB 4 -- PLAYER USAGE
# ============================================================

def render_tab_usage():
    st.subheader("Player Usage")

    lineup = st.session_state.lineup
    if lineup is None:
        st.info("No lineup generated yet.")
        return

    roster = st.session_state.roster
    pph    = st.session_state.possessions_per_half
    usage  = _build_usage_data(lineup, roster, pph)

    df = pd.DataFrame([{
        "Player":       r["name"],
        "Off Apps":     r["off_apps"],
        "Def Apps":     r["def_apps"],
        "Total Apps":   r["total_apps"],
        "Off Sits":     r["off_sits"],
        "Def Sits":     r["def_sits"],
        "Total Sits":   r["total_sits"],
        "Sit %":        f"{r['sit_pct']:.1f}%",
        "Top Partners": r["top_partners"],
    } for r in usage])

    st.dataframe(df, use_container_width=True, hide_index=True)
    st.markdown("---")

    fig1 = px.bar(
        pd.DataFrame(usage), x="name",
        y=["off_apps", "def_apps"],
        title="Appearances by Phase",
        labels={"name": "Player", "value": "Appearances", "variable": "Phase"},
        barmode="stack",
        color_discrete_map={"off_apps": "#2980b9", "def_apps": "#27ae60"},
    )
    fig1.update_layout(legend_title_text="Phase", xaxis_title="Player")
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.bar(
        pd.DataFrame(usage), x="name", y="total_sits",
        title="Total Sits per Player",
        labels={"name": "Player", "total_sits": "Sits"},
        color="total_sits",
        color_continuous_scale=["#27ae60", "#f39c12", "#c0392b"],
    )
    st.plotly_chart(fig2, use_container_width=True)

    fig3 = go.Figure(data=[go.Pie(
        labels=[r["name"] for r in usage],
        values=[r["total_sits"] for r in usage],
        hole=0.4,
    )])
    fig3.update_layout(title_text="Sit Distribution Across Players")
    st.plotly_chart(fig3, use_container_width=True)

# ============================================================
# TAB 5 -- EXPORT
# ============================================================

def render_tab_export():
    st.subheader("Export")

    lineup = st.session_state.lineup
    if lineup is None:
        st.info("No lineup to export. Generate a lineup first.")
        return

    roster = st.session_state.roster
    pph    = st.session_state.possessions_per_half
    validations = st.session_state.validation_results
    if not validations:
        validations = run_all_validations(
            lineup, roster, pph,
            st.session_state.qb_mode,
            st.session_state.locked_qb,
        )

    fails = [v for v in validations if v["status"] == "fail"]
    warns = [v for v in validations if v["status"] == "warn"]

    if fails:
        st.error("Export blocked -- resolve FAIL violations first:")
        for v in fails:
            detail = v["detail"]
            extra = ""
            if v.get("offending_players"):
                extra += f" | Players: {', '.join(v['offending_players'])}"
            if v.get("offending_segment"):
                extra += f" | Segment: {v['offending_segment']}"
            st.markdown(f"- **{v['rule']}**: {detail}{extra}")
        st.markdown(
            "Use the **Auto-Fix Lineup** button on the Generate tab, "
            "or regenerate the lineup."
        )
        return

    export_ok = True
    if warns:
        st.warning("The lineup has warnings:")
        for v in warns:
            st.markdown(f"- **{v['rule']}**: {v['detail']}")
        export_ok = st.checkbox(
            "I understand the warnings and want to proceed with export.",
            key="export_warn_ack",
        )

    if not export_ok:
        st.info("Acknowledge the warnings above to enable export.")
        return

    score = st.session_state.optimizer_score
    st.markdown("---")
    st.markdown("### Export Options")

    ec1, ec2 = st.columns(2)
    with ec1:
        st.markdown("**Full PDF** -- All segments, rules check, usage summary")
        if st.button("Export Full PDF", use_container_width=True):
            with st.spinner("Building PDF..."):
                pdf_buf = _make_full_pdf(lineup, roster, pph, validations, score)
            st.download_button(
                "Download Full PDF",
                data=pdf_buf,
                file_name="divaducks_full_lineup.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

    with ec2:
        st.markdown("**Field Card PDF** -- Compact landscape format")
        if st.button("Export Field Card PDF", use_container_width=True):
            with st.spinner("Building Field Card..."):
                pdf_buf = _make_field_card_pdf(lineup, roster, pph)
            st.download_button(
                "Download Field Card PDF",
                data=pdf_buf,
                file_name="divaducks_field_card.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

# ============================================================
# MAIN
# ============================================================

def main():
    init_session_state()

    st.markdown(
        "<h1 style='text-align:center;color:#C0392B'>"
        "🦆 DivaDucks Lineup Optimizer</h1>",
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Roster & Ratings",
        "Generate Lineup",
        "Lineup View",
        "Player Usage",
        "Export",
    ])

    with tab1:
        render_tab_roster()
    with tab2:
        render_tab_generate()
    with tab3:
        render_tab_lineup()
    with tab4:
        render_tab_usage()
    with tab5:
        render_tab_export()


if __name__ == "__main__":
    main()
