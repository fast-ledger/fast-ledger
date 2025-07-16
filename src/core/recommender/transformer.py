"""Strategies to embed a posting"""

import numpy as np
import pandas as pd
import re
import textwrap
from datetime import datetime
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.compose import ColumnTransformer

def row_preprocess(row):
    scopes = [ row['scope_1'], row['scope_2'], row['scope_3'], row['scope_4'] ]
    item = {
        'business_name': row['business_name'],
        'business_scopes': [s for s in scopes if not pd.isnull(s)],
        'datetime': datetime.strptime(row['datetime'], "%Y/%m/%d\xa0%H:%M"),
        'item': row['item'],
        'subtotal': row['subtotal'],
    }
    return item

def company_scope_item(postings):
    """embed(公司名稱行業1行業2行業3行業4商品品項)"""
    return (
        postings[['business_name', 'scope_1', 'scope_2', 'scope_3', 'scope_4', 'item']]
        .fillna('')
        .apply(lambda x: ''.join(x), axis=1))

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
    return postings.apply(item_repr_str, axis=1)

def all_labeled(postings):
    """embed(company: 公司名稱
    business scope: 行業1, 行業2, 行業3, 行業4
    datetime: 時間
    item: 商品品項
    subtotal: 金額)"""
    def item_repr_str(row):
        item_info = row_preprocess(row)
        return textwrap.dedent("""\
                               company: {}
                               business scope: {}
                               datetime: {}
                               item: {}
                               subtotal: {}""".format(
            item_info['business_name'],
            ", ".join(item_info['business_scopes']),
            item_info['datetime'].strftime("%Y/%m/%d %H:%M"),
            item_info['item'],
            item_info['subtotal'],
        ))
    return postings.apply(item_repr_str, axis=1)

def time_extractor(postings):
    def time_extract(row):
        time = re.search(
            r'(\d{4})/(\d{2})/(\d{2})\s(\d{2}):(\d{2})',
            row['datetime'])
        return pd.Series(
            [
                int(time.group(1)),
                int(time.group(2)),
                int(time.group(3)),
                int(time.group(4)),
                int(time.group(5)),
            ],
            index=['year', 'month', 'day', 'hour', 'minute']
        )
    return postings.apply(time_extract, axis=1)

def sin_transformer(period):
    return FunctionTransformer(lambda x: np.sin(x / period * 2 * np.pi))

def cos_transformer(period):
    return FunctionTransformer(lambda x: np.cos(x / period * 2 * np.pi))

time_cyclic_transformer = make_pipeline(
    FunctionTransformer(time_extractor),
    ColumnTransformer([
        ("hour_sin", sin_transformer(24), ["hour"]),
        ("hour_cos", cos_transformer(24), ["hour"]),
    ]),
)