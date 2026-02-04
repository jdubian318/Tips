import tkinter as tk
from tkinter import filedialog, messagebox, ttk, colorchooser
from database import LogDatabase
from services import LogService

PRESET_COLORS = {"Yellow": "#FFFF00", "Red": "#FF4444", "Green": "#00FF00", "Cyan": "#00FFFF", "White": "#FFFFFF", "Custom": ""}

class LogViewerApp:
    def __init__(self, root, service):
        self.root = root
        self.service = service
        self.current_offset = 0
        self.filter_rows = []
        self.search_mode = tk.StringVar(value="OR")
        self.tail_var = tk.BooleanVar(value=False)
        self._init_ui()

    def _init_ui(self):
        self.root.title("Safe Read-Only Log Viewer + Tail")
        self.root.geometry("1200x850")

        toolbar = tk.Frame(self.root, padx=10, pady=5)
        toolbar.pack(fill=tk.X)

        tk.Button(toolbar, text="+ Add Key", command=self.add_filter_row).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Import", command=self.handle_import).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Export", command=self.handle_export).pack(side=tk.LEFT, padx=2)
        
        # Tail ON/OFFスイッチ
        tk.Checkbutton(toolbar, text="Tail -f (Auto Update)", variable=self.tail_var, command=self.toggle_tail).pack(side=tk.LEFT, padx=10)

        tk.Label(toolbar, text="Mode:").pack(side=tk.LEFT)
        ttk.Radiobutton(toolbar, text="OR", variable=self.search_mode, value="OR", command=self.refresh_view).pack(side=tk.LEFT)
        ttk.Radiobutton(toolbar, text="AND", variable=self.search_mode, value="AND", command=self.refresh_view).pack(side=tk.LEFT)

        self.filter_container = tk.LabelFrame(self.root, text="Search Filters")
        self.filter_container.pack(fill=tk.X, padx=10, pady=5)

        view_frame = tk.Frame(self.root)
        view_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)
        self.text_area = tk.Text(view_frame, wrap=tk.NONE, bg="#1e1e1e", fg="#d4d4d4", font=("Consolas", 10), state=tk.DISABLED)
        self.text_area.pack(expand=True, fill=tk.BOTH)
        self.text_area.bind("<MouseWheel>", self.handle_mousewheel)
        self.add_filter_row()

    def toggle_tail(self):
        if self.tail_var.get():
            if not self.service.current_file:
                messagebox.showwarning("Warning", "Please import a file first.")
                self.tail_var.set(False)
                return
            # Tail開始。更新があったらメインスレッドで再描画
            self.service.start_tail_worker(lambda: self.root.after(0, self.refresh_view))
        else:
            self.service.stop_tail()

    def refresh_view(self, reset_scroll=False):
        patterns = [r["var"].get() for r in self.filter_rows]
        state = self.service.get_display_data(patterns, self.current_offset, self.search_mode.get())
        
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", "\n".join(state["logs"]))
        for r in self.filter_rows:
            if r["var"].get(): self._apply_highlight(r["var"].get(), r["current_hex"].get())
        self.text_area.config(state=tk.DISABLED)

    def add_filter_row(self):
        row = tk.Frame(self.filter_container)
        row.pack(fill=tk.X, pady=2)
        var = tk.StringVar()
        var.trace_add("write", lambda *a: self.refresh_view(True))
        tk.Entry(row, textvariable=var, width=40).pack(side=tk.LEFT, padx=5)
        
        color_name_var = tk.StringVar(value="Yellow")
        current_hex = tk.StringVar(value=PRESET_COLORS["Yellow"])
        color_combo = ttk.Combobox(row, textvariable=color_name_var, values=list(PRESET_COLORS.keys())[:-1], width=10, state="readonly")
        color_combo.pack(side=tk.LEFT, padx=5)
        
        picker_btn = tk.Button(row, text="🎨", bg=current_hex.get(), width=3, command=lambda: self.pick_custom_color(current_hex, color_name_var, picker_btn))
        picker_btn.pack(side=tk.LEFT)
        color_combo.bind("<<ComboboxSelected>>", lambda e: self.on_preset_change(color_name_var, current_hex, picker_btn))

        tk.Button(row, text="✕", command=lambda: self.remove_filter(row, row_data)).pack(side=tk.LEFT, padx=5)
        row_data = {"var": var, "current_hex": current_hex, "frame": row}
        self.filter_rows.append(row_data)

    def _apply_highlight(self, pattern, color):
        tag_id = f"tag_{pattern}"
        self.text_area.tag_config(tag_id, foreground=color)
        idx = "1.0"
        while True:
            idx = self.text_area.search(pattern, idx, tk.END, regexp=True)
            if not idx: break
            line_end = f"{idx.split('.')[0]}.end"
            self.text_area.tag_add(tag_id, idx, line_end)
            idx = line_end

    def on_preset_change(self, name_var, hex_var, btn):
        new_hex = PRESET_COLORS[name_var.get()]
        hex_var.set(new_hex); btn.config(bg=new_hex); self.refresh_view()

    def pick_custom_color(self, hex_var, name_var, btn):
        color = colorchooser.askcolor(initialcolor=hex_var.get())[1]
        if color: hex_var.set(color); name_var.set("Custom"); btn.config(bg=color); self.refresh_view()

    def handle_import(self):
        path = filedialog.askopenfilename()
        if path: self.service.async_import(path, lambda s, e: self.root.after(0, lambda: self.refresh_view(True)))

    def handle_export(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt")
        if path: self.service.export_data(path, [r["var"].get() for r in self.filter_rows], self.search_mode.get())

    def handle_mousewheel(self, event):
        self.current_offset += 10 if event.delta < 0 else -10
        self.refresh_view(); return "break"

    def remove_filter(self, frame, data):
        frame.destroy(); self.filter_rows.remove(data); self.refresh_view()

if __name__ == "__main__":
    db = LogDatabase(); svc = LogService(db)
    root = tk.Tk(); app = LogViewerApp(root, svc); root.mainloop()
