import tkinter as tk
from tkinter import filedialog, messagebox, ttk, colorchooser
import json
import os
import re
from database import LogDatabase
from services import LogService

CONFIG_FILE = "config.json"

class LogViewerApp:
    def __init__(self, root, service):
        self.root = root
        self.service = service
        self.config = self._load_config()
        
        # ユーザー設定の復元
        settings = self.config.get("user_settings", {})
        self.current_font_family = tk.StringVar(value=settings.get("font_family", "Consolas"))
        self.current_font_size = tk.IntVar(value=settings.get("font_size", 10))
        self.bg_combo_var = tk.StringVar(value=settings.get("bg_name", "Dark Gray"))
        self.h_scroll_var = tk.BooleanVar(value=settings.get("h_scroll", True))
        
        self.current_offset = 0
        self.filter_rows = []
        self.search_mode = tk.StringVar(value="OR")
        self.tail_var = tk.BooleanVar(value=False)
        
        self._init_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _load_config(self):
        """外部JSONファイルを読み込む。存在しない場合はデフォルト設定を作成。"""
        default_config = {
            "presets": {
                "highlights": {
                    "Yellow": "#FFFF00", "Red": "#FF4444", "Green": "#00FF00", 
                    "Cyan": "#00FFFF", "White": "#FFFFFF"
                },
                "level_colors": {
                    "ERROR": "#FF5555", "CRITICAL": "#FF0000", 
                    "WARNING": "#FFB86C", "INFO": "#50FA7B", "DEBUG": "#8BE9FD"
                },
                "bg_colors": {
                    "Dark Gray": "#1e1e1e", "Midnight": "#000033", 
                    "Deep Green": "#002200", "Paper": "#f5f5f5", "Classic Blue": "#000080"
                },
                "font_families": ["Consolas", "MS Gothic", "Courier New", "Lucida Console", "Arial"]
            },
            "user_settings": {
                "font_family": "Consolas", "font_size": 10, 
                "bg_name": "Dark Gray", "h_scroll": True
            }
        }
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return default_config
        return default_config

    def _save_config(self):
        """現在の設定をJSONファイルに保存する"""
        self.config["user_settings"] = {
            "font_family": self.current_font_family.get(),
            "font_size": self.current_font_size.get(),
            "bg_name": self.bg_combo_var.get(),
            "h_scroll": self.h_scroll_var.get()
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4)

    def _init_ui(self):
        self.root.title("Advanced Log Viewer Pro")
        self.root.geometry("1400x800")

        # --- ツールバー ---
        toolbar = tk.Frame(self.root, padx=10, pady=5)
        toolbar.pack(fill=tk.X)
        
        tk.Button(toolbar, text="Import File", command=self.handle_import).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Export Result", command=self.handle_export).pack(side=tk.LEFT, padx=2)
        
        # フォント設定
        tk.Label(toolbar, text=" | Font:").pack(side=tk.LEFT, padx=2)
        font_combo = ttk.Combobox(toolbar, textvariable=self.current_font_family, 
                                 values=self.config["presets"]["font_families"], width=15, state="readonly")
        font_combo.pack(side=tk.LEFT, padx=2)
        font_combo.bind("<<ComboboxSelected>>", self.update_font)
        
        size_spin = tk.Spinbox(toolbar, from_=6, to=72, textvariable=self.current_font_size, width=3, command=self.update_font)
        size_spin.pack(side=tk.LEFT, padx=2)
        size_spin.bind("<Return>", lambda e: self.update_font())

        # 背景色設定
        tk.Label(toolbar, text=" | BG:").pack(side=tk.LEFT, padx=2)
        bg_combo = ttk.Combobox(toolbar, textvariable=self.bg_combo_var, 
                               values=list(self.config["presets"]["bg_colors"].keys()), width=10, state="readonly")
        bg_combo.pack(side=tk.LEFT, padx=2)
        bg_combo.bind("<<ComboboxSelected>>", self.handle_bg_preset)

        tk.Checkbutton(toolbar, text="Tail -f", variable=self.tail_var, command=self.toggle_tail).pack(side=tk.LEFT, padx=5)
        tk.Checkbutton(toolbar, text="H-Scroll", variable=self.h_scroll_var, command=self.toggle_h_scroll).pack(side=tk.LEFT, padx=5)

        # --- フィルタエリア ---
        self.filter_container = tk.LabelFrame(self.root, text="Search Filters (Keyword & Bold)", padx=10, pady=5)
        self.filter_container.pack(fill=tk.X, padx=10, pady=5)
        
        btn_row = tk.Frame(self.filter_container)
        btn_row.pack(fill=tk.X, pady=(0, 5))
        tk.Button(btn_row, text="+ Add New Filter", command=self.add_filter_row, fg="blue").pack(side=tk.LEFT)
        
        tk.Label(btn_row, text="Mode:").pack(side=tk.LEFT, padx=(20, 5))
        tk.Radiobutton(btn_row, text="OR", variable=self.search_mode, value="OR", command=self.refresh_view).pack(side=tk.LEFT)
        tk.Radiobutton(btn_row, text="AND", variable=self.search_mode, value="AND", command=self.refresh_view).pack(side=tk.LEFT)

        self.rows_inner_frame = tk.Frame(self.filter_container)
        self.rows_inner_frame.pack(fill=tk.X)

        # --- ログ表示エリア ---
        view_frame = tk.Frame(self.root)
        view_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)
        
        self.v_scroll = tk.Scrollbar(view_frame, orient=tk.VERTICAL)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.h_scroll = tk.Scrollbar(view_frame, orient=tk.HORIZONTAL)
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        self.text_area = tk.Text(view_frame, wrap=tk.NONE, 
                                 font=(self.current_font_family.get(), self.current_font_size.get()), 
                                 state=tk.DISABLED, xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)
        self.text_area.pack(expand=True, fill=tk.BOTH)
        
        self.v_scroll.config(command=self.text_area.yview)
        self.h_scroll.config(command=self.text_area.xview)
        
        self.add_filter_row()
        self.handle_bg_preset()

    def update_font(self, event=None):
        new_font = (self.current_font_family.get(), self.current_font_size.get())
        self.text_area.config(font=new_font)
        self.refresh_view()

    def handle_bg_preset(self, event=None):
        color_hex = self.config["presets"]["bg_colors"].get(self.bg_combo_var.get(), "#1e1e1e")
        self.text_area.config(bg=color_hex)
        r, g, b = self.root.winfo_rgb(color_hex)
        new_fg = "#000000" if (r + g + b) / 3 > 32768 else "#d4d4d4"
        self.text_area.config(fg=new_fg, insertbackground=new_fg)
        self.refresh_view()

    def add_filter_row(self):
        row = tk.Frame(self.rows_inner_frame)
        row.pack(fill=tk.X, pady=2)
        
        var = tk.StringVar()
        var.trace_add("write", lambda *a: self.refresh_view(True))
        tk.Entry(row, textvariable=var, width=30).pack(side=tk.LEFT, padx=5)
        
        case_var = tk.BooleanVar(value=False)
        tk.Checkbutton(row, text="Aa", variable=case_var, command=lambda: self.refresh_view(True)).pack(side=tk.LEFT)
        
        bold_var = tk.BooleanVar(value=False)
        tk.Checkbutton(row, text="B", variable=bold_var, indicatoron=False, 
                       selectcolor="#ccc", command=lambda: self.refresh_view(True)).pack(side=tk.LEFT, padx=2)

        h_presets = self.config["presets"]["highlights"]
        color_name_var = tk.StringVar(value=list(h_presets.keys())[0])
        current_hex = tk.StringVar(value=h_presets[color_name_var.get()])
        
        color_combo = ttk.Combobox(row, textvariable=color_name_var, values=list(h_presets.keys()), width=8, state="readonly")
        color_combo.pack(side=tk.LEFT, padx=5)
        
        picker_btn = tk.Button(row, bg=current_hex.get(), width=2, 
                               command=lambda: self.pick_custom_highlight(current_hex, color_name_var, picker_btn))
        picker_btn.pack(side=tk.LEFT)

        row_data = {"var": var, "case_sensitive": case_var, "bold": bold_var, "current_hex": current_hex, "frame": row}
        color_combo.bind("<<ComboboxSelected>>", lambda e: self.on_highlight_change(color_name_var, current_hex, picker_btn))
        
        tk.Button(row, text="✕", command=lambda: self.remove_filter(row, row_data)).pack(side=tk.LEFT, padx=5)
        self.filter_rows.append(row_data)

    def on_highlight_change(self, name_var, hex_var, btn):
        new_hex = self.config["presets"]["highlights"].get(name_var.get())
        if new_hex:
            hex_var.set(new_hex)
            btn.config(bg=new_hex)
            self.refresh_view()

    def pick_custom_highlight(self, hex_var, name_var, btn):
        color = colorchooser.askcolor(initialcolor=hex_var.get())[1]
        if color:
            hex_var.set(color)
            name_var.set("Custom")
            btn.config(bg=color)
            self.refresh_view()

    def refresh_view(self, reset_scroll=False):
        """ログを表示し、フォーマットに合わせて自動着色およびハイライトを適用"""
        patterns_data = [("" if r["case_sensitive"].get() else "(?i)") + r["var"].get() for r in self.filter_rows if r["var"].get()]
        if reset_scroll: self.current_offset = 0
        
        state = self.service.get_display_data(patterns_data, self.current_offset, self.search_mode.get())
        
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete("1.0", tk.END)
        
        # ログフォーマット解析用 (例: [2026-02-04 12:00:00] ERROR   : Msg)
        log_pattern = re.compile(r'^\[(?P<date>.*?)\]\s+(?P<level>\w+)\s+:\s+(?P<msg>.*)$')
        level_colors = self.config["presets"].get("level_colors", {})

        for line in state["logs"]:
            match = log_pattern.match(line)
            if match:
                # 日付部分の挿入
                self.text_area.insert(tk.END, f"[{match.group('date')}] ", "fmt_date")
                self.text_area.tag_config("fmt_date", foreground="#888888")
                
                # レベル部分の挿入
                lvl = match.group('level').strip()
                lvl_tag = f"fmt_lvl_{lvl}"
                self.text_area.insert(tk.END, f"{lvl.ljust(8)}", lvl_tag)
                self.text_area.tag_config(lvl_tag, foreground=level_colors.get(lvl, None))
                
                # メッセージ部分の挿入
                self.text_area.insert(tk.END, f": {match.group('msg')}\n")
            else:
                self.text_area.insert(tk.END, f"{line}\n")

        # ユーザー指定のハイライト適用
        for r in self.filter_rows:
            if r["var"].get():
                self._apply_highlight(r["var"].get(), r["current_hex"].get(), r["case_sensitive"].get(), r["bold"].get())
        
        self.text_area.config(state=tk.DISABLED)

    def _apply_highlight(self, pattern, color, is_case_sensitive, is_bold):
        tag_id = f"tag_{pattern}_{is_case_sensitive}_{is_bold}"
        tag_font = [self.current_font_family.get(), self.current_font_size.get()]
        if is_bold: tag_font.append("bold")
        
        self.text_area.tag_config(tag_id, foreground=color, font=tuple(tag_font))
        try:
            flags = 0 if is_case_sensitive else re.IGNORECASE
            regex = re.compile(pattern, flags)
            full_text = self.text_area.get("1.0", tk.END)
            for match in regex.finditer(full_text):
                start = self._get_tk_index(full_text, match.start())
                end = self._get_tk_index(full_text, match.end())
                self.text_area.tag_add(tag_id, start, end)
        except Exception: pass

    def _get_tk_index(self, text, offset):
        lines = text[:offset].split('\n')
        return f"{len(lines)}.{len(lines[-1])}"

    def toggle_h_scroll(self):
        if self.h_scroll_var.get():
            self.text_area.config(wrap=tk.NONE)
            self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X, before=self.text_area)
        else:
            self.text_area.config(wrap=tk.WORD)
            self.h_scroll.pack_forget()
        self.refresh_view()

    def handle_import(self):
        path = filedialog.askopenfilename()
        if path:
            self.service.async_import(path, lambda s, e: self.root.after(0, lambda: self.refresh_view(True)))

    def handle_export(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt")
        if path:
            patterns = [("" if r["case_sensitive"].get() else "(?i)") + r["var"].get() for r in self.filter_rows if r["var"].get()]
            self.service.export_data(path, patterns, self.search_mode.get())

    def toggle_tail(self):
        if self.tail_var.get():
            if not self.service.current_file:
                messagebox.showwarning("Warning", "Please import a file first.")
                self.tail_var.set(False)
                return
            self.service.start_tail_worker(lambda: self.root.after(0, self.refresh_view))
        else:
            self.service.stop_tail()

    def remove_filter(self, frame, data):
        frame.destroy()
        if data in self.filter_rows:
            self.filter_rows.remove(data)
        self.refresh_view()

    def _on_closing(self):
        self._save_config()
        self.root.destroy()

if __name__ == "__main__":
    db = LogDatabase()
    svc = LogService(db)
    root = tk.Tk()
    app = LogViewerApp(root, svc)
    root.mainloop()
