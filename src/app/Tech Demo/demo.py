from qrcode_scanner import Qscanner
from image_pipeline import ImgProcess
from threading import Thread
import textwrap
import cv2

from kivy.graphics.texture import Texture
from kivymd.uix.label import MDLabel
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.gridlayout import MDGridLayout

Window.size = (800, 480)
Window.resizable = False

Builder.load_file("demo.kv")

class DummyCore:
    """Core is the whole backend, not yet packaged, use a dummy for now"""
    img_preprocess = ImgProcess()
    qrscanner = Qscanner()

class TextLabel(MDLabel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = (0, 0, 0, 1)
        self.font_name = "src/ui/fonts/NotoSansCJK-Regular.ttf"
        self.font_size = 20

# fmt: off
class TechDemoRoot(MDGridLayout):
    core = DummyCore()
    process_thread = Thread()

    __elapsed_time = 0
    __scan_miss = 0

    class Item:
        def __init__(self, item):
            self.name = item['name']
            self.quantity = item['amount']
            self.unit_price = item['price']
            self.subtotal = item['total']

        def is_valid(self):
            return not not self.name

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        capture = cv2.VideoCapture(0)
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        Clock.schedule_interval(self.render_image_routine, 1.0 / 90.0)
        Clock.schedule_interval(self.process_image_routine, 1.0 / 90.0)

        self.capture = capture

        self.reset()
        
    def render_image_routine(self, dt):
        ret, frame = self.capture.read()
        if ret:
            self.set_capture_image(frame, (576, 324), 1)
        
    def set_capture_image(self, img, size: tuple = (0, 0), scale_ratio: float | int = 1):
        img = cv2.resize(img, size, fx=scale_ratio, fy=scale_ratio)
        buf = cv2.flip(img, -1).tobytes()
        shape = img.shape
        texture = Texture.create(size=(shape[1], shape[0]), colorfmt="bgr")
        texture.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
        self.ids.capture_image.texture = texture

    def process_image_routine(self, dt):
        ret, frame = self.capture.read()
        self.__elapsed_time += dt
        if ret:
            thread = Thread(target=self.process_image, args=(frame, ))
            self.__elapsed_time = self.do_process_thread(thread, dt, self.__elapsed_time, 0.5)

    def do_process_thread(self, thread: Thread, dt, elapsed_time, space_time):
        if elapsed_time >= space_time:
            elapsed_time = 0

        if elapsed_time == 0:
            if self.process_thread.is_alive():
                return space_time - dt
            else:
                self.process_thread = thread
                self.process_thread.start()
                return 0
            
        return elapsed_time
        
    def process_image(self, frame):
        self.should_reset(10)
        result_list = self.core.img_preprocess(frame, 2)
        for result in result_list:
            if result.label_name != "elec":
                continue
            self.__scan_miss = 0
            scan_result = self.core.qrscanner(result.image)
            scan_result.print_invoice_info()

            self.set_receipt_info(scan_result)

    def should_reset(self, space: int):
        if self.__scan_miss > space:
            print('reset')
            Clock.schedule_once(self.reset)
            self.__scan_miss = 0
        self.__scan_miss += 1

    def reset(self, dt=None):
        self.ids.receipt_info_label.text = self.receipt_info_format()
        self.reset_items()
        
    def reset_items(self):
        self.ids.col_right.clear_widgets()

    def set_receipt_info(self, scan_result):
        if scan_result is not None and scan_result.invoice_number != '':
            self.set_item_info(scan_result)
            self.ids.receipt_info_label.text = self.receipt_info_format(
                scan_result.invoice_number,
                scan_result.invoice_date,
                scan_result.random_number,
                scan_result.seller_identifier,
                scan_result.buyer_identifier,
                scan_result.note,
            )

    def receipt_info_format(
            self,
            receipt_number="AA00000000",
            receipt_date="0000000",
            seller_ban="00000000",
            buyer_ban="00000000",
            random_number="0000",
            note="**********",
            text_head_bytes=6,
            text_body_bytes=15
        ):
        return textwrap.dedent(f"""\
            {'發票號碼:': <{text_head_bytes}}{receipt_number: <{text_body_bytes}}
            {'發票日期:': <{text_head_bytes}}{receipt_date: <{text_body_bytes}}
            {'賣方統編:': <{text_head_bytes}}{seller_ban: <{text_body_bytes}}
            {'買方統編:': <{text_head_bytes}}{buyer_ban: <{text_body_bytes}}
            {'隨機碼:': <{text_head_bytes}}{random_number: <{text_body_bytes}}
            {'Note:': <{text_head_bytes}}{note: <{text_body_bytes}}
        """)

    def set_item_info(self, scan_result, text_head_bytes=5, text_body_bytes=10):
        for item in scan_result.item:
            name = item.get('name')
            if  name != '' and name is not None:
                self.reset_items()
                break
        
        for item in scan_result.item:
            item = self.Item(item)
            if item.is_valid():
                label = TextLabel(text=textwrap.dedent(f"""\
                    {"商品:": <{text_head_bytes}}{item.name}
                    {"數量:": <{text_head_bytes}}{item.quantity: <{text_body_bytes}}
                    {"金額:": <{text_head_bytes}}{item.unit_price: <{text_body_bytes}}
                    {"總金額:": <{text_head_bytes}}{item.subtotal: <{text_body_bytes}}
                """))
                self.ids.col_right.add_widget(label)
    
    def on_stop(self):
        self.capture.release()
# fmt: on

class TechDemoApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        return TechDemoRoot()

if __name__ == "__main__":
    TechDemoApp().run()
