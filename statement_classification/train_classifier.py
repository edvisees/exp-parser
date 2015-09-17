import sys
from classifier import StatementClassifier

sc = StatementClassifier(train=True)
sc.train(sys.argv[1])

