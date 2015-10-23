import sys
import codecs
from svm_classifier import StatementClassifier

sc = StatementClassifier()
predictions = sc.predict(sys.argv[1])

outfile = codecs.open(sys.argv[2], "w", "utf-8")
print >>outfile, "Clause\tPrediction"
for label, clause in predictions:
  print >>outfile, "%s\t%s"%(clause, label)
outfile.close()
