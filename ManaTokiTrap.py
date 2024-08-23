import requests, asyncio, io, re, os, aiohttp
import nodriver as uc
from bs4 import BeautifulSoup
from PIL import Image
from urllib.parse import urlparse


class TokiDownloader:
    def __init__(self, user_agent="", cf_clearance=""):
        """
        TokiDownloader 클래스의 생성자 함수입니다.
        
        이 함수는 user-agent와 cf_clearance 값을 초기화하여 Cloudflare 보안 세션에 필요한 데이터로 사용됩니다.
        
        매개변수:
        user_agent (str): HTTP 요청에 사용되는 User-Agent 값입니다.
        cf_clearance (str): Cloudflare의 보안 인증을 우회하기 위한 cf_clearance 쿠키 값입니다.
        """
        self.cf_session_data = {"user-agent": user_agent, "cf_clearance": cf_clearance}

    async def get_cf_session(self, url):
        """
        Cloudflare 보안 세션을 획득하기 위한 함수입니다.

        주어진 URL을 통해 Cloudflare의 보안을 우회하기 위한 cf_clearance 쿠키 값을 얻습니다.
        얻은 쿠키 값과 User-Agent는 이후의 HTTP 요청에 사용됩니다.

        가끔 Captcha가 자동으로 넘어가지 않습니다만 손으로 풀거나 알아서 조치를 취해보시기 바랍니다.
        
        매개변수:
        url (str): Cloudflare 보안이 적용된 웹사이트의 URL입니다.
        """
        browser = await uc.start()
        page = await browser.get(url)

        try:
            cf_clearance_value = None

            while True:
                await asyncio.sleep(1)

                cookies = await browser.cookies.get_all()

                for cookie in cookies:
                    if cookie.name == "cf_clearance":
                        cf_clearance_value = cookie.value
                        break

                if cf_clearance_value:
                    break

            self.cf_session_data["user-agent"] = browser.info["User-Agent"]
            self.cf_session_data["cf_clearance"] = cf_clearance_value

        finally:
            try:
                await page.close()
            except Exception:
                pass  # 몰루

    def decode_html_data(self, encoded_html):
        """
        HTML 데이터를 디코딩하는 함수입니다.
        
        인코딩된 HTML 데이터를 해독하여 사람이 읽을 수 있는 형태로 변환합니다.
        
        매개변수:
        encoded_html (str): 인코딩된 HTML 문자열입니다.
        
        반환값:
        str: 디코딩된 HTML 문자열입니다.
        """
        return ''.join(chr(int(encoded_html[i:i + 2], 16)) for i in range(0, len(encoded_html), 3))

    async def download_images(self, url, image_path):
        """
        주어진 URL에서 이미지를 다운로드하고 지정된 경로에 저장하는 함수입니다.
        
        매개변수:
        url (str): 다운로드할 이미지의 URL입니다.
        image_path (str): 이미지를 저장할 로컬 경로입니다.
        """
        parsed_url = urlparse(url)
        headers = {
            "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            "Referer": f"{parsed_url.scheme}://{parsed_url.netloc}",
            "sec-ch-ua-mobile": "?0",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
            "sec-ch-ua-platform": '"Windows"',
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    content = await response.read()
                    image = Image.open(io.BytesIO(content))
                    image.verify()
                    image.close()

                    with open(image_path, "wb") as file:
                        file.write(content)
        except Exception:
            pass  # 몰루

    async def download_from_image_urls(self, image_urls, base_path):
        """
        이미지 URL 리스트를 통해 여러 이미지를 다운로드하고, 각각의 이미지를 지정된 경로에 저장하는 함수입니다.
        
        매개변수:
        image_urls (list): 다운로드할 이미지의 URL 리스트입니다.
        base_path (str): 이미지를 저장할 기본 디렉토리 경로입니다.
        """
        tasks = []
        for index, img_url in enumerate(image_urls, start=1):
            parsed_url = urlparse(img_url)
            file_extension = os.path.splitext(parsed_url.path)[1]

            os.makedirs(base_path, exist_ok=True)
            image_path = os.path.join(base_path, f"{index}{file_extension}")

            task = asyncio.create_task(self.download_images(img_url, image_path))
            tasks.append(task)

        await asyncio.gather(*tasks)

    async def get_manga_image_urls(self, url, counter=0):
        """
        주어진 만화 페이지 URL에서 이미지 URL을 추출하는 함수입니다.
        
        Cloudflare 보안 세션을 우회하여 웹 페이지의 스크립트를 분석하고, 만화 이미지를 나타내는 URL을 추출합니다.
        
        매개변수:
        url (str): 이미지 URL을 추출할 만화 페이지의 URL입니다.
        counter (int): 재시도 횟수를 나타냅니다. 기본값은 0이며, 최대 5회 재시도합니다.
        
        반환값:
        list: 만화 이미지의 URL 리스트입니다.
        """
        if counter > 5:
            raise Exception("Crawl Failed!")  # 몰루

        cookies = {"cf_clearance": self.cf_session_data["cf_clearance"]}

        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6,zh;q=0.5",
            "cache-control": "max-age=0",
            "if-modified-since": "Fri, 23 Aug 2024 15:04:03 GMT",
            "priority": "u=0, i",
            "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            "user-agent": self.cf_session_data["user-agent"],
        }

        response = requests.get(url, cookies=cookies, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        script = soup.find("script", string=re.compile("var html_data"))
        if script:
            js_code = script.string
            matches = re.findall(r"html_data\+=\'(.*?)\';", js_code, re.DOTALL)
            combined_html_data = "".join(matches)

            decoded_html = self.decode_html_data(combined_html_data)
            image_urls = re.findall(
                r'src="/img/loading-image\.gif"\s+data-\w+=["\'](https://img[^"\']+)["\']',
                decoded_html,
            )

            return image_urls
        else:
            await self.get_cf_session(url)
            return await self.get_manga_image_urls(url, counter + 1)

    async def get_manga_urls(self, url, counter=0):
        """
        주어진 만화 메인 페이지 URL에서 만화의 개별 챕터 또는 페이지의 URL을 추출하는 함수입니다.
        
        Cloudflare 보안 세션을 우회하여 각 만화 페이지의 URL을 추출합니다.
        
        매개변수:
        url (str): 만화 URL 리스트를 추출할 메인 페이지의 URL입니다.
        counter (int): 재시도 횟수를 나타냅니다. 기본값은 0이며, 최대 5회 재시도합니다.
        
        반환값:
        list: 만화의 각 페이지나 챕터에 해당하는 URL 리스트입니다.
        """
        if counter > 5:
            raise Exception("Crawl Failed!")  # 몰루

        cookies = {"cf_clearance": self.cf_session_data["cf_clearance"]}

        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6,zh;q=0.5",
            "cache-control": "max-age=0",
            "if-modified-since": "Fri, 23 Aug 2024 15:04:03 GMT",
            "priority": "u=0, i",
            "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            "user-agent": self.cf_session_data["user-agent"],
        }

        response = requests.get(url, cookies=cookies, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        manga_urls = []

        for element in soup.find_all("li", class_="list-item"):
            url = element.find("a", class_="item-subject")["href"]

            if url:
                parsed_url = urlparse(url)
                clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
                
                manga_urls.append(clean_url)

        if manga_urls:
            return manga_urls
        else:
            await self.get_cf_session(url)
            return await self.get_manga_urls(url, counter + 1)

    async def download_manga_images_directly(self, manga_url, path, semaphore):
        """
        주어진 만화 페이지 URL에서 한번에 이미지를 추출하고 다운로드한 후 저장하는 함수입니다.
        
        주어진 semaphore를 이용해 최대 동시 시행수를 제한합니다.
        
        매개변수:
        manga_url (str): 만화 이미지 URL을 추출할 페이지의 URL입니다.
        path (str): 이미지를 저장할 로컬 경로입니다.
        semaphore (asyncio.Semaphore): 동시에 다운로드할 작업 수를 제한하는 semaphore입니다.
        """
        async with semaphore:
            image_urls = await self.get_manga_image_urls(manga_url)
            await self.download_from_image_urls(image_urls, path)