# Django Static Redirects

![CI](https://github.com/RealOrangeOne/django-static-redirects/workflows/CI/badge.svg)
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
]
```

Redirect files are read in-order, with latter redirects taking precedence.

### CSV files

CSV files must contain 2 or 3 columns, without a header. The first column is the source path, second is the destination URL, and the (optional) third notes whether the redirect is permanent.

```csv
/source,/destination,true
/source2,/destination2
```

### JSON files

JSON files must contain a list of objects:

```json
[
    {
        "source": "/source",
        "destination": "/destination",
        "is_permanent": true
    },
    {
        "source": "/source2",
        "destination": "/destination2",
    }
]
```

Much like CSV, `is_permanent` is optional, defaulting to `false`.
