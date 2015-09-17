import sys
import codecs
from bioc_processor import BiocProcessor

bp = BiocProcessor(sys.argv[1])
outfile = codecs.open(sys.argv[2], "w", "utf-8")

text = bp.read_text()
print >>outfile, text

outfile.close()
