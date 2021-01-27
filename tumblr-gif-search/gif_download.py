__copyright__ = "Copyright (c) 2020 - 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"


import asyncio
import os
import time

import aiofiles
import aiohttp

batch_size = 30

with open('data/tgif-v1.0.tsv') as fp:
    all_urls = [v.split('\t')[0] for v in fp]
    print('%d urls' % len(all_urls))
    all_urls = [v for v in all_urls if not os.path.exists('data/%s' % v.split('/')[-1])]
    print('%d urls' % len(all_urls))


async def download(url):
    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.get(url) as r:
            print('downloading %s' % url)
            gif_data = await r.read()
        gif_name = 'data/%s' % url.split('/')[-1]
        print('save it to %s' % gif_name)
        async with aiofiles.open(gif_name, 'wb') as fp:
            await fp.write(gif_data)


async def main(urls):
    tasks = [asyncio.create_task(download(u)) for u in urls]
    await asyncio.gather(*tasks)


for _ in range(0, len(all_urls), batch_size):
    asyncio.run(main(all_urls[_:(_ + batch_size)]))
    time.sleep(1)
