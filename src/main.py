import testpostings
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.base import clone
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import LeaveOneOut

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

def embed_posting(postings, embedder):
    return embedder.encode(postings['商品品項'].to_list())

transform_strategies = {
    'item_only': FunctionTransformer(embed_posting)
}

if __name__ == "__main__":
    postings = testpostings.postings()
    
    X = postings
    y = postings['ljavuras']
    # y = postings['nelly']

    embedder = SentenceTransformer('sentence-transformers/multi-qa-MiniLM-L6-cos-v1')

    pipe = Pipeline([
        ('transformer', transform_strategies['item_only'].set_params(kw_args={'embedder': embedder})),
        ('classifier', KNeighborsClassifier(weights='distance'))
    ])

    printLeaveOneOutResult(pipe, X, y)