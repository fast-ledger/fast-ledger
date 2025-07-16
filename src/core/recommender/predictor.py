import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline, FeatureUnion, make_pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.compose import ColumnTransformer
from sklearn.neighbors import KNeighborsClassifier
from sentence_transformers import SentenceTransformer
from transformer import company_scope_item_labeled, time_cyclic_transformer

class Predictor:
    def __new__(cls):
        encoder = SentenceTransformer('sentence-transformers/multi-qa-MiniLM-L6-cos-v1')

        weight_time = 15
        weight_subtotal = 100
        KNN_weights = [1] * 384

        features = [(
            "item_embedding",
            Pipeline([
                ('transformer', FunctionTransformer(company_scope_item_labeled)),
                ('encoder', FunctionTransformer(lambda s: encoder.encode(s)))
            ])
        )]
        
        if (weight_time > 0):
            KNN_weights += [weight_time, weight_time]
            features += [("time_embedding", time_cyclic_transformer)]

        if (weight_subtotal > 0):
            KNN_weights += [weight_subtotal]
            features += [(
                "subtotal_embedding",
                ColumnTransformer([
                    (
                        "subtotal_sigmoid",
                        FunctionTransformer(lambda z: 1 / (1 + np.exp(-1 * z.astype(int)))),
                        ['subtotal']
                    )
                ])
            )]
        
        return make_pipeline(
            FeatureUnion(features),
            KNeighborsClassifier(
                weights='distance',
                metric_params={'w': KNN_weights}),
        )

if __name__ == "__main__":
    from datasets import fetch_dataset
    
    postings = fetch_dataset().frame
    X_train, X_test = postings.iloc[:-1], postings.iloc[-1:].reset_index()
    y_train = X_train['ljavuras']

    # Example usage
    predictor = Predictor()
    predictor.fit(X_train, y_train)
    possibilities = predictor.predict_proba(X_test)[0]

    print(pd.DataFrame({
        'accounts': sorted(y_train.unique()),
        'possibility': possibilities
    }).sort_values(by=['possibility'], ascending=False))