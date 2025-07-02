import testpostings
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.base import clone
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import LeaveOneOut

def embed_posting(postings, embedder):
    return embedder.encode(postings['商品品項'].to_list())

if __name__ == "__main__":
    postings = testpostings.postings()
    
    X = postings
    y = postings["ljavuras"]

    embedder = SentenceTransformer('sentence-transformers/multi-qa-MiniLM-L6-cos-v1')

    # print(embed_posting(X, embedder))

    pipe = Pipeline([
        ('embedding', FunctionTransformer(embed_posting, kw_args={'embedder':embedder})),
        ('classifier', KNeighborsClassifier(weights='distance'))
    ])

    loo = LeaveOneOut()

    items = []
    truths = []
    preds = []
    confs = []

    for _, (train_idx, test_idx) in enumerate(loo.split(X)):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        model = clone(pipe)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[0]
        idx = int(np.argmax(y_prob))

        preds.append(y_pred[0])
        confs.append(y_prob[idx])
        truths.append(y_test.values[0])
        items.append(X['商品品項'][test_idx[0]])

    recommendations = pd.DataFrame({
        'item': items,
        'truth': truths,
        'prediction': preds,
        'confidence': confs
    })

    print(recommendations)