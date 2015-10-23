import sys
from svm_classifier import StatementClassifier

sc = StatementClassifier(train=True)
sc.train(sys.argv[1])

