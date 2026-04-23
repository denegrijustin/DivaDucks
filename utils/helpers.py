from typing import List, Dict, Any

def get_active_players(players: List[Dict]) -> List[Dict]:
    return [p for p in players if not p.get("archived", False)]

def get_available_players(players: List[Dict]) -> List[Dict]:
    return [p for p in players if p.get("available", True) and not p.get("archived", False) and not p.get("injured", False)]

def get_player_by_id(players: List[Dict], player_id: int) -> Dict:
    return next((p for p in players if p["id"] == player_id), None)

def format_position_label(pos: str) -> str:
    labels = {
        "QB": "Quarterback", "RB": "Running Back", "Center": "Center",
        "WR1": "Wide Receiver 1", "WR2": "Wide Receiver 2",
        "Slot1": "Slot Receiver 1", "Slot2": "Slot Receiver 2",
        "OLB1": "Outside Linebacker 1", "OLB2": "Outside Linebacker 2",
        "MLB": "Middle Linebacker", "CB1": "Cornerback 1", "CB2": "Cornerback 2",
        "Safety": "Safety", "Blitzer": "Blitzer"
    }
    return labels.get(pos, pos)

def ordinal(n: int) -> str:
    if 11 <= n % 100 <= 13:
        suffix = "th"
    elif n % 10 == 1:
        suffix = "st"
    elif n % 10 == 2:
        suffix = "nd"
    elif n % 10 == 3:
        suffix = "rd"
    else:
        suffix = "th"
    return f"{n}{suffix}"
