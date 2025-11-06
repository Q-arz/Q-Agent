from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher


class IntentMatcher:
    def __init__(self, manifests: List[dict]):
        self.index: List[Tuple[str, dict, dict]] = []
        for manifest in manifests:
            for cmd in manifest.get("commands", []):
                synonyms = [s.lower() for s in cmd.get("synonyms", [])]
                trigger = cmd.get("trigger", "").lower()
                if trigger:
                    # include the trigger as an implicit synonym (without trailing space)
                    implicit = trigger.strip()
                    if implicit and implicit not in synonyms:
                        synonyms.append(implicit)
                self.index.append((manifest.get("id", "unknown"), manifest, {"trigger": trigger, "synonyms": synonyms, "handler": cmd.get("handler")}))

    def match(self, text: str) -> Optional[Tuple[dict, dict]]:
        t = text.strip().lower()
        # exact prefix by trigger already handled upstream; here try synonyms prefix
        best = (0.0, None, None)
        for _mod_id, manifest, cmd in self.index:
            for syn in cmd.get("synonyms", []):
                if t.startswith(syn + " ") or t == syn:
                    return manifest, cmd
                # fuzzy score for first word vs synonym
                first = t.split(" ")[0]
                score = SequenceMatcher(None, first, syn).ratio()
                if score > best[0]:
                    best = (score, manifest, cmd)
        if best[0] >= 0.8:
            return best[1], best[2]
        return None


