from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any
from core.platform import detect_os_family, is_windows, is_mac, is_linux


@dataclass
class Selector:
    title_contains: Optional[str] = None
    app: Optional[str] = None
    role: Optional[str] = None  # future: control type (button, edit, etc.)
    name: Optional[str] = None  # future: accessible name/label

    @staticmethod
    def from_text(text: str) -> "Selector":
        # very simple syntax: title="..." app="..."
        parts = text.strip().split()
        args: Dict[str, str] = {}
        for p in parts:
            if "=" in p:
                k, v = p.split("=", 1)
                v = v.strip('"')
                args[k.strip()] = v
        return Selector(
            title_contains=args.get("title"),
            app=args.get("app"),
            role=args.get("role"),
            name=args.get("name"),
        )


class UIAutomation:
    def __init__(self, config: Dict[str, Any] | None):
        fam = (config or {}).get("os_family")
        self.family = detect_os_family() if fam in (None, "auto") else fam

    def focus(self, selector: Selector) -> bool:
        if is_windows(self.family):
            try:
                import pygetwindow as gw  # type: ignore
                titles = gw.getAllTitles() or []
                target = None
                if selector.title_contains:
                    want = selector.title_contains.lower()
                    for t in titles:
                        if want in (t or "").lower():
                            target = t
                            break
                # future: app filter, role/name using UIA backend
                if not target:
                    return False
                wins = gw.getWindowsWithTitle(target)
                if not wins:
                    return False
                win = wins[0]
                try:
                    win.activate()
                except Exception:
                    try:
                        win.minimize(); win.restore()
                    except Exception:
                        pass
                return True
            except Exception:
                return False
        # TODO: mac/linux backends
        return False

    def click(self, selector: Selector) -> bool:
        # MVP: focus window; click center via pyautogui
        ok = self.focus(selector)
        if not ok:
            return False
        try:
            import pyautogui  # type: ignore
            w, h = pyautogui.size()
            pyautogui.click(w // 2, h // 2)
            return True
        except Exception:
            return False

    def type_text(self, text: str, selector: Selector | None = None) -> bool:
        if selector:
            self.focus(selector)
        try:
            import pyautogui  # type: ignore
            pyautogui.typewrite(text, interval=0.02)
            return True
        except Exception:
            return False


