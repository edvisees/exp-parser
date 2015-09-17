import sys
from preprocess import write_clauses

write_clauses(sys.argv[1], sys.argv[2], train=(sys.argv[3].lower() == "train")) 
