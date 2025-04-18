import pytest


class BaseTest:
    pytestmark = [pytest.mark.django_db]
