__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import torch
import torch.utils.data as data
import json as jsonmod
import os


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


class Flickr8kDataset(data.Dataset):
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
    elif dataset_type == 'f8k':
        dataset = Flickr8kDataset(images_root=root, captions_file_path=captions)
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
