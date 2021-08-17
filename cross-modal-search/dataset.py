__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"


import os
import json as jsonmod
import hashlib

import torch
import torch.utils.data as data
from jina import Document


cur_dir = os.path.dirname(os.path.abspath(__file__))


class Flickr30kDataset(data.Dataset):
    """
    Dataset loader for Flickr30k full datasets.
    """

    def __init__(self, images_root, json, split):
        self.images_root = images_root
        self.dataset = jsonmod.load(open(json, 'r'))['images']
        self.ids = []
        for i, d in enumerate(self.dataset):
            if d['split'] == split:
                self.ids += [(i, x) for x in range(len(d['sentences']))]

    def __getitem__(self, index):
        """This function returns a tuple that is further passed to collate_fn
        """
        images_root = self.images_root
        ann_id = self.ids[index]
        img_id = ann_id[0]
        caption = self.dataset[img_id]['sentences'][ann_id[1]]['raw']
        img_file_name = self.dataset[img_id]['filename']

        image_file_path = os.path.join(images_root, img_file_name)
        with open(image_file_path, 'rb') as fp:
            image_buffer = fp.read()
        return image_buffer, str(caption).lower()

    def __len__(self):
        return len(self.ids)


class FlickrDataset(data.Dataset):
    """
    Dataset loader for Flickr8k full datasets.
    """

    def __init__(self, images_root, captions_file_path):
        self.images_root = images_root
        self.captions_file_path = captions_file_path
        with open(self.captions_file_path, 'r') as cf:
            self.lines = cf.readlines()[1:]

    def __getitem__(self, index):
        """This function returns a tuple that is further passed to collate_fn
        """
        image_file_name, caption = self.lines[index*5].split(',', 1)
        with open(os.path.join(self.images_root, image_file_name), 'rb') as fp:
            image_buffer = fp.read()
        return image_buffer, str(caption).lower().rstrip()

    def __len__(self):
        return int(len(self.lines)/5)


def collate_fn(data):
    # Not sure this is actually needed
    images, captions = zip(*data)
    return images, captions


def get_data_loader(split, root, captions, batch_size=8, dataset_type='f30k', shuffle=False,
                    num_workers=1, collate_fn=collate_fn):
    """Returns torch.utils.data.DataLoader for custom coco dataset."""

    if dataset_type == 'f30k':
        dataset = Flickr30kDataset(images_root=root, split=split, json=captions)
    elif dataset_type == 'f8k' or dataset_type == 'toy-data':
        dataset = FlickrDataset(images_root=root, captions_file_path=captions)
    else:
        raise NotImplementedError(f'Not valid dataset type {dataset_type}')
    # Data loader
    data_loader = torch.utils.data.DataLoader(dataset=dataset,
                                              batch_size=batch_size,
                                              shuffle=shuffle,
                                              pin_memory=True,
                                              num_workers=num_workers,
                                              collate_fn=collate_fn)

    return data_loader


def input_index_data(num_docs=None, batch_size=8, dataset_type='f30k'):
    captions = 'dataset_flickr30k.json' if dataset_type == 'f30k' else 'captions.txt'
    if dataset_type == 'toy-data':
        base_folder = '.'
    else:
        base_folder = 'data'
    data_loader = get_data_loader(
        root=os.path.join(cur_dir, f'{base_folder}/{dataset_type}/images'),
        captions=os.path.join(cur_dir, f'{base_folder}/{dataset_type}/{captions}'),
        split='test',
        batch_size=batch_size,
        dataset_type=dataset_type
    )

    for i, (images, captions) in enumerate(data_loader):
        for image, caption in zip(images, captions):
            hashed = hashlib.sha1(image).hexdigest()
            document_img = Document()
            
            document_img.buffer = image
            document_img.modality = 'image'
            document_img.mime_type = 'image/jpeg'
            
            document_caption = Document(id=hashed)
            
            document_caption.text = caption
            document_caption.modality = 'text'
            document_caption.mime_type = 'text/plain'
            document_caption.tags['id'] = caption
            
            yield document_img
            yield document_caption

        if num_docs and (i + 1) * batch_size >= num_docs:
            break
