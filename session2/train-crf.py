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
    trainer.select('ap', 'crf1d')
    # ‘lbfgs’ for Gradient descent using the L-BFGS method,  73.7
    # ->‘l2sgd’ for Stochastic Gradient Descent with L2 regularization term 74.4
    # ‘ap’ for Averaged Perceptron  74.6
    # ‘pa’ for Passive Aggressive 74.5
    # ‘arow’ for Adaptive Regularization Of Weight Vector 62.4
    
    # This demonstrates how to list parameters and obtain their values.    
    trainer.set('feature.minfreq', 1) # mininum frequecy of a feature to consider it
    trainer.set('feature.possible_states', 0) # Force to generate possible state features.
    trainer.set('feature.possible_transitions', 0) # Force to generate possible transition features
    trainer.set('max_iterations', 50)  # The maximum number of iterations
    trainer.set('epsilon', 0.0)       # The stopping criterion (the ratio of incorrect label predictions)
    
    # trainer.set('c2', 0.1)          # coefficient for L2 regularization
    # trainer.set('c1', 0.01)
    # trainer.set('delta',1e-10)
    # trainer.set('period',10)
    # trainer.set('num_memories',10)

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
# feature.minfreq               1.0 The minimum frequency of features.
# feature.possible_states       False Force to generate possible state features.
# feature.possible_transitions  False Force to generate possible transition features.
# max_iterations                100 The maximum number of iterations.
# epsilon                       0.0 The stopping criterion (the ratio of incorrect label predictions).
# Feature generation
# type: CRF1d
# feature.minfreq: 1.000000
# feature.possible_states: 0
# feature.possible_transitions: 0
# 0....1....2....3....4....5....6....7....8....9....10
# Number of features: 59376
# Seconds required: 0.961

# Averaged perceptron
# max_iterations:   100
# epsilon:          0.000000