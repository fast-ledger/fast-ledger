from image_pipeline import ImgProcess
from qrcode_scanner import Qscanner
from threading import Thread
import math
import cv2

from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.graphics.texture import Texture
from kivymd.uix.label import MDLabel
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.clock import Clock
from kivymd.app import MDApp


Window.size = (1024, 640)
Window.resizable = False


class MyLabel(MDLabel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = (0, 0, 0, 1)
        self.font_name = "src/ui/fonts/NotoSansCJK-Regular.ttf"
        self.font_size = 20


class CameraApp(MDApp):
    count = 0
    process = ImgProcess()
    scanner = Qscanner()
    p = Thread()

    __elapsed_time = 0
    q_result = None
    process_times = 0

    test_image = cv2.imread("src/core/qrcode_scanner/receipt/Receipt_2.jpg")

    invoice_number = "AA00000000"
    invoice_date = "0000000"
    seller_identifier = "00000000"
    buyer_identifier = "00000000"
    random_number = "0000"
    note = "**********"

    item_label_list = []
    item_name = ""
    item_amount = ""
    item_price = ""
    item_total = ""

    def build(self):
        mainLayout = MDGridLayout(cols=2, rows=1)
        s_layout = MDBoxLayout(orientation="vertical")
        f_layout = MDFloatLayout()

        self.img = Image(pos=(0, 200))
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
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        Clock.schedule_interval(self.update, 1.0 / 90.0)
        Clock.schedule_interval(self.counter, 1.0 / 90.0)
        return self.mainLayout

    def counter(self, dt):
        ret, frame = self.capture.read()
        self.__elapsed_time += dt
        self.process_times += dt
        if ret:
            if self.__elapsed_time > 0.5:
                self.__elapsed_time = 0

            if self.__elapsed_time == 0:
                if self.p.is_alive():
                    self.__elapsed_time = 1 - dt
                else:
                    self.p = Thread(target=self.invoice_process, args=(frame,))
                    self.p.start()

    def update(self, dt):
        ret, frame = self.capture.read()
        if ret:
            cv2.imwrite("src/app/pictures/frame.png", frame)
            self.img.texture = self.to_texture(frame, (576, 324), 1)

        self.setLabel_text()

    def on_stop(self):
        self.capture.release()

    def invoice_process(self, frame):
        self.process.set_saving_directory("src/app/picture")
        results = self.process(frame, 0.3, save_result=False)
        for result in results:
            if result.label_name == "elec":
                self.q_result = self.scanner(result.image)
                self.q_result.print_invoice_info()
        # self.q_result = self.scanner(frame)
        # self.q_result.print_invoice_info()

    def to_texture(self, img, size: tuple = (0, 0), scale_ratio: float | int = 0.8):
        img = cv2.resize(img, size, fx=scale_ratio, fy=scale_ratio)
        buf = cv2.flip(img, -1).tobytes()
        texture = Texture.create(size=(img.shape[1], img.shape[0]), colorfmt="bgr")
        texture.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
        return texture

    def setLabel_text(self):
        if self.q_result is not None:
            if self.q_result.invoice_number != "":
                self.invoice_number = self.q_result.invoice_number
                self.invoice_date = self.q_result.invoice_date
                self.seller_identifier = self.q_result.seller_identifier
                self.buyer_identifier = self.q_result.buyer_identifier
                self.random_number = self.q_result.random_number
                self.note = self.q_result.note

                for item in self.q_result.item:
                    if item.get("name") != "":
                        for label in self.item_label_list:
                            self.s_layout.remove_widget(label)
                        break

                for i, item in enumerate(self.q_result.item):
                    if item.get("name") != "":
                        self.item_name = item.get("name")
                        self.item_amount = item.get("amount")
                        self.item_price = item.get("price")
                        self.item_total = item.get("total")

                        item_text = f"""
{"商品:": <5}{self.item_name}
{"數量:": <5}{self.item_amount: <10}
{"金額:": <5}{self.item_price: <10}
{"總金額:": <5}{self.item_total: <10}"""
                        label = MyLabel(text=item_text)
                        self.s_layout.add_widget(label)
                        self.item_label_list.append(label)

        text = f"""
{"發票號碼:": <6}{self.invoice_number: <15}
{"發票日期:": <6}{self.invoice_date: <15}
{"賣方統編:": <6}{self.seller_identifier: <15}
{"買方統編:": <6}{self.buyer_identifier: <15}
{"隨機碼:": <6}{self.random_number: <15}
{"Note:": <6}{self.note: <15}
"""
        self.label.text = text


CameraApp().run()
