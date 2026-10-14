import json
import tkinter as tk
from datetime import date, timedelta
from pathlib import Path
from tkinter import messagebox, ttk


DATA_FILE = Path(__file__).with_name("words.json")
LEVEL_NAMES = ["不认识", "刚认识", "有点熟", "比较熟", "很熟", "已掌握"]
REVIEW_DAYS = [0, 1, 3, 7, 14, 30]


class WordApp:
    def __init__(self, root):
        self.root = root
        self.root.title("英语单词本")
        self.root.geometry("1000x680")
        self.root.minsize(820, 560)
        self.words = self.load_words()
        self.word_map = {}

        self.build_ui()
        self.refresh_table()

    def load_words(self):
        if not DATA_FILE.exists():
            return []
        try:
            with DATA_FILE.open("r", encoding="utf-8") as f:
                words = json.load(f)
            return words if isinstance(words, list) else []
        except (OSError, json.JSONDecodeError):
            messagebox.showwarning("提示", "单词数据文件无法读取，将从空单词本开始。")
            return []

    def save_words(self):
        with DATA_FILE.open("w", encoding="utf-8") as f:
            json.dump(self.words, f, ensure_ascii=False, indent=2)

    def build_ui(self):
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")

        outer = ttk.Frame(self.root, padding=14)
        outer.pack(fill="both", expand=True)

        ttk.Label(outer, text="英语单词本", font=("Microsoft YaHei UI", 20, "bold")).pack(anchor="w")
        ttk.Label(outer, text="添加单词、查询释义、记录熟练程度，并按计划复习。", foreground="#666666").pack(anchor="w", pady=(2, 12))

        form = ttk.LabelFrame(outer, text="单词信息", padding=10)
        form.pack(fill="x", pady=(0, 10))
        form.columnconfigure(1, weight=1)
        form.columnconfigure(3, weight=2)

        ttk.Label(form, text="英文单词").grid(row=0, column=0, sticky="w", padx=(0, 6), pady=5)
        self.word_entry = ttk.Entry(form)
        self.word_entry.grid(row=0, column=1, sticky="ew", padx=(0, 12), pady=5)

        ttk.Label(form, text="中文释义").grid(row=0, column=2, sticky="w", padx=(0, 6), pady=5)
        self.meaning_entry = ttk.Entry(form)
        self.meaning_entry.grid(row=0, column=3, sticky="ew", pady=5)

        ttk.Label(form, text="例句（可选）").grid(row=1, column=0, sticky="w", padx=(0, 6), pady=5)
        self.example_entry = ttk.Entry(form)
        self.example_entry.grid(row=1, column=1, columnspan=3, sticky="ew", pady=5)

        form_buttons = ttk.Frame(form)
        form_buttons.grid(row=2, column=0, columnspan=4, sticky="w", pady=(6, 0))
        ttk.Button(form_buttons, text="添加单词", command=self.add_word).pack(side="left", padx=(0, 8))
        ttk.Label(form_buttons, text="熟练程度").pack(side="left", padx=(10, 6))
        self.level_box = ttk.Combobox(form_buttons, state="readonly", width=14,
                                      values=[f"{i} - {name}" for i, name in enumerate(LEVEL_NAMES)])
        self.level_box.current(0)
        self.level_box.pack(side="left", padx=(0, 8))
        ttk.Button(form_buttons, text="更新选中单词", command=self.update_level).pack(side="left", padx=(0, 8))
        ttk.Button(form_buttons, text="删除选中单词", command=self.delete_word).pack(side="left")

        search_frame = ttk.Frame(outer)
        search_frame.pack(fill="x", pady=(0, 8))
        ttk.Label(search_frame, text="查询").pack(side="left", padx=(0, 6))
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.search_entry.bind("<Return>", lambda event: self.refresh_table())
        ttk.Button(search_frame, text="搜索", command=self.refresh_table).pack(side="left", padx=(0, 6))
        ttk.Button(search_frame, text="显示全部", command=self.show_all).pack(side="left", padx=(0, 6))
        ttk.Button(search_frame, text="开始复习", command=self.start_review).pack(side="left")

        table_frame = ttk.Frame(outer)
        table_frame.pack(fill="both", expand=True)
        columns = ("word", "meaning", "level", "next_review")
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        self.table.heading("word", text="英文单词")
        self.table.heading("meaning", text="中文释义")
        self.table.heading("level", text="熟练程度")
        self.table.heading("next_review", text="下次复习日期")
        self.table.column("word", width=180, anchor="w")
        self.table.column("meaning", width=300, anchor="w")
        self.table.column("level", width=150, anchor="center")
        self.table.column("next_review", width=150, anchor="center")
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        self.table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.table.bind("<<TreeviewSelect>>", self.on_select)

        self.status_label = ttk.Label(outer, text="共 0 个单词", foreground="#666666")
        self.status_label.pack(anchor="w", pady=(8, 0))

    def level_text(self, level):
        return f"{level} - {LEVEL_NAMES[level]}"

    def find_word(self, word):
        word = word.lower()
        for item in self.words:
            if item["word"].lower() == word:
                return item
        return None

    def add_word(self):
        word = self.word_entry.get().strip()
        meaning = self.meaning_entry.get().strip()
        example = self.example_entry.get().strip()

        if not word or not meaning:
            messagebox.showinfo("提示", "请至少填写英文单词和中文释义。")
            return
        if self.find_word(word):
            messagebox.showinfo("提示", "这个单词已经存在，可以先搜索再更新。")
            return

        self.words.append({
            "word": word,
            "meaning": meaning,
            "example": example,
            "level": 0,
            "next_review": date.today().isoformat()
        })
        self.save_words()
        self.word_entry.delete(0, "end")
        self.meaning_entry.delete(0, "end")
        self.example_entry.delete(0, "end")
        self.search_entry.delete(0, "end")
        self.refresh_table()
        self.word_entry.focus_set()

    def refresh_table(self):
        keyword = self.search_entry.get().strip().lower()
        self.table.delete(*self.table.get_children())
        self.word_map = {item["word"].lower(): item for item in self.words}
        count = 0
        for item in self.words:
            searchable = " ".join([item["word"], item["meaning"], item.get("example", "")]).lower()
            if keyword and keyword not in searchable:
                continue
            self.table.insert("", "end", iid=item["word"].lower(), values=(
                item["word"], item["meaning"], self.level_text(item["level"]), item["next_review"]
            ))
            count += 1
        self.status_label.config(text=f"当前显示 {count} 个单词 / 单词本共 {len(self.words)} 个")

    def show_all(self):
        self.search_entry.delete(0, "end")
        self.refresh_table()

    def on_select(self, event=None):
        selected = self.table.selection()
        if not selected:
            return
        item = self.word_map.get(selected[0])
        if not item:
            return
        self.word_entry.delete(0, "end")
        self.word_entry.insert(0, item["word"])
        self.meaning_entry.delete(0, "end")
        self.meaning_entry.insert(0, item["meaning"])
        self.example_entry.delete(0, "end")
        self.example_entry.insert(0, item.get("example", ""))
        self.level_box.set(self.level_text(item["level"]))

    def update_level(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showinfo("提示", "请先在列表中选中一个单词。")
            return
        item = self.word_map.get(selected[0])
        if not item:
            return
        level = self.level_box.current()
        if level < 0:
            messagebox.showinfo("提示", "请先选择熟练程度。")
            return
        item["level"] = level
        item["next_review"] = (date.today() + timedelta(days=REVIEW_DAYS[level])).isoformat()
        self.save_words()
        self.refresh_table()
        messagebox.showinfo("已更新", f"{item['word']} 的熟练程度已更新。")

    def delete_word(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showinfo("提示", "请先在列表中选中一个单词。")
            return
        item = self.word_map.get(selected[0])
        if not item:
            return
        if not messagebox.askyesno("确认删除", f"确定删除单词 {item['word']} 吗？"):
            return
        self.words.remove(item)
        self.save_words()
        self.refresh_table()
        self.word_entry.delete(0, "end")
        self.meaning_entry.delete(0, "end")
        self.example_entry.delete(0, "end")

    def start_review(self):
        today = date.today().isoformat()
        due_words = sorted(
            [item for item in self.words if item["next_review"] <= today],
            key=lambda item: (item["next_review"], item["level"])
        )
        if not due_words:
            messagebox.showinfo("复习完成", "今天没有到期的单词。添加新单词后就可以开始复习了。")
            return

        win = tk.Toplevel(self.root)
        win.title("单词复习")
        win.geometry("560x420")
        win.transient(self.root)
        win.grab_set()

        progress = ttk.Label(win, text="", padding=(16, 14))
        progress.pack()
        word_label = ttk.Label(win, text="", font=("Arial", 26, "bold"), padding=12)
        word_label.pack()
        meaning_label = ttk.Label(win, text="", font=("Microsoft YaHei UI", 13), wraplength=500,
                                  justify="center", padding=10)
        meaning_label.pack(fill="x")
        example_label = ttk.Label(win, text="", foreground="#666666", wraplength=500,
                                  justify="center", padding=8)
        example_label.pack(fill="x")

        reveal_button = ttk.Button(win, text="显示释义")
        reveal_button.pack(pady=12)
        answer_frame = ttk.Frame(win, padding=8)
        answer_frame.pack()
        known_button = ttk.Button(answer_frame, text="记住了")
        known_button.pack(side="left", padx=8)
        unknown_button = ttk.Button(answer_frame, text="没记住")
        unknown_button.pack(side="left", padx=8)
        result_label = ttk.Label(win, text="先回想单词的意思，再点击“显示释义”。", foreground="#666666")
        result_label.pack(pady=10)

        index = 0

        def show_question():
            nonlocal index
            if index >= len(due_words):
                win.destroy()
                self.refresh_table()
                messagebox.showinfo("复习完成", f"本轮复习了 {len(due_words)} 个单词。")
                return
            item = due_words[index]
            progress.config(text=f"第 {index + 1} / {len(due_words)} 个")
            word_label.config(text=item["word"])
            meaning_label.config(text="")
            example_label.config(text="")
            reveal_button.config(state="normal")
            known_button.config(state="disabled")
            unknown_button.config(state="disabled")
            result_label.config(text="先回想单词的意思，再点击“显示释义”。")

        def reveal():
            item = due_words[index]
            meaning_label.config(text=item["meaning"])
            example = item.get("example", "")
            example_label.config(text=f"例句：{example}" if example else "")
            reveal_button.config(state="disabled")
            known_button.config(state="normal")
            unknown_button.config(state="normal")
            result_label.config(text="根据自己的回忆情况选择。")

        def record_answer(known):
            nonlocal index
            item = due_words[index]
            if known:
                item["level"] = min(5, item["level"] + 1)
                days = REVIEW_DAYS[item["level"]]
                item["next_review"] = (date.today() + timedelta(days=days)).isoformat()
            else:
                item["level"] = max(0, item["level"] - 1)
                item["next_review"] = date.today().isoformat()
            self.save_words()
            index += 1
            show_question()

        reveal_button.config(command=reveal)
        known_button.config(command=lambda: record_answer(True))
        unknown_button.config(command=lambda: record_answer(False))
        show_question()


def main():
    root = tk.Tk()
    WordApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
