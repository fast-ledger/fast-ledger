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

Window.size = (1024, 640)
Window.resizable = False

Builder.load_file("demo.kv")

class TextLabel(MDLabel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = (0, 0, 0, 1)
        self.font_name = "src/ui/fonts/NotoSansCJK-Regular.ttf"
        self.font_size = 20

# fmt: off
class TechDemoRoot(MDGridLayout):
    process = ImgProcess()
    scanner = Qscanner()
    process_thread = Thread()

    __elapsed_time = 0
    __run_times = 0

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

        invs_info_label = TextLabel(pos=(20, -200), text="")

        self.ids.col_left.add_widget(invs_info_label)

        capture = cv2.VideoCapture(0)
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        Clock.schedule_interval(self.update, 1.0 / 90.0)
        Clock.schedule_interval(self.processing, 1.0 / 90.0)

        self.capture = capture
        self.invs_info_label = invs_info_label

        self.reset()

    def reset(self, dt=None):
        self.scan_result = None

        self.invoice_number = "AA00000000"
        self.invoice_date = "0000000"
        self.seller_identifier = "00000000"
        self.buyer_identifier = "00000000"
        self.random_number = "0000"
        self.note = "**********"

        self.items = []
        self.reset_items()
        
    def reset_items(self):
        self.ids.col_right.clear_widgets()
        
    def update(self, dt):
        ret, frame = self.capture.read()
        if ret:
            self.set_capture_image(frame, (576, 324), 1)
        self.set_receipt_info()

    def processing(self, dt):
        ret, frame = self.capture.read()
        self.__elapsed_time += dt
        if ret:
            thread = Thread(target=self.frame_process, args=(frame, ))
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
        
    def set_capture_image(self, img, size: tuple = (0, 0), scale_ratio: float | int = 1):
        img = cv2.resize(img, size, fx=scale_ratio, fy=scale_ratio)
        buf = cv2.flip(img, -1).tobytes()
        shape = img.shape
        texture = Texture.create(size=(shape[1], shape[0]), colorfmt="bgr")
        texture.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
        self.ids.capture_image.texture = texture
        
    def frame_process(self, frame):
        self.should_reset(10)
        result_list = self.process(frame, 2)
        for result in result_list:
            if result.label_name != "elec":
                continue
            self.__run_times = 0
            scan_result = self.scanner(result.image)
            scan_result.print_invoice_info()

            self.scan_result = scan_result

    def set_receipt_info(self):
        scan_result = self.scan_result
        if scan_result is not None and scan_result.invoice_number != '':
            self.set_item_info()
            self.invoice_number = scan_result.invoice_number
            self.invoice_date = scan_result.invoice_date
            self.random_number = scan_result.random_number
            self.seller_identifier = scan_result.seller_identifier
            self.buyer_identifier = scan_result.buyer_identifier
            self.note = scan_result.note
        
        invs_info_text = self.receipt_info_format()
        self.invs_info_label.text = invs_info_text

    def receipt_info_format(self, text_head_bytes=6, text_body_bytes=15):
        return textwrap.dedent(f"""\
            {'發票號碼:': <{text_head_bytes}}{self.invoice_number: <{text_body_bytes}}
            {'發票日期:': <{text_head_bytes}}{self.invoice_date: <{text_body_bytes}}
            {'賣方統編:': <{text_head_bytes}}{self.seller_identifier: <{text_body_bytes}}
            {'買方統編:': <{text_head_bytes}}{self.buyer_identifier: <{text_body_bytes}}
            {'隨機碼:': <{text_head_bytes}}{self.random_number: <{text_body_bytes}}
            {'Note:': <{text_head_bytes}}{self.note: <{text_body_bytes}}
        """)

    def set_item_info(self, text_head_bytes=5, text_body_bytes=10):
        for item in self.scan_result.item:
            name = item.get('name')
            if  name != '' and name is not None:
                self.reset_items()
                break
        
        self.items.clear()

        for item in self.scan_result.item:
            item = self.Item(item)
            if item.is_valid():
                self.items.append(item)
                label = TextLabel(text=textwrap.dedent(f"""\
                    {"商品:": <{text_head_bytes}}{item.name}
                    {"數量:": <{text_head_bytes}}{item.quantity: <{text_body_bytes}}
                    {"金額:": <{text_head_bytes}}{item.unit_price: <{text_body_bytes}}
                    {"總金額:": <{text_head_bytes}}{item.subtotal: <{text_body_bytes}}
                """))
                self.ids.col_right.add_widget(label)

    def should_reset(self, space:int):
        if self.__run_times > space:
            print('reset')
            Clock.schedule_once(self.reset)
            self.__run_times = 0
        self.__run_times += 1
    
    def on_stop(self):
        self.capture.release()
# fmt: on

class TechDemoApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        return TechDemoRoot()

if __name__ == "__main__":
    TechDemoApp().run()
