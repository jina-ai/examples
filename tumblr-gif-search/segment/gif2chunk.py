__copyright__ = "Copyright (c) 2020 - 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import io
from typing import List

import numpy as np
from PIL import Image, ImageFile
# workaround initialization code
from PIL.GifImagePlugin import GifImageFile, _accept, _save, _save_all
from jina.executors.segmenters import BaseSegmenter
from jina.executors.decorators import single


class GifPreprocessor(BaseSegmenter):
    def __init__(self, img_shape: int = 96, every_k_frame: int = 1, max_frame: int = None, from_bytes: bool = False,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.img_shape = img_shape
        self.every_k_frame = every_k_frame
        self.max_frame = max_frame

    @single(slice_nargs=2, flatten_output=False)
    def segment(self, buffer, id):
        result = []
        try:
            im = Image.open(io.BytesIO(buffer))
            idx = 0
            for frame in get_frames(im):
                try:
                    if idx % self.every_k_frame == 0 and (
                            (self.max_frame is not None and idx < self.max_frame) or self.max_frame is None):
                        new_frame = frame.convert('RGB').resize([self.img_shape, ] * 2)
                        img = (np.array(new_frame) / 255).astype(np.float32)
                        # build chunk next, if the previous fail, then no chunk will be add
                        result.append(dict(id=id, offset=idx,
                                           weight=1., blob=img))
                except Exception as ex:
                    self.logger.error(ex)
                finally:
                    idx = idx + 1

            return result

        except Exception as ex:
            self.logger.error(ex)


class AnimatedGifImageFile(GifImageFile):

    def load_end(self):
        ImageFile.ImageFile.load_end(self)


Image.register_open(AnimatedGifImageFile.format, AnimatedGifImageFile, _accept)
Image.register_save(AnimatedGifImageFile.format, _save)
Image.register_save_all(AnimatedGifImageFile.format, _save_all)
Image.register_extension(AnimatedGifImageFile.format, ".gif")
Image.register_mime(AnimatedGifImageFile.format, "image/gif")


# end of workaround initialization code

def get_frames(gif: Image.Image) -> List[Image.Image]:
    """
    Extract all frames from gif.

    This function is just slight adjustment of the for-cycle from the workaround.
    """
    last_frame = None
    all_frames = []
    i = 0
    try:
        while True:
            gif.seek(i)
            new_frame = gif.convert('RGBA')
            if last_frame is not None and gif.disposal_method == 1:
                updated = new_frame.crop(gif.dispose_extent)
                last_frame.paste(updated, gif.dispose_extent, updated)
                new_frame = last_frame
            else:
                last_frame = new_frame

            # do resizing on new_frame here...

            all_frames.append(new_frame.copy())
            i += 1
    except EOFError:
        gif.seek(0)

    return all_frames
