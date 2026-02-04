import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
from database import LogDatabase
from services import LogService

class LogViewerApp:
    def __init__(self, root, service):
        self.root = root
        self.service = service
        self.current_offset = 0
        self.filter_rows = [] # 各検索行のGUIパーツを管理
        
        self._init_ui()

    def _init_ui(self):
        self.root.title("Advanced Log Viewer")
        self.root.geometry("1000x800")

        # --- 設定パネル ---
        self.ctrl_frame = tk.LabelFrame(self.root, text="Controls", padx=10, pady=5)
        self.ctrl_frame.pack(fill=tk.X)

        btn_box = tk.Frame(self.ctrl_frame)
        btn_box.pack(fill=tk.X)
        tk.Button(btn_box, text="+ Add Key", command=self.add_filter_row).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_box, text="Import", command=self.on_import).pack(side=tk.LEFT, padx=2)

        # --- ログ表示エリア ---
        display_frame = tk.Frame(self.root)
        display_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

        self.scrollbar = tk.Scrollbar(display_frame, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_area = tk.Text(display_frame, wrap=tk.NONE, bg="#1e1e1e", fg="white",
                                 font=("Consolas", 10), state=tk.DISABLED,
                                 yscrollcommand=self.scrollbar.set)
        self.text_area.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        
        # 初期の検索行を追加
        self.add_filter_row()

    def add_filter_row(self):
        """新しいフィルタ入力行を追加"""
        row = tk.Frame(self.ctrl_frame)
        row.pack(fill=tk.X, pady=2)

        var = tk.StringVar()
        # 入力があるたびにリフレッシュ（reset_scroll=True）
        var.trace_add("write", lambda *a: self.refresh_view(True))

        ent = tk.Entry(row, textvariable=var, width=40)
        ent.pack(side=tk.LEFT, padx=5)

        color_btn = tk.Button(row, text="Color", bg="yellow", width=8)
        color_btn.current_color = "yellow"
        color_btn.config(command=lambda: self.on_pick_color(color_btn))
        color_btn.pack(side=tk.LEFT)

        del_btn = tk.Button(row, text="✕", command=lambda: self.on_remove_row(row))
        del_btn.pack(side=tk.LEFT, padx=5)

        self.filter_rows.append({"var": var, "btn": color_btn, "frame": row})

    def refresh_view(self, reset_scroll=False):
        """画面を最新の状態に更新"""
        if reset_scroll:
            self.current_offset = 0

        patterns = [r["var"].get() for r in self.filter_rows]
        state = self.service.get_display_state(patterns, self.current_offset)
        
        self.current_offset = state["offset"]
        
        # テキストエリアの更新
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", "\n".join(state["logs"]))
        
        # ハイライト処理
        for r in self.filter_rows:
            pattern = r["var"].get()
            if pattern:
                self._apply_highlight(pattern, r["btn"].current_color)
                
        self.text_area.config(state=tk.DISABLED)

    def _apply_highlight(self, pattern, color):
        """特定パターンのテキストに色をつける"""
        tag_name = f"tag_{pattern}"
        self.text_area.tag_config(tag_name, foreground=color)
        idx = "1.0"
        while True:
            idx = self.text_area.search(pattern, idx, tk.END, regexp=True)
            if not idx: break
            # 行末までタグを設定
            line_end = f"{idx.split('.')[0]}.end"
            self.text_area.tag_add(tag_name, idx, line_end)
            idx = line_end

    def on_import(self):
        path = filedialog.askopenfilename()
        if not path: return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f]
            self.service.db.clear_and_import(lines)
            self.refresh_view(True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load: {e}")

    def on_pick_color(self, btn):
        color = colorchooser.askcolor()[1]
        if color:
            btn.config(bg=color)
            btn.current_color = color
            self.refresh_view()

    def on_remove_row(self, frame):
        frame.destroy()
        self.filter_rows = [r for r in self.filter_rows if r["frame"] != frame]
        self.refresh_view()

if __name__ == "__main__":
    # 依存性の注入: DB -> Service -> App の順に組み立てる
    db = LogDatabase()
    svc = LogService(db, page_limit=500)
    
    root = tk.Tk()
    app = LogViewerApp(root, svc)
    root.mainloop()
