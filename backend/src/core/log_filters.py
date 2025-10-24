# backend/src/core/log_filters.py
import logging
import re

# Match common WP/legacy probes we want to ignore in access logs
_SUPPRESS = re.compile(
    r" (GET|HEAD) /(wp(?:-|/)|wordpress/|blog/|web/|news/|site/|media/|cms/|wp1/|wp2/)"
    r"| (GET|HEAD) /.*/wlwmanifest\.xml"
    r"| (GET|HEAD) /xmlrpc\.php"
    r"| (GET|HEAD) /(?:\d{4})/wp-includes/wlwmanifest\.xml",
    re.IGNORECASE,
)


class AccessPathSuppressFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        try:
            msg = record.getMessage()
        except Exception:
            return True
        return not _SUPPRESS.search(msg)
