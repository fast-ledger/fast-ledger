import testpostings
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.base import clone
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import LeaveOneOut, cross_val_score
from sklearn.metrics import accuracy_score, make_scorer
import warnings

warnings.filterwarnings('ignore') 

def printLeaveOneOutResult(model, X, y):
    loo = LeaveOneOut()

    items = []
    truths = []
    preds = []
    confs = []
    correct = 0

    for _, (train_idx, test_idx) in enumerate(loo.split(X)):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        model = clone(model)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)[0]
        y_prob = model.predict_proba(X_test)[0]
        idx = int(np.argmax(y_prob))
        truth = y_test.values[0]

        if truth == y_pred:
            print(X['商品品項'][test_idx[0]], truth)
            correct += 1

        preds.append(y_pred)
        confs.append(y_prob[idx])
        truths.append(truth)
        items.append(X['商品品項'][test_idx[0]])

    recommendations = pd.DataFrame({
        'item': items,
        'truth': truths,
        'prediction': preds,
        'confidence': confs
    })

    print(f"Correct: {correct}")
    print(recommendations)

def embed_item_only(postings, embedder):
    return embedder.encode(postings['商品品項'].to_list())

def embed_company_item(postings, embedder):
    return embedder.encode((postings['公司名稱'] + postings['商品品項']).to_list())

def embed_company_item_sep(postings, embedder):
    company_embeddings = embedder.encode(postings['公司名稱'].to_list())
    item_embeddings = embedder.encode(postings['商品品項'].to_list())
    return np.array([company_embeddings[i] + item_embeddings[i] for i in range(len(postings))])

def embed_company_scope_item(postings, embedder):
    return embedder.encode(
        postings[['公司名稱', '行業1', '行業2', '行業3', '行業4', '商品品項']]
        .fillna('')
        .apply(lambda x: ''.join(x), axis=1)
        .to_list()
    )

if __name__ == "__main__":
    postings = testpostings.postings()
    
    X = postings
    y = postings['ljavuras']
    # y = postings['nelly']

    embedder = SentenceTransformer('sentence-transformers/multi-qa-MiniLM-L6-cos-v1')
    # pipe = Pipeline([
    #     ('transformer', transform_strategies['item_only'].set_params(kw_args={'embedder': embedder})),
    #     ('classifier', KNeighborsClassifier(weights='distance'))
    # ])

    # printLeaveOneOutResult(pipe, X, y)

    transform_strategies = {
        # 'item_only': FunctionTransformer(embed_item_only),  # 17
        'company_item': FunctionTransformer(embed_company_item),  # 54
        # 'company_scope_item': FunctionTransformer(embed_company_scope_item),  # 60, significantly longer time
        'company_item_sep': FunctionTransformer(embed_company_item_sep),  #47
    }

    accuracies = {}
    for strategy, transformer in transform_strategies.items():
        pipe = Pipeline([
            ('transformer', transformer.set_params(kw_args={'embedder': embedder})),
            ('classifier', KNeighborsClassifier(weights='distance'))
        ])

        scores = cross_val_score(pipe, X, y, cv=LeaveOneOut(), scoring=make_scorer(accuracy_score))
        accuracies[strategy] = sum(scores)

    print(accuracies)