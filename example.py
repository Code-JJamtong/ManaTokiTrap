from tqdm.asyncio import tqdm
from ManaTokiTrap import TokiDownloader
import asyncio


async def main():
    downloader = TokiDownloader()

    manga_urls = await downloader.get_manga_urls("https://manatoki350.net/comic/122227")

    tasks = []
    semaphore = asyncio.Semaphore(10)

    for index, manga_url in enumerate(manga_urls):
        if index < 10: # 최신화부터 10화 가져옴
            task = asyncio.create_task(
                downloader.download_manga_images_directly(
                    manga_url, f"다운로드/{len(manga_urls)-index}", semaphore
                )
            )
            tasks.append(task)

    for _ in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="다운로드 중"):
        await _


if __name__ == "__main__":
    asyncio.run(main())
