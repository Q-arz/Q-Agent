import threading
import tkinter as tk
from tkinter import ttk, messagebox
from core.auto import board


class PopoutService:
    _instance = None

    def __init__(self):
        self._thread = None
        self._root = None
        self._router = None

    @classmethod
    def instance(cls):
        if not cls._instance:
            cls._instance = PopoutService()
        return cls._instance

    def _ensure_loop(self):
        if self._root and self._root.winfo_exists():
            return
        def runner():
            self._root = tk.Tk()
            self._root.withdraw()
            self._root.mainloop()
        self._thread = threading.Thread(target=runner, daemon=True)
        self._thread.start()

    def set_router(self, router):
        self._router = router

    def show_board(self):
        self._ensure_loop()
        def open_window():
            win = tk.Toplevel(self._root)
            win.title("Q•Agent Board")
            win.geometry("520x420")

            frame = ttk.Frame(win)
            frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            cols = ("#", "Type", "Title", "Status")
            tree = ttk.Treeview(frame, columns=cols, show="headings")
            for c in cols:
                tree.heading(c, text=c)
                tree.column(c, width=100 if c != "Title" else 260, anchor=tk.W)
            tree.pack(fill=tk.BOTH, expand=True)

            btns = ttk.Frame(frame)
            btns.pack(fill=tk.X, pady=6)

            def refresh():
                for i in tree.get_children():
                    tree.delete(i)
                tasks = board.load_tasks()
                for idx, t in enumerate(tasks, start=1):
                    tree.insert("", tk.END, values=(idx, t.get("type",""), t.get("title",""), t.get("status","pending")))

            def complete_selected():
                sel = tree.selection()
                if not sel:
                    return
                item = tree.item(sel[0])
                idx = int(item["values"][0])
                try:
                    board.complete_task(idx)
                    refresh()
                except Exception as e:
                    messagebox.showerror("Q•AI", f"Error: {e}")

            ttk.Button(btns, text="Refresh", command=refresh).pack(side=tk.LEFT)
            ttk.Button(btns, text="Complete", command=complete_selected).pack(side=tk.LEFT, padx=6)
            ttk.Button(btns, text="Close", command=win.destroy).pack(side=tk.RIGHT)

            refresh()

        # schedule in Tk loop
        if self._root:
            self._root.after(0, open_window)

    def show_table(self, title: str, columns, rows):
        self._ensure_loop()
        def open_window():
            win = tk.Toplevel(self._root)
            win.title(title or "Q•Agent")
            win.geometry("600x420")
            frame = ttk.Frame(win)
            frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            cols = tuple(columns or [])
            tree = ttk.Treeview(frame, columns=cols, show="headings")
            for c in cols:
                tree.heading(c, text=c)
                tree.column(c, width=max(100, int(480/len(cols))) if cols else 120, anchor=tk.W)
            tree.pack(fill=tk.BOTH, expand=True)
            for r in rows or []:
                tree.insert("", tk.END, values=tuple(r))
            ttk.Button(frame, text="Close", command=win.destroy).pack(anchor=tk.E, pady=6)
        if self._root:
            self._root.after(0, open_window)

    def show_text(self, title: str, content: str):
        self._ensure_loop()
        def open_window():
            win = tk.Toplevel(self._root)
            win.title(title or "Q•Agent")
            win.geometry("600x420")
            txt = tk.Text(win, wrap=tk.WORD)
            txt.pack(fill=tk.BOTH, expand=True)
            txt.insert("1.0", content or "")
            txt.configure(state=tk.DISABLED)
            ttk.Button(win, text="Close", command=win.destroy).pack(anchor=tk.E, pady=6)
        if self._root:
            self._root.after(0, open_window)

    def show_schema(self, title: str, schema: dict):
        """Render a simple schema with tabs (views: text/table/form)."""
        self._ensure_loop()
        def open_window():
            win = tk.Toplevel(self._root)
            win.title(title or schema.get("title") or "Q•AI")
            win.geometry("700x520")
            nb = ttk.Notebook(win)
            nb.pack(fill=tk.BOTH, expand=True)
            for view in schema.get("views", []):
                vtype = view.get("type")
                tab = ttk.Frame(nb)
                nb.add(tab, text=view.get("title") or vtype or "view")
                if vtype == "text":
                    txt = tk.Text(tab, wrap=tk.WORD)
                    txt.pack(fill=tk.BOTH, expand=True)
                    txt.insert("1.0", view.get("content", ""))
                    txt.configure(state=tk.DISABLED)
                elif vtype == "table":
                    cols = tuple(view.get("columns", []))
                    tree = ttk.Treeview(tab, columns=cols, show="headings")
                    for c in cols:
                        tree.heading(c, text=c)
                        tree.column(c, width=max(90, int(560/len(cols))) if cols else 120, anchor=tk.W)
                    tree.pack(fill=tk.BOTH, expand=True)
                    for r in view.get("rows", []):
                        tree.insert("", tk.END, values=tuple(r))
                elif vtype == "form":
                    fields = view.get("fields", [])
                    frm = ttk.Frame(tab)
                    frm.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                    entries = {}
                    for i, f in enumerate(fields):
                        ttk.Label(frm, text=f.get("label") or f.get("name")).grid(row=i, column=0, sticky=tk.W, pady=4)
                        e = ttk.Entry(frm, width=50)
                        e.grid(row=i, column=1, sticky=tk.W)
                        entries[f.get("name")] = e
                    def do_submit():
                        cmd_tpl = (view.get("submit") or {}).get("command")
                        if not cmd_tpl:
                            messagebox.showwarning("Q•AI", "No submit command configured")
                            return
                        vals = {k: v.get() for k, v in entries.items()}
                        cmd = cmd_tpl.format(**vals)
                        try:
                            if self._router:
                                result = self._router.route(cmd)
                                messagebox.showinfo("Q•AI", str(result))
                            else:
                                messagebox.showinfo("Q•AI", cmd)
                        except Exception as e:
                            messagebox.showerror("Q•AI", str(e))
                    ttk.Button(frm, text=view.get("submit", {}).get("label", "Submit"), command=do_submit).grid(row=len(fields), column=1, sticky=tk.E, pady=6)
        if self._root:
            self._root.after(0, open_window)

    def show_palette(self, on_submit):
        """Open a simple command palette popout that calls on_submit(text)."""
        self._ensure_loop()
        def open_window():
            win = tk.Toplevel(self._root)
            win.title("Q•Agent Command Palette")
            win.geometry("520x120")
            frm = ttk.Frame(win)
            frm.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            ent = ttk.Entry(frm, width=60)
            ent.pack(fill=tk.X, expand=True)
            ent.focus_set()
            def _submit():
                val = ent.get().strip()
                if val:
                    try:
                        on_submit(val)
                    except Exception:
                        pass
                try:
                    win.destroy()
                except Exception:
                    pass
            ttk.Button(frm, text="Run", command=_submit).pack(anchor=tk.E, pady=8)
            ent.bind("<Return>", lambda e: _submit())
        if self._root:
            self._root.after(0, open_window)


