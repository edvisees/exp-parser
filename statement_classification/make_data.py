import sys
from preprocess import write_clauses

train = False
results_only = True
if len(sys.argv) > 2:
  train = sys.argv[3].lower() == "train"
if len(sys.argv) > 3:
  results_only = sys.argv[4].lower() == "results_only"

write_clauses(sys.argv[1], sys.argv[2], train=train, results_only=results_only) 
