# https://github.com/python-pillow/Pillow/issues/2893#issuecomment-502712486

from typing import List

from PIL import Image, ImageFile
# workaround initialization code
from PIL.GifImagePlugin import GifImageFile, _accept, _save, _save_all


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
