import os
import shutil
import webbrowser
from datetime import datetime
from core.platform import detect_os_family, is_windows, is_mac, is_linux
from core.ui_automation import UIAutomation, Selector


def get_manifest():
    return {
        "id": "qai.modules.system",
        "name": "System Module",
        "version": "0.1.0",
        "description": "Safe system operations: open apps/URLs and basic file ops.",
        "permissions": [
            "process.spawn",
            "filesystem.read",
            "filesystem.write",
            "ui.automation",
        ],
        "commands": [
            {"trigger": "open_url ", "description": "Open a URL in default browser.", "args": [{"name": "url", "type": "string", "required": True}], "synonyms": ["abrir_url", "browse"], "handler": handle_open_url},
            {"trigger": "open_app ", "description": "Open a file or application.", "args": [{"name": "path", "type": "string", "required": True}], "synonyms": ["abrir", "launch"], "handler": handle_open_app},
            {"trigger": "list_dir ", "description": "List directory entries.", "args": [{"name": "path", "type": "string", "required": True}], "synonyms": ["ls", "listar"], "handler": handle_list_dir},
            {"trigger": "move_file ", "description": "Move a file.", "args": [{"name": "src dest", "type": "string", "required": True}], "synonyms": ["mv", "mover"], "handler": handle_move_file},
            {"trigger": "type_text ", "description": "Type text into the active window.", "args": [{"name": "text", "type": "string", "required": True}], "synonyms": ["escribir", "teclear"], "handler": handle_type_text},
            {"trigger": "notepad_write ", "description": "Open Notepad and write text.", "args": [{"name": "text", "type": "string", "required": True}], "synonyms": ["np_write", "bloc_notas"], "handler": handle_notepad_write},
            {"trigger": "focus_window ", "description": "Focus window by title substring.", "args": [{"name": "title", "type": "string", "required": True}], "synonyms": ["focus", "enfocar"], "handler": handle_focus_window},
            {"trigger": "focus_selector ", "description": "Focus via selector (title=... app=...)", "args": [{"name": "selector", "type": "string", "required": True}], "synonyms": ["focus_sel"], "handler": handle_focus_selector},
            {"trigger": "click_selector ", "description": "Click via selector (center)", "args": [{"name": "selector", "type": "string", "required": True}], "synonyms": ["click_sel"], "handler": handle_click_selector},
            {"trigger": "type_selector ", "description": "Type via selector", "args": [{"name": "selector text", "type": "string", "required": True}], "synonyms": ["type_sel"], "handler": handle_type_selector},
            {"trigger": "organize_dir ", "description": "Organize files by extension or date.", "args": [{"name": "path", "type": "string", "required": True}], "synonyms": ["organizar"], "handler": handle_organize_dir},
            {"trigger": "clean_empty_dirs ", "description": "Remove empty directories recursively.", "args": [{"name": "path", "type": "string", "required": True}], "synonyms": ["limpiar_vacias"], "handler": handle_clean_empty_dirs},
        ],
    }


def handle_open_url(command, router):
    raw = command[len("open_url ") :].strip()
    url = raw
    # resolve alias from config shortcuts
    shortcuts = ((router.config or {}).get("shortcuts", {}) or {}).get("urls", {})
    if raw and raw.lower() in {k.lower(): v for k, v in shortcuts.items()}:
        # case-insensitive lookup
        for k, v in shortcuts.items():
            if k.lower() == raw.lower():
                url = v
                break
    if not (url.startswith("http://") or url.startswith("https://")):
        return "[Q•Agent] Invalid URL."
    try:
        webbrowser.open(url)
        return "🌐 URL opened."
    except Exception as e:
        return f"[Q•Agent] Could not open URL: {e}"


def handle_open_app(command, router):
    raw = command[len("open_app ") :].strip().strip('"')
    if not raw:
        return "[Q•Agent] Path required."
    # resolve alias from config shortcuts
    path = raw
    shortcuts = ((router.config or {}).get("shortcuts", {}) or {}).get("apps", {})
    if raw and raw.lower() in {k.lower(): v for k, v in shortcuts.items()}:
        for k, v in shortcuts.items():
            if k.lower() == raw.lower():
                path = v
                break
    try:
        family = (router.config or {}).get("os_family")
        family = detect_os_family() if family in (None, "auto") else family
        if is_windows(family):
            os.startfile(path)  # type: ignore[attr-defined]
            return "🟢 Application opened."
        if is_mac(family):
            import subprocess
            subprocess.check_call(["open", path])
            return "🟢 Application opened."
        if is_linux(family):
            import subprocess
            subprocess.Popen([path])
            return "🟢 Application opened."
        return "[Q•Agent] Unsupported OS."
    except Exception as e:
        return f"[Q•Agent] Failed to open: {e}"


def handle_list_dir(command, router):
    path = command[len("list_dir ") :].strip().strip('"')
    if not os.path.isdir(path):
        return "[Q•Agent] Directory not found."
    try:
        entries = os.listdir(path)[:50]
        return "\n".join(entries) or "[Q•Agent] (empty)"
    except Exception as e:
        return f"[Q•Agent] Error listing directory: {e}"


def handle_move_file(command, router):
    rest = command[len("move_file ") :].strip()
    if not rest:
        return "[Q•Agent] Usage: move_file <src> <dest>"
    try:
        parts = rest.split(" ")
        if len(parts) < 2:
            return "[Q•Agent] Usage: move_file <src> <dest>"
        src = parts[0].strip('"')
        dest = " ".join(parts[1:]).strip('"')
        if not os.path.isfile(src):
            return "[Q•Agent] Source file not found."
        shutil.move(src, dest)
        return "📁 File moved."
    except Exception as e:
        return f"[Q•Agent] Error moving file: {e}"


def _import_pyautogui():
    try:
        import pyautogui  # type: ignore
        pyautogui.FAILSAFE = False
        return pyautogui
    except Exception as e:
        return None


def _import_pygetwindow():
    try:
        import pygetwindow as gw  # type: ignore
        return gw
    except Exception:
        return None


def _focus_first_window_matching(keywords):
    gw = _import_pygetwindow()
    if not gw:
        return False, "pygetwindow not installed"
    try:
        all_titles = gw.getAllTitles() or []
        target = None
        lowered = [k.lower() for k in keywords]
        for t in all_titles:
            lt = (t or "").lower()
            if any(k in lt for k in lowered):
                target = t
                break
        if not target:
            return False, "window not found"
        wins = gw.getWindowsWithTitle(target)
        if not wins:
            return False, "window handle not found"
        win = wins[0]
        try:
            win.activate()
        except Exception:
            try:
                win.minimize(); win.restore()
            except Exception:
                pass
        return True, target
    except Exception as e:
        return False, str(e)


def handle_type_text(command, router):
    text = command[len("type_text ") :].strip()
    if not text:
        return "[Q•Agent] Text required."
    pg = _import_pyautogui()
    if not pg:
        return "[Q•Agent] pyautogui is not installed. Run: pip install pyautogui"
    try:
        pg.typewrite(text, interval=0.02)
        return "⌨️ Text typed into active window."
    except Exception as e:
        return f"[Q•Agent] Could not type: {e}"


def handle_notepad_write(command, router):
    text = command[len("notepad_write ") :].strip()
    if not text:
        return "[Q•Agent] Text required."
    try:
        # open notepad using shortcut if available
        shortcuts = ((router.config or {}).get("shortcuts", {}) or {}).get("apps", {})
        np_path = shortcuts.get("notepad") or "C:/Windows/System32/notepad.exe"
        if os.name == "nt":
            os.startfile(np_path)  # type: ignore[attr-defined]
        else:
            return "[Q•Agent] notepad_write is Windows-only."
    except Exception as e:
        return f"[Q•Agent] Failed to open Notepad: {e}"
    # small delay and attempt to focus Notepad window
    try:
        import time
        time.sleep(0.8)
        # try to focus by common titles
        ok, detail = _focus_first_window_matching(["notepad", "bloc de notas"])  # es/en
        pg = _import_pyautogui()
        if not pg:
            return "[Q•Agent] pyautogui is not installed. Run: pip install pyautogui"
        pg.typewrite(text, interval=0.02)
        return "📝 Notepad wrote the text." if ok else "📝 Typed text (window focus best-effort)."
    except Exception as e:
        return f"[Q•Agent] Could not write in Notepad: {e}"


def handle_focus_window(command, router):
    title = command[len("focus_window ") :].strip()
    if not title:
        return "[Q•Agent] Title required."
    ok, detail = _focus_first_window_matching([title])
    if ok:
        return f"[Q•Agent] Focused window: {detail}"
    return f"[Q•Agent] Could not focus window: {detail}"


def handle_focus_selector(command, router):
    raw = command[len("focus_selector ") :].strip()
    if not raw:
        return "[Q•Agent] Selector required."
    ui = UIAutomation(router.config)
    ok = ui.focus(Selector.from_text(raw))
    return "[Q•Agent] Focused via selector." if ok else "[Q•Agent] Selector did not match."


def handle_click_selector(command, router):
    raw = command[len("click_selector ") :].strip()
    if not raw:
        return "[Q•Agent] Selector required."
    ui = UIAutomation(router.config)
    ok = ui.click(Selector.from_text(raw))
    return "[Q•Agent] Clicked via selector." if ok else "[Q•Agent] Selector did not match."


def handle_type_selector(command, router):
    rest = command[len("type_selector ") :].strip()
    if not rest:
        return "[Q•Agent] Usage: type_selector <selector> <text>"
    # split by first space outside quotes (simplified): assume selector has key="value" pairs (no spaces in values)
    parts = rest.split(" ", 1)
    if len(parts) < 2:
        return "[Q•Agent] Usage: type_selector <selector> <text>"
    sel_txt, text = parts[0], parts[1]
    ui = UIAutomation(router.config)
    ok = ui.type_text(text, Selector.from_text(sel_txt))
    return "[Q•Agent] Typed via selector." if ok else "[Q•Agent] Could not type via selector."


def _within_limits(path: str, router) -> bool:
    try:
        limits = ((router.config or {}).get("security", {}).get("path_limits", []))
        ap = os.path.abspath(path)
        for base in limits:
            if ap.startswith(os.path.abspath(base)):
                return True
        return False if limits else True
    except Exception:
        return True


def handle_organize_dir(command, router):
    path = command[len("organize_dir ") :].strip().strip('"')
    if not os.path.isdir(path):
        return "[Q•Agent] Directory not found."
    if not _within_limits(path, router):
        return "[Q•Agent] Path not allowed by policy."
    try:
        moved = 0
        for entry in os.listdir(path):
            src = os.path.join(path, entry)
            if os.path.isfile(src):
                ext = os.path.splitext(entry)[1].lower().strip('.') or 'noext'
                target = os.path.join(path, ext)
                os.makedirs(target, exist_ok=True)
                shutil.move(src, os.path.join(target, entry))
                moved += 1
        return f"🧹 Organized {moved} files by extension."
    except Exception as e:
        return f"[Q•Agent] Error organizing: {e}"


def handle_clean_empty_dirs(command, router):
    path = command[len("clean_empty_dirs ") :].strip().strip('"')
    if not os.path.isdir(path):
        return "[Q•Agent] Directory not found."
    if not _within_limits(path, router):
        return "[Q•Agent] Path not allowed by policy."
    removed = 0
    try:
        for root, dirs, files in os.walk(path, topdown=False):
            if not dirs and not files:
                try:
                    os.rmdir(root)
                    removed += 1
                except Exception:
                    pass
        return f"🗑️ Removed {removed} empty directories."
    except Exception as e:
        return f"[Q•Agent] Error cleaning: {e}"


