"""Strategies to embed a posting"""

import numpy as np
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

# TODO
# def company_scope_item_desc(postings):
#     """embed(company: 公司名稱
#     business scope: 行業1行業2行業3行業4
#     item: 商品品項)"""
#     return embedder.encode(
#         postings[['公司名稱', '行業1', '行業2', '行業3', '行業4', '商品品項']]
#         .fillna('')
#         .apply(lambda x: ''.join(x), axis=1)
#         .to_list()
#     )

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