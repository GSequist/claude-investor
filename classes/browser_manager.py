from classes.simpletextbrowser import SimpleTextBrowser
from dotenv import load_dotenv
from utils.utils import WORK_FOLDER
import os

load_dotenv()


class BrowserManager:
    def __init__(self):
        self.browsers = {}

    def get_browser(self, user_id):
        if user_id not in self.browsers:
            default_request_kwargs = {
                "timeout": (10, 10),
                "headers": {
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0 Safari/537.36"
                    )
                },
            }
            self.browsers[user_id] = SimpleTextBrowser(
                start_page="about:blank",
                viewport_size=1024 * 8,
                downloads_folder=os.path.join(WORK_FOLDER, user_id),
                serpapi_key=os.getenv("SERPAPI_KEY"),
                request_kwargs=default_request_kwargs,
                user_id=user_id,
            )
        return self.browsers[user_id]
