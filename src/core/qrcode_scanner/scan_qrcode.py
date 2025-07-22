import os
import re
from image_pipeline import ImgProcess
from pathlib import Path
import numpy as np
import zxingcpp
import cv2

class Q_result:
    def __init__(
        self,
        raw: str="",
        s_id: str="",
        b_id: str="",
        i_number: str="",
        r_number: str="",
        date: str="",
        note: str="",
        item: list[dict]=[],
    ):
        self.raw: str = raw
        self.seller_identifier: str = s_id
        self.buyer_identifier: str = b_id
        self.invoice_number: str = i_number
        self.random_number: str = r_number
        self.invoice_date: str = date
        self.note: str = note
        self.item: list[dict] = item

    def print_invoice_info(self):
        print(self.raw)
        print("發票號碼:", self.invoice_number)
        print("發票日期:", self.invoice_date)
        print("　隨機碼:", self.random_number)
        print("買方統編:", self.buyer_identifier)
        print("賣方統編:", self.seller_identifier)
        print("備　　註:", self.note)
        print("---------------------------------------------------------")
        for item in self.item:
            print("商品:", item["name"])
            print("數量:", item["amount"])
            print("單價:", item["price"])
            print("總價:", item["total"])

# fmt: off
class Qscanner:
    raw = []
    item = []

    def __init__(self):
        self.seller_identifier = ""
        self.buyer_identifier = ""
        self.invoice_number = ""
        self.random_number = ""
        self.invoice_date = ""
        self.note = ""

        self.raw = ""
        self.item = []

    def __call__(self, src: Path | str | np.ndarray, debug=False) -> Q_result:
        self.__init__()

        src = ImgProcess.get_src(ImgProcess, src, True)
        if isinstance(src, (str | Path)):
            src = cv2.imread(src)

        gray = cv2.cvtColor(src, cv2.COLOR_RGBA2GRAY)

        reader = zxingcpp.read_barcodes(gray)
        if len(reader) < 2:
            # Failed to detect 2 QRCode
            if len(reader) == 0:
                return Q_result()
            self.raw += reader[0].text  # Try parse single QR Code
        else:
            # Concat contents of 2 QRCodes into self.raw
            if reader[1].text[:2] == "**":
                self.raw = reader[0].text + reader[1].text[2:]
            elif reader[0].text[:2] == "**":
                self.raw = reader[1].text + reader[0].text[2:]
            else:
                # Invalid einvoice QR Code
                return Q_result(reader[0].text + reader[1].text)

        # Parse self.raw
        try:
            self.invoice_number = self.raw[:10]
            self.invoice_date = self.raw[10:17]
            self.random_number = self.raw[17:21]
            # self.raw[21:29] # Grand total in hex
            # self.raw[29:37] # Grand total with tax in hex
            self.buyer_identifier = self.raw[37:45]
            self.seller_identifier = self.raw[45:53]
            # self.raw[53:77] # AES key
            # self.raw[77] # ":"
            btext = self.raw[78:].split(":")
            self.note = btext[0]
            # btext[1] # 左右兩個二維條碼記載消費品目筆數
            # btext[2] # 該張發票記載消費品目總筆數
            # btext[3] # Chinese encoding, 0=Big5; 1=UTF-8; 2=Base64

            for n in range((len(btext) - 4) // 3):
                self.add_item(btext[(4+3*n):(7+3*n)])

        except:
            pass

        # Check format
        if not re.match(r'[A-Z]{2}\d{8}', self.invoice_number):
            self.invoice_number = ""
        if not re.match(r'\d{3}[01]\d[0123]\d', self.invoice_date):
            self.invoice_date = ""
        if not re.match(r'\d{4}', self.random_number):
            self.random_number = ""
        if not re.match(r'\d{8}', self.buyer_identifier):
            self.buyer_identifier = ""
        if not re.match(r'\d{8}', self.seller_identifier):
            self.seller_identifier = ""

        return Q_result(
            self.raw,
            self.seller_identifier,
            self.buyer_identifier,
            self.invoice_number,
            self.random_number,
            self.invoice_date,
            self.note,
            self.item   
        )
                
    def add_item(self, item_info):
        self.item.append({
            "name": item_info[0],
            "amount": int(item_info[1]),
            "price": int(item_info[2]),
            "total": int(item_info[1]) * int(item_info[2])
        })
# fmt: on


if __name__ == "__main__":
    path = Path(__file__).parts
    index = path.index("src")
    path = (
        Path("\\".join(path[: index + 1])) / "core" / "qrcode_scanner" / "receipt" / "*"
    )
    process = ImgProcess()
    scn = Qscanner()

    results = process(path, scale_ratio=2)

    for i, result in enumerate(results):
        print("=========================================================")
        print(os.path.basename(result.path))
        res = scn(result.image)
        res.print_invoice_info()
