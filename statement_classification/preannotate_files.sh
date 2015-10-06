if [ "$#" -ne 3 ]; then
  echo "Usage: $0 INPUT_DIR CLAUSE_DIR OUTPUT_DIR" >&2
  echo "\tINPUT_DIR: Directory containing plain text papers (output of nxml2txt)" >&2
  echo "\tCLAUSE_DIR: Intermediate directory where clauses from results section are stored" >&2
  echo "\tOUTPUT_DIR: Output directory where tsv and xlsx files are written" >&2
  exit 1
fi

input_dir=$1
interm_dir=$2
output_dir=$3
#input_dir="../../../bigmech/statement_classification/preannotation/input"
#interm_dir="../../../bigmech/statement_classification/preannotation/res_clauses_10-06"
#output_dir="../../../bigmech/statement_classification/preannotation/predictions_clause-fix_2015_09_10"

for file in `ls $input_dir`
do
  echo "Processing $file"
  int_file=`echo $file | sed 's/.txt/.res_clauses.txt/g'`
  out_file_tsv=`echo $file | sed 's/.txt/.res_preds.tsv/g'`
  out_file_xlsx=`echo $file | sed 's/.txt/.res_preds.xlsx/g'`
  python make_data.py $input_dir/$file $interm_dir/$int_file test
  python predict.py $interm_dir/$int_file $output_dir/$out_file_tsv
  ssconvert $output_dir/$out_file_tsv $output_dir/$out_file_xlsx
done
