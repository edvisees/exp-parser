import sys
import codecs

paralens = [len(line.strip().split(" ")) for line in codecs.open(sys.argv[1], "r", "utf-8")]
parsefile = codecs.open(sys.argv[2], "r", "utf-8")

for paralen in paralens:
	i = 0
	for line in parsefile:
		lnstrp = line.strip()
		if lnstrp == "":
			if i == paralen:
				print
				break
			continue
		print lnstrp.encode("utf-8")
		i += 1
