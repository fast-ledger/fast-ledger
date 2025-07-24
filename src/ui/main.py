# main.py

from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
import os
from kivy.core.text import LabelBase  # 引入 LabelBase 以註冊字體
import kivymd  # 引入 kivymd 以便獲取其安裝路徑

# 引入所有畫面
from ui.screens import (
    HomeScreen,
    CameraScreen,
    JournalScreen,
)  # ***修正: 新增導入 JournalScreen***


class MainApp(MDApp):
    dialog = None  # 用於彈出視窗

    def build(self):
        # 設置應用程式主題
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"

        # --- 全局字體路徑配置 ---
        # 獲取應用程式根目錄 (main.py 所在目錄)
        app_root_dir = os.path.dirname(os.path.abspath(__file__))

        # 中文字體路徑
        chinese_font_name = "NotoSansCJK"
        chinese_font_path = os.path.join(
            app_root_dir, "fonts", "NotoSansCJK-Regular.ttf"
        )

        # KivyMD 內建 Material Design Icons 字體路徑
        kivymd_icons_font_path = os.path.join(
            os.path.dirname(kivymd.__file__), "fonts", "kivymd-icon.ttf"
        )

        # ===================================================================
        # START: CHINESE FONT LOADING AND CONFIGURATION
        # ===================================================================
        print(f"嘗試通過 LabelBase 註冊中文字體: {chinese_font_path}")
        if not os.path.exists(chinese_font_path):
            print(f"錯誤：中文字體檔案不存在於此路徑: {chinese_font_path}")
            print("請確保 'NotoSansCJK-Regular.ttf' 存在於 'ui/fonts/' 資料夾中。")
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

        # 定義 KivyMD 中常用於顯示 "文字" 的字體樣式
        text_font_styles = [
            "H1",
            "H2",
            "H3",
            "H4",
            "H5",
            "H6",
            "Subtitle1",
            "Subtitle2",
            "Body1",
            "Body2",
            "Button",
            "Caption",
            "Overline",
        ]

        # 遍歷並應用中文字體到這些特定的文字樣式
        for style in text_font_styles:
            if style in self.theme_cls.font_styles:
                self.theme_cls.font_styles[style][0] = chinese_font_name
        print("中文字體已應用到 KivyMD 的文字樣式。")
        # ===================================================================
        # END: CHINESE FONT LOADING AND CONFIGURATION
        # ===================================================================

        # ===================================================================
        # START: KIVYMD ICONS FONT LOADING
        # ===================================================================
        print(f"嘗試通過 LabelBase 註冊 KivyMD 圖示字體: {kivymd_icons_font_path}")
        if not os.path.exists(kivymd_icons_font_path):
            print(
                f"警告：KivyMD 圖示字體檔案不存在於此路徑: {kivymd_icons_font_path}。圖示可能仍會缺失。"
            )
            print("請確保 'kivymd-icon.ttf' 存在於 KivyMD 的安裝目錄下。")
        else:
            try:
                LabelBase.register(
                    name="Icons",
                    fn_regular=kivymd_icons_font_path,
                )
                print(
                    f"KivyMD 圖示字體 '{kivymd_icons_font_path}' 已在應用啟動前通過 LabelBase 成功註冊為 'Icons'."
                )
            except Exception as e:
                print(f"KivyMD 圖示字體通過 LabelBase 註冊失敗或已註冊: {e}")
                pass
        # ===================================================================
        # END: KIVYMD ICONS FONT LOADING
        # ===================================================================

        # 使用 os.path.join 構建絕對路徑來加載 .kv 文件
        # 加載 home_screen.kv
        home_kv_path = os.path.join(app_root_dir, "kv", "home_screen.kv")
        print(f"嘗試從路徑加載 KV 檔案: {home_kv_path}")
        if not os.path.exists(home_kv_path):
            print(f"錯誤：KV 檔案不存在於此路徑: {home_kv_path}")
            print("請確保 'home_screen.kv' 存在於 'kv/' 資料夾中。")
            import sys

            sys.exit(1)
        Builder.load_file(home_kv_path)
        print(f"KV 檔案 '{home_kv_path}' 已加載。")

        # 加載 camera_screen.kv
        camera_kv_path = os.path.join(app_root_dir, "kv", "camera_screen.kv")
        print(f"嘗試從路徑加載 KV 檔案: {camera_kv_path}")
        if not os.path.exists(camera_kv_path):
            print(f"錯誤：KV 檔案不存在於此路徑: {camera_kv_path}")
            print("請確保 'camera_screen.kv' 存在於 'kv/' 資料夾中。")
            import sys

            sys.exit(1)
        Builder.load_file(camera_kv_path)
        print(f"KV 檔案 '{camera_kv_path}' 已加載。")

        # ***修正: 新增載入 journal_screen.kv***
        journal_kv_path = os.path.join(app_root_dir, "kv", "journal_screen.kv")
        print(f"嘗試從路徑加載 KV 檔案: {journal_kv_path}")
        if not os.path.exists(journal_kv_path):
            print(f"錯誤：KV 檔案不存在於此路ih: {journal_kv_path}")
            print("請確保 'journal_screen.kv' 存在於 'kv/' 資料夾中。")
            import sys

            sys.exit(1)
        Builder.load_file(journal_kv_path)
        print(f"KV 檔案 '{journal_kv_path}' 已加載。")

        self.sm = ScreenManager()
        # ***修正: 將 HomeScreen 的名稱改為 'home_screen' 以與 home_screen.py 內部邏輯一致***
        self.sm.add_widget(HomeScreen(name="home_screen"))
        self.sm.add_widget(CameraScreen(name="camera_screen"))
        # ***修正: 新增將 JournalScreen 添加到 ScreenManager***
        self.sm.add_widget(JournalScreen(name="journal_screen"))

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
                    MDFlatButton(text="OK", on_release=self.close_dialog),
                ],
            )
        else:
            self.dialog.text = text
        self.dialog.open()

    def close_dialog(self, obj):
        self.dialog.dismiss()


if __name__ == "__main__":
    MainApp().run()
