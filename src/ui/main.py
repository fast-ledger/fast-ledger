# main.py
import sys
import os
from os import environ
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivy.core.text import LabelBase
import kivymd

# 關鍵修改：手動將專案根目錄添加到 sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    print(f"專案根目錄 '{project_root}' 已添加到 sys.path。")

# 導入所有畫面 - 注意這裡的導入路徑，都是絕對導入
from ui.screens.home_screen import HomeScreen
from ui.screens.camera_screen import CameraScreen
from ui.screens.journal_screen import JournalScreen
from ui.screens.transaction_screen import TransactionScreen

# --- Kivy 環境變數與視窗的預設設定 (在 MainApp 類別定義之前執行) ---
density = 2.265
dpi = 157
environ['KIVY_METRICS_FONTSCALE'] = '1'
environ['KIVY_METRICS_DENSITY'] = str(density)
environ['KIVY_DPI'] = str(dpi)
print(f"Kivy 預設環境變數已設定: DENSITY={density}, DPI={dpi}, FONTSCALE=1")

default_window_width_px = 1080
default_window_height_px = 2400
Window.size = (default_window_width_px, default_window_height_px)
print(f"Kivy 預設視窗尺寸已設定為 (像素): {Window.size}")
# --- 預設設定結束 ---


class MainApp(MDApp):
    dialog = None

    def build(self):
        print(f"應用程式實際啟動的視窗尺寸 (像素): {Window.size}")

        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"

        # --- 全局字體路徑配置 ---
        app_root_dir = os.path.dirname(os.path.abspath(__file__))
        chinese_font_name = "NotoSansCJK"
        chinese_font_path = os.path.join(app_root_dir, 'fonts', 'NotoSansCJK-Regular.ttf')

        print(f"嘗試通過 LabelBase 註冊中文字體: {chinese_font_path}")
        if not os.path.exists(chinese_font_path):
            print(f"錯誤：中文字體檔案不存在於此路徑: {chinese_font_path}")
            print("請確保 'NotoSansCJK-Regular.ttf' (或 .ttc) 存在於 'fonts/' 資料夾中。")
            sys.exit(1)
        else:
            try:
                LabelBase.register(
                    name=chinese_font_name,
                    fn_regular=chinese_font_path,
                    fn_bold=chinese_font_path,
                    fn_italic=chinese_font_path
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

        kivymd_icons_font_path = os.path.join(os.path.dirname(kivymd.__file__), 'fonts', 'kivymd-icon.ttf')
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
                if kv_file == 'journal_screen.kv':
                    print(f"警告：KV 檔案不存在於此路徑: {kv_path}。 {kv_file} 將不包含 .kv 定義。")
                else:
                    print(f"錯誤：KV 檔案不存在於此路徑: {kv_path}")
                    print(f"請確保 '{kv_file}' 存在於 'kv/' 資料夾中。")
                    sys.exit(1)
            else:
                Builder.load_file(kv_path)
                print(f"KV 檔案 '{kv_path}' 已加載。")

        # --- 配置 ScreenManager ---
        self.sm = ScreenManager(transition=NoTransition())
        self.sm.add_widget(HomeScreen(name='home'))
        self.sm.add_widget(CameraScreen(name='camera_screen'))
        self.sm.add_widget(JournalScreen(name='journal_screen'))
        self.sm.add_widget(TransactionScreen(name='transaction_screen'))

        # 將此行更改為您希望啟動的畫面
        self.sm.current = 'home'

        # 新增的返回鍵處理邏7
        Window.bind(on_keyboard=self.on_keyboard)

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

    def on_keyboard(self, window, key, *args):
        if key == 27: # keycode 27 是 Android 的返回鍵
            current_screen = self.sm.current
            print(f"監聽到返回鍵，當前畫面: {current_screen}")

            if current_screen == 'home':
                print("在首頁，退出應用程式。")
                self.stop()
                return True

            elif current_screen in ['journal_screen', 'camera_screen', 'transaction_screen']:
                print(f"從 {current_screen} 返回 Home。")
                self.sm.current = 'home'
                return True

        return False

    # 方便其他螢幕調用的方法
    def go_to_home_screen(self):
        self.sm.current = 'home'

    def go_to_transaction_screen(self):
        self.sm.current = 'transaction_screen'

    def go_to_camera_screen(self):
        self.sm.current = 'camera_screen'

    def go_to_journal_screen(self):
        self.sm.current = 'journal_screen'


if __name__ == '__main__':
    MainApp().run()