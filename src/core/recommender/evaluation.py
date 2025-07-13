import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from sklearn.base import clone
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import LeaveOneOut, KFold
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from recommender import embedder, testpostings
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
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

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

    embed_strategies = [
        # embedder.item,
        # embedder.company_item,
        embedder.company_scope_item,
        # embedder.company_n_item,
        # embedder.company_n_scope_n_item,
        # embedder.company_scope_n_item,
        # embedder.company_scope_item_labeled,
        embedder.all_labeled,
    ]

    class Transformer(FunctionTransformer):
        def __init__(self, func = None, inverse_func = None, *, validate = False, accept_sparse = False, check_inverse = True, feature_names_out = None, kw_args = None, inv_kw_args = None):
            super().__init__(func, inverse_func, validate=validate, accept_sparse=accept_sparse, check_inverse=check_inverse, feature_names_out=feature_names_out, kw_args=kw_args, inv_kw_args=inv_kw_args)
            self.name: str = func.__name__
            self.desc: str = func.__doc__

    transformers: list[Transformer] = [Transformer(f) for f in embed_strategies]

    # Tested journals
    journals = [
        "ljavuras",
        "nelly",
        "hsuan",
    ]

    results = [None] * len(transformers)
    for i, transformer in enumerate(transformers):
        X = pd.DataFrame(transformer.fit_transform(postings))
        pipe = Pipeline([
            # ('transformer', transformer.func),
            ('classifier', KNeighborsClassifier(weights='distance', n_neighbors=3))
        ])
        results[i] = {
            'name': transformer.name,
            'desc': transformer.desc,
            'journal': [None] * len(journals)
        }

        # Evaluation
        for j, journal in enumerate(journals):
            print("[Validating] embedder: {},\tjournal: {}".format(transformer.name, journal))
            y = postings[journal]
            results[i]["journal"][j] = {
                "name": journal,
                "true": y,
                "pred": predict_journal(pipe, X, y),
            }

    print("Validation complete")
    plot_results(results)
