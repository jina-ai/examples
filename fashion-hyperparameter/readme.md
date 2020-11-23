# Fashion-MNIST Evaluate & Optimize  
This examples showcases evaluation capabilities of Jina. You can use evaluation to try out different components and select the best. To make it easier we also show how to use Optuna to optimise faster. We are using the fashion-MNIST dataset for this purpose. It has greyscale cloth images and 10 type of category labels. 

We use the label of images for evaluating our encoder. We optimize `target_dimension` in encoder for metric precision@1.

## Installation  
```pip install requirements.txt```

## Evaluation  
First we index all the images along with its category as label. We define a custom evaluator in `pods/evaluate.py` which checks if the label of first result matches with the label of query image. Then we query with a pair of query and groundtruth. Query consists of image while groundtruth consists of true label.  

Running `python evaluate.py` will download data, index it and run the evaluation.   

## Optimize  
Define the parameter to be optimised in `sample_run_parameters` in `optimize.py`. On running `python optimize.py` it uses `Optuna` to run evaluations for our metric which is mean precision@1. It finally prints out the best parameters. Increase `n_trials` in `optimize.py` to run more experiments.   

## Serving for query  
Now manually fix up best value of hyperparameter `target_dimension` we found by optimizing, in `encoder.yml` to serve for query.  
Run `jina run flow flow/query.yml` to start the server for querying.  

## Modules
```
├── fashion
│   ├── config.py -> define jina config + hyperparameters
│   ├── data.py -> downloads the data
│   └── evaluation.py -> modules required for evaluation
│
├── flows
│   ├── evaluate.yml -> evaluate flow
│   ├── index.yml -> index flow
│   └── query.yml -> query flow
│
├── evaluate.py -> run this to get the evaluation
├── optimize.py -> define optuna parameters & run this to find the best parameters
│
├── pods
│   ├── components.py -> custom encoder
│   ├── encoder.yml
│   ├── evaluate.py -> custom evaluator
│   ├── evaluate.yml
│   ├── indexer.yml
│   └── reduce.yml
│
├── readme.md
└── requirements.txt
```