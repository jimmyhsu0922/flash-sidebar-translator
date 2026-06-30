import tkinter as tk
import keyboard
import threading
import time
import ctypes
import os
import requests
import urllib.parse
import sys

class UltimateHUDTranslator:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)
        
        self.active_timer_id = None
        self.history_file = "vocabulary_log.txt"
        
        self.is_input_active = False 
        self.is_vocab_open = False 

        # ==================== THEME CONFIGURATION ====================
        self.theme = {"bg": "#1A252F", "fg": "#F1C40F", "font": ("Microsoft JhengHei", 13, "bold")}
        # =============================================================

        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()
        
        self.win_width = 240
        self.base_height = 110  
        self.max_height = 400  
        
        self.x_pos = self.screen_width - self.win_width - 20
        self.y_pos = self.screen_height - self.base_height - 70
        
        self.root.geometry(f"{self.win_width}x{self.base_height}+{self.x_pos}+{self.y_pos}")
        self.root.configure(bg=self.theme["bg"])
        self.root.lower() 
        self.root.attributes('-alpha', 0.90)

        try:
            GWL_EXSTYLE = -20
            WS_EX_TOOLWINDOW = 0x00000080
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            style |= WS_EX_TOOLWINDOW
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        except:
            pass

        # 右上角關閉按鈕
        self.close_btn = tk.Button(root, text="×", font=("Arial", 11, "bold"),
                                    bg=self.theme["bg"], fg="#E74C3C", bd=0, 
                                    activebackground=self.theme["bg"], activeforeground="#C0392B",
                                    command=self.hide_window, cursor="hand2")
        self.close_btn.place(x=self.win_width - 24, y=2, width=20, height=20)

        # 主翻譯顯示框
        self.output_box = tk.Text(root, bg=self.theme["bg"], fg=self.theme["fg"], font=self.theme["font"],
                                  bd=1, relief=tk.SOLID, highlightthickness=0,
                                  padx=12, pady=8, state=tk.DISABLED, wrap=tk.WORD)
        self.output_box.pack(fill=tk.BOTH, expand=True, padx=(4, 24), pady=(4, 25))

        # 底部的單字庫按鈕
        self.vocab_btn = tk.Button(root, text="Open Vocabulary DB (HotKey: `+3)", font=("Microsoft JhengHei", 8, "bold"),
                                   bg="#2C3E50", fg="#ECF0F1", bd=0, activebackground="#34495E",
                                   activeforeground="#FFFFFF", command=self.open_vocabulary_window)
        self.vocab_btn.place(x=4, y=self.base_height - 22, width=self.win_width - 8, height=18)

        self.hotkey_thread = threading.Thread(target=self.setup_hotkeys, daemon=True)
        self.hotkey_thread.start()

    def setup_hotkeys(self):
        keyboard.add_hotkey('`+1', lambda: self.handle_hotkey_trigger('en_to_zh'))
        keyboard.add_hotkey('`+2', lambda: self.open_chinese_input_window())
        keyboard.add_hotkey('`+3', lambda: self.open_vocabulary_window())
        keyboard.add_hotkey('`+4', lambda: self.quit_program())
        keyboard.wait()

    def handle_hotkey_trigger(self, mode):
        if self.active_timer_id:
            self.root.after_cancel(self.active_timer_id)
            self.active_timer_id = None

        self.root.clipboard_clear()
        self.root.update()

        keyboard.send('ctrl+c')
        time.sleep(0.15) 

        try:
            text = self.root.clipboard_get().strip()
            if text:
                self.show_hud_window()
                self._update_box("Processing...")
                self.process_translation(text, mode)
        except tk.TclError:
            pass

    def open_chinese_input_window(self):
        if self.is_input_active:
            return
        
        self.is_input_active = True

        if self.active_timer_id:
            self.root.after_cancel(self.active_timer_id)
            self.active_timer_id = None

        input_win = tk.Toplevel()
        input_win.title("中翻英輸入")
        input_win.geometry("320x100")
        input_win.configure(bg="#2C3E50")
        input_win.attributes('-topmost', True)
        
        input_win.update_idletasks()
        w = input_win.winfo_width()
        h = input_win.winfo_height()
        x = (input_win.winfo_screenwidth() // 2) - (w // 2)
        y = (input_win.winfo_screenheight() // 2) - (h // 2)
        input_win.geometry(f"+{x}+{y}")

        lbl = tk.Label(input_win, text="請輸入欲翻譯的中文 (按 Enter 送出):", font=("Microsoft JhengHei", 10, "bold"), bg="#2C3E50", fg="#ECF0F1")
        lbl.pack(pady=(10, 5))

        entry = tk.Entry(input_win, font=("Microsoft JhengHei", 12), width=28, bd=1, relief=tk.SOLID)
        entry.pack(pady=5)
        entry.focus_set()

        def on_close_entry_window():
            self.is_input_active = False
            input_win.destroy()
        input_win.protocol("WM_DELETE_WINDOW", on_close_entry_window)

        def on_submit(event=None):
            user_text = entry.get().strip()
            input_win.destroy() 
            
            if user_text:
                self.show_hud_window()
                self._update_box("Processing...")
                
                def run_translation_task():
                    self.process_translation(user_text, 'zh_to_en')
                    time.sleep(0.5) 
                    self.is_input_active = False

                threading.Thread(target=run_translation_task, daemon=True).start()
            else:
                self.is_input_active = False

        entry.bind("<Return>", on_submit)

    def show_hud_window(self):
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.attributes('-topmost', False)

    def direct_translate(self, text, source_lang, target_lang):
        try:
            encoded_text = urllib.parse.quote(text)
            url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={source_lang}&tl={target_lang}&dt=t&q={encoded_text}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                result_segments = [sentence[0] for sentence in data[0] if sentence[0]]
                return "".join(result_segments)
        except:
            pass
        return None

    def process_translation(self, text, mode):
        try:
            if mode == 'en_to_zh':
                result = self.direct_translate(text, 'en', 'zh-TW')
                if result:
                    self._update_box(result)
                    self.log_to_vocabulary(text, result)
                else:
                    raise Exception()
            else:
                result = self.direct_translate(text, 'zh-TW', 'en')
                if result:
                    self._update_box(result)
                else:
                    raise Exception()
                
            self.reset_dismiss_timer()
        except:
            self._update_box("Translation error")
            self.reset_dismiss_timer()

    def log_to_vocabulary(self, english, chinese):
        cleaned_en = english.replace('\n', ' ').strip()
        cleaned_zh = chinese.replace('\n', ' ').strip()
        try:
            with open(self.history_file, "a", encoding="utf-8") as f:
                f.write(f"{cleaned_en} ---> {cleaned_zh}\n")
        except:
            pass

    def open_vocabulary_window(self):
        if self.is_vocab_open:
            return
        
        self.is_vocab_open = True

        vocab_win = tk.Toplevel()
        vocab_win.title("Vocabulary Database Log")
        vocab_win.geometry("460x500")
        vocab_win.configure(bg="#F8F9FA")
        vocab_win.attributes('-topmost', True)
        
        def on_close_vocab():
            self.is_vocab_open = False
            vocab_win.destroy()
        vocab_win.protocol("WM_DELETE_WINDOW", on_close_vocab)
        
        lbl = tk.Label(vocab_win, text="Collected Vocabularies (EN -> ZH)", font=("Microsoft JhengHei", 11, "bold"), bg="#F8F9FA", fg="#2C3E50")
        lbl.pack(pady=10)
        
        container = tk.Frame(vocab_win, bg="#F8F9FA")
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        canvas = tk.Canvas(container, bg="#FFFFFF", bd=1, relief=tk.SOLID, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#FFFFFF")
        
        def configure_canvas(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas_window, width=event.width)

        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.bind("<Configure>", configure_canvas)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 【修正】移除 -1，恢復 Windows 正常滾輪方向映射
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", on_mousewheel)

        def on_close_vocab_with_unbind():
            canvas.unbind_all("<MouseWheel>")
            self.is_vocab_open = False
            vocab_win.destroy()
        vocab_win.protocol("WM_DELETE_WINDOW", on_close_vocab_with_unbind)

        def refresh_list():
            for widget in scrollable_frame.winfo_children():
                widget.destroy()
                
            if not os.path.exists(self.history_file) or os.path.getsize(self.history_file) == 0:
                empty_lbl = tk.Label(scrollable_frame, text="Database is currently empty!", font=("Microsoft JhengHei", 10), bg="#FFFFFF", fg="#7F8C8D", height=5)
                empty_lbl.pack(fill=tk.X, padx=10, pady=10)
                return

            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
            except:
                lines = []

            for index, line in enumerate(lines):
                if "----" in line or "--->" in line:
                    item_frame = tk.Frame(scrollable_frame, bg="#FFFFFF", pady=4)
                    item_frame.pack(fill=tk.X, anchor="w", padx=5)
                    
                    del_btn = tk.Button(item_frame, text="❌", font=("Arial", 8), bg="#E74C3C", fg="white", bd=0, padx=4, cursor="hand2",
                                        command=lambda idx=index: delete_item(idx))
                    del_btn.pack(side=tk.LEFT, padx=(5, 10))
                    
                    content_lbl = tk.Label(item_frame, text=line.strip(), font=("Microsoft JhengHei", 9), bg="#FFFFFF", fg="#2C3E50", anchor="w", justify=tk.LEFT)
                    content_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)

        def delete_item(idx_to_delete):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                
                if 0 <= idx_to_delete < len(lines):
                    del lines[idx_to_delete]
                    
                with open(self.history_file, "w", encoding="utf-8") as f:
                    f.writelines(lines)
                    
                refresh_list()
            except Exception as e:
                pass

        refresh_list()

    def reset_dismiss_timer(self):
        self.active_timer_id = self.root.after(5000, self.hide_window)

    def _update_box(self, text):
        self.output_box.config(state=tk.NORMAL)
        self.output_box.delete("1.0", tk.END)
        self.output_box.insert(tk.END, text)
        self.output_box.config(state=tk.DISABLED)
        self.root.update()

        try:
            num_lines = int(self.output_box.index('end-1c').split('.')[0])
        except:
            num_lines = 1

        dynamic_height = self.base_height + (max(0, num_lines - 3) * 22)
        final_height = min(max(self.base_height, dynamic_height), self.max_height)
        new_y_pos = self.screen_height - final_height - 70
        
        self.root.geometry(f"{self.win_width}x{final_height}+{self.x_pos}+{new_y_pos}")
        self.vocab_btn.place(x=4, y=final_height - 22, width=self.win_width - 8, height=18)
        self.root.update()

    def hide_window(self):
        if self.active_timer_id:
            self.root.after_cancel(self.active_timer_id)
            self.active_timer_id = None
        self.root.lower()

    def quit_program(self):
        self.root.quit()
        self.root.destroy()
        sys.exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = UltimateHUDTranslator(root)
    root.mainloop()
