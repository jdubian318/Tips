import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser, ttk
from database import LogDatabase
from services import LogService

class LogViewerApp:
    def __init__(self, root, service):
        self.root = root
        self.service = service
        self.current_offset = 0
        self.filter_rows = []
        self.search_mode = tk.StringVar(value="OR")
        
        self._init_ui()

    def _init_ui(self):
        self.root.title("Clean Professional Log Viewer")
        self.root.geometry("1100x850")

        # --- ツールバーエリア ---
        toolbar = tk.Frame(self.root, padx=10, pady=5)
        toolbar.pack(fill=tk.X)

        tk.Button(toolbar, text="+ Add Key", command=self.add_filter_row).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Import", command=self.handle_import).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Export", command=self.handle_export).pack(side=tk.LEFT, padx=2)
        
        tk.Label(toolbar, text="  Mode:").pack(side=tk.LEFT)
        ttk.Radiobutton(toolbar, text="OR", variable=self.search_mode, value="OR", command=self.refresh_view).pack(side=tk.LEFT)
        ttk.Radiobutton(toolbar, text="AND", variable=self.search_mode, value="AND", command=self.refresh_view).pack(side=tk.LEFT)

        # --- フィルタ入力エリア ---
        self.filter_container = tk.LabelFrame(self.root, text="Search Filters")
        self.filter_container.pack(fill=tk.X, padx=10, pady=5)

        # --- ログ表示エリア ---
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
        tk.Entry(row, textvariable=var, width=50).pack(side=tk.LEFT, padx=5)

        c_btn = tk.Button(row, text="Color", bg="yellow", width=8)
        c_btn.current_color = "yellow"
        c_btn.config(command=lambda: self.pick_color(c_btn))
        c_btn.pack(side=tk.LEFT)

        tk.Button(row, text="✕", command=lambda: self.remove_filter(row)).pack(side=tk.LEFT, padx=5)
        self.filter_rows.append({"var": var, "btn": c_btn, "frame": row})

    def refresh_view(self, reset_scroll=False):
        if reset_scroll: self.current_offset = 0

        patterns = [r["var"].get() for r in self.filter_rows]
        state = self.service.get_display_data(patterns, self.current_offset, self.search_mode.get())
        
        self.current_offset = state["offset"]
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", "\n".join(state["logs"]))
        
        for r in self.filter_rows:
            if r["var"].get():
                self._apply_highlight(r["var"].get(), r["btn"].current_color)
        
        self.text_area.config(state=tk.DISABLED)

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

    def handle_import(self):
        path = filedialog.askopenfilename()
        if not path: return
        self.root.config(cursor="watch")
        
        def on_done(success, error_msg):
            self.root.config(cursor="")
            if success:
                self.refresh_view(True)
                messagebox.showinfo("Success", "Imported successfully.")
            else:
                messagebox.showerror("Error", error_msg)

        # Service層でスレッドを開始
        self.service.async_import(path, lambda s, e: self.root.after(0, lambda: on_done(s, e)))

    def handle_export(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt")
        if not path: return
        patterns = [r["var"].get() for r in self.filter_rows]
        success, err = self.service.export_data(path, patterns, self.search_mode.get())
        if success:
            messagebox.showinfo("Success", "Exported successfully.")
        else:
            messagebox.showerror("Error", err)

    def handle_mousewheel(self, event):
        self.current_offset += 10 if event.delta < 0 else -10
        self.refresh_view()
        return "break"

    def pick_color(self, btn):
        color = colorchooser.askcolor()[1]
        if color:
            btn.config(bg=color)
            btn.current_color = color
            self.refresh_view()

    def remove_filter(self, frame):
        frame.destroy()
        self.filter_rows = [r for r in self.filter_rows if r["frame"] != frame]
        self.refresh_view()

if __name__ == "__main__":
    db = LogDatabase()
    svc = LogService(db)
    root = tk.Tk()
    app = LogViewerApp(root, svc)
    root.mainloop()
