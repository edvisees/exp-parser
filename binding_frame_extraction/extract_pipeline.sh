#!/bin/bash
wd=`echo $0 | rev | cut -d'/' -f2- | rev`
input_dir=$1
intermediate_dir="/tmp"
output_dir=$2
for fname in `ls $1/*.txt | sed 's/.txt//g'`
do
	pmid=`echo $fname | rev | cut -d'/' -f1 | rev`
	echo "Processing $pmid"
	python $wd/extract_results_section.py $input_dir/"$pmid".txt > $intermediate_dir/"$pmid".results.paratok
	python $wd/split_sentences.py $intermediate_dir/"$pmid".results.paratok > $intermediate_dir/"$pmid".results.senttok

	# Uncomment the following three lines if the original text is not parsed
	cd /usr1/shared/tools/fanseparser
	./parse.sh < $intermediate_dir/"$pmid".results.senttok > $intermediate_dir/"$pmid".results.fansed
	cd -
	# Uncomment the following line if the original text is parsed
	#python extract_results_parses.py $intermediate_dir/"$pmid".fansed > $intermediate_dir/"$pmid".results.fansed

	# Uncomment one of the fllowing two lines depending on the version of fanseparser
	python $wd/merge_parses.py $intermediate_dir/"$pmid".results.paratok $intermediate_dir/"$pmid".results.fansed| cut -f2,5,8,11,13 | sed 's/\t/ /g' > $intermediate_dir/"$pmid".crf_in
	#python merge_parses.py $intermediate_dir/"$pmid".results.paratok $intermediate_dir/"$pmid".results.fansed | cut -f2,3,4,6,7 | sed 's/null$/_/g' | sed 's/\t/ /g' > $intermediate_dir/"$pmid".crf_in
	java -cp ":/usr1/shared/tools/mallet-2.0.7/dist/mallet.jar:/usr1/shared/tools/mallet-2.0.7/dist/mallet-deps.jar:" cc.mallet.fst.SimpleTagger --train false --threads 10 --model-file $wd/para_model.crf $intermediate_dir/"$pmid".crf_in > $intermediate_dir/"$pmid".crf_out
	cut -d" " -f1 $intermediate_dir/"$pmid".crf_in | paste - $intermediate_dir/"$pmid".crf_out > $intermediate_dir/"$pmid".crf_result
	python $wd/unmerge_sents.py $intermediate_dir/"$pmid".crf_result $intermediate_dir/"$pmid".results.fansed > $output_dir/"$pmid".pradsys.out
done
