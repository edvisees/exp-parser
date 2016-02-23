#Code for preparing data for statement classification, training the classifier and classifying new files

## Dependencies
* Stanford Basic English POS Tagger: Download from http://nlp.stanford.edu/software/stanford-postagger-2015-04-20.zip and install
* Stanford Parser: Download from http://nlp.stanford.edu/software/stanford-parser-full-2015-04-20.zip and install

Change the locations in PATHS to the paths to the tagger and parser

## SVM Classifier (clause level labeling)
### Training
* Input: Tab-separated file with clause in the first column and label in the second 
* Output: Cross-validation scores written to stderr and trained classifier saved to disk
* Run: `python train_classifier.py <input-file>`

### Prediction
* Input: Plain text file with one clause per line
* Output: Tab separated file with input clause in the first column and predicted label in the second
* Run: `python predict.py <input-file> <output-file>`

## CRF tagger (paragraph level labeling)
### Training
* Input: Tab-separated file with clause in the first column and label in the second, blank lines separating paragraphs
* Output: Cross-validation scores written to stderr and trained classifier saved to disk
* Run: `python train_passage_tagger.py <input-file>`

### Prediction
* Input: Plain text file with one clause per line, blank lines separating paragraphs
* Output: Tab separated file with input clause in the first column and predicted label in the second, writtent to stdout
* Run: `python tag_passages.py <input-file>`

Note: You can use `make_data.py` to separate passages into clauses:
`python make_data.py <input-passages-file> <output-clauses-file>`
