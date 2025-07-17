from image_pipeline import ImgProcess
from qrcode_scanner import Qscanner
from kivymd.app import MDApp
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.stacklayout import MDStackLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.image import Image
from kivymd.uix.label import MDLabel
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.core.window import Window
from threading import Thread
import math
import cv2

Window.size = (1024, 640)
Window.resizable = False


class MyLabel(MDLabel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = (0, 0, 0, 1)
        self.font_name = "src/ui/fonts/NotoSansCJK-Regular.ttf"
        self.font_size = 20


class CameraApp(MDApp):
    process = ImgProcess()
    scanner = Qscanner()
    p = Thread()

    __elapsed_time = 0
    q_result = None
    process_times = 0

    test_image = cv2.imread("src/core/qrcode_scanner/receipt/Receipt_2.jpg")

    item_label_list = []

    def build(self):
        mainLayout = MDGridLayout(cols=2, rows=1)
        s_layout = MDBoxLayout(orientation="vertical")
        f_layout = MDFloatLayout()
        self.img = Image(pos=(-50, 200))
        self.label = MyLabel(
            pos=(20, -200),
            text="",
        )

        f_layout.add_widget(self.img)
        f_layout.add_widget(self.label)
        mainLayout.add_widget(f_layout)
        mainLayout.add_widget(s_layout)
        self.f_layout = f_layout
        self.s_layout = s_layout
        self.mainLayout = mainLayout

        self.capture = cv2.VideoCapture(0)
        Clock.schedule_interval(self.update, 1.0 / 90.0)
        return self.mainLayout

    def update(self, dt):
        ret, frame = self.capture.read()
        self.input_img = self.test_image

        if ret:
            frame = cv2.resize(frame, (0, 0), fx=0.8, fy=0.8)
            buf = cv2.flip(frame, -1).tobytes()
            texture = Texture.create(
                size=(frame.shape[1], frame.shape[0]), colorfmt="bgr"
            )
            texture.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
            self.img.texture = texture

        self.setLabel_text()

        self.__elapsed_time += dt

        if self.__elapsed_time > 0.5:
            self.__elapsed_time = 0

        if self.__elapsed_time == 0:
            if self.p.is_alive():
                self.__elapsed_time = 1 - dt
            else:
                self.p = Thread(target=self.invoice_process, args=(self.test_image,))
                self.p.start()

    def on_stop(self):
        self.capture.release()

    def invoice_process(self, frame):
        self.process_times += 1

        if self.process_times >= 2:
            self.process_times = 0
            self.q_result = None

        results = self.process(frame, scale_ratio=1.5)
        for result in results:
            if result.label_name == "elec":
                self.process_times = 0
                self.q_result = self.scanner(result.image)
                self.q_result.print_invoice_info()

    def setLabel_text(self):
        invoice_number = "AA00000000"
        invoice_date = "0000000"
        seller_identifier = "00000000"
        buyer_identifier = "00000000"
        randan_number = "0000"
        note = "**********"

        item_name = ""
        item_amount = ""
        item_price = ""
        item_total = ""

        for label in self.item_label_list:
            self.s_layout.remove_widget(label)

        if self.q_result is not None:
            invoice_number = self.q_result.invoice_number
            invoice_date = self.q_result.invoice_date
            seller_identifier = self.q_result.seller_identifier
            buyer_identifier = self.q_result.buyer_identifier
            randan_number = self.q_result.randan_number
            note = self.q_result.note

            for i, item in enumerate(self.q_result.item):
                item_name = item.get("name")
                item_amount = item.get("amount")
                item_price = item.get("price")
                item_total = item.get("total")

                item_text = f"""
{"商品:": <5}{item_name}
{"數量:": <5}{item_amount: <10}
{"金額:": <5}{item_price: <10}
{"總金額:": <5}{item_total: <10}"""
                label = MyLabel(text=item_text)
                self.s_layout.add_widget(label)
                self.item_label_list.append(label)

        text = f"""
{"發票號碼:": <6}{invoice_number: <15}
{"發票日期:": <6}{invoice_date: <15}
{"賣方統編:": <6}{seller_identifier: <15}
{"買方統編:": <6}{buyer_identifier: <15}
{"隨機碼:": <6}{randan_number: <15}
{"Note:": <6}{note: <15}
"""
        self.label.text = text


CameraApp().run()
