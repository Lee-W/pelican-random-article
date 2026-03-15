# pelican-random-article

**pelican-random-article** is a Pelican plugin that automatically generates a `/random` page.  
Visiting `/random` instantly redirects the reader to a randomly chosen article — just like [wiwi.blog/random](https://wiwi.blog/random).

## Features

* Generates a static `random/index.html` page at build time.
* Picks a random article **client-side** using JavaScript — no server required.
* Works with any Pelican theme; no template changes needed.
* Configurable output path via `pelicanconf.py`.

## Installation

```bash
pip install pelican-random-article
```

Or with `uv`:

```bash
uv add pelican-random-article
```

## Usage

### 1. Enable the plugin in `pelicanconf.py`

```python
PLUGINS = [
    # ... your other plugins ...
    "pelican.plugins.random_article",
]
```

### 2. (Optional) Add a link in your navigation

Point any link to `/random` (or wherever `RANDOM_ARTICLE_SAVE_AS` points):

```html
<a href="{{ SITEURL }}/random/">Random</a>
```

### 3. Build your site

```bash
pelican content
```

The plugin will write `output/random/index.html` automatically.

## Configuration

Add these to `pelicanconf.py` to customise the output path:

```python
# Default values shown below
RANDOM_ARTICLE_SAVE_AS = "random/index.html"
```

> **Note:** `RANDOM_ARTICLE_URL` is not consumed by the plugin itself —  
> it is only needed if you want Pelican's link helpers to resolve `/random`.  
> Set it to match `RANDOM_ARTICLE_SAVE_AS`:

 ```python
 RANDOM_ARTICLE_URL = "random/"
 RANDOM_ARTICLE_SAVE_AS = "random/index.html"
> ```

## How it works

At build time the plugin:

1. Connects to Pelican's `article_generator_finalized` signal.
2. Collects all published article URLs.
3. Renders a tiny HTML page that contains the full URL list as a JSON array.
4. On page load, JavaScript picks a random entry and calls `window.location.href`.

Because the redirect happens client-side, the page is completely static and  
requires no server-side logic.

## Requirements

* Python >= 3.11
* Pelican >= 4.5
* Jinja2 (bundled with Pelican)

## License

MIT License © Wei Lee
