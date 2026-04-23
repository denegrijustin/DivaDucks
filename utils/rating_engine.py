from typing import Dict, Any

def compute_ratings(player: Dict[str, Any], weights: Dict[str, Any]) -> Dict[str, float]:
    def weighted(attrs):
        total = sum(player.get(a, 5) * w for a, w in attrs.items())
        weight_sum = sum(attrs.values())
        return round(total / weight_sum, 2) if weight_sum > 0 else 5.0

    w = weights
    ratings = {}
    ratings["offense_rating"] = weighted(w.get("offense", {}))
    ratings["defense_rating"] = weighted(w.get("defense", {}))
    ratings["qb_rating"] = weighted(w.get("qb", {})) if player.get("can_play_qb") else 0.0
    ratings["rb_rating"] = weighted(w.get("rb", {}))
    ratings["wr_rating"] = weighted(w.get("wr", {}))
    ratings["slot_rating"] = weighted(w.get("slot", {}))
    ratings["center_rating"] = weighted(w.get("center", {}))
    ratings["olb_rating"] = weighted(w.get("olb", {}))
    ratings["mlb_rating"] = weighted(w.get("mlb", {}))
    ratings["cb_rating"] = weighted(w.get("cb", {}))
    ratings["safety_rating"] = weighted(w.get("safety", {}))
    ratings["blitzer_rating"] = weighted(w.get("blitzer", {}))
    
    active_ratings = [v for v in ratings.values() if v > 0]
    ratings["versatility_rating"] = round(sum(active_ratings) / len(active_ratings), 2) if active_ratings else 5.0
    ratings["composite_rating"] = round((ratings["offense_rating"] + ratings["defense_rating"]) / 2, 2)
    
    return ratings

def enrich_players(players, settings):
    weights = settings.get("rating_weights", {})
    enriched = []
    for p in players:
        p_copy = dict(p)
        p_copy.update(compute_ratings(p, weights))
        enriched.append(p_copy)
    return enriched
