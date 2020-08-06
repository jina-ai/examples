# Vector Indexer based on Faiss

This image is used for running a pod with a vector indexer running inside. The vector indexer is based on Faiss. 

Please find more information about Faiss at [https://github.com/facebookresearch/faiss/](https://github.com/facebookresearch/faiss/).

## Usages

By default, the pod will save the index at `/workspace`. The training data for Faiss index is expected to be at `/data/train.tgz`. Here are sample codes for generating the training data.

```python
import gzip
import numpy as np
train_filepath = 'train.tgz'
train_data = np.random.rand(10000, 128)
with gzip.open(train_filepath, 'wb', compresslevel=1) as f:
    f.write(train_data.astype('float32'))
```

To run the pods in production, you will need to map a local volume to the index folder when running the pod. With the following lines, we run the pod with the local folder `./workspace ` being mapped to `/workspace` and `./data` being mapped to `/data`. The training data is supposed to be at `./data/train.tgz`

```bash
jina pod --image jinaai/hub.executors.indexers.vector.faiss:latest --volumes "$(pwd)/workspace" --volumes "$(pwd)/data"
```

To further customize the pod, you can use your own `.yml` file as well. For example, you are highly possible to prefer a simple PCA-based index method rather than the default `IVF10,PQ4`. Here is the customized `.yml`, namely, `./yaml/my_awesome.yml`. You can find more details about the index methods at [https://github.com/facebookresearch/faiss/wiki/The-index-factory](https://github.com/facebookresearch/faiss/wiki/The-index-factory).

```yaml
!FaissIndexer
with:
  index_key: 'PCA80,Flat'
  index_filename: 'faiss.tgz'
  train_filepath: './data/train.tgz'
metas:
  workspace: './workspace'
```

To load the customized `.yml` file, one needs to specify the `--yaml_path` when running the pod as follwing, 

```bash
jina pod --image jinaai/hub.executors.indexers.vector.faiss:latest --volumes "$(pwd)/workspace --volumes "$(pwd)/data --volumes "$(pwd)/yaml --yaml_path /yaml/my_awesome.yml"
```


## Build locally

You are encouraged to customize and improve the image. The following commands are for building and testing your own image,

```bash
cd hub/executors/indexers/vector/faiss
docker build -t jinaai/hub.executors.indexers.vector.your_awesome_faiss .
docker run -v "$(pwd)/workspace:/workspace" jinaai/hub.executors.indexers.vector.your_awesome_faiss:latest
```

## Reference
- documents about running pods in containers: [https://docs.jina.ai/chapters/cli/jina-pod.html#pea%20container%20arguments](https://docs.jina.ai/chapters/cli/jina-pod.html#pea%20container%20arguments)

## License

Copyright (c) 2020 Jina AI Limited. All rights reserved.

Jina is licensed under the Apache License, Version 2.0. See [LICENSE](https://github.com/jina-ai/jina/blob/master/LICENSE) for the full license text.