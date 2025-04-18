__all__ = ["RedditSubFactory"]

from factory import Faker, LazyAttribute
from factory.fuzzy import FuzzyChoice

from src.reddit.models import RedditSub
from factory.django import DjangoModelFactory

from src.reddit.models.sub import SubCategory


class RedditSubFactory(DjangoModelFactory):
    category = FuzzyChoice(SubCategory)
    should_scrape = True
    subscribers = Faker("random_int", max=100_000_000)
    _word = Faker("word")
    tag = LazyAttribute(lambda obj: f"{obj.category}-{obj._word}")

    class Meta:
        model = RedditSub
        exclude = ["_word"]
