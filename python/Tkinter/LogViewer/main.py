import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser, ttk
from database import LogDatabase
from services import LogService

# 代表的な色のプリセット
PRESET_COLORS = {
    "Yellow": "#FFFF00",
    "Red": "#FF4444",
    "Green": "#00FF00",
    "Cyan": "#00FFFF",
    "Magenta": "#FF00FF",
    "Orange": "#FFA500",
    "White": "#FFFFFF",
    "Custom": "" # カラーピッカーで選んだ時用
}

class LogViewerApp:
    def __init__(self, root, service):
        self.root = root
        self.service = service
        self.current_offset = 0
        self.filter_rows = []
        self.search_mode = tk.StringVar(value="OR")
        self._init_ui()

    def _init_ui(self):
        self.root.title("Clean Professional Log Viewer (Multi-Color Mode)")
        self.root.geometry("1200x850")

        # ツールバー
        toolbar = tk.Frame(self.root, padx=10, pady=5)
        toolbar.pack(fill=tk.X)
        tk.Button(toolbar, text="+ Add Key", command=self.add_filter_row).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Import", command=self.handle_import).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Export", command=self.handle_export).pack(side=tk.LEFT, padx=2)
        
        tk.Label(toolbar, text="  Mode:").pack(side=tk.LEFT)
        ttk.Radiobutton(toolbar, text="OR", variable=self.search_mode, value="OR", command=self.refresh_view).pack(side=tk.LEFT)
        ttk.Radiobutton(toolbar, text="AND", variable=self.search_mode, value="AND", command=self.refresh_view).pack(side=tk.LEFT)

        self.filter_container = tk.LabelFrame(self.root, text="Search Filters (Keyword | Preset Color | Custom Picker)")
        self.filter_container.pack(fill=tk.X, padx=10, pady=5)

        view_frame = tk.Frame(self.root)
        view_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)
        self.scrollbar = tk.Scrollbar(view_frame, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area = tk.Text(view_frame, wrap=tk.NONE, bg="#1e1e1e", fg="#d4d4d4",
                                 font=("Consolas", 10), state=tk.DISABLED,
                                 yscrollcommand=self.scrollbar.set)
        self.text_area.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.text_area.bind("<MouseWheel>", self.handle_mousewheel)
        self.add_filter_row()

    def add_filter_row(self):
        row = tk.Frame(self.filter_container)
        row.pack(fill=tk.X, pady=2)

        var = tk.StringVar()
        var.trace_add("write", lambda *a: self.refresh_view(True))
        tk.Entry(row, textvariable=var, width=40).pack(side=tk.LEFT, padx=5)

        # 1. 代表的な色の選択 (Combobox)
        color_name_var = tk.StringVar(value="Yellow")
        color_combo = ttk.Combobox(row, textvariable=color_name_var, values=list(PRESET_COLORS.keys())[:-1], width=10, state="readonly")
        color_combo.pack(side=tk.LEFT, padx=5)

        # 2. 自由な色選択ボタン (Color Picker)
        # 現在適用されている色を視覚的に表示するプレビューラベルを兼ねたボタン
        current_hex = tk.StringVar(value=PRESET_COLORS["Yellow"])
        picker_btn = tk.Button(row, text="🎨", bg=current_hex.get(), width=3)
        picker_btn.pack(side=tk.LEFT, padx=2)

        # イベント設定
        def on_combo_change(e):
            new_hex = PRESET_COLORS[color_name_var.get()]
            current_hex.set(new_hex)
            picker_btn.config(bg=new_hex)
            self.refresh_view()

        def on_picker_click():
            color = colorchooser.askcolor(initialcolor=current_hex.get())[1]
            if color:
                current_hex.set(color)
                color_name_var.set("Custom") # コンボボックスをCustom表示に
                picker_btn.config(bg=color)
                self.refresh_view()

        color_combo.bind("<<ComboboxSelected>>", on_combo_change)
        picker_btn.config(command=on_picker_click)

        tk.Button(row, text="✕", command=lambda: self.remove_filter(row, row_data)).pack(side=tk.LEFT, padx=5)
        
        row_data = {"var": var, "current_hex": current_hex, "frame": row}
        self.filter_rows.append(row_data)

    def refresh_view(self, reset_scroll=False):
        if reset_scroll: self.current_offset = 0
        patterns = [r["var"].get() for r in self.filter_rows]
        state = self.service.get_display_data(patterns, self.current_offset, self.search_mode.get())
        
        self.current_offset = state["offset"]
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", "\n".join(state["logs"]))
        
        for r in self.filter_rows:
            pattern = r["var"].get()
            if pattern:
                self._apply_highlight(pattern, r["current_hex"].get())
        
        self.text_area.config(state=tk.DISABLED)

    def _apply_highlight(self, pattern, color_code):
        tag_id = f"tag_{pattern}"
        self.text_area.tag_config(tag_id, foreground=color_code)
        idx = "1.0"
        while True:
            idx = self.text_area.search(pattern, idx, tk.END, regexp=True)
            if not idx: break
            line_end = f"{idx.split('.')[0]}.end"
            self.text_area.tag_add(tag_id, idx, line_end)
            idx = line_end

    # (handle_import, handle_export, handle_mousewheel, remove_filter は以前と同じ)
    def handle_import(self):
        path = filedialog.askopenfilename()
        if not path: return
        self.root.config(cursor="watch")
        def on_done(s, e):
            self.root.config(cursor=""); self.refresh_view(True)
            if not s: messagebox.showerror("Error", e)
        self.service.async_import(path, lambda s, e: self.root.after(0, lambda: on_done(s, e)))

    def handle_export(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt")
        if not path: return
        patterns = [r["var"].get() for r in self.filter_rows]
        s, e = self.service.export_data(path, patterns, self.search_mode.get())
        if s: messagebox.showinfo("Success", "Exported.")
        else: messagebox.showerror("Error", e)

    def handle_mousewheel(self, event):
        self.current_offset += 10 if event.delta < 0 else -10
        self.refresh_view(); return "break"

    def remove_filter(self, frame, row_data):
        frame.destroy()
        self.filter_rows.remove(row_data)
        self.refresh_view()

if __name__ == "__main__":
    db = LogDatabase()
    svc = LogService(db)
    root = tk.Tk()
    app = LogViewerApp(root, svc)
    root.mainloop()
