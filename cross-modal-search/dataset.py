import torch
import torch.utils.data as data
import json as jsonmod
import os


class FlickrDataset(data.Dataset):
    """
    Dataset loader for Flickr30k and Flickr8k full datasets.
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


def collate_fn(data):
    # Not sure this is actually needed
    images, captions = zip(*data)
    return images, captions


def get_data_loader(split, root, json, batch_size=8, shuffle=True,
                    num_workers=1, collate_fn=collate_fn):
    """Returns torch.utils.data.DataLoader for custom coco dataset."""

    dataset = FlickrDataset(images_root=root, split=split, json=json)

    # Data loader
    data_loader = torch.utils.data.DataLoader(dataset=dataset,
                                              batch_size=batch_size,
                                              shuffle=shuffle,
                                              pin_memory=True,
                                              num_workers=num_workers,
                                              collate_fn=collate_fn)

    return data_loader
