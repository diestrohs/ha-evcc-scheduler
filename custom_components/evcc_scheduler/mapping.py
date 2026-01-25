from typing import Dict, List, Optional

def extract_plans(state: Dict) -> Dict:
    vehicles: Dict[str, dict] = {}
    id_to_title: Dict[str, str] = {}

    raw_vehicles = state.get("vehicles", {})
    if not isinstance(raw_vehicles, dict):
        return {"vehicles": vehicles, "id_map": id_to_title}

    for vehicle_id, vehicle_data in raw_vehicles.items():
        if not isinstance(vehicle_data, dict):
            continue

        title = vehicle_data.get("title", vehicle_id)
        plans = vehicle_data.get("repeatingPlans", [])
        if not isinstance(plans, list):
            plans = []

        # Struktur: {vehicle_id: {"title": "...", "repeatingPlans": [...]}}
        vehicles[vehicle_id] = {
            "title": title,
            "repeatingPlans": plans
        }
        id_to_title[vehicle_id] = title

    return {"vehicles": vehicles, "id_map": id_to_title}


def build_entity_id(vehicle_id: str, index: int, title: str = None) -> str:
    # Entity IDs stay stable across languages; always derive from vehicle_id
    safe_name = (
        vehicle_id.lower()
        .replace(":", "_")
        .replace("-", "_")
        .replace(" ", "_")
    )
    return f"evcc_{safe_name}_repeating_plan_{index}"
