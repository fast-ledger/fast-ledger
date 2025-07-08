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
        # y_pred = model.predict(X_test)[0]
        print(X_test)
        print(model.predict(X_test))
        # preds.append(y_pred)
        preds.extend(model.predict(X_test))
    return preds

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

# accuracies = {}
y_preds = []
for transformer in transformers:
    pipe = Pipeline([
        ('transformer', transformer['func']),
        ('classifier', KNeighborsClassifier(weights='distance'))
    ])

    # Evaluation
    # scores = cross_val_score(pipe, X, y, cv=LeaveOneOut(), scoring=make_scorer(accuracy_score))
    # accuracies[strategy] = sum(scores)
    for journal in journals:
        y = postings[journal]
        y_pred = predict_journal(pipe, X, y)
        y_preds.append(y_pred)

matplotlib.rc('font', family='Microsoft JhengHei', size=6)

plot_index = 0
total_correct = 0
total_test = 0
fig, axes = plt.subplots(
    len(transformers),
    len(journals),
    figsize=(7 * len(journals), 7 * len(transformers)))
for j, transformer in enumerate(transformers):
    for i, journal in enumerate(journals):
        y = postings[journal]
        y_pred = y_preds[plot_index]
        correct = sum([i == j for i, j in zip(y, y_pred)])
        total_correct += correct
        total_test += len(y)

        ax = axes[j, i]
        labels = sorted(postings[journal].unique())
        disp = ConfusionMatrixDisplay(
            confusion_matrix=confusion_matrix(y, y_pred),
            display_labels=labels
        )
        disp.plot(
            # cmap=plt.cm.Blues,
            ax=ax)
        ax.set_title(
            """encoder: {0}
            {1}
            journal: {2}, {3}/{4} ({5:.2f})""".format(
                transformer['name'],
                transformer['desc'],
                journal,
                correct,
                len(y),
                correct/len(y)
            ),
            fontsize=10)
        ax.set_xticklabels(labels, rotation=-45, ha='left')
        ax.tick_params('x', labelsize=6)
        ax.tick_params('y', labelsize=6)

        plot_index += 1
fig.suptitle(
    # """langauge model: {}
    """overall accuracy: {}/{} ({:.2f})""".format(
    #     language_model,
        total_correct,
        total_test,
        total_correct / total_test
    ))
plt.tight_layout()
plt.show()