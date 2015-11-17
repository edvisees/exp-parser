#Code for preparing data for statement classification, training the classifier and classifying new files

## Dependencies
* Stanford Basic English POS Tagger: Download from http://nlp.stanford.edu/software/stanford-postagger-2015-04-20.zip and install
* Stanford Parser: Download from http://nlp.stanford.edu/software/stanford-parser-full-2015-04-20.zip and install

Change the locations in PATHS to the paths to the tagger and parser

## Training classifier
* Input: Tab-separated file with label in the first column and clause in the second 
* Output: Cross-validation scores written to stderr and trained classifier saved to disk
* Run: `python train_classifier.py <input-file>`

## Prediction
* Input: Plain text file with one clause per line
* Output: Tab separated file with input clause in the first column and predicted label in the second
* Run: `python predict.py <input-file> <output-file>`

Note: You can use `make_data.py` to separate passages into clauses:
`python make_data.py <input-passages-file> <output-clauses-file>`
