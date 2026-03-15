import json
import logging
import os

from jinja2 import Environment

from pelican import signals

log = logging.getLogger(__name__)

_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>{{ SITENAME }} – Random Article</title>
  <meta name="robots" content="noindex, nofollow" />
  <style>
    body {
      font-family: sans-serif;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      margin: 0;
      background: #fafafa;
      color: #333;
    }
    p { font-size: 1.1rem; }
    a { color: #0078d4; }
  </style>
</head>
<body>
  <p>⏳ Redirecting to a random article…</p>
  <p><small>If nothing happens, <a id="fallback" href="{{ SITEURL }}">click here</a>.</small></p>

  <script>
    var articles = {{ article_urls | tojson }};

    function randomRedirect() {
      if (!articles || articles.length === 0) {
        window.location.href = "{{ SITEURL }}";
        return;
      }
      var target = articles[Math.floor(Math.random() * articles.length)];
      document.getElementById("fallback").href = target;
      window.location.href = target;
    }

    randomRedirect();
  </script>
</body>
</html>
"""


def generate_random_page(generator):
    """Collect all article URLs and write the random-redirect page."""
    context = generator.context

    # Collect published article URLs
    articles = [
        a
        for a in generator.articles
        if getattr(a, "status", "published") == "published"
    ]
    if not articles:
        log.warning(
            "pelican-random-article: No published articles found; skipping page generation."
        )
        return

    siteurl = context.get("SITEURL", "")
    article_urls = []
    for article in articles:
        url = article.url
        # Make absolute if SITEURL is provided
        if siteurl and not url.startswith(("http://", "https://")):
            url = siteurl.rstrip("/") + "/" + url.lstrip("/")
        article_urls.append(url)

    # Render template
    env = Environment()
    env.filters["tojson"] = lambda x: json.dumps(x)
    tmpl = env.from_string(_TEMPLATE)

    html = tmpl.render(
        SITENAME=context.get("SITENAME", ""),
        SITEURL=siteurl,
        article_urls=article_urls,
    )

    # Determine output path
    output_path = generator.output_path
    save_as = context.get("RANDOM_ARTICLE_SAVE_AS", "random/index.html")
    dest = os.path.join(output_path, save_as)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        f.write(html)

    log.info(
        "pelican-random-article: Generated %s with %d articles.",
        dest,
        len(article_urls),
    )


def register():
    signals.article_generator_finalized.connect(generate_random_page)
