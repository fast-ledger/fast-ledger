from scanner import Scanner
from company_id import CompanyID
from recommender import Recommender

class Core:
    _instance = None
    scanner = Scanner()
    business_lookup = CompanyID
    recommender = Recommender()
    _template_name = None
    _journal_loaded = False
    
    # Singleton
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def set_template(self, template_name):
        """Load template, and re-fit recommender when user journal is loaded"""
        self._template_name = template_name
        if self._journal_loaded:
            self.recommender.load_journal(self._template_name)

    # TODO: actually load user's journal
    def load_journal(self):
        """Load user journal, and fit recommender"""
        self._journal_loaded = True
        self.recommender.load_journal(self._template_name)

core = Core()