from classes.browser_manager import BrowserManager
from classes._md_convert import MarkdownConverter
from utils.utils import WORK_FOLDER, tokenizer
from dotenv import load_dotenv
import requests
import os

load_dotenv()

browser_manager = BrowserManager()

##############################################################


def web_search(query: str, filter_year: int = None, *, user_id: str) -> str:
    """search the web for information
    #parameters:
    query: a text query to search for in the web
    filter_year: an optional year filter (e.g., 2020)
    """
    max_tokens = 30000
    browser = browser_manager.get_browser(user_id)
    browser.visit_page(f"google: {query}", filter_year=None)
    header, content = browser._state()
    result = header.strip() + "\n=======================\n" + content
    return result, result, "", max_tokens


def visit_url(url: str, *, user_id: str) -> str:
    """Visit a webpage at a given URL and return its text. Given a url to a YouTube video, this returns the transcript. if you give this file url like "https://example.com/file.pdf", it will download that file and then you can use text_file tool on it.
    #parameters:
    url: the relative or absolute url of the webapge to visit
    """
    max_tokens = 30000
    browser = browser_manager.get_browser(user_id)
    browser.visit_page(url)
    header, content = browser._state()
    result = header.strip() + "\n=======================\n" + content
    return result, result, url, max_tokens


def archive_search(url: str, date: str, *, user_id: str) -> str:
    """Given a url, searches the Wayback Machine and returns the archived version of the url that's closest in time to the desired date.
    #parameters:
    url: The url to archive.
    date: The desired date in 'YYYYMMDD' format.
    """
    max_tokens = 30000
    browser = browser_manager.get_browser(user_id)
    base_api = f"https://archive.org/wayback/available?url={url}"
    archive_api = base_api + f"&timestamp={date}"
    res_with_ts = requests.get(archive_api).json()
    res_without_ts = requests.get(base_api).json()
    if (
        "archived_snapshots" in res_with_ts
        and "closest" in res_with_ts["archived_snapshots"]
    ):
        closest = res_with_ts["archived_snapshots"]["closest"]
    elif (
        "archived_snapshots" in res_without_ts
        and "closest" in res_without_ts["archived_snapshots"]
    ):
        closest = res_without_ts["archived_snapshots"]["closest"]
    else:
        raise Exception(f"Archive not found for {url}.")
    target_url = closest["url"]
    browser.visit_page(target_url)
    header, content = browser._state()
    result = (
        f"web archive for url {url}, snapshot on {closest['timestamp'][:8]}:\n"
        + header.strip()
        + "\n=======================\n"
        + content
    )
    return (
        result,
        result,
        url,
        max_tokens,
    )


def page_up(user_id: str) -> str:
    """Scroll up one page."""
    max_tokens = 30000
    browser = browser_manager.get_browser(user_id)
    browser.page_up()
    header, content = browser._state()
    result = header.strip() + "\n=======================\n" + content
    return result, result, "", max_tokens


def page_down(user_id: str) -> str:
    """Scroll down one page."""
    max_tokens = 30000
    browser = browser_manager.get_browser(user_id)
    browser.page_down()
    header, content = browser._state()
    result = header.strip() + "\n=======================\n" + content
    return result, result, "", max_tokens


def find_on_page(search_string: str, *, user_id: str) -> str:
    """Scroll the viewport to the first occurrence of the search string. This is equivalent to Ctrl+F.
    #parameters:
    search_string: The string to search for; supports wildcards like '*'
    """
    max_tokens = 30000
    browser = browser_manager.get_browser(user_id)
    result = browser.find_on_page(search_string)
    header, content = browser._state()
    if result is None:
        return (
            (
                header.strip()
                + f"\n=======================\nThe search string '{search_string}' was not found on this page."
            ),
            "",
            "",
            max_tokens,
        )
    end_result = header.strip() + "\n=======================\n" + content
    return end_result, end_result, "", max_tokens


def find_next(user_id: str) -> str:
    max_tokens = 30000
    browser = browser_manager.get_browser(user_id)
    result = browser.find_next()
    header, content = browser._state()
    if result is None:
        return (
            (
                header.strip()
                + "\n=======================\nNo further occurrences found."
            ),
            "",
            "",
            max_tokens,
        )
    end_result = header.strip() + "\n=======================\n" + content
    return (
        end_result,
        end_result,
        "",
        max_tokens,
    )
