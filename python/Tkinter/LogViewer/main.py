import tkinter as tk
from tkinter import filedialog, messagebox, ttk, colorchooser, font
import json
import os
import re
from database import LogDatabase
from services import LogService

CONFIG_FILE = "config.json"

class ConfigEditor(tk.Toplevel):
    def __init__(self, parent, current_config, on_save_callback):
        super().__init__(parent)
        self.title("GUI Configuration Editor")
        self.geometry("800x650")
        self.config_data = current_config
        self.on_save_callback = on_save_callback
        
        self.tab_control = ttk.Notebook(self)
        self.tab_fonts = ttk.Frame(self.tab_control)
        self.tab_highlights = ttk.Frame(self.tab_control)
        self.tab_levels = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.tab_fonts, text='フォント管理')
        self.tab_control.add(self.tab_highlights, text='検索ハイライト色')
        self.tab_control.add(self.tab_levels, text='ログレベル色')
        self.tab_control.pack(expand=1, fill="both", padx=5, pady=5)
        
        self._setup_font_tab()
        self._setup_dynamic_color_tab(self.tab_highlights, "highlights")
        self._setup_dynamic_color_tab(self.tab_levels, "level_colors")
        
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=10)
        tk.Button(btn_frame, text="設定を保存して適用", command=self._apply, bg="#4CAF50", fg="white", padx=15).pack(side=tk.RIGHT, padx=10)
        tk.Button(btn_frame, text="キャンセル", command=self.destroy).pack(side=tk.RIGHT)

    def _setup_font_tab(self):
        """フォント追加・削除UI（前回作成分）"""
        main_f = tk.Frame(self.tab_fonts)
        main_f.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # OS List
        lf = tk.Frame(main_f); lf.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Label(lf, text="OSフォント一覧").pack()
        self.os_font_list = tk.Listbox(lf); all_f = sorted(list(set(font.families())))
        for f in all_f: self.os_font_list.insert(tk.END, f)
        self.os_font_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Mid Buttons
        mf = tk.Frame(main_f); mf.pack(side=tk.LEFT, padx=10)
        tk.Button(mf, text="追加 ➔", command=self._add_font).pack(pady=5)
        tk.Button(mf, text="✕ 削除", command=self._remove_font, fg="red").pack(pady=5)
        
        # App List
        rf = tk.Frame(main_f); rf.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Label(rf, text="現在の設定").pack()
        self.app_font_list = tk.Listbox(rf)
        for f in self.config_data["presets"]["font_families"]: self.app_font_list.insert(tk.END, f)
        self.app_font_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def _add_font(self):
        sel = self.os_font_list.curselection()
        if sel:
            f = self.os_font_list.get(sel[0])
            if f not in self.app_font_list.get(0, tk.END): self.app_font_list.insert(tk.END, f)

    def _remove_font(self):
        sel = self.app_font_list.curselection()
        if sel: self.app_font_list.delete(sel[0])

    def _setup_dynamic_color_tab(self, tab, config_key):
        """色設定の追加・削除ができる動的UI"""
        top_f = tk.Frame(tab, pady=10)
        top_f.pack(fill=tk.X)
        tk.Button(top_f, text="+ 新しい色を追加", command=lambda k=config_key: self._add_color_row(k)).pack(side=tk.LEFT, padx=10)

        # スクロールエリア
        container = tk.Frame(tab)
        container.pack(fill=tk.BOTH, expand=True, padx=10)
        
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 行を管理するリスト
        setattr(self, f"{config_key}_rows", [])
        setattr(self, f"{config_key}_frame", scrollable_frame)

        # 既存データを流し込み
        for name, hex_val in self.config_data["presets"][config_key].items():
            self._create_row_ui(config_key, name, hex_val)

    def _create_row_ui(self, key, name="", hex_val="#FFFFFF"):
        parent = getattr(self, f"{key}_frame")
        row_f = tk.Frame(parent, pady=2)
        row_f.pack(fill=tk.X)
        
        n_var = tk.StringVar(value=name)
        h_var = tk.StringVar(value=hex_val)
        
        tk.Entry(row_f, textvariable=n_var, width=20).pack(side=tk.LEFT, padx=5)
        h_ent = tk.Entry(row_f, textvariable=h_var, width=10)
        h_ent.pack(side=tk.LEFT, padx=5)
        
        btn = tk.Button(row_f, bg=hex_val, width=2, command=lambda v=h_var, e=h_ent: self._pick_color(v, e))
        btn.pack(side=tk.LEFT, padx=5)
        
        del_btn = tk.Button(row_f, text="✕", fg="red", command=lambda f=row_f, k=key: self._remove_color_row(f, k))
        del_btn.pack(side=tk.LEFT, padx=10)
        
        getattr(self, f"{key}_rows").append({"frame": row_f, "n_var": n_var, "h_var": h_var, "btn": btn})

    def _add_color_row(self, key):
        self._create_row_ui(key, "New Item", "#FFFFFF")

    def _remove_color_row(self, frame, key):
        rows = getattr(self, f"{key}_rows")
        for i, r in enumerate(rows):
            if r["frame"] == frame:
                frame.destroy()
                rows.pop(i)
                break

    def _pick_color(self, hex_var, entry_widget):
        color = colorchooser.askcolor(initialcolor=hex_var.get())[1]
        if color:
            hex_var.set(color)
            # 対応するプレビューボタンの色も更新
            for key in ["highlights", "level_colors"]:
                for row in getattr(self, f"{key}_rows"):
                    if row["h_var"] == hex_var: row["btn"].config(bg=color)

    def _apply(self):
        # フォント保存
        self.config_data["presets"]["font_families"] = list(self.app_font_list.get(0, tk.END))
        
        # カラー設定保存
        for key in ["highlights", "level_colors"]:
            new_dict = {}
            for row in getattr(self, f"{key}_rows"):
                name = row["n_var"].get().strip()
                if name: new_dict[name] = row["h_var"].get()
            self.config_data["presets"][key] = new_dict
        
        self.on_save_callback(self.config_data)
        self.destroy()

class LogViewerApp:
    def __init__(self, root, service):
            self.root = root
            self.service = service
            self.config = self._load_config()
            
            # --- 設定値の初期化（ここを _init_ui よりも前に書く） ---
            settings = self.config.get("user_settings", {})
            self.current_font_family = tk.StringVar(value=settings.get("font_family", "Consolas"))
            self.current_font_size = tk.IntVar(value=10)
            self.bg_combo_var = tk.StringVar(value=settings.get("bg_name", "Dark Gray"))
            self.h_scroll_var = tk.BooleanVar(value=settings.get("h_scroll", True))
            self.search_mode = tk.StringVar(value="OR")
            self.tail_var = tk.BooleanVar(value=False)
            self.filter_rows = []
            self.current_offset = 0  # <--- これが重要です！
            # --------------------------------------------------

            # UIの構築（この中で current_offset を参照するメソッドが動く）
            self._init_ui()
            
            self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _load_config(self):
        default = {
            "presets": {
                "highlights": {"Yellow": "#FFFF00", "Red": "#FF4444", "Green": "#00FF00"},
                "level_colors": {"ERROR": "#FF5555", "INFO": "#50FA7B", "DEBUG": "#8BE9FD"},
                "bg_colors": {"Dark Gray": "#1e1e1e", "Midnight": "#000033", "Paper": "#f5f5f5"},
                "font_families": ["Consolas", "MS Gothic"]
            },
            "user_settings": {"font_family": "Consolas", "font_size": 10, "bg_name": "Dark Gray", "h_scroll": True}
        }
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f: return json.load(f)
            except: return default
        return default

    def _save_config(self, new_config=None):
        if new_config: self.config = new_config
        else:
            self.config["user_settings"].update({
                "font_family": self.current_font_family.get(),
                "font_size": self.current_font_size.get(),
                "bg_name": self.bg_combo_var.get(),
                "h_scroll": self.h_scroll_var.get()
            })
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4)
        
        # UIパーツの更新
        self._refresh_comboboxes()
        self.refresh_view()

    def _refresh_comboboxes(self):
        """設定変更後にメイン画面のプルダウン項目を更新"""
        # フォントリストの更新
        self.font_combo['values'] = self.config["presets"]["font_families"]
        # 各フィルタ行のハイライト色の更新
        h_list = list(self.config["presets"]["highlights"].keys())
        for row in self.filter_rows:
            row_cb = row["frame"].winfo_children()[3] # Comboboxのインデックス
            if isinstance(row_cb, ttk.Combobox):
                row_cb['values'] = h_list

    def _init_ui(self):
        self.root.title("Log Viewer Pro - Customizable")
        self.root.geometry("1400x850")

        toolbar = tk.Frame(self.root, padx=10, pady=5); toolbar.pack(fill=tk.X)
        tk.Button(toolbar, text="Import", command=self.handle_import).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="⚙ Settings", command=lambda: ConfigEditor(self.root, self.config, self._save_config), bg="#eee").pack(side=tk.RIGHT, padx=5)

        tk.Label(toolbar, text=" | Font:").pack(side=tk.LEFT, padx=2)
        self.font_combo = ttk.Combobox(toolbar, textvariable=self.current_font_family, width=20, state="readonly")
        self.font_combo['values'] = self.config["presets"]["font_families"]
        self.font_combo.pack(side=tk.LEFT, padx=2)
        self.font_combo.bind("<<ComboboxSelected>>", self.update_font)
        
        tk.Spinbox(toolbar, from_=6, to=72, textvariable=self.current_font_size, width=3, command=self.update_font).pack(side=tk.LEFT, padx=2)

        tk.Label(toolbar, text=" | BG:").pack(side=tk.LEFT, padx=2)
        self.bg_combo = ttk.Combobox(toolbar, textvariable=self.bg_combo_var, width=12, state="readonly")
        self.bg_combo['values'] = list(self.config["presets"]["bg_colors"].keys())
        self.bg_combo.pack(side=tk.LEFT, padx=2)
        self.bg_combo.bind("<<ComboboxSelected>>", self.handle_bg_preset)

        tk.Checkbutton(toolbar, text="Tail -f", variable=self.tail_var, command=self.toggle_tail).pack(side=tk.LEFT, padx=5)
        tk.Checkbutton(toolbar, text="H-Scroll", variable=self.h_scroll_var, command=self.toggle_h_scroll).pack(side=tk.LEFT, padx=5)

        self.filter_container = tk.LabelFrame(self.root, text="Search Filters", padx=10, pady=5); self.filter_container.pack(fill=tk.X, padx=10, pady=5)
        btn_row = tk.Frame(self.filter_container); btn_row.pack(fill=tk.X, pady=(0, 5))
        tk.Button(btn_row, text="+ Add Filter", command=self.add_filter_row, fg="blue").pack(side=tk.LEFT)

        self.rows_inner_frame = tk.Frame(self.filter_container); self.rows_inner_frame.pack(fill=tk.X)

        view_frame = tk.Frame(self.root); view_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)
        self.v_scroll = tk.Scrollbar(view_frame); self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.h_scroll = tk.Scrollbar(view_frame, orient=tk.HORIZONTAL); self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.text_area = tk.Text(view_frame, wrap=tk.NONE, font=(self.current_font_family.get(), self.current_font_size.get()), 
                                 state=tk.DISABLED, xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)
        self.text_area.pack(expand=True, fill=tk.BOTH)
        self.v_scroll.config(command=self.text_area.yview); self.h_scroll.config(command=self.text_area.xview)
        
        self.add_filter_row()
        self.handle_bg_preset()

    def update_font(self, event=None):
        self.text_area.config(font=(self.current_font_family.get(), self.current_font_size.get()))
        self.refresh_view()

    def handle_bg_preset(self, event=None):
        color = self.config["presets"]["bg_colors"].get(self.bg_combo_var.get(), "#1e1e1e")
        self.text_area.config(bg=color)
        r, g, b = self.root.winfo_rgb(color)
        new_fg = "#000000" if (r + g + b) / 3 > 32768 else "#d4d4d4"
        self.text_area.config(fg=new_fg, insertbackground=new_fg)
        self.refresh_view()

    def add_filter_row(self):
        row = tk.Frame(self.rows_inner_frame); row.pack(fill=tk.X, pady=2)
        var = tk.StringVar(); var.trace_add("write", lambda *a: self.refresh_view(True))
        tk.Entry(row, textvariable=var, width=30).pack(side=tk.LEFT, padx=5)
        case_var = tk.BooleanVar(value=False); tk.Checkbutton(row, text="Aa", variable=case_var, command=lambda: self.refresh_view(True)).pack(side=tk.LEFT)
        bold_var = tk.BooleanVar(value=False); tk.Checkbutton(row, text="B", variable=bold_var, indicatoron=False, command=lambda: self.refresh_view(True)).pack(side=tk.LEFT, padx=2)
        
        h_presets = self.config["presets"]["highlights"]
        c_name = tk.StringVar(value=list(h_presets.keys())[0]); c_hex = tk.StringVar(value=h_presets[c_name.get()])
        
        cb = ttk.Combobox(row, textvariable=c_name, values=list(h_presets.keys()), width=10, state="readonly"); cb.pack(side=tk.LEFT, padx=5)
        btn = tk.Button(row, bg=c_hex.get(), width=2, command=lambda: self.pick_custom_highlight(c_hex, c_name, btn)); btn.pack(side=tk.LEFT)
        cb.bind("<<ComboboxSelected>>", lambda e: self.on_highlight_preset_change(c_name, c_hex, btn))
        
        row_data = {"var": var, "case_sensitive": case_var, "bold": bold_var, "current_hex": c_hex, "frame": row}
        tk.Button(row, text="✕", command=lambda: self.remove_filter(row, row_data)).pack(side=tk.LEFT, padx=5)
        self.filter_rows.append(row_data)

    def on_highlight_preset_change(self, name_var, hex_var, btn):
        val = self.config["presets"]["highlights"].get(name_var.get())
        if val: hex_var.set(val); btn.config(bg=val); self.refresh_view()

    def pick_custom_highlight(self, hex_var, name_var, btn):
        color = colorchooser.askcolor(initialcolor=hex_var.get())[1]
        if color: hex_var.set(color); name_var.set("Custom"); btn.config(bg=color); self.refresh_view()

    def refresh_view(self, reset_scroll=False):
        patterns = [("" if r["case_sensitive"].get() else "(?i)") + r["var"].get() for r in self.filter_rows if r["var"].get()]
        state = self.service.get_display_data(patterns, 0 if reset_scroll else self.current_offset, self.search_mode.get())
        self.text_area.config(state=tk.NORMAL); self.text_area.delete("1.0", tk.END)
        log_pattern = re.compile(r'^\[(?P<date>.*?)\]\s+(?P<level>\w+)\s+:\s+(?P<msg>.*)$')
        lv_colors = self.config["presets"].get("level_colors", {})
        for line in state["logs"]:
            m = log_pattern.match(line)
            if m:
                self.text_area.insert(tk.END, f"[{m.group('date')}] ", "fmt_date")
                lvl = m.group('level').strip(); tag = f"fmt_{lvl}"
                self.text_area.insert(tk.END, f"{lvl.ljust(8)}", tag)
                self.text_area.tag_config(tag, foreground=lv_colors.get(lvl, None))
                self.text_area.insert(tk.END, f": {m.group('msg')}\n")
            else: self.text_area.insert(tk.END, f"{line}\n")
        self.text_area.tag_config("fmt_date", foreground="#888888")
        for r in self.filter_rows:
            if r["var"].get(): self._apply_highlight(r["var"].get(), r["current_hex"].get(), r["case_sensitive"].get(), r["bold"].get())
        self.text_area.config(state=tk.DISABLED)

    def _apply_highlight(self, pattern, color, case, bold):
        tag_id = f"tag_{pattern}"; f_style = [self.current_font_family.get(), self.current_font_size.get()]
        if bold: f_style.append("bold")
        self.text_area.tag_config(tag_id, foreground=color, font=tuple(f_style))
        try:
            regex = re.compile(pattern, 0 if case else re.IGNORECASE); ft = self.text_area.get("1.0", tk.END)
            for m in regex.finditer(ft):
                s = self._get_tk_index(ft, m.start()); e = self._get_tk_index(ft, m.end())
                self.text_area.tag_add(tag_id, s, e)
        except: pass

    def _get_tk_index(self, text, offset):
        lines = text[:offset].split('\n')
        return f"{len(lines)}.{len(lines[-1])}"

    def toggle_h_scroll(self):
        if self.h_scroll_var.get(): self.text_area.config(wrap=tk.NONE); self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X, before=self.text_area)
        else: self.text_area.config(wrap=tk.WORD); self.h_scroll.pack_forget()
        self.refresh_view()

    def handle_import(self):
        path = filedialog.askopenfilename()
        if path: self.service.async_import(path, lambda s, e: self.root.after(0, lambda: self.refresh_view(True)))

    def toggle_tail(self):
        if self.tail_var.get():
            if not self.service.current_file: self.tail_var.set(False); return
            self.service.start_tail_worker(lambda: self.root.after(0, self.refresh_view))
        else: self.service.stop_tail()

    def remove_filter(self, frame, data):
        frame.destroy(); self.filter_rows.remove(data); self.refresh_view()

    def _on_closing(self):
        self._save_config(); self.root.destroy()

if __name__ == "__main__":
    db = LogDatabase(); svc = LogService(db); root = tk.Tk(); app = LogViewerApp(root, svc); root.mainloop()
