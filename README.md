# ManaTokiTrap

## 개요

`ManaTokiTrap`는 클라우드플레어(Cloudflare) 보안이 적용된 만화 웹사이트 Manatoki의 만화 이미지를 자동으로 다운로드할 수 있도록 도와주는 파이썬 비동기 프로그램입니다.
특정 만화 챕터 또는 페이지의 이미지 URL을 추출하고, 해당 이미지를 로컬 경로에 저장할 수 있습니다.
[tokiDownloader](https://github.com/crossSiteKikyo/tokiDownloader)를 보고 영감을 얻어 제작했습니다.

## 기능

- Cloudflare 보안 세션 획득
- HTML 데이터 디코딩
- 이미지 URL 추출
- 이미지 다운로드
- 비동기 다운로드

## 설치

1. 이 저장소를 클론하거나 다운로드합니다.

   ```bash
   git clone https://github.com/Code-JJamtong/ManaTokiTrap.git
   ```
2. 필요한 파이썬 패키지를 설치합니다.

   ```bash
   pip install -r requirements.txt
   ```

## 사용법

### 설정

`ManaTokiTrap.py` 파일에 있는 `TokiDownloader` 클래스는 `user-agent`와 `cf_clearance` 값을 초기화하여 Cloudflare 보안 세션에 필요한 데이터로 사용합니다.
만약 더 탁월한 세션 조회 방식이 있다면 직접 초기화 하셔도 괜찮습니다.

### 예제

`example.py` 파일은 `TokiDownloader` 클래스를 사용하여 만화 이미지를 다운로드하는 예제 코드입니다.

1. `example.py` 파일을 실행하여 만화를 다운로드합니다.

   ```bash
   python example.py
   ```
2. 만화의 URL을 가져온 후, `다운로드` 폴더에 저장합니다.

### 주요 메서드

- `get_cf_session(url)`: Cloudflare 보안을 우회하기 위한 세션을 획득합니다.
- `decode_html_data(encoded_html)`: 인코딩된 HTML 데이터를 디코딩합니다.
- `download_images(url, image_path)`: 주어진 URL에서 이미지를 다운로드하고 지정된 경로에 저장합니다.
- `get_manga_image_urls(url)`: 주어진 만화 페이지 URL에서 이미지 URL을 추출합니다.
- `get_manga_urls(url)`: 주어진 만화 메인 페이지 URL에서 만화의 개별 챕터 또는 페이지의 URL을 추출합니다.
- `download_manga_images_directly(manga_url, path, semaphore)`: 만화 페이지 URL에서 이미지를 추출하고 다운로드하여 저장합니다.

## ⚠️주의⚠️

README와 대부분의 주석은 작성에 있어 귀찮음으로 인해 LLM에게 짬처리를 했으며 이에 부정확한 부분이 있을 수 있음을 알립니다!
