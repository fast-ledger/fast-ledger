"""Strategies to embed a posting"""

import numpy as np
import pandas as pd
import textwrap
from datetime import datetime
from sentence_transformers import SentenceTransformer

language_models = [
    'sentence-transformers/multi-qa-MiniLM-L6-cos-v1',
    'shibing624/text2vec-base-chinese'
]
language_model = language_models[1]
encoder = SentenceTransformer(language_model)

def row_preprocess(row):
    scopes = [ row['行業1'], row['行業2'], row['行業3'], row['行業4'] ]
    item = {
        'business_name': row['公司名稱'],
        'business_scopes': [s for s in scopes if not pd.isnull(s)],
        'datetime': datetime.strptime(row['時間'], "%Y/%m/%d\xa0%H:%M"),
        'item': row['商品品項'],
        'amount': row['金額'],
    }
    return item

def company_scope_item(postings):
    """embed(公司名稱行業1行業2行業3行業4商品品項)"""
    return pd.DataFrame(encoder.encode(
        postings[['公司名稱', '行業1', '行業2', '行業3', '行業4', '商品品項']]
        .fillna('')
        .apply(lambda x: ''.join(x), axis=1)
        .to_list()
    ))

def company_scope_item_labeled(postings):
    """embed(company: 公司名稱
    business scope: 行業1, 行業2, 行業3, 行業4
    item: 商品品項)"""
    def item_repr_str(row):
        item_info = row_preprocess(row)
        return textwrap.dedent("""\
                               company: {}
                               business scope: {}
                               item: {}""".format(
            item_info['business_name'],
            ", ".join(item_info['business_scopes']),
            item_info['item']
        ))
    return pd.DataFrame(encoder.encode(
        postings.apply(item_repr_str, axis=1).to_list()
    ))

def all_labeled(postings):
    """embed(company: 公司名稱
    business scope: 行業1, 行業2, 行業3, 行業4
    datetime: 時間
    item: 商品品項
    amount: 金額)"""
    def item_repr_str(row):
        item_info = row_preprocess(row)
        return textwrap.dedent("""\
                               company: {}
                               business scope: {}
                               datetime: {}
                               item: {}
                               amount: {}""".format(
            item_info['business_name'],
            ", ".join([s for s in item_info['business_scopes'] if not pd.isnull(s)]),
            item_info['datetime'].strftime("%Y/%m/%d %H:%M"),
            item_info['item'],
            item_info['amount'],
        ))
    return pd.DataFrame(encoder.encode(
        postings.apply(item_repr_str, axis=1).to_list()
    ))