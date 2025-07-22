from image_pipeline import ImgProcess
from qrcode_scanner import Qscanner
from company_id import CompanyID

class Core:
    img_preprocess = ImgProcess()
    qrscanner = Qscanner()
    business_lookup = CompanyID

core = Core()