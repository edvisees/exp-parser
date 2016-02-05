import sys, codecs
from nltk.tokenize import sent_tokenize, word_tokenize

for line in codecs.open(sys.argv[1], "r", "utf-8"):
	sents = sent_tokenize(line.strip())
	print ("\n".join([" ".join(word_tokenize(sent)) for sent in sents])).encode('utf-8')
