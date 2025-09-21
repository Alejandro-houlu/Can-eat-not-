from __future__ import annotations
import json, re
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

class FoodDB:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.data = self._load()

    def _load(self) -> Dict[str, Any]:
        raw = self.path.read_text(encoding="utf-8")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return json.loads(raw.strip())

    def _items(self):
        return self.data.get("food_response", [])

    def find_match(self, name: str) -> Optional[Dict[str, Any]]:
        name_l = name.lower()
        for item in self._items():
            entry = (item.get("food_entry_name") or "").lower()
            if entry == name_l or name_l in entry or entry in name_l:
                return item
            eaten = item.get("eaten", {})
            for k in ("food_name_singular","food_name_plural"):
                v = (eaten.get(k) or "").lower()
                if v and (v == name_l or name_l in v or v in name_l):
                    return item
        return None

    def calories_for(self, text: str) -> Optional[Tuple[int, str]]:
        m = re.match(r"\s*(\d+)\s+([\w\s\-]+)\s*$", text.strip(), flags=re.I)
        if not m:
            qty, item_name = 1, text.strip()
        else:
            qty, item_name = int(m.group(1)), m.group(2).strip()

        match = self.find_match(item_name)
        if not match:
            return None
        eaten = match.get("eaten", {})
        tn = eaten.get("total_nutritional_content", {})
        try:
            per_unit = float(tn.get("calories"))
        except (TypeError, ValueError):
            return None
        return int(round(qty * per_unit)), match.get("food_entry_name", item_name)
