# main.py

from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
import os
from kivy.core.text import LabelBase # 引入 LabelBase 以註冊字體
import kivymd # 引入 kivymd 以便獲取其安裝路徑

# 引入所有畫面
from screens.home_screen import HomeScreen
from screens.camera_screen import CameraScreen
from screens.journal_screen import JournalScreen # 導入 JournalScreen
from screens.transaction_screen import TransactionScreen # 導入 TransactionScreen

class MainApp(MDApp):
    dialog = None # 用於彈出視窗

    def build(self):
        # 設置應用程式主題
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"

        # --- 全局字體路徑配置 ---
        # 獲取應用程式根目錄 (main.py 所在目錄)
        app_root_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 中文字體路徑
        chinese_font_name = "NotoSansCJK"
        chinese_font_path = os.path.join(app_root_dir, 'fonts', 'NotoSansCJK-Regular.ttf')

        # KivyMD 內建 Material Design Icons 字體路徑
        # 這裡假設 kivymd-icon.ttf 在 kivymd 模組的 fonts 資料夾下
        kivymd_icons_font_path = os.path.join(
            os.path.dirname(kivymd.__file__), 'fonts', 'kivymd-icon.ttf'
        )

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
        home_kv_path = os.path.join(app_root_dir, 'kv', 'home_screen.kv')
        print(f"嘗試從路徑加載 KV 檔案: {home_kv_path}")
        if not os.path.exists(home_kv_path):
            print(f"錯誤：KV 檔案不存在於此路徑: {home_kv_path}")
            print("請確保 'home_screen.kv' 存在於 'kv/' 資料夾中。")
            import sys
            sys.exit(1)
        Builder.load_file(home_kv_path)
        print(f"KV 檔案 '{home_kv_path}' 已加載。")

        camera_kv_path = os.path.join(app_root_dir, 'kv', 'camera_screen.kv')
        print(f"嘗試從路徑加載 KV 檔案: {camera_kv_path}")
        if not os.path.exists(camera_kv_path):
            print(f"錯誤：KV 檔案不存在於此路徑: {camera_kv_path}")
            print("請確保 'camera_screen.kv' 存在於 'kv/' 資料夾中。")
            import sys
            sys.exit(1)
        Builder.load_file(camera_kv_path)
        print(f"KV 檔案 '{camera_kv_path}' 已加載。")
        
        # 載入 journal_screen.kv (已取消註銷)
        journal_kv_path = os.path.join(app_root_dir, 'kv', 'journal_screen.kv')
        print(f"嘗試從路徑加載 KV 檔案: {journal_kv_path}")
        if not os.path.exists(journal_kv_path):
            print(f"警告：KV 檔案不存在於此路徑: {journal_kv_path}。 journal_screen 將不包含 .kv 定義。")
            pass
        else:
            Builder.load_file(journal_kv_path)
            print(f"KV 檔案 '{journal_kv_path}' 已加載。")

        # 載入 transaction_screen.kv (已取消註銷)
        transaction_kv_path = os.path.join(app_root_dir, 'kv', 'transaction_screen.kv')
        print(f"嘗試從路徑加載 KV 檔案: {transaction_kv_path}")
        if not os.path.exists(transaction_kv_path):
            print(f"錯誤：KV 檔案不存在於此路徑: {transaction_kv_path}")
            print("請確保 'transaction_screen.kv' 存在於 'kv/' 資料夾中。")
            import sys
            sys.exit(1)
        Builder.load_file(transaction_kv_path)
        print(f"KV 檔案 '{transaction_kv_path}' 已加載。")

        # --- 配置 ScreenManager ---
        self.sm = ScreenManager()
        self.sm.add_widget(HomeScreen(name='home'))
        self.sm.add_widget(CameraScreen(name='camera_screen'))
        self.sm.add_widget(JournalScreen(name='journal_screen')) # 添加 JournalScreen
        self.sm.add_widget(TransactionScreen(name='transaction_screen')) # 添加 TransactionScreen

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
                    ),
                ],
            )
        else:
            self.dialog.text = text
        self.dialog.open()

    def close_dialog(self, obj):
        self.dialog.dismiss()


if __name__ == '__main__':
    MainApp().run()