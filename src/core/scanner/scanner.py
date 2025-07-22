from .image_pipeline import ImgProcess
from .qrcode_scanner import Qscanner
from company_id import CompanyID

img_preprocess = ImgProcess()
qrscanner = Qscanner()

class ScanResult:
    post_process = None
    receipt_info = None
    business_info = None

    def is_success(self):
        return bool(self.receipt_info)

class Scanner:
    def scan(self, frame):
        result = ScanResult()
        
        post_processes = img_preprocess(frame, 2)
        if len(post_processes) < 1: return result
        result.post_process = post_processes[0]

        if result.post_process.label_name == "elec":
            result.receipt_info = qrscanner(result.post_process.image)
        else:
            # TODO: Traditional receipt, handwritten receipt
            pass

        if bool(result.receipt_info):
            result.business_info = CompanyID.ban_lookup(
                result.receipt_info.seller_identifier
            )
        
        return result
