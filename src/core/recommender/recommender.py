from datetime import datetime
import re
import pandas as pd
from .datasets import fetch_dataset
from .predictor import Predictor

class Recommender:
    _instance = None
    _predictor = Predictor()

    # Singleton
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    # TODO: load user journal after ledger module is completed
    def load_journal(
            self,
            template_name,
            # journal # User journal
        ):
        postings_dummy = None
        postings_user = None

        postings = fetch_dataset().frame
        if template_name in postings.columns:
            postings_dummy = postings[
                postings[template_name].notnull()
            ].reset_index()
        
        # TODO: load user journal

        # Combine template and user postings to create training data
        if postings_dummy is not None:
            X = postings_dummy
            y = postings_dummy[template_name]
        
        # Train predictor
        self._predictor.fit(X, y)

    def suggest_receipt(self, scan_result):
        if not scan_result: return []
        if len(scan_result.receipt_info.item) < 1: return []

        business_name = scan_result.business_info['business_name']
        scopes = scan_result.business_info['business_scope']
        scope_1 = scopes[0] if 0 < len(scopes) else None
        scope_2 = scopes[1] if 1 < len(scopes) else None
        scope_3 = scopes[2] if 2 < len(scopes) else None
        scope_4 = scopes[3] if 3 < len(scopes) else None
        ban = scan_result.receipt_info.seller_identifier
        date_match = re.match(
            r'(\d{3})(\d{2})(\d{2})',
            scan_result.receipt_info.invoice_date
        )
        time_match = re.match(
            r'(\d{2}):(\d{2}):(\d{2})',
            scan_result.receipt_info.invoice_time
        )
        dt = datetime(
            int(date_match.group(1)) + 1911,
            int(date_match.group(2)),
            int(date_match.group(3)),
            int(time_match.group(1)) if bool(time_match) else 0,
            int(time_match.group(2)) if bool(time_match) else 0,
            int(time_match.group(3)) if bool(time_match) else 0,
        )
        X = pd.DataFrame(columns=[
            'business_name',
            'scope_1',
            'scope_2',
            'scope_3',
            'scope_4',
            'ban',
            'datetime',
            'item',
            'subtotal',
        ])

        for item in scan_result.receipt_info.item:
            scopes = scan_result.business_info['business_scope']
            X.loc[len(X)] = [
                business_name,
                scope_1,
                scope_2,
                scope_3,
                scope_4,
                ban,
                dt.strftime("%Y/%m/%d %H:%M"),
                item['name'],
                item['total'],
            ]
        
        return self._predictor.predict(X)

    def suggest_item():
        pass

    def suggest_fuzzy():
        pass