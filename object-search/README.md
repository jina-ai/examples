
# Object detection with fasterrcnn and MobileNetV2

# Overview
| Parameter | Description |
| ------------- | ------------- |
| Learnings | How Jina can help you with Object search |
| Used for indexing | Dataset of images |
| Used for querying | An image |
| Dataset used | [Flickr8k](https://www.kaggle.com/adityajn105/flickr8k) |
| Model used | [fasterrcnn_resnet50_fpn](https://pytorch.org/vision/stable/_modules/torchvision/models/detection/faster_rcnn.html), [MobileNetV2](https://keras.io/api/applications/mobilenet/) |

In this example, we use [`fasterrcnn_resnet50_fpn`](https://pytorch.org/vision/stable/_modules/torchvision/models/detection/faster_rcnn.html) for object detection (finding the bounding boxes of objects in the image) and then index these cropped object images with [`MobileNetV2`](https://keras.io/api/applications/mobilenet/). This example will show you how to index an image dataset and query for the most similar objects in those images.

# 🐍 Build yourself and deploy with Python
You can build this example yourself and deploy it with Python. This allows you to see each step in the process better. 

## Pre requirements:
1. You have a working Python 3.8 environment 
2. We recommend creating a [new python virtual envoriment](https://docs.python.org/3/tutorial/venv.html) to have a clean install.  
3. You have at least 8GB of free space on your hard drive. 


## Step 1. Clone the repo and install Jina

Begin by cloning the repo so you can get the required files and datasets. 

```shell
git clone https://github.com/jina-ai/examples
cd examples/object-search
```

On your terminal,  you should now be located in you the `object-search` folder. Let's install Jina and the other required python libraries. 

```shell
pip install -r requirements.txt
```

## Step 2. Download the dataset

We will run this example with the [Flickr8k](https://www.kaggle.com/adityajn105/flickr8k)  object detection dataset. 

Flickr8k is a dataset of 8,000 images each paired with a short description of entities and objects contained in this image.

1. Create a [Kaggle](https://www.kaggle.com/) account
2. Set up Kaggle API keys according to the instructions [here](https://github.com/Kaggle/kaggle-api)
3. Download the Flickr8k from [Kaggle](https://www.kaggle.com/)

```shell
kaggle datasets download adityajn105/flickr8k
unzip flickr8k.zip 
rm flickr8k.zip
mkdir -p data/f8k/
mv Images data/f8k/images
```

Note: We are using Flickr8k here due to its small size which means the example can run faster. Feel free to experiment with other datasets like  [COCO](https://cocodataset.org/#home)  &  [Open Images 2019](https://www.kaggle.com/c/open-images-2019-object-detection/overview) or many other image datasets you can find online.


## Step 2. Indexing your data

Let's start with by indexing only 1000 images to save time. If it still takes too much time, you can reduce the number even more but keep in mind this will affect the quality of results.

```shell
python app.py -t index -n 1000 -overwrite True
```

To index the entire dataset simply run: (This will take a lot longer)

```shell
python app.py -t index -n 8000 -overwrite True
```

During Indexing, our Flow logic is performing the following steps.
1. Iterate through all images and identify various objects contained.
2. Identify the bounding boxes of objects contained in the image and their labels.
3. Store all of the occurences for each object type.
![image](https://user-images.githubusercontent.com/23415764/116535968-b190d180-a8e4-11eb-9197-5f20ddf2682b.png)

## Step 3. Start the server
You can test this example with two different Query Flows; object and original.

The object Query Flow works as follows:
1. Identify the object in the query image
2. Find all other images that contain this object
3. Order the images by best match

The `flow-query-object.yml` will return a cropped image containing the `object` identified in the query image. To start the `flow-query-object.yml` run the following

```shell
python app.py -t query -r object
```

![image](https://user-images.githubusercontent.com/23415764/116536115-d422ea80-a8e4-11eb-934b-503fe5cfe296.png)

The `flow-query-original.yml` Flow will search all indexed object images and return the original parent image in which the object was found. Start the server which returns the `original` images by running

```shell
python app.py -t query -r original
```
The original Query Flow works as follows:
1. Find the maching cropped images as with the object Flow
2. Identify the parent images and return them as the result of the query
![image](https://user-images.githubusercontent.com/23415764/116536214-f0bf2280-a8e4-11eb-9ec3-92ca1aa7e167.png)

## Step 4. 🔍 Search your data
Jina offers several different ways to search (query) your data. In this example, we show two of the most common ones. 


### Option 1: Using Jina REST API
Begin by running the following command to open the REST API interface.

When the REST gateway is enabled, Jina uses the  [data URI scheme](https://en.wikipedia.org/wiki/Data_URI_scheme)  to represent multimedia data such as images and allow them to be transfered using HTTP.

In order to query using the REST API:
1. Pick the images that you want to inlcude in your query.
2. Convert them to a data URI format (for testing you can use any 'image to URI' converter tool)
3. Simply send a POST request to  `http://0.0.0.0:45678/api/search` with the following parameters in the payload

| Parameter | Description |
| ------------- | ------------- |
| top_k | Number of top results the query will return|
| mode | Should be one of `index`, `train` and `search`. In order to query choose `search` |
| data | A list of all query images in a data URI format (you can query for more than 1 image in a signle request)|

You can read more about the Jina `/api/search` endpoint and its JSON syntax [here](https://docs.jina.ai/chapters/restapi/#).

Below is an example request made using CURL (a query request with 2 images that will return 10 top matching results)
```sh
curl --verbose --request POST -d '{"top_k": 10, "mode": "search",  "data": ["data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAIAAABLbSncAAAA2ElEQVR4nADIADf/AxWcWRUeCEeBO68T3u1qLWarHqMaxDnxhAEaLh0Ssu6ZGfnKcjP4CeDLoJok3o4aOPYAJocsjktZfo4Z7Q/WR1UTgppAAdguAhR+AUm9AnqRH2jgdBZ0R+kKxAFoAME32BL7fwQbcLzhw+dXMmY9BS9K8EarXyWLH8VYK1MACkxlLTY4Eh69XfjpROqjE7P0AeBx6DGmA8/lRRlTCmPkL196pC0aWBkVs2wyjqb/LABVYL8Xgeomjl3VtEMxAeaUrGvnIawVh/oBAAD///GwU6v3yCoVAAAAAElFTkSuQmCC", "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAIAAABLbSncAAAA2ElEQVR4nADIADf/AvdGjTZeOlQq07xSYPgJjlWRwfWEBx2+CgAVrPrP+O5ghhOa+a0cocoWnaMJFAsBuCQCgiJOKDBcIQTiLieOrPD/cp/6iZ/Iu4HqAh5dGzggIQVJI3WqTxwVTDjs5XJOy38AlgHoaKgY+xJEXeFTyR7FOfF7JNWjs3b8evQE6B2dTDvQZx3n3Rz6rgOtVlaZRLvR9geCAxuY3G+0mepEAhrTISES3bwPWYYi48OUrQOc//IaJeij9xZGGmDIG9kc73fNI7eA8VMBAAD//0SxXMMT90UdAAAAAElFTkSuQmCC"]}' -H 'Content-Type: application/json' 'http://0.0.0.0:45678/api/search'
```

### Option 2: Using JinaBox; our frontend search interface

**JinaBox** is a light-weight, highly customizable JavaScript based front-end search interface. To use it for this example, begin by opening the REST API interface. 

In your browser, open up the hosted JinaBox  on [jina.ai/jinabox.js](https://jina.ai/jinabox.js/).  In the configuration bar on the left hand side, choose a custom endpoint and enter the following information  `http://127.0.0.1:45678/search` . You can drag and drop query images into the text box on the right hand side!

# Overview of the files in this example
Here is a small overview if you're interested in understanding what each file in this example is doing. 

`app.py`  - main orchestrator of the indexing and querying process. Flows are created and and run from here.

`flow-index.yml` - Index Flow configuration 

`flow-query-object.yml` - Query Flow definition for finding cropped images of Objects

`flow-query-original.yml` - Query Flow definition for finding entire parent images

`pods/chunk.yml` - 

`pods/craft-normalize.yml` - 

`pods/craft-object.yml` - 

`pods/craft-reader.yml` - 

`pods/doc.yml` - 

`pods/encode.yml` - 

`pods/rank.yml` - 

`pods/vec.yml` - 

`test/*` - various maintenance tests to keep the example running. 

`requirements.txt` - contains all required python libraries


# Next steps, building your own app
Did you like this example and are you interested in building your own? For a detailed tuturial on how to build your Jina app check out [How to Build Your First Jina App](https://docs.jina.ai/chapters/my_first_jina_app/#how-to-build-your-first-jina-app) guide in our documentation. 

If you have any issues following this guide, you can get support from our [Slack community](https://join.slack.com/t/jina-ai/shared_invite/zt-dkl7x8p0-rVCv~3Fdc3~Dpwx7T7XG8w) .

# Community

- [Slack channel](https://join.slack.com/t/jina-ai/shared_invite/zt-dkl7x8p0-rVCv~3Fdc3~Dpwx7T7XG8w) - a communication platform for developers to discuss Jina
- [Community newsletter](mailto:newsletter+subscribe@jina.ai) - subscribe to the latest update, release and event news of Jina
- [LinkedIn](https://www.linkedin.com/company/jinaai/) - get to know Jina AI as a company and find job opportunities
- [![Twitter Follow](https://img.shields.io/twitter/follow/JinaAI_?label=Follow%20%40JinaAI_&style=social)](https://twitter.com/JinaAI_) - follow us and interact with us using hashtag `#JinaSearch`  
- [Company](https://jina.ai) - know more about our company, we are fully committed to open-source!

# License

Copyright (c) 2021 Jina AI Limited. All rights reserved.

Jina is licensed under the Apache License, Version 2.0. See LICENSE for the full license text.
