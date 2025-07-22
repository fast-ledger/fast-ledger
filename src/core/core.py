from scanner import Scanner
from company_id import CompanyID

class Core:
    _instance = None
    scanner = Scanner()
    business_lookup = CompanyID
    
    # Singleton
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

core = Core()