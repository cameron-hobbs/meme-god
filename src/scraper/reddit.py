from datetime import datetime, timezone

import requests  # type: ignore
from django.db import transaction
from requests import HTTPError

from src.reddit.models import RedditUser
from src.reddit.models.post import RedditPost, RedditPostChangeLog
from src.reddit.models.sub import RedditSub
from src.scraper.base import ComparisonScraper


class RedditScraper(ComparisonScraper[RedditPost]):
    comparison_model = RedditPost
    change_log_model = RedditPostChangeLog

    def ignore_change_fields(self) -> set[str]:
        ignore = super().ignore_change_fields()
        ignore.add("subreddit_subscribers")
        return ignore

    def cancel_comparison(self, field: str, old_value: str, new_value: str) -> bool:
        return super().cancel_comparison(field, old_value, new_value) or (
            field == "upvote_ratio" and float(old_value) == float(new_value)
        )

    def scrape(self) -> None:
        categories = ["best", "new", "hot", "rising"]

        for subreddit in RedditSub.objects.filter(should_scrape=True):
            for category in categories:
                self._scrape_category(subreddit, category)

    def _scrape_category(self, subreddit: RedditSub, category: str) -> None:
        print(f"Scraping subreddit {subreddit.tag}, category: {category}")
        response = requests.get(
            f"https://www.reddit.com/r/{subreddit.tag}/{category}/.json",
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
            },
        )
        try:
            response.raise_for_status()
        except HTTPError:
            print(f"failed scrape for {subreddit.tag} {category}")
            return
        print("Got data successfully")
        children = response.json()["data"]["children"]

        print("Processing posts now")
        for child in children:
            post = child["data"]
            try:
                self._process_post(subreddit, post)
            except Exception as e:
                print(e)
                continue
        print("Done processing posts")

    def _process_post(self, subreddit: RedditSub, post: dict) -> None:
        if "author_fullname" not in post:
            return

        author, _ = RedditUser.objects.get_or_create(full_name=post["author_fullname"])
        post_id = post.pop("id")
        if post_id is None:
            return

        model_fields = {
            field.name
            for field in RedditPost._meta.get_fields()
            if field.name
            not in {"id", "created_at", "updated_at", "subreddit", "author"}
        }
        post["post_created_at"] = datetime.fromtimestamp(
            post["created_utc"], tz=timezone.utc
        )
        post = {key: val for key, val in post.items() if key in model_fields}
        reddit_post = RedditPost(
            post_id=post_id, author=author, subreddit=subreddit, **post
        )
        with transaction.atomic():
            try:
                existing_reddit_post = RedditPost.objects.get(post_id=post_id)
            except RedditPost.DoesNotExist:
                print(f"Found new reddit post {post_id}")
                reddit_post.save()
            else:
                self.compare_changes(existing_reddit_post, reddit_post)
                for field, value in {
                    "author": author,
                    "subreddit": subreddit,
                    **post,
                }.items():
                    setattr(existing_reddit_post, field, value)
                existing_reddit_post.save()
