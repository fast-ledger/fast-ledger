import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from sklearn.base import clone
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.preprocessing import FunctionTransformer
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import LeaveOneOut, KFold
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sentence_transformers import SentenceTransformer
from recommender import testpostings, transformer
import warnings

def predict_journal(model, X, y):
    """
    Run prediction on every entry, each prediction excludes tested entry in training set
    """
    # Cross validation method
    cv = LeaveOneOut()
    # cv = KFold(len(y) // 10)

    preds = []
    for _, (train_idx, test_idx) in enumerate(cv.split(X)):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        model = clone(model)
        model.fit(X_train, y_train)
        preds.extend(model.predict(X_test))
    return preds


def plot_results(results):
    matplotlib.rc("font", family="Microsoft JhengHei", size=6)

    transformer_count = len(results)
    journal_count = len(results[0]["journal"])
    fig = plt.figure(
        layout="constrained", figsize=(15 * transformer_count, 15 * journal_count)
    )
    subfigs = fig.subfigures(nrows=transformer_count, ncols=1)
    if (transformer_count < 2): subfigs = [subfigs]

    for transformer, subfig in zip(results, subfigs):
        axes = subfig.subplots(nrows=1, ncols=journal_count)
        if journal_count > 1:
            axes = axes.flatten()
            ax_id = 0
        else:
            ax = axes

        embedder_correct, embedder_tests = 0, 0
        for journal in transformer["journal"]:
            labels = sorted(journal["true"].unique())
            journal_correct = sum(
                [a == b for a, b in zip(journal["true"], journal["pred"])]
            )
            embedder_correct += journal_correct
            embedder_tests += len(journal["true"])

            # Plot results for each embedder journal combination
            disp = ConfusionMatrixDisplay(
                confusion_matrix=confusion_matrix(journal["true"], journal["pred"]),
                display_labels=labels,
            )

            try:
                ax = axes[ax_id]
                ax_id += 1
            except NameError:
                pass

            disp.plot(colorbar=False, ax=ax)

            # Confusion matrix title
            ax.set_title(
                """[journal] {}
                {}/{} ({:.2f})""".format(
                    journal["name"],
                    journal_correct,
                    len(journal["true"]),
                    journal_correct / len(journal["true"]),
                ),
                fontsize=10,
            )

            ax.set_xticklabels(labels, rotation=-45, ha="left")
            ax.tick_params("x", labelsize=6)
            ax.tick_params("y", labelsize=6)

        subfig.suptitle(
            """[embedder] {}
            {}
            {}/{} ({:.2f})""".format(
                transformer["name"],
                transformer["desc"],
                embedder_correct,
                embedder_tests,
                embedder_correct / embedder_tests,
            )
        )
    plt.show()


if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    postings = testpostings.postings()

    # dinner/lunch dataset
    postings = postings[postings['ljavuras'].str.contains("expenses:food:dining:")].reset_index()

    language_models = [
        'sentence-transformers/multi-qa-MiniLM-L6-cos-v1',
        'shibing624/text2vec-base-chinese'
    ]
    language_model = language_models[1]
    encoder = SentenceTransformer(language_model)

    item_embed_strategies = [
        # transformer.company_scope_item,
        transformer.company_scope_item_labeled,
        transformer.all_labeled,
    ]

    # Tested journals
    journals = [
        "ljavuras",
        "nelly",
        # "hsuan",
    ]

    results = [None] * len(item_embed_strategies)
    for i, item_embedder in enumerate(item_embed_strategies):
        embedder = FeatureUnion([
            (
                "item_embedding",
                Pipeline([
                    ('transformer', FunctionTransformer(item_embedder)),
                    ('encoder', FunctionTransformer(lambda p: encoder.encode(p))),
                ])
            ),
            (
                "time_embedding",
                transformer.time_cyclic_transformer
            )
        ])
        X = embedder.fit_transform(postings)

        results[i] = {
            'name': item_embedder.__name__,
            'desc': item_embedder.__doc__,
            'journal': [None] * len(journals)
        }

        # Evaluation
        for j, journal in enumerate(journals):
            print("[Validating] embedder: {},\tjournal: {}".format(item_embedder.__name__, journal))
            y = postings[journal]
            results[i]["journal"][j] = {
                "name": journal,
                "true": y,
                "pred": predict_journal(
                    KNeighborsClassifier(weights='distance', n_neighbors=3), 
                    X, 
                    y),
            }

    print("Validation complete")
    plot_results(results)
