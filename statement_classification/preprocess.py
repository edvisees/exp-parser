import os
from nltk.parse import stanford
import sys
import codecs
from nltk.tokenize import word_tokenize, sent_tokenize
import re

os.environ['STANFORD_PARSER'] = "/usr1/shared/tools/stanford-parser-full-2015-04-20"
os.environ['STANFORD_MODELS'] = "/usr1/shared/tools/stanford-parser-full-2015-04-20"
parser = stanford.StanfordParser()

def get_longest_cand(cands):
  maxlen = 0
  bestcand = ''
  for cand in cands:
    if len(cand) > maxlen:
      maxlen = len(cand)
      bestcand = cand
  return bestcand

def extract_sat_clause(tree, is_root = True):
  if len(tree) == 0 or type(tree) == unicode:
    return ""
  elif tree.label() == 'S' or tree.label() == 'SBAR':
    if is_root:
      return get_longest_cand([extract_sat_clause(t, is_root = False) for t in tree])
    else:
      phrase = " ".join(tree.leaves())
      return phrase.replace("-LRB-", "(").replace("-RRB-", ")").replace("-LSB-", "[").replace("-RSB-", "]")
  else:
    return get_longest_cand([extract_sat_clause(t, is_root) for t in tree])


def separate_clauses(lines):
  parse_iters = parser.parse_sents(lines)
  clauses = []
  #print "Got: ", lines
  for words, parse_iter in zip(lines, parse_iters):
    sent = " ".join(words)
    sat_clause = extract_sat_clause(parse_iter.next())
    #print >>sys.stderr, "Looking for %s in %s"%(sat_clause, sent)
    ind = sent.index(sat_clause)
    sat_len = len(sat_clause)
    main_clause = sent[sat_len:] if ind == 0 else sent[:ind]
    clauses.append((sat_clause, main_clause))
  return clauses

def tokenize_sentences(phrase):
  phrase_sents = sent_tokenize(phrase)
  fixed_phrase_sents = [phrase_sents[0]]
  i = 1
  while i < len(phrase_sents):
    if (phrase_sents[i-1].endswith("Fig.") or phrase_sents[i-1].endswith("et al.") ) and re.match("[0-9a-z]", phrase_sents[i][0]) is not None:
      fixed_phrase_sents[-1] += " "+phrase_sents[i]
    else:
      fixed_phrase_sents.append(phrase_sents[i])
    i += 1
  return fixed_phrase_sents 
