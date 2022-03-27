#!/usr/bin/env python3

import pycrfsuite
import sys
from contextlib import redirect_stdout

def instances(fi):
    xseq = []
    yseq = []
    
    for line in fi:
        line = line.strip('\n')
        if not line:
            # An empty line means the end of a sentence.
            # Return accumulated sequences, and reinitialize.
            yield xseq, yseq
            xseq = []
            yseq = []
            continue

        # Split the line with TAB characters.
        fields = line.split('\t')
        
        # Append the item features to the item sequence.
        # fields are:  0=sid, 1=form, 2=span_start, 3=span_end, 4=tag, 5...N = features
        item = fields[5:]        
        xseq.append(item)
        
        # Append the label to the label sequence.
        yseq.append(fields[4])


if __name__ == '__main__':

    # get file where model will be written
    modelfile = sys.argv[1]
    
    # Create a Trainer object.
    trainer = pycrfsuite.Trainer()
    
    # Read training instances from STDIN, and append them to the trainer.
    for xseq, yseq in instances(sys.stdin):
        trainer.append(xseq, yseq, 0)

    # Use L2-regularized SGD and 1st-order dyad features.
    trainer.select('l2sgd', 'crf1d')
    
    # This demonstrates how to list parameters and obtain their values.    
    trainer.set('feature.minfreq', 1) # mininum frequecy of a feature to consider it
    trainer.set('c2', 0.1)           # coefficient for L2 regularization
    trainer.set('delta',1e-10)
    trainer.set('period',10)
    # trainer.set('max_iterations',2000)
    # trainer.set('feature.possible_states',1)

    # trainer.set('calibration.eta', 0.2)
    # trainer.set('calibration.rate', 1.5)



    print("Training with following parameters: ")
    for name in trainer.params():
        print (name, trainer.get(name), trainer.help(name), file=sys.stderr)
        
    # Start training and dump model to modelfile
    trainer.train(modelfile, -1)

# Training with following parameters: 
# feature.minfreq           1.0         The minimum frequency of features.
# feature.possible_states   False       Force to generate possible state features.
# feature.possible_transitions False    Force to generate possible transition features.
# c2                        0.1         Coefficient for L2 regularization.
# max_iterations            1000        The maximum number of iterations (epochs) for SGD optimization.
# period                    10          The duration of iterations to test the stopping criterion.
# delta                     1e-06       The threshold for the stopping criterion; an optimization process stops when
#                                       the improvement of the log likelihood over the last ${period} iterations is no
#                                       greater than this threshold.
# calibration.eta           0.1         The initial value of learning rate (eta) used for calibration.
# calibration.rate          2.0         The rate of increase/decrease of learning rate for calibration.
# calibration.samples       1000.0      The number of instances used for calibration.
# calibration.candidates    10          The number of candidates of learning rate.
# calibration.max_trials    20          The maximum number of trials of learning rates for calibration.
# Feature generation
# type:                         CRF1d
# feature.minfreq:              1.000000
# feature.possible_states:      0
# feature.possible_transitions: 0
# 0....1....2....3....4....5....6....7....8....9....10
# Number of features:           133841
# Seconds required:             1.768

# Stochastic Gradient Descent (SGD)
# c2:               0.100000
# max_iterations:   1000
# period:           10
# delta:            0.000001