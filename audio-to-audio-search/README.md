

# Find Similar Audio Clips

This example checks if the query audio clip is part of the indexed audio tracks.

![Demo](.github/demo.png)

## Prerequisites

To run this example, the user is required to `cd` into the directory containing
`requirements.txt` to install:

```
sudo apt-get -y update && sudo apt-get install libsndfile1 ffmpeg
pip install -r requirements.txt
```



## Basic Usages

You can run `app.py` by doing the following:

```shell
python app.py index
```

By default, audio tracks in the `data/mp3/index` will be indexed. You can specify custom data path by:

```
export JINA_DATA_FILE=<custom_data_path>
```
where audios to be indexed are stored in `<custom_data_path>/index`.


Then, to search the documents, do:

```shell
python app.py search
```

This will generate a set of query audio clips on the fly in `data/mp3/query` (or, if you are using
custom data path, in `<custom_data_path>/query`) by extracting snippets from a set of randomly sampled
of index audio clips. The program then matches each query doc with the most similar index docs.

The `-s` option allows user to specify which segmenter to use. `vad` uses Jinahub's VADSpeechSegmenter, and
`time` uses TimeSegmenter.

The `-e` option allows user to specify which encoder to use. `vgg` uses Jinahub's VGGishEncoder, and
`clip` uses AudioCLIPEncoder.

The `-t` option allows user to specify what the match threshold is. If score of match is below threshold,
then it is not considered a match.



## Results and Demo



Results are as follows.

With `segmenter=VADSpeechSegmenter` and `encoder=AudioCLIPEncoder`:

```
+-------------+-------------+------------+ 
|    target   |  prediction | is_correct | 
+-------------+-------------+------------+ 
| -0jeONf82dE | -0jeONf82dE |    True    | 
| -CXICIHCb6Y | -CXICIHCb6Y |    True    | 
| -OMB-w3LPNY | -By6I234TSs |   False    | 
| -QX2Gv7J5gY | -QX2Gv7J5gY |    True    | 
| -UKH_6moRZc | -UKH_6moRZc |    True    | 
| -ZJqu_4zLMc | -ZJqu_4zLMc |    True    | 
| -gz_moHFwl4 | -gz_moHFwl4 |    True    | 
| -i9uQMysy_A | -mKtgDnG0oM |   False    | 
| -mpapCZXors | -mpapCZXors |    True    | 
| 0KKTw8pfNjg | 0KKTw8pfNjg |    True    | 
| 0LTmV_dOmmo | 0LTmV_dOmmo |    True    | 
| 0N17tEW_WEU | 0N17tEW_WEU |    True    | 
| 0YIWrXgCjiM | 0YIWrXgCjiM |    True    | 
| 0YsC6M4GFoc | 0YsC6M4GFoc |    True    | 
| 0_O6nVfnCH8 | -sevczF5etI |   False    | 
| 0cZQm65sZjc | 0cZQm65sZjc |    True    | 
| 0jnvb2H25_Q | 0jnvb2H25_Q |    True    | 
| 0kQjfwXjFuY | -D--GWwca0g |   False    | 
| 0rbUCEM20aw | 0rbUCEM20aw |    True    | 
| 0slyl34xWug | 0slyl34xWug |    True    | 
+-------------+-------------+------------+ 
accuracy: 0.8
```

With `segmenter=TimeSegmenter` and `encoder=AudioCLIPEncoder`:

```
+-------------+-------------+------------+
|    target   |  prediction | is_correct |
+-------------+-------------+------------+
| -Bu7YaslRW0 | -Bu7YaslRW0 |    True    |
| -CXICIHCb6Y | -CXICIHCb6Y |    True    |
| -D--GWwca0g | -D--GWwca0g |    True    |
| -OMB-w3LPNY | -OMB-w3LPNY |    True    |
| -Z8bjo6q6jc | -CXICIHCb6Y |   False    |
| -ZJqu_4zLMc | -ZJqu_4zLMc |    True    |
| -_HXiz8XnV0 | -_HXiz8XnV0 |    True    |
| -fz6omiAhZ8 | -fz6omiAhZ8 |    True    |
| -mpapCZXors | -jaY3LS3Dv0 |   False    |
| 05JAmKFVy44 | 05JAmKFVy44 |    True    |
| 0YIWrXgCjiM | 0YIWrXgCjiM |    True    |
| 0YsC6M4GFoc | 0YsC6M4GFoc |    True    |
| 0ZN2HKsFg4A | 0ZN2HKsFg4A |    True    |
| 0_O6nVfnCH8 | 0_O6nVfnCH8 |    True    |
| 0cZQm65sZjc | 0cZQm65sZjc |    True    |
| 0izHOfrwPn4 | 0izHOfrwPn4 |    True    |
| 0qZ54ovyEWQ | 0qZ54ovyEWQ |    True    |
| 0sYXPO7lzco | 0sYXPO7lzco |    True    |
| 0slyl34xWug | 0slyl34xWug |    True    |
| 0vg9qxNKXOw | 0vg9qxNKXOw |    True    |
+-------------+-------------+------------+
accuracy: 0.9
```

With `segmenter=TimeSegmenter` and `encoder=VGGishAudioEncoder`:

```
+-------------+-------------+------------+
|    target   |  prediction | is_correct |
+-------------+-------------+------------+
| -Bu7YaslRW0 | -Bu7YaslRW0 |    True    |
| -IvJaK7HLtQ | -IvJaK7HLtQ |    True    |
| -OMB-w3LPNY | -OMB-w3LPNY |    True    |
| -QX2Gv7J5gY | -QX2Gv7J5gY |    True    |
| -UKH_6moRZc | -UKH_6moRZc |    True    |
| -ZJqu_4zLMc | -ZJqu_4zLMc |    True    |
| -mKtgDnG0oM | -mKtgDnG0oM |    True    |
| -mpapCZXors | -mpapCZXors |    True    |
| -nlkWWphiaM | -nlkWWphiaM |    True    |
| -pUfYFcsgG4 | -pUfYFcsgG4 |    True    |
| -sevczF5etI | -sevczF5etI |    True    |
| 0N17tEW_WEU | 0N17tEW_WEU |    True    |
| 0XeH2s-LzZE | 0XeH2s-LzZE |    True    |
| 0YIWrXgCjiM | 0YIWrXgCjiM |    True    |
| 0YsC6M4GFoc | 0YsC6M4GFoc |    True    |
| 0bRUkLsttto | 0bRUkLsttto |    True    |
| 0izHOfrwPn4 | 0izHOfrwPn4 |    True    |
| 0jFQ21A6GRA | 0jFQ21A6GRA |    True    |
| 0sYXPO7lzco | 0sYXPO7lzco |    True    |
| 0vg9qxNKXOw | 0vg9qxNKXOw |    True    |
+-------------+-------------+------------+
accuracy: 1.0
```

With `segmenter=VADSpeechSegmenter` and `encoder=VGGishAudioEncoder`:

```
+-------------+-------------+------------+
|    target   |  prediction | is_correct |
+-------------+-------------+------------+
| -0jeONf82dE | -0jeONf82dE |    True    |
| -OMB-w3LPNY | 0sYXPO7lzco |   False    |
| -QX2Gv7J5gY | 0LTmV_dOmmo |   False    |
| -WKYdeVL3_k | -WKYdeVL3_k |    True    |
| -Z8bjo6q6jc | -Z8bjo6q6jc |    True    |
| -_HXiz8XnV0 | -_HXiz8XnV0 |    True    |
| -e4wXAy1iVo | -e4wXAy1iVo |    True    |
| -gz_moHFwl4 | -gz_moHFwl4 |    True    |
| -i9uQMysy_A | -i9uQMysy_A |    True    |
| -jaY3LS3Dv0 | -jaY3LS3Dv0 |    True    |
| -sevczF5etI | -sevczF5etI |    True    |
| 05JAmKFVy44 | 05JAmKFVy44 |    True    |
| 0N17tEW_WEU | 0N17tEW_WEU |    True    |
| 0OY8XXZ98rw | -0jeONf82dE |   False    |
| 0YIWrXgCjiM | 0YIWrXgCjiM |    True    |
| 0rbUCEM20aw | 0rbUCEM20aw |    True    |
| 0vg9qxNKXOw | 0vg9qxNKXOw |    True    |
+-------------+-------------+------------+
accuracy: 0.8235294117647058
```

After searching is completed, the program will open `demo.html` where user can click
to listen to the query and matched docs.
