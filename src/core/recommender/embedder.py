"""Strategies to embed a posting"""

import numpy as np
import pandas as pd
import textwrap
from sentence_transformers import SentenceTransformer

language_models = [
    'sentence-transformers/multi-qa-MiniLM-L6-cos-v1',
    'shibing624/text2vec-base-chinese'
]
language_model = language_models[1]
encoder = SentenceTransformer(language_model)

def item(postings):
    """embed(商品品項)"""
    return encoder.encode(postings['商品品項'].to_list())

def company_item(postings):
    """embed(公司名稱商品品項)"""
    return encoder.encode((postings['公司名稱'] + postings['商品品項']).to_list())

def company_scope_item(postings):
    """embed(公司名稱行業1行業2行業3行業4商品品項)"""
    return encoder.encode(
        postings[['公司名稱', '行業1', '行業2', '行業3', '行業4', '商品品項']]
        .fillna('')
        .apply(lambda x: ''.join(x), axis=1)
        .to_list()
    )

def company_scope_item_labeled(postings):
    """embed(company: 公司名稱
    business scope: 行業1, 行業2, 行業3, 行業4
    item: 商品品項)"""
    def build_string(row):
        item_info = {
            'business_name': row['公司名稱'],
            'business_scopes': [ row['行業1'], row['行業2'], row['行業3'], row['行業4'] ],
            'item': row['商品品項']
        }
        return textwrap.dedent("""\
            company: {}
            business scope: {}
            item: {}""".format(
                item_info['business_name'],
                ", ".join([s for s in item_info['business_scopes'] if not pd.isnull(s)]),
                item_info['item']
        ))
    return encoder.encode(
        postings[['公司名稱', '行業1', '行業2', '行業3', '行業4', '商品品項']]
        .apply(build_string, axis=1)
        .to_list()
    )

def company_n_item(postings):
    """embed(公司名稱)+embed(商品品項)"""
    company_embeddings = encoder.encode(postings['公司名稱'].to_list())
    item_embeddings = encoder.encode(postings['商品品項'].to_list())
    return np.array(
        [company_embeddings[i] + item_embeddings[i] for i in range(len(postings))]
    )

def company_n_scope_n_item(postings):
    """embed(公司名稱)+embed(行業1行業2行業3行業4)+embed(商品品項)"""
    company_embeddings = encoder.encode(postings['公司名稱'].to_list())
    scope_embeddings = encoder.encode(
        postings[['行業1', '行業2', '行業3', '行業4']].fillna('')
        .apply(lambda x: ''.join(x), axis=1).to_list()
    )
    item_embeddings = encoder.encode(postings['商品品項'].to_list())
    return np.array(
        [company_embeddings[i] + scope_embeddings[i] + item_embeddings[i] for i in range(len(postings))]
    )

def company_scope_n_item(postings):
    """embed(公司名稱行業1行業2行業3行業4)+embed(商品品項)"""
    company_embeddings = encoder.encode(
        postings[['公司名稱', '行業1', '行業2', '行業3', '行業4']].fillna('')
        .apply(lambda x: ''.join(x), axis=1).to_list()
    )
    item_embeddings = encoder.encode(postings['商品品項'].to_list())
    return np.array(
        [company_embeddings[i] + item_embeddings[i] for i in range(len(postings))]
    )