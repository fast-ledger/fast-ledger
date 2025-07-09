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

warnings.filterwarnings('ignore')

def predict_journal(model, X, y):
    """
    Run prediction on every entry, each prediction excludes tested entry in training set
    """
    # Cross validation method
    # cv = LeaveOneOut()
    cv = KFold(len(y) // 10)

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
    fig, axes = plt.subplots(
        transformer_count,
        1,
        figsize=(7 * transformer_count, 7 * journal_count))

    if (hasattr(axes, 'flatten')):
        axes = axes.flatten()
        ax_id = 0
    else:
        ax = axes

    for transformer in results:

        # Process results for each transformer
        labels, labels_true, labels_pred = [], [], []
        for journal in transformer['journal']:
            labels.extend(journal['true'].unique())
            labels_true.extend(journal['true'])
            labels_pred.extend(journal['pred'])
        correct = sum([a == b for a, b in zip(labels_true, labels_pred)])

        # Plot results for each transformer
        disp = ConfusionMatrixDisplay(
            confusion_matrix=confusion_matrix(labels_true, labels_pred),
            display_labels=labels
        )

        try:
            ax = axes[ax_id]
            ax_id += 1
        except NameError:
            pass

        disp.plot(
            # cmap=plt.cm.Blues,
            ax=ax)
        
        ax.set_title(
            """encoder: {}
            {}
            journal: {}, {}/{} ({:.2f})""".format(
                transformer['name'],
                transformer['desc'],
                journal['name'], correct, len(labels_true), correct / len(labels_true)
            ),
            fontsize=10)
        
        ax.set_xticklabels(labels, rotation=-45, ha='left')
        ax.tick_params('x', labelsize=6)
        ax.tick_params('y', labelsize=6)

    # fig.suptitle(
    #     # """langauge model: {}
    #     """overall accuracy: {}/{} ({:.2f})""".format(
    #     #     language_model,
    #         total_correct,
    #         total_test,
    #         total_correct / total_test
    #     ))
    plt.tight_layout()
    plt.show()

embed_strategies = [
    # embedder.item,
    # embedder.company_item,
    embedder.company_scope_item,
    # embedder.company_n_item,
    # embedder.company_n_scope_n_item,
    embedder.company_scope_n_item,
]

transformers = [
    {
        'name': f.__name__,
        'desc': f.__doc__,
        'func': FunctionTransformer(f)
    }
    for f in embed_strategies]

### 測試帳本 ###

journals = [
    'ljavuras',
    'nelly',
    # 'hsuan',
]

postings = testpostings.postings()
X = postings

results = [None] * len(transformers)
for i, transformer in enumerate(transformers):
    pipe = Pipeline([
        ('transformer', transformer['func']),
        ('classifier', KNeighborsClassifier(weights='distance'))
    ])
    results[i] = {
        'name': transformer['name'],
        'desc': transformer['desc'],
        'journal': [None] * len(journals)
    }

    # Evaluation
    for j, journal in enumerate(journals):
        y = postings[journal]
        results[i]['journal'][j] = {
            'name': journal,
            'true': y,
            'pred': predict_journal(pipe, X, y),
        }

plot_results(results)