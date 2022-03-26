#! /bin/bash

BASEDIR=../

# convert datasets to feature vectors
# echo "Extracting features..."
# python3.7 extract-features.py $BASEDIR/data/train/ > Train/train.feat
# python3.7 extract-features.py $BASEDIR/data/devel/ > Devel/devel.feat
# python3.7 extract-features.py $BASEDIR/data/test/ > Test/test.feat

# train CRF model
echo "Training model..."
python3.7 train-crf.py model.crf < Train/train.feat
# run CRF model
echo "Running model..."
python3.7 predict.py model.crf < Train/train.feat > Train/train-CRF.out
python3.7 predict.py model.crf < Devel/devel.feat > Devel/devel-CRF.out
# python3.7 predict.py model.crf < Test/test.feat > Test/test-CRF.out
# evaluate CRF results
echo "Evaluating results..."
python3.7 $BASEDIR/util/evaluator.py NER $BASEDIR/data/train Train/train-CRF.out > Train/train-CRF-results.csv
python3.7 $BASEDIR/util/evaluator.py NER $BASEDIR/data/devel Devel/devel-CRF.out > Devel/devel-CRF-results.csv
# python3.7 $BASEDIR/util/evaluator.py NER $BASEDIR/data/test Test/test-CRF.out > Test/test-CRF-results.csv


# # train MEM model
# cat train.feat | cut -f5- | grep -v ^$ > train.mem.feat
# ./megam-64.opt -nobias -nc -repeat 4 multiclass train.mem.feat > model.mem
# rm train.mem.feat
# # run MEM model
# python3 predict.py model.mem < devel.feat > devel-MEM.out
# python3 predict.py model.mem < test.feat > test-MEM.out
# # evaluate MEM results
# python3 $BASEDIR/util/evaluator.py NER $BASEDIR/data/devel devel-MEM.out > devel-MEM.stats
# python3 $BASEDIR/util/evaluator.py NER $BASEDIR/data/test test-MEM.out > test-MEM.stats
