# This code takes the output of Fanseparser on sentences.
# This is a stupid logic for extracting the parses of sentences in the result section

import sys
import codecs
import re

infile = codecs.open(sys.argv[1], "r", "utf-8")
in_res_section = False

sent_words = []
stored_parse = []
for line in infile:
	lnstrp = line.strip()
	if lnstrp == "":
		if len(sent_words) < 4:
			if sent_words[0].lower() == "results":
				in_res_section = True
			elif in_res_section and re.search("[0-9]", sent_words[0]) is None:	
				in_res_section = False
				break
		elif in_res_section:
			print ("\n".join(stored_parse)).encode('utf-8')
			print
		sent_words = []
		stored_parse = []
	else:
		lnparts = lnstrp.split()
		sent_words.append(lnparts[1])
		stored_parse.append(lnstrp)
