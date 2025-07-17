# main.py

from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, NoTransition # <--- 修正：將 FadeTransition 替換為 NoTransition
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
import os
from kivy.core.text import LabelBase # 引入 LabelBase 以註冊字體
import kivymd # 引入 kivymd 以便獲取其安裝路徑
from kivy.core.window import Window # <--- 新增這行來引入 Window

# 引入所有畫面
from screens.home_screen import HomeScreen
from screens.camera_screen import CameraScreen
from screens.journal_screen import JournalScreen
from screens.transaction_screen import TransactionScreen

class MainApp(MDApp):
    dialog = None # 用於彈出視窗

    def build(self):
        # 設置應用程式主題
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"

        # --- 全局字體路徑配置 ---
        app_root_dir = os.path.dirname(os.path.abspath(__file__))
        # 注意：根據您項目的結構，這裡假設字體在 'fonts' 目錄下，且該目錄與 'main.py' 同級或在 'ui' 下
        # 這裡會調整為 'fonts' 與 main.py 同級
        chinese_font_name = "NotoSansCJK"
        chinese_font_path = os.path.join(app_root_dir, 'fonts', 'NotoSansCJK-Regular.ttf') # 更正路徑
        kivymd_icons_font_path = os.path.join(os.path.dirname(kivymd.__file__), 'fonts', 'kivymd-icon.ttf')

        print(f"嘗試通過 LabelBase 註冊中文字體: {chinese_font_path}")
        if not os.path.exists(chinese_font_path):
            print(f"錯誤：中文字體檔案不存在於此路徑: {chinese_font_path}")
            print("請確保 'NotoSansCJK-Regular.ttf' 存在於 'fonts/' 資料夾中。") # 更正提示
            import sys
            sys.exit(1)
        try:
            LabelBase.register(
                name=chinese_font_name,
                fn_regular=chinese_font_path,
            )
            print(f"中文字體 '{chinese_font_path}' 已成功註冊為 '{chinese_font_name}'.")
        except Exception as e:
            print(f"中文字體通過 LabelBase 註冊失敗或已註冊: {e}")
            pass

        text_font_styles = [
            "H1", "H2", "H3", "H4", "H5", "H6",
            "Subtitle1", "Subtitle2",
            "Body1", "Body2",
            "Button", "Caption", "Overline"
        ]

        for style in text_font_styles:
            if style in self.theme_cls.font_styles:
                self.theme_cls.font_styles[style][0] = chinese_font_name
        print("中文字體已應用到 KivyMD 的文字樣式。")

        print(f"嘗試通過 LabelBase 註冊 KivyMD 圖示字體: {kivymd_icons_font_path}")
        if not os.path.exists(kivymd_icons_font_path):
            print(f"警告：KivyMD 圖示字體檔案不存在於此路徑: {kivymd_icons_font_path}。圖示可能仍會缺失。")
            print("請確保 'kivymd-icon.ttf' 存在於 KivyMD 的安裝目錄下。")
        else:
            try:
                LabelBase.register(
                    name='Icons',
                    fn_regular=kivymd_icons_font_path,
                )
                print(f"KivyMD 圖示字體 '{kivymd_icons_font_path}' 已在應用啟動前通過 LabelBase 成功註冊為 'Icons'.")
            except Exception as e:
                print(f"KivyMD 圖示字體通過 LabelBase 註冊失敗或已註冊: {e}")
                pass

        # --- 加載 KV 檔案 ---
        kv_files = {
            'home_screen.kv',
            'journal_screen.kv',
            'camera_screen.kv',
            'transaction_screen.kv'
        }
        for kv_file in kv_files:
            kv_path = os.path.join(app_root_dir, 'kv', kv_file)
            print(f"嘗試從路徑加載 KV 檔案: {kv_path}")
            if not os.path.exists(kv_path):
                # 對於 journal_screen.kv，如果它是可選的，可以將錯誤改為警告
                if kv_file == 'journal_screen.kv':
                    print(f"警告：KV 檔案不存在於此路徑: {kv_path}。 {kv_file} 將不包含 .kv 定義。")
                else:
                    print(f"錯誤：KV 檔案不存在於此路徑: {kv_path}")
                    print(f"請確保 '{kv_file}' 存在於 'kv/' 資料夾中。")
                    import sys
                    sys.exit(1)
            else:
                Builder.load_file(kv_path)
                print(f"KV 檔案 '{kv_path}' 已加載。")

        # --- 配置 ScreenManager ---
        # 核心改動：將 ScreenManager 的 transition 設置為 NoTransition()
        self.sm = ScreenManager(transition=NoTransition()) # <--- 修正：這裡已添加 transition=NoTransition()
        self.sm.add_widget(HomeScreen(name='home'))
        self.sm.add_widget(CameraScreen(name='camera_screen'))
        self.sm.add_widget(JournalScreen(name='journal_screen'))
        self.sm.add_widget(TransactionScreen(name='transaction_screen'))

        # <--- 新增的返回鍵處理邏輯 --->
        Window.bind(on_keyboard=self.on_keyboard)
        # <--- 新增的返回鍵處理邏輯 --->

        return self.sm

    def on_start(self):
        print("應用程式已啟動。")

    def on_stop(self):
        print("應用程式已關閉。")

    def show_alert_dialog(self, text):
        if not self.dialog:
            self.dialog = MDDialog(
                text=text,
                buttons=[
                    MDFlatButton(
                        text="OK",
                        on_release=self.close_dialog
                    )
                ]
            )
        else:
            self.dialog.text = text
        self.dialog.open()

    def close_dialog(self, obj):
        self.dialog.dismiss()

    # <--- 新增的返回鍵處理方法 --->
    def on_keyboard(self, window, key, *args):
        # keycode 27 是 Android 的返回鍵 (也對應桌面版的 'escape' 鍵)
        if key == 27:
            current_screen = self.sm.current
            print(f"監聽到返回鍵，當前畫面: {current_screen}")

            if current_screen == 'home':
                # 如果在首頁，則退出應用程式
                print("在首頁，退出應用程式。")
                self.stop()
                return True # 表示事件已處理

            # 從其他畫面返回 Home
            elif current_screen in ['journal_screen', 'camera_screen', 'transaction_screen']:
                print(f"從 {current_screen} 返回 Home。")
                self.sm.current = 'home'
                return True
            # 如果有其他畫面需要特定的返回邏輯，可以在這裡添加 elif 判斷

        return False # 返回 False 表示事件未完全處理，允許其他監聽器處理
    # <--- 新增的返回鍵處理方法 --->

if __name__ == '__main__':
    MainApp().run()