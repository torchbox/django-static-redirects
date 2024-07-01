# Django Static Redirects

![CI](https://github.com/torchbox/django-static-redirects/workflows/CI/badge.svg)
![PyPI](https://img.shields.io/pypi/v/django-static-redirects.svg)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-static-redirects.svg)
![PyPI - License](https://img.shields.io/pypi/l/django-static-redirects.svg)

Define redirects in your repository as either CSV of JSON files, and have Django performantly serve them.

Redirect matching is designed to be as fast as possible, and does not use the database.

## Installation

```
pip install django-static-redirects
```

Then, add `static_redirects` to `INSTALLED_APPS`.

The redirect is done as a middleware. Add `static_redirects.StaticRedirectsMiddleware` wherever makes sense for you in `MIDDLEWARE` - ideally below any middleware which modify the response (eg `GzipMiddleware`) but above anything especially intensive, so the redirects are applied before them.

## Usage

To add files containing redirects, set them in `STATIC_REDIRECTS`:

```python
STATIC_REDIRECTS = [
    BASE_DIR / "static-redirect.csv",
    BASE_DIR / "static-redirect.json",
]
```

Redirect files are read in-order, with latter redirects taking precedence.

Redirects can either be just paths, in which case they match all hostnames, or include a hostname. Schemes are not included as part of the match. If a request contains a querystring, it is ignored, unless a match containing the querystring is found.

### Redirect files

Redirect files must contain a "source", a "destination", a "permanent" (optional) and a "host" (optional). "source" is the source path, "destination" is the destination URL, "permanent" whether the redirect is permanent (defaults to `false`), and "host" allows constraining which host the redirect applies to.

```csv
source,destination,permanent,host
/source,/destination,true
/source2,/destination2
/source3,/destination3,false,example.com
```

```json
[
    {
        "source": "/source",
        "destination": "/destination",
        "permanent": true
    },
    {
        "source": "/source2",
        "destination": "/destination2",
    },
    {
        "source": "/source3",
        "destination": "/destination3",
        "host": "example.com"
    },

]
```

For CSV files, the columns may be in any order, however the column names are case-sensitive.
