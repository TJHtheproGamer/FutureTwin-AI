"""Local text preparation: retain source wording, exclude HTML and company intros."""
import re
from html import unescape
from html.parser import HTMLParser


class _Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.hidden += 1
        if tag in {"p", "div", "li", "h1", "h2", "h3", "h4", "br"}:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self.hidden = max(0, self.hidden - 1)

    def handle_data(self, text):
        if not self.hidden:
            self.parts.append(text)


def plain_job_text(value):
    # Some ATS feeds HTML-escape their markup inside JSON content.
    text = str(value or "")
    for _ in range(2):
        text = unescape(text)
    parser = _Text()
    parser.feed(text)
    return re.sub(r"[ \t]+", " ", "\n".join(
        part.strip() for part in "".join(parser.parts).splitlines()
        if part.strip()
    )).strip()


def relevant_responsibilities(value):
    text = plain_job_text(value)
    marker = re.search(
        r"\b(?:what you[’']?ll do|what you will do|your responsibilities|"
        r"responsibilities|what you[’']?ll be doing|what you do|"
        r"about the role|the role|your role|what you[’']?ll own)\b",
        text,
        re.IGNORECASE,
    )
    return (text[marker.start():] if marker else text)[:2200]
