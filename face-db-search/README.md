In this demo, we use the  Labeled Faces in the Wild (LFW) Dataset data from [http://vis-www.cs.umass.edu/lfw/lfw.tgz](http://vis-www.cs.umass.edu/lfw/#download) to build a face search system so one can run facial search on their own dataset. Make sure you have gone through our lovely [Jina 101](https://github.com/jina-ai/jina/tree/master/docs/chapters/101) and understood the [take-home-message](https://github.com/jina-ai/examples/tree/master/urbandict-search#wrap-up) in [our bert-based semantic search demo](https://github.com/jina-ai/examples/tree/master/urbandict-search) before moving on. 

  


## <a name="custom-encoder">Overview</a>

The overall design is similar to the semantic search demo. We consider each image as a Document and put the RGB array in the Chunk. Therefore, each Document has a single Chunk. The pretrained `facenet` model is used to encode the Chunks into vectors. 

In this demo, we will show how to define a custom Encoder to support a variety of models and use the pretrained model for indexing and searching.

<p align="center">
  <img src=".github/dataset.png" alt="Dataset Example" width="90%">
</p>






-----




### Query

In Jina , Querying images located in 'image_src' folder is as simple as the following command.
'print_result' is the callback function used. Here the top k (here k=5) is returned. In this example, we use the meta_info tag in response to create the image. 

```python
from jina.flow import Flow
f = Flow.load_config('flow-index.yml')
with f:
    f.search_files(image_src, sampling_rate=.01, batch_size=8, output_fn=print_result, top_k=5)
```

Run the following command to search images and display them in a webpage.

```bash
python make_html.py
```

<details>
<summary>Click here to see result of old API</summary>

<p align="center">
  <img src=".github/query-demo.png?raw=true" alt="query flow console output">
</p>

</details> 

<img src=".github/face-demo.jpg" alt="query flow console output">
</p>
Note : We have only used 500 images with only one or two images of each person. Hence the results are only as good as the database you have. It returns the closest matching face in the dataset.

<br /><br />

