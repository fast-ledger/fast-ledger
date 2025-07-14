class Q_result:
    def __init__(self, **kwds):
        self.invoice_number = kwds.get("i_number")
        self.randan_number = kwds.get("r_number")
        self.seller_identifier = kwds.get("s_id")
        self.buyer_identifier = kwds.get("b_id")
        self.invoice_date = kwds.get("date")
        self.qrcode = kwds.get("qrcode")
        self.note = kwds.get("note")
        self.item = kwds.get("item")

    def __call__(
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
        return Q_result(
            s_id=s_id,
            b_id=b_id,
            i_number=i_number,
            r_number=r_number,
            date=date,
            note=note,
            qrcode=qrcode,
            item=item,
        )

    def print_invoice_info(self):
        # print("=========================================================")
        # for q in self.qrcode:
        #     print(q)
        # print("=========================================================")
        print("=========================================================")
        print("發票號碼:", self.invoice_number)
        print("發票日期:", self.invoice_date)
        print("隨機碼:", self.randan_number)
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
