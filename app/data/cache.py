"""In-memory data cache loaded at startup for deterministic engine calls."""
from __future__ import annotations

from functools import lru_cache

from app.data.loaders import load_accessories, load_expert_packs, load_productlist, load_specific_yield


@lru_cache(maxsize=1)
def get_data_cache() -> dict:
    return {
        "specific_yield": load_specific_yield(),
        "products": load_productlist(),
        "expert_packs": load_expert_packs(),
        "accessories": load_accessories(),
    }
