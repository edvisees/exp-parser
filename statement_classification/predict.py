import sys
import codecs
from classifier import StatementClassifier

sc = StatementClassifier()
predictions = sc.predict(sys.argv[1])

outfile = codecs.open(sys.argv[2], "w", "utf-8")
for label, clause in predictions:
  print >>outfile, "%s\t%s"%(label, clause)
outfile.close()
