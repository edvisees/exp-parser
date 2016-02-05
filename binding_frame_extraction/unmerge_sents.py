import sys, codecs

tagged_file = codecs.open(sys.argv[1], "r", "utf-8")
sent_parse_file = codecs.open(sys.argv[2], "r", "utf-8")

sentlens = []
sentlen = 0
for line in sent_parse_file:
	if line.strip() != "":
		sentlen += 1
	else:
		sentlens.append(sentlen)
		sentlen = 0
if sentlen!=0:
	sentlens.append(sentlen)
#sentlens = [len(line.strip().split(" ")) for line in codecs.open(sys.argv[2], "r", "utf-8")]

for sent_len in sentlens:
	i = 0
	sent = []
	slots = []
	curr_slot_words = []
	curr_slot_name = ''
	for line in tagged_file:
		lnstrp = line.strip()
		if lnstrp != "":
			i += 1
			word, tag = lnstrp.split()
			sent.append(word)
			if tag == 'O':
				if len(curr_slot_words) != 0:
					slots.append((curr_slot_name, i, " ".join(curr_slot_words)))
					curr_slot_words = []
					curr_slot_name = ''
			else:
				if tag.startswith('S-'):
					slots.append((tag[2:], i, word))
				else:
					curr_slot_words.append(word)
					curr_slot_name = tag[2:]
			if i == sent_len:
				full_sent = " ".join(sent)
				outline = "%s\t%s"%(full_sent, "\t".join("%s:%s"%(slot_name, phrase) for slot_name, _, phrase in slots))
				print outline.encode("utf-8")
				break
				
					
