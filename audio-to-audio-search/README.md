

# Find Similar Audio Cuts

This example checks if the query audio clip is part of the indexed audio tracks.


## Prerequisites

To run this example, the user is required to `cd` into the directory containing
`requirements.txt` and download one of:

1. `VGGISH` model with the provided shell script:

```
bash download_vggish_model.sh
```

2. `AudioCLIP` model with the provided shell script:

```
bash download_audio_clip_model.sh
```

Then, install the following:

```
sudo apt-get -y update && sudo apt-get install libsndfile1 ffmpeg
pip install -r requirements.txt
```



## Basic Usages

You can run `app.py` by doing the following:

```shell
python app.py index
```

will index the audio tracks in the `data/index`. 

Then:

```shell
python app.py search
```

will generate a set of query audio clips on the fly by extracting snippets from a set of randomly sampled
of index audio clips. The program then matches each query doc with the most similar index docs.

The `-s` option allows user to specify which segmenter to use. `vad` uses Jinahub's VADSpeechSegmenter,  and
`time` uses TimeSegmenter.

The `-e` option allows user to specify which encoder to use. `vgg` uses Jinahub's VGGishEncoder,  and
`clip` uses AudioCLIPEncoder.

The `-t` option allows user to specify what the match threshold is. If score of match is below threshold,
then it is not considered a match.



## Results and Demo

An example result is shown below:

```
+-------------+-------------+------------+
|    target   |  prediction | is_correct |
+-------------+-------------+------------+
| -BHPu-dPmWQ | -BHPu-dPmWQ |    True    |
| -HKAgW-vzSI | -HKAgW-vzSI |    True    |
| -Irh7_N5Kjs | -Irh7_N5Kjs |    True    |
| -aJYgmhyrvQ | 0MEPG8c0jqk |   False    |
| -dVgUSrR8g4 | -dVgUSrR8g4 |    True    |
| -xfgovG6-KU | -xfgovG6-KU |    True    |
| 0D9ZiiYArKw | 0D9ZiiYArKw |    True    |
| 0J_TdiZ3TKA | 0J_TdiZ3TKA |    True    |
| 0PMFAO4TIU4 | 0PMFAO4TIU4 |    True    |
| 0RcMzUdXDRQ | 0RcMzUdXDRQ |    True    |
| 0SLv6CmZas8 | 0SLv6CmZas8 |    True    |
| 0XeH2s-LzZE | 0XeH2s-LzZE |    True    |
| 0ZN2HKsFg4A | 0ZN2HKsFg4A |    True    |
| 0bP2MH3LqvI | 0bP2MH3LqvI |    True    |
| 0fqtA_ZBn_8 | 0fqtA_ZBn_8 |    True    |
| 0k6KjLouAHs | 0k6KjLouAHs |    True    |
| 0wgqpjfTmJI | 0wgqpjfTmJI |    True    |
+-------------+-------------+------------+
```

```shell
accuracy: 0.9411764705882353
```

After searching is completed, the program will open `demo.html` where user can click
to listen to the query and matched docs.
