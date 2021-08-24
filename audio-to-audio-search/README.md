

# Find Similar Audio Cuts

In this example, the code check if the query audio clip is part of the indexed audio tracks.


## Prerequisites

The program in `app.py`  uses a `VGGISH` model to encode audio data and search audio data.

To use this code the user is required to first download one of:

1. the `VGGISH` model with the provided shell script:

```
bash download_vggish_model.sh
```

2. the `AudioCLIP` model with the provided shell script:

```
bash download_audio_clip_model.sh
```

Then, `cd` into the directory containing `requirements.txt` install the following:

```
sudo apt-get -y update && sudo apt-get install libsndfile1 ffmpeg
pip install -r requirements.txt
```



## Basic Usages

The `app.py` can be used in two shell commands:

```shell
python app.py index
```

will index the audio tracks in the `toy_data/index`. 

Then:

```shell
python app.py search
```

will read a set of query audio clips generated on the fly by extracting a portion of some index
audio clips and and predict whether they are part of the audio tracks.

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
