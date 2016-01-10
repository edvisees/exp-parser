#!/bin/bash
# Input: TSV file with format:
#sentence<==tab==>[categoryTag]<==tab==>paragraphCode

#1. categoryTag can be exLink, inLink or header-X (X=0 means its a section, X=1 means its a subsection )
#2. paragraphCode is either titleX or pX (X is just an incremental

# Output: TSV file with format:
#clause<==tab==>[categoryTag]<==tab==>paragraphCode<==tab==>[discourseTag]<==tab==>[cosidTag]

# Note on filepaths:
# Make sure the input files are at <somepath>/input/<inputfile>, and there exist directories called <somepath>/intermediate/ and <somepath>/output/
# Output files will be stored in the output direcotry

infilename=$1
clausefilename=`echo $1 | sed 's/input/intermediate/g' |  sed 's/.txt/_clauses.txt/g'`
paraclausefilename=`echo $1 | sed 's/input/intermediate/g' |  sed 's/.txt/_para_clauses.txt/g'`
paraclausecrfout=`echo $1 | sed 's/input/intermediate/g' | sed 's/.txt/_para_clauses.crfout/g'`
sectionclausecrfout=`echo $1 | sed 's/input/intermediate/g' |  sed 's/.txt/_sec_clauses.crfout/g'`
cosid_int=`echo $1 | sed 's/input/intermediate/g' | sed 's/.txt/_cosid_int.tsv/g'`
cosidout=`echo $1 | sed 's/input/output/g' | sed 's/.txt/_cosid.tsv/g'`
echo "Processing $infilename"
python make_data.py <(cut -f1 $infilename) $clausefilename test results_only
echo "Extracted clauses"
python separate_formatted_passages.py $infilename $clausefilename para > $paraclausefilename
echo "Separated paragraphs"
python tag_passages.py $paraclausefilename > $paraclausecrfout
echo "Tagged paragraphs"
python separate_formatted_passages.py $infilename <( paste <( awk 'NF > 0'  $paraclausefilename) <( awk 'NF > 0' $paraclausecrfout )) section > $sectionclausecrfout
echo "Separated sections"
python make_cosid_frames.py $sectionclausecrfout > $cosid_int
echo "Made CoSID frames"
python repack_fries_file.py $infile $cosid_int > $cosidout
echo "Done"
