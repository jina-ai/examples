import os
import zipfile
import csv
from collections import defaultdict
import json
from io import TextIOWrapper

# create the new directory for saving data
data_fn = "urbandict-word-defs.json"
root_path = '/tmp/jina/'
demo_name = 'urbandict'
data_path = os.path.join(root_path, demo_name)
if not os.path.exists(data_path):
    print("data output dir: {}".format(data_path))
    if not os.path.exists(root_path):
        os.mkdir(root_path)
    os.mkdir(data_path)

# unzip the data and sorted
raw_fn = 'urban-dictionary-words-dataset.zip'
illegal_counts = 0
word2def = []
illegal_dump = []
stats_list = []
with zipfile.ZipFile(os.path.join('/tmp', raw_fn)) as z:
    with z.open('urbandict-word-defs.csv', 'r') as f:
        r = csv.reader(TextIOWrapper(f, 'utf-8'))
        for idx, l in enumerate(r):
            if idx == 0:  # skip the header
                continue
            if len(l) != 6:  # drop the empty lines
                illegal_counts += 1
                print(''.format(l))
                continue
            _, word, up_votes, down_votes, _, word_def = l
            up_votes = int(up_votes)
            down_votes = int(down_votes)
            weight = up_votes * 1.0 / down_votes if down_votes != 0 else up_votes
            if len(word_def) == 0:
                continue
            if up_votes <= 2 or (up_votes+down_votes) <= 4 or weight <= 1.0:
                # filter out the entries that have too few up-votes
                continue
            if len(word) <= 1 or len(word) > 16:
                # filter out the entries that are too short or too long
                continue
            if not word:
                # filter out the empty entries
                continue
            word = word.lower().strip()
            stats_list.append(f'{word},{up_votes},{down_votes},{weight}')
            word2def.append({"word": word, "text": word_def, "weight": weight})
print("illegal counts: {}/{}".format(illegal_counts, idx))
print("word2def size: {}/{}".format(len(frozenset([w['word'] for w in word2def])), idx))
print("definition size: {}/{}".format(len(word2def), idx))

tmp_data_path = os.path.join(data_path, data_fn)

with open(tmp_data_path, 'w') as f:
    json.dump(word2def, f, ensure_ascii=False, indent=4)

with open(os.path.join(data_path, 'stats.csv'), 'w') as f:
    f.write('\n'.join(stats_list))
