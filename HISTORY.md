Release History
===============

dev
---

- \[Short description of non-trivial change.\]

2.27.1 (2022-01-05)
-------------------

**Bugfixes**

- Fixed parsing issue that resulted in the `auth` component being
  dropped from proxy URLs. (#6028)

2.27.0 (2022-01-03)
-------------------

**Improvements**

- Officially added support for Python 3.10. (#5928)

- Added a `requests.exceptions.JSONDecodeError` to unify JSON exceptions between
  Python 2 and 3. This gets raised in the `response.json()` method, and is
  backwards compatible as it inherits from previously thrown exceptions.
  Can be caught from `requests.exceptions.RequestException` as well. (#5856)

- Improved error text for misnamed `InvalidSchema` and `MissingSchema`
  exceptions. This is a temporary fix until exceptions can be renamed
  (Schema->Scheme). (#6017)

- Improved proxy parsing for proxy URLs missing a scheme. This will address
  recent changes to `urlparse` in Python 3.9+. (#5917)

**Bugfixes**

- Fixed defect in `extract_zipped_paths` which could result in an infinite loop
  for some paths. (#5851)

- Fixed handling for `AttributeError` when calculating length of files obtained
  by `Tarfile.extractfile()`. (#5239)

- Fixed urllib3 exception leak, wrapping `urllib3.exceptions.InvalidHeader` with
  `requests.exceptions.InvalidHeader`. (#5914)

- Fixed bug where two Host headers were sent for chunked requests. (#5391)

- Fixed regression in Requests 2.26.0 where `Proxy-Authorization` was
  incorrectly stripped from all requests sent with `Session.send`. (#5924)

- Fixed performance regression in 2.26.0 for hosts with a large number of
  proxies available in the environment. (#5924)

- Fixed idna exception leak, wrapping `UnicodeError` with
  `requests.exceptions.InvalidURL` for URLs with a leading dot (.) in the
  domain. (#5414)

**Deprecations**

- Requests support for Python 2.7 and 3.6 will be ending in 2022. While we
  don't have exact dates, Requests 2.27.x is likely to be the last release
  series providing support.

2.26.0 (2021-07-13)
-------------------

**Improvements**

- Requests now supports Brotli compression, if either the `brotli` or
  `brotlicffi` package is installed. (#5783)

- `Session.send` now correctly resolves proxy configurations from both
  the Session and Request. Behavior now matches `Session.request`. (#5681)

**Bugfixes**

- Fixed a race condition in zip extraction when using Requests in parallel
  from zip archive. (#5707)

**Dependencies**

- Instead of `chardet`, use the MIT-licensed `charset_normalizer` for Python3
  to remove license ambiguity for projects bundling requests. If `chardet`
  is already installed on your machine it will be used instead of `charset_normalizer`
  to keep backwards compatibility. (#5797)

  You can also install `chardet` while installing requests by
  specifying `[use_chardet_on_py3]` extra as follows:

    ```shell
    pip install "requests[use_chardet_on_py3]"
    ```

  Python2 still depends upon the `chardet` module.

- Requests now supports `idna` 3.x on Python 3. `idna` 2.x will continue to
  be used on Python 2 installations. (#5711)

**Deprecations**

- The `requests[security]` extra has been converted to a no-op install.
  PyOpenSSL is no longer the recommended secure option for Requests. (#5867)

- Requests has officially dropped support for Python 3.5. (#5867)

0.2.4 (2011-02-19)
------------------

-   Python 2.5 Support
-   PyPy-c v1.4 Support
-   Auto-Authentication tests
-   Improved Request object constructor

0.2.3 (2011-02-15)
------------------

-

    New HTTPHandling Methods

    :   -   Response.\_\_nonzero\_\_ (false if bad HTTP Status)
        -   Response.ok (True if expected HTTP Status)
        -   Response.error (Logged HTTPError if bad HTTP Status)
        -   Response.raise\_for\_status() (Raises stored HTTPError)

0.2.2 (2011-02-14)
------------------

-   Still handles request in the event of an HTTPError. (Issue \#2)
-   Eventlet and Gevent Monkeypatch support.
-   Cookie Support (Issue \#1)

0.2.1 (2011-02-14)
------------------

-   Added file attribute to POST and PUT requests for multipart-encode
    file uploads.
-   Added Request.url attribute for context and redirects

0.2.0 (2011-02-14)
------------------

-   Birth!

0.0.1 (2011-02-13)
------------------

-   Frustration
-   Conception
