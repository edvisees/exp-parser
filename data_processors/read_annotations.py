import sys
import codecs
from bioc_processor import BiocProcessor

bp = BiocProcessor(sys.argv[1])
outfile = codecs.open(sys.argv[2], "w", "utf-8")

anns = bp.read_annotations("epistSeg")
print >>outfile, "\n".join("%s\t%s"%(label, text) for label, text in anns)

outfile.close()
