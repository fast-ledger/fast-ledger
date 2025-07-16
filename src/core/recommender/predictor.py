import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline, FeatureUnion, make_pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.compose import ColumnTransformer
from sklearn.neighbors import KNeighborsClassifier
from sentence_transformers import SentenceTransformer
from transformer import company_scope_item_labeled, time_cyclic_transformer
import time

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
    time_load_predictor = time.time()
    predictor = Predictor()  # Create predictor
    time_train_start = time.time()
    predictor.fit(X_train, y_train)  # Train predictor
    time_train_end = time.time()
    possibilities = predictor.predict_proba(X_test)[0]  # Predict result
    time_pred_end = time.time()

    print(pd.DataFrame({
        'accounts': sorted(y_train.unique()),
        'score': possibilities
    }).sort_values(by=['score'], ascending=False))
    print("Prediction:", predictor.predict(X_test)[0])
    
    print("========== Time Evaluation ==========")
    print("Load predictor: {:.2f}s".format(time_train_start - time_load_predictor))
    print("Training: {:.2f}s\tPredict: {:.2f}s".format(
        time_train_end - time_train_start,
        time_pred_end - time_train_end
    ))