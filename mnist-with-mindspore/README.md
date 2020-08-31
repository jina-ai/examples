# MNIST Search with Mindspore

## Train LeNet with Mindspore

Get the tutorial example file from https://gitee.com/mindspore/docs/blob/r0.6/tutorials/tutorial_code/lenet.py


```bash
cd mnist-with-mindspore
python lenet.py
```

The above script will load the MNIST dataset and train `LeNet5`. After training, the trained model is saved at `checkpoint_lenet-1_1875.ckpt` and folder structure is as following,

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

We define a new network `LeNetFeat` in `pods/lenet_mindspore.py`. This network share the most operations with the `LeNet` that is trained in the previous section. The only difference is that  the last operation `self.fc3(x)` is removed in order to get the feature representation from the second last layer. `LeNetFeat` is used to encode the image into a dense vector in the size of `(1, 84)`.

```
class LeNet5Feat(LeNet5):
    def construct(self, x):
        x = self.conv1(x)
        x = self.relu(x)
        x = self.max_pool2d(x)
        x = self.conv2(x)
        x = self.relu(x)
        x = self.max_pool2d(x)
        x = self.flatten(x)
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        x = self.relu(x)
        return x
```

Besides, `MnistImageReader` is defined to convert the `mnist` data vector in the size of `(1, 784)` to an image in the size of `(3, 28, 28)`. The image is store in the `blob` field of the `Document`. Afterwards, the image in the `blob` is resized to `(3, 32, 32)` in order to fit to `LeNet`'s input shape.

## Search the data

```bash
python app.py -t query
```

The results is shown at `results.html`


## TODOs

- [ ] Check out the reason why the images are flipped in the `results.html`.
