__copyright__ = 'Copyright (c) 2020 Jina AI Limited. All rights reserved.'
__license__ = 'Apache-2.0'

import csv
import itertools
import json
import os
import sys
import subprocess

from jina.flow import Flow
import pytest
from jina.proto import jina_pb2

TOP_K = 3
INDEX_FLOW_FILE_PATH = 'flows/index.yml'
QUERY_FLOW_FILE_PATH = 'flows/query.yml'
PORT = 45678


# TODO restructure project so we don't duplicate input_fn
def input_fn():
    lyrics_file = os.environ.get('JINA_DATA_FILE')
    with open(lyrics_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in itertools.islice(reader, int(os.environ.get('JINA_MAX_DOCS'))):
            if row[-1] == 'ENGLISH':
                d = jina_pb2.Document()
                d.tags['ALink'] = row[0]
                d.tags['SName'] = row[1]
                d.tags['SLink'] = row[2]
                d.text = row[3]
                yield d


def config(tmpdir):
    parallel = 2 if sys.argv[1] == 'index' else 1

    os.environ.setdefault('JINA_MAX_DOCS', '100')
    os.environ.setdefault('JINA_PARALLEL', str(parallel))
    os.environ.setdefault('JINA_SHARDS', str(1))
    os.environ.setdefault('JINA_WORKSPACE', str(tmpdir))
    os.environ.setdefault('JINA_DATA_FILE', 'tests/data-index.csv')
    os.environ.setdefault('JINA_PORT', str(PORT))

    os.makedirs(os.environ['JINA_WORKSPACE'], exist_ok=True)
    return


def index_documents():
    f = Flow().load_config(INDEX_FLOW_FILE_PATH)

    with f:
        f.index(input_fn)


def call_api(url, payload=None, headers=None):
    if headers is None:
        headers = {'Content-Type': 'application/json; charset=utf-8'}
    import requests

    return requests.post(url, data=json.dumps(payload), headers=headers).json()


def get_results(query, top_k=TOP_K):
    return call_api(
        f'http://0.0.0.0:{PORT}/api/search', payload={'top_k': top_k, 'data': [query]}
    )


def get_flow():
    f = Flow().load_config(QUERY_FLOW_FILE_PATH)
    f.use_rest_gateway()
    return f


@pytest.fixture
def queries_and_expected_replies():
    return [
        (
            'Trudging slowly\n',
            [
                "Trudging slowly over wet sand. Back to the bench where your clothes were "
                "stolen. This is a coastal town. That they forgot to close down. Armagedon - "
                "come armagedon come armagedon come. Everyday is like sunday. Everyday is "
                "silent and grey. Hide on a promanade. Etch on a post card:. How I dearly "
                "wish I was not here. In the seaside town. That they forgot to bomb. Come, "
                "come nuclear bomb!. Everyday is like sunday. Everyday is silent and grey. "
                "Trudging back over pebbles and sand. And a strange dust lands on your hands. "
                "(and on your face). Everyday is like sunday. Win yourself a cheap tray. "
                "Share some grease tea with me. Everyday is silent and grey",
                "These are. These are days you'll remember. Never before and never since, I "
                "promise. Will the whole world be warm as this. And as you feel it,. You'll "
                "know it's true. That you - you are blessed and lucky. It's true - that you. "
                "Are touched by something. That will grow and bloom in you. These are days "
                "you'll remember. When May is rushing over you. With desire to be part of the "
                "miracles. You see in every hour. You'll know it's true. That you are blessed "
                "and lucky. It's true that you are touched. By something that will grow and "
                "bloom in you. These are days. These are the days you might fill. With "
                "laughter until you break. These days you might feel. A shaft of light. Make "
                "its way across your face. And when you do. You'll know how it was meant to "
                "be. See the signs and know their meaning. You'll know how it was meant to "
                "be. Hear the signs and know they're speaking. To you, to you",
            ],
        ),
        (
            'I could feel at the time\n',
            [
                "I could feel at the time. There was no way of knowing. Fallen leaves in the "
                "night. Who can say where they're blowing. As free as the wind. Hopefully "
                "learning. Why the sea on the tide. Has no way of turning. More than this. "
                "You know there's nothing. More than this. Tell me one thing. More than this. "
                "You know there's nothing. It was fun for a while. There was no way of "
                "knowing. Like a dream in the night. Who can say where we're going. No care "
                "in the world. Maybe I'm learning. Why the sea on the tide. Has no way of "
                "turning. More than this. You know there's nothing. More than this. Tell me "
                "one thing. More than this. You know there's nothing. More than this. You "
                "know there's nothing. More than this. Tell me one thing. More than this. "
                "There's nothing.",
                'A lie to say, "O my mountain has coal veins and beds to dig.. 500 men with '
                'axes and they all dig for me." A lie to ssay, "O my. river where mant fish '
                'do swim, half of the catch is mine when you haul. your nets in." Never will '
                "he believe that his greed is a blinding. ray. No devil or redeemer will "
                "cheat him. He'll take his gold to. where he's lying cold.. A lie to say, "
                '"O my mine gave a diamond as big as a fist.". But with every gem in his '
                'pocket, the jewels he has missed. A lie to. say, "O my garden is growing '
                'taller by the day." He only eats the. best and tosses the rest away. Never '
                "will he be believe that his. greed is a blinding ray. No devil or redeemer "
                "can cheat him. he'll. take his gold to where he's lying cold. Six deep in "
                "the grave.. Something is out of reach. something he wanted. something is out "
                "of reach. he's being taunted. something is out of reach. that he can' beg or "
                "steal nor can he buy. his oldest pain. and fear in life. there'll not be "
                "time. his oldest pain. and fear in life. there'll not be time. A lie to say "
                "\"O my forest has trees that block the sun and. when I cut them down I don't "
                'answer to anyone." No, no, never will he. believe that his greed is a '
                "blinding ray no devil or redeemer can. cheat. him. He'll take his gold where "
                "he's lying cold..",
                "Don't talk, I will listen. Don't talk, you keep your distance. For I'd "
                "rather hear some truth tonight. Than entertain your lies,. So take you "
                "poison silently. Let me be let me close my eyes. Don't talk, I'll believe "
                "it. Don't talk, listen to me instead,. I know that if you think of it,. Both "
                "long enough and hard. The drink you drown your troubles. In is the trouble "
                "you're in now. Talk talk talk about it,. If you talk as if you care. But "
                "when your talk is over. Tilt that bottle in the air,. Tossing back more than "
                "your share. Don't talk, I can guess it. Don't talk, well now your restless. "
                "And you need somewhere to put the blame. For how you feel inside. You'll "
                "look for a close. And easy mark and you'll see me as fair game. Talk talk "
                "talk about it,. Talk as if you care. But when your talk is over tilt. That "
                "bottle in the air. Tossing back more than your share. You talk talk talk "
                "about it,. You talk as if you care. I'm marking every word. And can tell "
                "this time for sure,. Your talk is the finest I have heard. So don't talk, "
                "I'll be sleeping,. Let me go on dreaming. How your eyes they glow so "
                "fiercely. I can tell your inspired. By the name you just chose for me. Now "
                "what was it?. O, never mind it. We will talk talk. Talk about this when your "
                "head is clear. I'll discuss this in the morning,. But until then you may "
                "talk but I won't hear",
            ],
        ),
        (
            'I promise.\n',
            [
                "These are. These are days you'll remember. Never before and never since, I "
                "promise. Will the whole world be warm as this. And as you feel it,. You'll "
                "know it's true. That you - you are blessed and lucky. It's true - that you. "
                "Are touched by something. That will grow and bloom in you. These are days "
                "you'll remember. When May is rushing over you. With desire to be part of the "
                "miracles. You see in every hour. You'll know it's true. That you are blessed "
                "and lucky. It's true that you are touched. By something that will grow and "
                "bloom in you. These are days. These are the days you might fill. With "
                "laughter until you break. These days you might feel. A shaft of light. Make "
                "its way across your face. And when you do. You'll know how it was meant to "
                "be. See the signs and know their meaning. You'll know how it was meant to "
                "be. Hear the signs and know they're speaking. To you, to you",
                "[ music: Dennis Drew/lyric: Natalie Merchant ]. . science. is truth for "
                "life. watch religion fall obsolete. science. will be truth for life. "
                "technology as nature. science. truth for life. in fortran tongue the. "
                "answer. with wealth and prominence. man so near perfection. possession. it's "
                "an absence of interim. secure no demurrer. defense against divine. defense "
                "against his true. image. human conflict number five. discovery. dissolved "
                "all illusion. mystery. destroyed with conclusion. and illusion never "
                "restored. any modern man can see. that religion is. obsolete. piety. "
                "obsolete. ritual. obsolete. martyrdom. obsolete. prophetic vision. obsolete. "
                "mysticism. obsolete. commitment. obsolete. sacrament. obsolete. revelation. "
                "obsolete.",
                "Don't talk, I will listen. Don't talk, you keep your distance. For I'd "
                "rather hear some truth tonight. Than entertain your lies,. So take you "
                "poison silently. Let me be let me close my eyes. Don't talk, I'll believe "
                "it. Don't talk, listen to me instead,. I know that if you think of it,. Both "
                "long enough and hard. The drink you drown your troubles. In is the trouble "
                "you're in now. Talk talk talk about it,. If you talk as if you care. But "
                "when your talk is over. Tilt that bottle in the air,. Tossing back more than "
                "your share. Don't talk, I can guess it. Don't talk, well now your restless. "
                "And you need somewhere to put the blame. For how you feel inside. You'll "
                "look for a close. And easy mark and you'll see me as fair game. Talk talk "
                "talk about it,. Talk as if you care. But when your talk is over tilt. That "
                "bottle in the air. Tossing back more than your share. You talk talk talk "
                "about it,. You talk as if you care. I'm marking every word. And can tell "
                "this time for sure,. Your talk is the finest I have heard. So don't talk, "
                "I'll be sleeping,. Let me go on dreaming. How your eyes they glow so "
                "fiercely. I can tell your inspired. By the name you just chose for me. Now "
                "what was it?. O, never mind it. We will talk talk. Talk about this when your "
                "head is clear. I'll discuss this in the morning,. But until then you may "
                "talk but I won't hear",
            ],
        ),
    ]


def test_query(tmpdir, queries_and_expected_replies):
    config(tmpdir)
    index_documents()
    f = get_flow()
    with f:
        for query, exp_result in queries_and_expected_replies:
            output = get_results(query)
            matches = output['search']['docs'][0]['matches']
            assert len(matches) <= TOP_K  # check the number of docs returned
            result = []
            for match in matches:
                match_text = match['text']
                result.append(match_text)
            assert result == exp_result
