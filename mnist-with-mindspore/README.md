# MNIST Search with Mindspore

## Train LeNet with Mindspore

Get the tutorial example file from https://gitee.com/mindspore/docs/blob/r0.6/tutorials/tutorial_code/lenet.py


```bash
cd mnist-with-mindspore
python lenet.py
```

The above script will load the MNIST dataset and train `LeNet5`. the folder structure is 

```bash
.
├── MNIST_Data
│   ├── test
│   │   ├── t10k-images-idx3-ubyte
│   │   └── t10k-labels-idx1-ubyte
│   └── train
│       ├── train-images-idx3-ubyte
│       └── train-labels-idx1-ubyte
├── README.md
├── app.py
├── checkpoint_lenet-1_1875.ckpt
└── train.py

```

## Index the data

```bash
python app.py -t index -n 100
```

## Search the data

```bash
python app.py -t query
```

The results is shown at `results.html`


## TODOs

We still need to figure out how to extract the outputs of the second last layer.

reference:

[https://github.com/mindspore-ai/mindspore/issues/76](https://github.com/mindspore-ai/mindspore/issues/76#issuecomment-675840001)