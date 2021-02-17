def sget(l, i, default=None, force_default=True):
    value = next(iter(l[i : i + 1]), default)
    if value is None and force_default:
        value = default
    return value


def create_url(url_str: str) -> str:
    url_str = url_str.strip("/")
    if not url_str.startswith("http://") and not url_str.startswith("https://"):
        url_str = f"https://{url_str}"
    return url_str
