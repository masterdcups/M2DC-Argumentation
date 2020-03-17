from sklearn import naive_bayes, linear_model, svm, ensemble


def GaussianNB():
    return naive_bayes.GaussianNB()

def LogisticRegression(C=1.0):
    return linear_model.LogisticRegression(C=C, solver='saga')

"""
Methods implemented by Carstents-Toni in
'Using argumentation to improve classification in Natural Language problems'
Method: SVM, Random Forest
"""

def SVC(C=1.0):
    return svm.SVC(C=C, kernel='poly')

def RandomForestClassifier(
            n_estimators=256, max_depth=10,
        ):
    return ensemble.RandomForestClassifier(n_estimators=n_estimators)

