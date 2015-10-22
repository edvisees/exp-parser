import sys
import codecs
from nltk.tokenize import word_tokenize
from preprocess import tokenize_sentences, separate_clauses
for line in codecs.open(sys.argv[1], "r", "utf-8"):
  label, phrase = line.strip().split('\t')
  phrase_sents = tokenize_sentences(phrase)
  for phrase_sent in phrase_sents:
    sent_words = word_tokenize(phrase_sent)
    clause_set = separate_clauses([sent_words])
    for clauses in clause_set:
      for clause in clauses:
        clause = clause.strip()
        if clause != "":
          print "%s\t%s"%(label, clause)
