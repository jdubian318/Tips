import tkinter as tk
from tkinter import filedialog, messagebox, ttk, colorchooser
import re
from database import LogDatabase
from services import LogService

# ハイライト用のプリセット
PRESET_HIGHLIGHTS = {"Yellow": "#FFFF00", "Red": "#FF4444", "Green": "#00FF00", "Cyan": "#00FFFF", "White": "#FFFFFF", "Custom": ""}
# ログ背景用のプリセット
PRESET_BG_COLORS = {"Dark Gray": "#1e1e1e", "Midnight": "#000033", "Deep Green": "#002200", "Paper": "#f5f5f5", "Classic Blue": "#000080"}

class LogViewerApp:
    def __init__(self, root, service):
        self.root = root
        self.service = service
        self.current_offset = 0
        self.filter_rows = []
        self.search_mode = tk.StringVar(value="OR")
        self.tail_var = tk.BooleanVar(value=False)
        self.h_scroll_var = tk.BooleanVar(value=True)
        self._init_ui()

    def _init_ui(self):
        self.root.title("Professional Log Viewer (Log Area BG Control)")
        self.root.geometry("1400x900")

        # --- Toolbar ---
        toolbar = tk.Frame(self.root, padx=10, pady=5)
        toolbar.pack(fill=tk.X)
        
        tk.Button(toolbar, text="Import File", command=self.handle_import).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Export Result", command=self.handle_export).pack(side=tk.LEFT, padx=2)
        
        tk.Frame(toolbar, width=15).pack(side=tk.LEFT)
        tk.Checkbutton(toolbar, text="Tail -f", variable=self.tail_var, command=self.toggle_tail).pack(side=tk.LEFT, padx=5)
        tk.Checkbutton(toolbar, text="H-Scroll", variable=self.h_scroll_var, command=self.toggle_h_scroll).pack(side=tk.LEFT, padx=5)
        
        # --- ログ表示部分の背景色設定 (追加) ---
        tk.Label(toolbar, text=" | Log BG:").pack(side=tk.LEFT, padx=2)
        self.bg_combo_var = tk.StringVar(value="Dark Gray")
        bg_combo = ttk.Combobox(toolbar, textvariable=self.bg_combo_var, values=list(PRESET_BG_COLORS.keys()), width=12, state="readonly")
        bg_combo.pack(side=tk.LEFT, padx=2)
        bg_combo.bind("<<ComboboxSelected>>", self.handle_bg_preset)
        
        tk.Button(toolbar, text="RGB 🎨", command=self.pick_log_bg_rgb, font=("", 8)).pack(side=tk.LEFT, padx=2)

        tk.Label(toolbar, text=" | Mode:").pack(side=tk.LEFT)
        ttk.Radiobutton(toolbar, text="OR", variable=self.search_mode, value="OR", command=self.refresh_view).pack(side=tk.LEFT)
        ttk.Radiobutton(toolbar, text="AND", variable=self.search_mode, value="AND", command=self.refresh_view).pack(side=tk.LEFT)

        # --- Filter Area ---
        self.filter_container = tk.LabelFrame(self.root, text="Search Filters", padx=10, pady=5)
        self.filter_container.pack(fill=tk.X, padx=10, pady=5)
        
        btn_row = tk.Frame(self.filter_container)
        btn_row.pack(fill=tk.X, pady=(0, 5))
        tk.Button(btn_row, text="+ Add New Filter", command=self.add_filter_row, fg="blue").pack(side=tk.LEFT)

        self.rows_inner_frame = tk.Frame(self.filter_container)
        self.rows_inner_frame.pack(fill=tk.X)

        # --- Log View Area ---
        view_frame = tk.Frame(self.root)
        view_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)
        
        self.v_scroll = tk.Scrollbar(view_frame, orient=tk.VERTICAL)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.h_scroll = tk.Scrollbar(view_frame, orient=tk.HORIZONTAL)
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        self.text_area = tk.Text(view_frame, wrap=tk.NONE, bg=PRESET_BG_COLORS["Dark Gray"], fg="#d4d4d4", font=("Consolas", 10), 
                                 state=tk.DISABLED, xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set,
                                 insertbackground="white")
        self.text_area.pack(expand=True, fill=tk.BOTH)
        
        self.v_scroll.config(command=self.text_area.yview)
        self.h_scroll.config(command=self.text_area.xview)
        self.text_area.bind("<MouseWheel>", self.handle_mousewheel)
        
        self.add_filter_row()

    def handle_bg_preset(self, event=None):
        """プリセットから背景色を適用"""
        color_hex = PRESET_BG_COLORS[self.bg_combo_var.get()]
        self._apply_log_area_bg(color_hex)

    def pick_log_bg_rgb(self):
        """RGBカラーピッカーから背景色を適用"""
        color = colorchooser.askcolor(initialcolor=self.text_area.cget("bg"))[1]
        if color:
            self._apply_log_area_bg(color)

    def _apply_log_area_bg(self, color_hex):
        """ログエリアの背景色と文字色を自動調整して適用"""
        self.text_area.config(bg=color_hex)
        # 輝度判定で文字色を白か黒に自動調整
        r, g, b = self.root.winfo_rgb(color_hex)
        brightness = (r + g + b) / 3
        new_fg = "#000000" if brightness > 32768 else "#d4d4d4"
        self.text_area.config(fg=new_fg, insertbackground=new_fg)

    def add_filter_row(self):
        row = tk.Frame(self.rows_inner_frame)
        row.pack(fill=tk.X, pady=2)
        var = tk.StringVar()
        var.trace_add("write", lambda *a: self.refresh_view(True))
        tk.Entry(row, textvariable=var, width=40).pack(side=tk.LEFT, padx=5)
        case_var = tk.BooleanVar(value=False)
        tk.Checkbutton(row, text="Aa", variable=case_var, command=lambda: self.refresh_view(True)).pack(side=tk.LEFT, padx=5)
        
        color_name_var = tk.StringVar(value="Yellow")
        current_hex = tk.StringVar(value=PRESET_HIGHLIGHTS["Yellow"])
        color_combo = ttk.Combobox(row, textvariable=color_name_var, values=list(PRESET_HIGHLIGHTS.keys())[:-1], width=10, state="readonly")
        color_combo.pack(side=tk.LEFT, padx=5)
        
        picker_btn = tk.Button(row, text="🎨", bg=current_hex.get(), width=3, 
                               command=lambda: self.pick_custom_highlight(current_hex, color_name_var, picker_btn))
        picker_btn.pack(side=tk.LEFT)

        color_combo.bind("<<ComboboxSelected>>", lambda e: self.on_highlight_preset_change(color_name_var, current_hex, picker_btn))
        tk.Button(row, text="✕", command=lambda: self.remove_filter(row, row_data)).pack(side=tk.LEFT, padx=5)
        row_data = {"var": var, "case_sensitive": case_var, "current_hex": current_hex, "frame": row}
        self.filter_rows.append(row_data)

    def refresh_view(self, reset_scroll=False):
        patterns_data = []
        for r in self.filter_rows:
            p = r["var"].get()
            if p:
                prefix = "" if r["case_sensitive"].get() else "(?i)"
                patterns_data.append(prefix + p)
        if reset_scroll: self.current_offset = 0
        state = self.service.get_display_data(patterns_data, self.current_offset, self.search_mode.get())
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", "\n".join(state["logs"]))
        for r in self.filter_rows:
            p = r["var"].get()
            if p: self._apply_highlight(p, r["current_hex"].get(), r["case_sensitive"].get())
        self.text_area.config(state=tk.DISABLED)
        self.root.update_idletasks()

    def _apply_highlight(self, pattern, color, is_case_sensitive):
        tag_id = f"tag_{pattern}_{is_case_sensitive}"
        self.text_area.tag_config(tag_id, foreground=color)
        try:
            flags = 0 if is_case_sensitive else re.IGNORECASE
            regex = re.compile(pattern, flags)
        except Exception: return
        full_text = self.text_area.get("1.0", tk.END)
        for match in regex.finditer(full_text):
            start_idx = self._get_tk_index(full_text, match.start())
            end_idx = self._get_tk_index(full_text, match.end())
            self.text_area.tag_add(tag_id, start_idx, end_idx)

    def _get_tk_index(self, text, offset):
        before_text = text[:offset]
        lines = before_text.split('\n')
        return f"{len(lines)}.{len(lines[-1])}"

    def on_highlight_preset_change(self, name_var, hex_var, btn):
        new_hex = PRESET_HIGHLIGHTS[name_var.get()]; hex_var.set(new_hex); btn.config(bg=new_hex); self.refresh_view()

    def pick_custom_highlight(self, hex_var, name_var, btn):
        color = colorchooser.askcolor(initialcolor=hex_var.get())[1]
        if color: hex_var.set(color); name_var.set("Custom"); btn.config(bg=color); self.refresh_view()

    def toggle_h_scroll(self):
        if self.h_scroll_var.get():
            self.text_area.config(wrap=tk.NONE)
            self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X, before=self.text_area)
        else:
            self.text_area.config(wrap=tk.WORD); self.h_scroll.pack_forget()
        self.refresh_view()

    def handle_import(self):
        path = filedialog.askopenfilename()
        if path: self.service.async_import(path, lambda s, e: self.root.after(0, lambda: self.refresh_view(True)))

    def handle_export(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt")
        if path:
            patterns_data = [("" if r["case_sensitive"].get() else "(?i)") + r["var"].get() for r in self.filter_rows if r["var"].get()]
            self.service.export_data(path, patterns_data, self.search_mode.get())

    def toggle_tail(self):
        if self.tail_var.get():
            if not self.service.current_file:
                messagebox.showwarning("Warning", "Please import a file first."); self.tail_var.set(False); return
            self.service.start_tail_worker(lambda: self.root.after(0, self.refresh_view))
        else: self.service.stop_tail()

    def handle_mousewheel(self, event):
        direction = -1 if event.delta > 0 else 1
        self.text_area.yview_scroll(direction, "units")
        return "break"

    def remove_filter(self, frame, data):
        frame.destroy(); self.filter_rows.remove(data); self.refresh_view()

if __name__ == "__main__":
    db = LogDatabase(); svc = LogService(db)
    root = tk.Tk(); app = LogViewerApp(root, svc); root.mainloop()
