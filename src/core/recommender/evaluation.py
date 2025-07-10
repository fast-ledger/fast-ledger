import testpostings
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from sklearn.base import clone
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import LeaveOneOut, cross_val_score, KFold
from sklearn.metrics import accuracy_score, make_scorer, confusion_matrix, ConfusionMatrixDisplay
import warnings
import embedder
from typing import TypedDict

warnings.filterwarnings('ignore')

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
    matplotlib.rc('font', family='Microsoft JhengHei', size=6)

    transformer_count = len(results)
    journal_count = len(results[0]['journal'])
    fig = plt.figure(layout='constrained', figsize=(15 * transformer_count, 15 * journal_count))
    subfigs = fig.subfigures(nrows=transformer_count, ncols=1)

    for transformer, subfig in zip(results, subfigs):
        axes = subfig.subplots(nrows=1, ncols=journal_count)
        if (journal_count > 1):
            axes = axes.flatten()
            ax_id = 0
        else:
            ax = axes

        embedder_correct, embedder_tests = 0, 0
        for journal in transformer['journal']:
            labels = journal['true'].unique()
            journal_correct = sum([a == b for a, b in zip(journal['true'], journal['pred'])])
            embedder_correct += journal_correct
            embedder_tests += len(journal['true'])

            # Plot results for each embedder journal combination
            disp = ConfusionMatrixDisplay(
                confusion_matrix=confusion_matrix(journal['true'], journal['pred']),
                display_labels=labels
            )

            try:
                ax = axes[ax_id]
                ax_id += 1
            except NameError:
                pass

            disp.plot(
                colorbar=False,
                ax=ax)

            # Confusion matrix title
            ax.set_title(
                """[journal] {}
                {}/{} ({:.2f})""".format(
                    journal['name'], journal_correct, len(journal['true']), journal_correct / len(journal['true'])
                ),
                fontsize=10)
        
            ax.set_xticklabels(labels, rotation=-45, ha='left')
            ax.tick_params('x', labelsize=6)
            ax.tick_params('y', labelsize=6)
        
        subfig.suptitle(
            """[embedder] {}
            {}
            {}/{} ({:.2f})""".format(
                transformer['name'],\
                transformer['desc'],
                embedder_correct, embedder_tests, embedder_correct / embedder_tests)
        )
    plt.show()

embed_strategies = [
    # embedder.item,
    # embedder.company_item,
    embedder.company_scope_item,
    # embedder.company_n_item,
    # embedder.company_n_scope_n_item,
    embedder.company_scope_n_item,
]

class Transformer(TypedDict):
    name: str
    desc: str
    func: FunctionTransformer

transformers: list[Transformer] = [
    {
        'name': f.__name__,
        'desc': f.__doc__,
        'func': FunctionTransformer(f)
    }
    for f in embed_strategies]

# Tested journals
journals = [
    'ljavuras',
    'nelly',
    'hsuan',
]

postings = testpostings.postings()
results = [None] * len(transformers)
for i, transformer in enumerate(transformers):
    X = pd.DataFrame(transformer['func'].fit_transform(postings))
    pipe = Pipeline([
        # ('transformer', transformer['func']),
        ('classifier', KNeighborsClassifier(weights='distance'))
    ])
    results[i] = {
        'name': transformer['name'],
        'desc': transformer['desc'],
        'journal': [None] * len(journals)
    }

    # Evaluation
    for j, journal in enumerate(journals):
        print("[Validating] embedder: {},\tjournal: {}".format(transformer['name'], journal))
        y = postings[journal]
        results[i]['journal'][j] = {
            'name': journal,
            'true': y,
            'pred': predict_journal(pipe, X, y),
        }

print("Validation complete")
plot_results(results)