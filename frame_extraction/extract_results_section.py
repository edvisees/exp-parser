# This code takes a sentence-tokenized and word-tokenized plain text file as input.
# This is a stupid logic for result section extraction

import sys
import codecs

infile = codecs.open(sys.argv[1], "r", "utf-8")
in_res_section = False
for line in infile:
	line_parts = line.split()
	if len(line_parts) == 0:
		continue
	if line.lower().startswith("results") and len(line_parts) < 4:
		in_res_section = True
	elif len(line_parts) < 4 and len(line_parts[0]) > 5:
		if in_res_section:
			in_res_section = False
	elif in_res_section:
		print line.strip().encode('utf-8')
