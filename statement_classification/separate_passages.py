# Simple script for reading plain text of papers and annotations, and aggregating them at passage or section level
# Run: python separate_passages.py nxml2txt-output annotated-clause-level-file [para/section]
# clausefile should be tab-separated with clauses on the first column and gold labels on the second
import sys
import codecs

passage_file = codecs.open(sys.argv[1], "r", "utf-8")
clauses_file = codecs.open(sys.argv[2], "r", "utf-8")
mode = "para"
if len(sys.argv) > 3:
    if sys.argv[3] != "para":
        mode = "section"

despaced_passages = [x.strip().replace(" ", "") for x in passage_file.readlines()]

passage_ind = 0
prev_passage_ind = 0
passage_clauses = []

for clause_line in clauses_file:
    clause_parts = clause_line.strip().split("\t")
    if len(clause_parts) > 1:
        clause, label = clause_parts
    else:
        continue
        #clause = clause_parts[0]
    despaced_clause = clause.replace(" ", "")
    try:
        while despaced_clause not in despaced_passages[passage_ind]:
            passage_ind += 1
        if prev_passage_ind != passage_ind:
            if len(passage_clauses) == 1:
                if mode == "section":
                    print
                #print passage_clauses[0]
            elif len(passage_clauses) > 0:
                print "\n".join(passage_clauses)
                #print passage_clauses[-1]
            passage_clauses = []
            if mode == "para":
                print
        passage_clauses.append(clause_line.strip())
        prev_passage_ind = passage_ind
    except:
        #print
        break
