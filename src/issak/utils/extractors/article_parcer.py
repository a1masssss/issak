import requests

from newspaper import Article

def parse_article(url):
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
            )
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 403:
            raise Exception("403 Forbidden - Access Denied. Try using a different URL.")

        if response.status_code != 200:
            raise Exception(f"Failed to fetch the URL. Status code: {response.status_code}")

        article = Article(url, request_headers=headers)


        article.download()
        article.parse()

        return {
            "title": article.title or "Untitled",
            "content": article.text,
            "top_image": article.top_image,
        }

    except Exception as e:
        return {"error": f"Failed to parse article: this is parse_article "}