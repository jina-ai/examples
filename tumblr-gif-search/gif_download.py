__copyright__ = "Copyright (c) 2020 - 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"


import asyncio
import os
import time

import click
import aiofiles
import aiohttp

BATCH_SIZE = 30
DEFAULT_MAX_GIFS = 2000


async def download(url):
    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.get(url) as r:
            print('downloading %s' % url)
            gif_data = await r.read()
        gif_name = 'data/%s' % url.split('/')[-1]
        print('save it to %s' % gif_name)
        async with aiofiles.open(gif_name, 'wb') as fp:
            await fp.write(gif_data)


async def task_trigger(urls):
    tasks = [asyncio.create_task(download(u)) for u in urls]
    await asyncio.gather(*tasks)


@click.command()
@click.option("--limit", "-l", default=DEFAULT_MAX_GIFS)
def main(limit: int):
    with open('data/tgif-v1.0.tsv') as fp:
        all_urls = [v.split('\t')[0] for v in fp]
        if len(all_urls) > limit:
            all_urls = all_urls[:limit]
        print('%d urls' % len(all_urls))
        all_urls = [v for v in all_urls if not os.path.exists('data/%s' % v.split('/')[-1])]

    for _ in range(0, len(all_urls), BATCH_SIZE):
        asyncio.run(task_trigger(all_urls[_:(_ + BATCH_SIZE)]))
        time.sleep(1)


if __name__ == '__main__':
    main()
