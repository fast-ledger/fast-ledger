from scanner.image_pipeline import ImgProcess, P_Result
from scanner.qrcode_scanner import Qscanner, ScanResult
from company_id import CompanyID

img_preprocess = ImgProcess()
qrscanner = Qscanner()


class Scan_Result:
    post_process: P_Result = None
    receipt_info: ScanResult = None
    business_info = None

    def is_success(self):
        return bool(self.receipt_info)


class Scanner:
    def scan(self, frame):
        result = Scan_Result()

        post_processes = img_preprocess(frame, 2)
        if len(post_processes) < 1:
            return result
        result.post_process = post_processes[0]

        if result.post_process.label_name == "elec":
            result.receipt_info = qrscanner(result.post_process.image)
        else:
            # TODO: Traditional receipt, handwritten receipt
            pass

        if result.is_success():
            result.business_info = CompanyID.ban_lookup(
                result.receipt_info.seller_identifier
            )

        return result
