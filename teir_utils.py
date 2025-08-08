import json

def load_tiers():
    with open("tiers.json", "r") as f:
        return json.load(f)

def get_user_tier(user_id: int) -> str:
    tiers = load_tiers()
    return tiers.get("users", {}).get(str(user_id), "free")

def get_group_tier(group_id: int) -> str:
    tiers = load_tiers()
    return tiers.get("groups", {}).get(str(group_id), "free")

def get_tier_rules(tier_name: str):
    tiers = load_tiers()
    return tiers.get("tiers", {}).get(tier_name, {})