from image_pipeline import ImgProcess
from pathlib import Path
import numpy as np
import unicodedata
import zxingcpp
import cv2

class Q_result:
    def __init__(
        self,
        s_id: str,
        b_id: str,
        i_number: str,
        r_number: str,
        date: str,
        note: str,
        qrcode: list[str],
        item: list[dict],
    ):
        self.seller_identifier: str = s_id
        self.buyer_identifier: str = b_id
        self.invoice_number: str = i_number
        self.random_number: str = r_number
        self.invoice_date: str = date
        self.note: str = note
        self.qrcode: list[str] = qrcode
        self.item: list[dict] = item

    def print_invoice_info(self):
        # print("=========================================================")
        # for q in self.qrcode:
        #     print(q)
        # print("=========================================================")
        print("=========================================================")
        print("發票號碼:", self.invoice_number)
        print("發票日期:", self.invoice_date)
        print("隨機碼:", self.random_number)
        print("買方統編:", self.buyer_identifier)
        print("賣方統編:", self.seller_identifier)
        print("Note:", self.note)
        print("=========================================================")
        for item in self.item:
            print("商品:", item["name"])
            print("數量:", item["amount"])
            print("金額:", item["price"])
            print("總金額:", item["total"])
            print("=========================================================")

# fmt: off
class Qscanner:
    qrcode = []
    item = []

    def __init__(self):
        self.seller_identifier = ""
        self.buyer_identifier = ""
        self.invoice_number = ""
        self.random_number = ""
        self.invoice_date = ""
        self.note = ""

        self.qrcode = []
        self.item = []

    def __call__(self, src: Path | str | np.ndarray, debug=False) -> Q_result:
        self.__init__()

        src = ImgProcess.get_src(ImgProcess, src, True)
        if isinstance(src, (str | Path)):
            src = cv2.imread(src)

        gray = cv2.cvtColor(src, cv2.COLOR_RGBA2GRAY)

        reader = zxingcpp.read_barcodes(gray)

        for r in reader:
            text = r.text
            self.qrcode.append(text)

            notChinese = False if 'CJK UNIFIED' in unicodedata.name(text[1], '') else True
            if len(text) > 20 and text[:2] != "**" and notChinese:
                if debug:
                    print(text)
                self.invoice_number = text[:10]
                self.invoice_date = text[10:17]
                self.random_number = text[17:21]

                btext = text[21:]
                btext = btext.split(":")
                btext_0 = btext[0]

                self.buyer_identifier = btext_0[-40:-32]
                self.seller_identifier = btext_0[-32:-24]
                self.note = btext[1]

                if btext[-1] == "":
                    merchandise = btext[5:-1]
                else:
                    merchandise = btext[5:]

                self.save_merchandise_info(merchandise)

            elif not notChinese:
                if debug:
                    print(text)
                self.note = text

            elif text[:2] == "**" and len(text) > 2:
                if debug:
                    print(text)
                text = text[2:].split(":")
                if text[0] == '':
                    text = text[1:]
                self.save_merchandise_info(text)

        return Q_result(
            self.seller_identifier,
            self.buyer_identifier,
            self.invoice_number,
            self.random_number,
            self.invoice_date,
            self.note,
            self.qrcode,
            self.item   
        )
                
    def save_merchandise_info(self, merchandise):
        i = 1

        for t in merchandise:
            if i == 1:
                item_name = t
            elif i == 2:
                item_amount = t
            elif i == 3:
                item_price = t

                try:
                    total = int(item_amount) * int(item_price)
                except Exception as e:
                    total = 0
                    print(e)

                self.item.append({"name": item_name,"amount": item_amount,"price": item_price,"total": total})
                
            i = i + 1 if i < 3 else 1
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
        print(i)
        res = scn(result.image)
        res.print_invoice_info()
