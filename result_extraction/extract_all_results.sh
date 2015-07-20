wd=`echo $0 | rev | cut -d'/' -f2- | rev`
for x in `ls $1/*.txt`
do python $wd/extract_results.py $x $2
done
