from sklearn.ensemble import RandomForestClassifier

def Model(parameters={}):
    return RandomForestClassifier(n_estimators=256)
