import tkinter as tk
import translators as ts
import keyboard
import threading
import time

class ElegantMicroTranslator:
    def __init__(self, root):
        self.root = root
        self.root.title("翻譯")

        # ==================== 自訂設定區 ====================
        # 已為你切換至【優美】風格，並調整為更高雅的字體
        theme_style = "預設" 
        
        self.themes = {
            "預設": {"bg": "#FFFFFF", "fg": "#111111", "font": ("Microsoft JhengHei", 14, "bold")},
            "卡通": {"bg": "#FFC0CB", "fg": "#D02090", "font": ("Microsoft JhengHei", 14, "bold")},
            "文青": {"bg": "#F5F5DC", "fg": "#556B2F", "font": ("Microsoft JhengHei", 14, "bold")},
            # 【優美字體優化】改用「標楷體」(DFKai-SB) 搭配 15 級字，呈現古典、優美的視覺感
            "優美": {"bg": "#1C2833", "fg": "#F1C40F", "font": ("DFKai-SB", 15, "bold")}
        }
        theme = self.themes[theme_style]
        # ===================================================

        # 1. 調整為微型尺寸，並精準定位在右下角
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        win_width = 240
        win_height = 140 # 微調高 10 像素，確保大字體排版優美
        
        x_pos = screen_width - win_width - 20
        y_pos = screen_height - win_height - 70
        
        self.root.geometry(f"{win_width}x{win_height}+{x_pos}+{y_pos}")
        self.root.configure(bg=theme["bg"])
        
        # 預設隱藏在最下層
        self.root.lower() 
        
        # 透明度設定為 90%
        self.root.attributes('-alpha', 0.90)

        # 2. 介面極簡化：優美字體顯示框
        self.output_box = tk.Text(root, bg=theme["bg"], fg=theme["fg"], font=theme["font"],
                                  bd=1, relief=tk.SOLID, padx=12, pady=12, 
                                  state=tk.DISABLED, wrap=tk.WORD)
        self.output_box.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 3. 快捷鍵監聽線程
        self.hotkey_thread = threading.Thread(target=self.setup_hotkey, daemon=True)
        self.hotkey_thread.start()

    def setup_hotkey(self):
        keyboard.add_hotkey('ctrl+q', self.on_hotkey_pressed)
        keyboard.wait()

    def on_hotkey_pressed(self):
        # 彈出視窗
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.attributes('-topmost', False)
        
        self._update_box("⏳ 讀取中...")
        
        keyboard.send('ctrl+c')
        time.sleep(0.2) 

        try:
            text_to_translate = self.root.clipboard_get().strip()
            if text_to_translate:
                self.translate_text(text_to_translate)
            else:
                self._update_box("❌ 剪貼簿無文字")
                # 【修改】改為 5000 毫秒 (5秒) 後隱藏
                self.root.after(5000, self.hide_window)
        except:
            self._update_box("❌ 抓取失敗")
            self.root.after(5000, self.hide_window)

    def translate_text(self, text):
        try:
            result = ts.translate_text(text, from_language='en', to_language='zh-TW', translator='google')
            
            # 顯示優美字體的翻譯結果
            self._update_box(result)
            
            # 【修改】改為 5000 毫秒 (5秒) 後自動退場
            self.root.after(5000, self.hide_window)
        except Exception:
            self._update_box("❌ 翻譯出錯")
            self.root.after(5000, self.hide_window)

    def _update_box(self, text):
        self.output_box.config(state=tk.NORMAL)
        self.output_box.delete("1.0", tk.END)
        self.output_box.insert(tk.END, text)
        self.output_box.config(state=tk.DISABLED)
        self.root.update()

    def hide_window(self):
        self.root.lower()

if __name__ == "__main__":
    root = tk.Tk()
    app = ElegantMicroTranslator(root)
    root.mainloop()