import sys
import re
from nltk.tokenize import sent_tokenize

def char_range(c1, c2):
	"""Generates the characters from `c1` to `c2`, inclusive."""
	for c in xrange(ord(c1), ord(c2)+1):
		yield chr(c)

filename = sys.argv[1]
outdir = sys.argv[2]
infile = open(filename)

res_section = True
floats = False
fig_pointers = {}
fig_captions = {}
last_fig_ind = ''
last_subfig_ind = ''

for line in infile:
	lnstrp = line.strip()
	lnstrp = lnstrp.replace("\xc2\xa0", " ")
	# Replace all non-breaking spaces to normal ones
	if lnstrp == "":
		continue
	header_text = lnstrp.replace('.', '').strip().lower()
	if 'results' in header_text and len(header_text.split()) < 4:
		res_section = True
		# Start looking for figure references from now on
	if header_text == 'floating objects':
		res_section = False
		floats = True 
	sents = sent_tokenize(lnstrp)
	cleaned_sents = []
	for i in range(len(sents)):
		if len(cleaned_sents) == 0:
			cleaned_sents.append(sents[i].strip())
			continue
		if cleaned_sents[-1].endswith("Fig.") or cleaned_sents[-1].endswith("et al.") or sents[i][0].islower():
			cleaned_sents[-1] = " ".join([cleaned_sents[-1], sents[i]])
		else:
			cleaned_sents.append(sents[i])
	if res_section:	
		last_inds = []
		for sent in cleaned_sents:
			sent = re.sub("__[se]_[^_]+__", "", sent)
			if "Fig" in sent or "Figure" in sent:
				f_inds = re.findall('Fig.? *[1-9]+ *[A-Za-z]{0,2}[^a-zA-Z]', sent) + re.findall('Figure *[1-9]+ *[A-Za-z]{0,2}[^a-zA-Z]', sent)
				#print >>sys.stderr, sent, f_inds
				last_inds = f_inds
				for ind in f_inds:
					r_ind = ind.lower().replace('figure', '').replace('fig', '').replace('.','').replace(' ', '').replace(')', '').replace(',', '').replace(';','')
					if r_ind in fig_pointers:
						fig_pointers[r_ind].append(sent)
					else:
						fig_pointers[r_ind] = [sent]
			else:
				for ind in last_inds:
					r_ind = ind.lower().replace('figure', '').replace('fig', '').replace('.','').replace(' ', '').replace(')', '').replace(',', '').replace(';', '')
					if r_ind in fig_pointers:
						fig_pointers[r_ind].append(sent)
					else:
						fig_pointers[r_ind] = [sent]
					
					
	if floats:
		for sent in cleaned_sents:
			sent = re.sub("__[se]_[^_]+__", "", sent)
			if sent.startswith("Figure"):
				f_id = re.findall('^[Ff]igure [1-9]+', sent)[0]
				last_fig_ind = re.sub('[Ff]igure ?', '', f_id)
				last_subfig_ind = ''
			if last_fig_ind == '':
				continue
				# This means we haven't even seen the first figure label
			sf_id = re.findall('^\( *[A-Za-z]+ *\)', sent)
			if len(sf_id) != 0:
				last_subfig_ind = re.sub('[() ]', '', sf_id[0]).lower()
			sf_id_range = re.findall('^\( *[A-Za-z]+[-,][A-Za-z]+ *\)', sent)
			if len(sf_id_range) != 0:
				last_subfig_range = re.sub('[() ]', '', sf_id_range[0]).lower()
				sf_range = True
				# We are dealing with range of subfigures, not just one.
				range_parts = re.split('[-,]', last_subfig_range)
				sf1 = range_parts[0]
				sf2 = range_parts[1]
				if ',' in last_subfig_range:
					last_subfig_inds = [sf1, sf2]
				elif '-' in last_subfig_range:
					last_subfig_inds = char_range(sf1, sf2)
			else:
				last_subfig_inds = [last_subfig_ind]
			for lsi in last_subfig_inds:
				fig_ind = last_fig_ind+lsi
				if fig_ind in fig_captions:
					fig_captions[fig_ind].append(sent)
				else:
					fig_captions[fig_ind] = [sent]

reffile = open(outdir+"/"+filename.split('/')[-1].replace(".txt", "_ref.txt"), "w")
capfile = open(outdir+"/"+filename.split('/')[-1].replace(".txt", "_cap.txt"), "w")

for ind in sorted(fig_pointers):
	for sent in fig_pointers[ind]:
		print >>reffile, "%s\t%s"%(ind, sent)

for ind in sorted(fig_captions):
	for sent in fig_captions[ind]:
		print >>capfile, "%s\t%s"%(ind, sent)
