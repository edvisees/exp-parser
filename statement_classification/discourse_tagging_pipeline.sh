#!/bin/bash

# Input: TSV file with format:
#sentence<==tab==>[categoryTag]<==tab==>paragraphCode<==tab==>[FRIESsentence]<==tab==>[FRIESevent]

#1. categoryTag can be exLink, inLink or header-X (X=0 means its a section, X=1 means its a subsection )
#2. paragraphCode is either titleX or pX (X is just an incremental
#3. FRIES sentence is a pointer to the FRIES sentence frame
#4. FRIES event is a pointer to the FRIES event mention frame, if there exists one.

# Output: TSV file with format:
#clause<==tab==>[categoryTag]<==tab==>paragraphCode<==tab==>[FRIESsentence]<==tab==>[FRIESevent]<==tab==>[discourseTag]

# Note on filepaths:
# Make sure the input files are at <somepath>/input/<inputfile>, and there exist directories called <somepath>/intermediate/ and <somepath>/output/
# Output files will be stored in the output direcotry

infilename=$1
clausefilename=`echo $1 | sed 's/input/intermediate/g' |  sed 's/.txt/_clauses.txt/g'`
paraclausefilename=`echo $1 | sed 's/input/intermediate/g' |  sed 's/.txt/_para_clauses.txt/g'`
paraclausecrfout=`echo $1 | sed 's/input/intermediate/g' | sed 's/.txt/_para_clauses.crfout/g'`
repackedfries=`echo $1 | sed 's/input/output/g' | sed 's/.txt/_discoursetagged.txt/g'`
echo "Processing $infilename"
python make_data.py <(cut -f1 $infilename) $clausefilename test results_only
echo "Extracted clauses"
python separate_formatted_passages.py $infilename $clausefilename para > $paraclausefilename
echo "Separated paragraphs"
python tag_passages.py $paraclausefilename > $paraclausecrfout
echo "Tagged paragraphs"
python repack_fries_file.py $infilename <(paste <(awk 'NF > 0' $paraclausefilename) <(awk 'NF > 0' $paraclausecrfout)) > $repackedfries
