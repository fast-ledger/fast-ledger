# screens/camera_screen.py
from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.clock import Clock # 用於延遲執行
import os # 用於文件路徑操作
import time # 用於時間戳命名文件

class CameraScreen(MDScreen):
    """
    相機功能頁面
    """
    def __init__(self, **kw):
        super().__init__(**kw)
        print("CameraScreen initialized")
        # 確保在畫面進入時啟用相機，離開時停用
        self.bind(on_enter=self.start_camera, on_leave=self.stop_camera)

    def start_camera(self, *args):
        """在畫面進入時啟動相機預覽"""
        print("Starting camera...")
        # 獲取 kv 檔案中定義的 Camera 元件
        camera = self.ids.camera_preview
        if camera:
            camera.play = True # 設置 play 為 True 啟用相機

    def stop_camera(self, *args):
        """在畫面離開時停止相機預覽"""
        print("Stopping camera...")
        camera = self.ids.camera_preview
        if camera:
            camera.play = False # 設置 play 為 False 停用相機

    def capture_photo(self):
        """捕獲相機照片"""
        camera = self.ids.camera_preview
        if camera:
            # 創建一個目錄來保存照片（如果不存在）
            output_dir = "captured_photos"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # 生成一個帶時間戳的檔案名
            timestr = time.strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(output_dir, f"IMG_{timestr}.png")

            # 捕獲照片並保存
            # Kivy 的 Camera.export_to_png() 會將當前幀保存為圖片
            try:
                camera.export_to_png(filename)
                print(f"照片已保存到: {filename}")
                # 可以在這裡添加一個彈出訊息或通知用戶
                self.show_capture_success_dialog(filename)
            except Exception as e:
                print(f"保存照片失敗: {e}")
                self.show_capture_error_dialog(str(e))
        else:
            print("未找到相機元件。")

    def show_capture_success_dialog(self, filename):
        """顯示捕獲成功的彈窗"""
        app = App.get_running_app() # 獲取 App 實例
        app.show_alert_dialog(f"照片已成功保存到:\n{os.path.basename(filename)}")

    def show_capture_error_dialog(self, error_message):
        """顯示捕獲失敗的彈窗"""
        app = App.get_running_app() # 獲取 App 實例
        app.show_alert_dialog(f"保存照片失敗:\n{error_message}")

# 由於我們在 main.py 中 Builder.load_file，這裡不再需要 Builder.load_string 或 Builder.load_file
# 如果你希望這個單獨檔案可以獨立預覽，可以保留以下註釋掉的程式碼
# class TestApp(MDApp):
#     def build(self):
#         return Builder.load_string(
#             """
# ScreenManager:
#     CameraScreen:
# """
#         )
# if __name__ == '__main__':
#     TestApp().run()