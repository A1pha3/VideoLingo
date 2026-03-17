#!/usr/bin/env python3

import re
import sys


SECRET_KEY_VALUE_RE = re.compile(
    r'((?:api(?:[._-]?key)?|token|secret|password|authorization|bearer)[^:=\n]{0,40}[:=]\s*["\']?)([^"\'\s\n]+)',
    re.IGNORECASE,
)
STRING_VALUE_RE = re.compile(r'(string_value:\s*")([^"\n]+)(")')


def mask_value(value: str) -> str:
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}{'*' * (len(value) - 8)}{value[-4:]}"


def looks_sensitive(value: str) -> bool:
    lower_value = value.lower()
    if value.startswith(("http://", "https://")):
        return False
    if lower_value in {
        "your_api_key",
        "your_302_api_key",
        "your_elevenlabs_api_key",
        "your_sf_key",
    }:
        return True
    if value.startswith(("sk-", "pk-")):
        return True
    if len(value) >= 20 and " " not in value and any(ch.isalpha() for ch in value) and any(ch.isdigit() for ch in value):
        return True
    return False


def redact_line(line: str) -> str:
    line = SECRET_KEY_VALUE_RE.sub(lambda match: f"{match.group(1)}{mask_value(match.group(2))}", line)

    def replace_string_value(match: re.Match[str]) -> str:
        value = match.group(2)
        if looks_sensitive(value):
            return f'{match.group(1)}{mask_value(value)}{match.group(3)}'
        return match.group(0)

    return STRING_VALUE_RE.sub(replace_string_value, line)


def main() -> int:
    for raw_line in sys.stdin:
        sys.stdout.write(redact_line(raw_line))
        sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())