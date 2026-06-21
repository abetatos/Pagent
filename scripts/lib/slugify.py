"""Title → filesystem-safe slug."""

from __future__ import annotations

import re
import unicodedata


def slugify(title: str) -> str:
    """Convert a title to a lowercase, hyphenated, ASCII-only slug.

    Examples:
        >>> slugify("La Sombra del Cardenal")
        'la-sombra-del-cardenal'
        >>> slugify("Wind, Ash & Blue")
        'wind-ash-and-blue'
    """
    text = title.replace("&", " and ")
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    if not text:
        text = "untitled"
    return text[:80]
