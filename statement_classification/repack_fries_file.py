# Simple script for reading plain text of papers and annotations, and aggregating them at passage or section level
# Run: python separate_passages.py nxml2txt-output annotated-clause-level-file [para/section]
# clausefile should be tab-separated with clauses on the first column and gold labels on the second
import sys
import codecs

passage_file = codecs.open(sys.argv[1], "r", "utf-8")
clauses_file = codecs.open(sys.argv[2], "r", "utf-8")
#despaced_passages = [x.strip().replace(" ", "") for x in passage_file.readlines()]

despaced_passage = ""
passage_line = ""
passage_line_num = 0

for clause_line in clauses_file:
    clause_parts = clause_line.strip().split("\t")
    if len(clause_parts) == 2:
        clause, label = clause_parts
    elif len(clause_parts) == 3:
        clause, disc_label, cosid_label = clause_parts
    elif len(clause_parts) == 4:
        clause, disc_label, disc_prob, cosid_label = clause_parts
    despaced_clause = clause.replace(" ", "").replace("`", "").replace("'", "").replace('"', '')
    #try:
    while despaced_clause not in despaced_passage:
        if passage_line != "":
            if len(clause_parts) == 2:
                print "%d\t%s\t-"%(passage_line_num, passage_line)
            else:
                print "%d\t%s\t-\t-\t-"%(passage_line_num, passage_line)
        passage_line = passage_file.readline().strip()
        passage_line_num += 1
        passage_line_parts = passage_line.split("\t")
        passage = passage_line_parts[0]
        despaced_passage = passage.replace(" ", "").replace("`", "").replace("'", "").replace('"', '')
    passage_line = ""
    clstrp = clause_line.strip()
    if clstrp != "":
        print "%d\t%s\t%s\t%s"%(passage_line_num, clause, "\t".join(passage_line_parts[1:]), "\t".join(clause_parts[1:]))
