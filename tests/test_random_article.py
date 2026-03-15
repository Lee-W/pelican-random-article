import json
import os
import re
import tempfile
from unittest.mock import MagicMock

from pelican.plugins.random_article.random_article import generate_random_page


def _make_article(url, status="published"):
    a = MagicMock()
    a.url = url
    a.status = status
    return a


def _make_generator(articles, settings=None):
    settings = settings or {}
    generator = MagicMock()
    generator.articles = articles
    generator.output_path = tempfile.mkdtemp()
    generator.context = {
        "SITENAME": "Test Site",
        "SITEURL": "https://example.com",
        "RANDOM_ARTICLE_SAVE_AS": "random/index.html",
        **settings,
    }
    return generator


class TestGenerateRandomPage:
    def test_creates_output_file(self):
        articles = [_make_article("posts/hello/"), _make_article("posts/world/")]
        gen = _make_generator(articles)
        generate_random_page(gen)
        dest = os.path.join(gen.output_path, "random", "index.html")
        assert os.path.exists(dest)

    def test_html_contains_article_urls(self):
        articles = [_make_article("posts/hello/"), _make_article("posts/world/")]
        gen = _make_generator(articles)
        generate_random_page(gen)
        dest = os.path.join(gen.output_path, "random", "index.html")
        content = open(dest).read()
        assert "https://example.com/posts/hello/" in content
        assert "https://example.com/posts/world/" in content

    def test_skips_draft_articles(self):
        articles = [
            _make_article("posts/published/", status="published"),
            _make_article("posts/draft/", status="draft"),
        ]
        gen = _make_generator(articles)
        generate_random_page(gen)
        dest = os.path.join(gen.output_path, "random", "index.html")
        content = open(dest).read()
        assert "posts/published/" in content
        assert "posts/draft/" not in content

    def test_no_articles_skips_generation(self, caplog):
        gen = _make_generator([])
        generate_random_page(gen)
        dest = os.path.join(gen.output_path, "random", "index.html")
        assert not os.path.exists(dest)

    def test_custom_save_as(self):
        articles = [_make_article("posts/hello/")]
        gen = _make_generator(
            articles, {"RANDOM_ARTICLE_SAVE_AS": "go-random/index.html"}
        )
        generate_random_page(gen)
        dest = os.path.join(gen.output_path, "go-random", "index.html")
        assert os.path.exists(dest)

    def test_urls_are_valid_json_array(self):
        articles = [_make_article("posts/a/"), _make_article("posts/b/")]
        gen = _make_generator(articles)
        generate_random_page(gen)
        dest = os.path.join(gen.output_path, "random", "index.html")
        content = open(dest).read()
        # Extract the JSON array from the JS
        match = re.search(r"var articles = (\[.*?\]);", content, re.DOTALL)
        assert match, "Could not find articles JSON array in output"
        urls = json.loads(match.group(1))
        assert len(urls) == 2
