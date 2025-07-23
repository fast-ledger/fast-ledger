from threading import Thread
import textwrap
import cv2

from kivy.graphics.texture import Texture
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.clock import Clock
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.gridlayout import MDGridLayout

from core import core

Window.size = (800, 480)
Window.resizable = False

Builder.load_file("demo.kv")

class TextLabel(MDLabel):
    pass

# fmt: off
class TechDemoRoot(MDGridLayout):
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

        core.set_template("standard zh-TW")
        core.load_journal()  # TODO: load user journal

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
        """Send image to core, and display result"""
        self.should_reset(10)
        result = core.scanner.scan(frame)
        if result.is_success():
            self.__scan_miss = 0
            recommend_accounts = core.recommender.suggest_receipt(result)

            # Print to console
            result.receipt_info.print_invoice_info()
            print(recommend_accounts)

            # Display
            self.set_receipt_info(result.receipt_info)
            Clock.schedule_once(
                lambda x: self.set_item_info(
                    result.receipt_info,
                    recommend_accounts
                )
            )
            self.set_business_info(result.business_info)

    def should_reset(self, space: int):
        if self.__scan_miss > space:
            print('reset')
            Clock.schedule_once(self.reset)
            self.__scan_miss = 0
        self.__scan_miss += 1

    def reset(self, dt=None):
        self.ids.receipt_info_label.text = self.receipt_info_format()
        self.set_business_info()
        self.reset_items()
        
    def reset_items(self):
        self.ids.col_right.clear_widgets()

    def set_receipt_info(self, scan_result):
        if scan_result is not None and scan_result.invoice_number != '':
            self.ids.receipt_info_label.text = self.receipt_info_format(
                scan_result.invoice_number,
                scan_result.invoice_date,
                scan_result.invoice_time,
                scan_result.random_number,
                scan_result.seller_identifier,
                scan_result.buyer_identifier,
                scan_result.note,
            )

    def receipt_info_format(
            self,
            receipt_number="AA00000000",
            receipt_date="0000000",
            receipt_time="00:00:00",
            seller_ban="00000000",
            buyer_ban="00000000",
            random_number="0000",
            note="**********",
        ):
        return textwrap.dedent(f"""\
            {'發票號碼：'}{receipt_number}
            {'日　　期：'}{receipt_date}
            {'時　　間：'}{receipt_time}
            {'賣方統編：'}{seller_ban}
            {'買方統編：'}{buyer_ban}
            {'　隨機碼：'}{random_number}
            {'備　　註：'}{note}
        """)

    def set_item_info(self, scan_result, recommend_accounts):
        for (item, account) in zip(scan_result.item, recommend_accounts):
            name = item.get('name')
            if name != '' and name is not None:
                self.reset_items()
                break
        
        for item in scan_result.item:
            item = self.Item(item)
            if item.is_valid():
                label = TextLabel(text=textwrap.dedent(f"""\
                    商品：{item.name}
                    數量：{item.quantity}　單價：{item.unit_price}　總價：{item.subtotal}
                    建議科目：{account}"""))
                self.ids.col_right.add_widget(label)
    
    def set_business_info(
            self, 
            business_info={'business_name': "", 'business_scope': []}
        ):
        scope_newline = '\n　　　　　　'
        self.ids.business_info_label.text = f"""\
營業人名稱：{business_info['business_name']}
行　　　業：{scope_newline.join(business_info['business_scope'])}"""
    
    def on_stop(self):
        self.capture.release()
# fmt: on

class TechDemoApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        LabelBase.register(
            "NotoSansCJK",
            fn_regular="src/ui/fonts/NotoSansCJK-Regular.ttf",
        )
        return TechDemoRoot()

if __name__ == "__main__":
    TechDemoApp().run()
