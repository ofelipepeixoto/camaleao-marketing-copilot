"""Strict v1 contracts and deterministic observations using only the standard library.

Input: schema_version='camaleao.marketing.input/v1', mode, context, and page OR rows.
Context always requires project_id, date_start/date_end (canonical ISO dates). Ads
also requires currency, conversion_definition, attribution_window, timezone and
UTC data_as_of. Examples are executable contract specimens. Unknown keys fail.

All data is untrusted. Findings contain JSON pointers, codes and numbers only;
source text, URLs, IDs, queries, campaign labels and HTML never enter reports.
Heuristics describe the submitted snapshot/export, never ranking or future ROI.
"""

import hashlib
import json
import os
import re
import stat
from datetime import date, datetime
from decimal import Decimal, localcontext, ROUND_HALF_UP
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

INPUT_SCHEMA = "camaleao.marketing.input/v1"
OUTPUT_SCHEMA = "camaleao.marketing.report/v1"
MAX_INPUT_BYTES = 1024 * 1024
MAX_HTML_BYTES = 256 * 1024
MAX_ROWS = 5000
MAX_FINDINGS = 100
MAX_INTEGER = 10**12
CHANNELS = {"google_ads", "meta_ads", "linkedin_ads", "tiktok_ads", "amazon_ads", "other"}
CURRENCIES = {"BRL", "USD", "EUR"}
IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}\Z")
MONEY = re.compile(r"(?:0|[1-9][0-9]{0,11})\.[0-9]{2}\Z")
POSITION = re.compile(r"(?:0|[1-9][0-9]{0,3})(?:\.[0-9]{1,6})?\Z")


class InputError(ValueError):
    """A generic failure; callers must not echo untrusted content in error messages."""


def _fail():
    raise InputError("Invalid or unsafe input.")


def _exact(obj, keys):
    if type(obj) is not dict or set(obj) != set(keys):
        _fail()


def _string(value, maximum, minimum=0):
    if type(value) is not str or not minimum <= len(value) <= maximum:
        _fail()
    try:
        value.encode("utf-8", errors="strict")
    except UnicodeError:
        _fail()
    return value


def _identifier(value):
    if not IDENTIFIER.fullmatch(_string(value, 64, 1)):
        _fail()


def _integer(value):
    if type(value) is not int or not 0 <= value <= MAX_INTEGER:
        _fail()
    return value


def _money(value):
    if not MONEY.fullmatch(_string(value, 15, 4)):
        _fail()
    return Decimal(value)


def _position(value):
    if not POSITION.fullmatch(_string(value, 11, 1)):
        _fail()
    number = Decimal(value)
    if not Decimal(1) <= number <= Decimal(1000):
        _fail()
    return number


def _date(value):
    _string(value, 10, 10)
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        _fail()
    if parsed.isoformat() != value:
        _fail()
    return parsed


def _url(value):
    """An absolute HTTPS URL without userinfo, query, fragment or control bytes.

    This is a syntax check only: no URL is requested and no host ownership or
    public routability is asserted. Canonical links are observations, not trust.
    """
    _string(value, 2048, 9)
    if any(ord(c) < 33 or ord(c) == 127 for c in value) or "\\" in value:
        _fail()
    try:
        url = urlsplit(value)
        if (url.scheme != "https" or not url.hostname or url.username is not None
                or url.password is not None or url.query or url.fragment
                or url.port not in (None, 443)):
            _fail()
        # A limited ASCII hostname avoids ambiguous Unicode host spellings.
        if not re.fullmatch(r"[A-Za-z0-9.-]+", url.hostname) or ".." in url.hostname:
            _fail()
    except ValueError:
        _fail()
    return value


def _parent_fd(path):
    """Traverse using no-follow directory handles, including every parent.

    Existing parent directories are required. O_NOFOLLOW is a POSIX contract;
    unsupported platforms fail closed rather than silently following symlinks.
    """
    if os.name != "posix" or any(not isinstance(getattr(os, flag, None), int)
                                or getattr(os, flag) <= 0
                                for flag in ("O_DIRECTORY", "O_NOFOLLOW")):
        _fail()
    path = Path(path)
    if ".." in path.parts or not path.name:
        _fail()
    absolute = Path(os.path.abspath(path))
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    current = os.open("/", flags)
    try:
        for part in absolute.parts[1:-1]:
            next_fd = os.open(part, flags, dir_fd=current)
            os.close(current)
            current = next_fd
        return current, absolute.name
    except BaseException:
        os.close(current)
        raise


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            _fail()
        result[key] = value
    return result


def _constant(_):
    _fail()


def _validate_unicode(value, depth=0):
    if depth > 24:
        _fail()
    if type(value) is str:
        _string(value, MAX_HTML_BYTES)
    elif type(value) is list:
        if len(value) > MAX_ROWS:
            _fail()
        for item in value:
            _validate_unicode(item, depth + 1)
    elif type(value) is dict:
        for key, item in value.items():
            _string(key, 64, 1)
            _validate_unicode(item, depth + 1)


def parse_input(raw):
    if type(raw) is not bytes or len(raw) > MAX_INPUT_BYTES:
        _fail()
    try:
        data = json.loads(raw.decode("utf-8", errors="strict"), object_pairs_hook=_pairs,
                          parse_constant=_constant, parse_float=_constant)
        _validate_unicode(data)
    except (UnicodeError, ValueError, RecursionError):
        _fail()
    return data


def load_input(path):
    parent, name = _parent_fd(path)
    try:
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        with os.fdopen(fd, "rb") as source:
            if not stat.S_ISREG(os.fstat(source.fileno()).st_mode):
                _fail()
            raw = source.read(MAX_INPUT_BYTES + 1)
        parse_input(raw)
        return raw
    finally:
        os.close(parent)


def write_report(path, report):
    payload = (json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2,
                          allow_nan=False) + "\n").encode("utf-8")
    if len(payload) > MAX_INPUT_BYTES:
        _fail()
    parent, name = _parent_fd(path)
    try:
        fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                     0o600, dir_fd=parent)
        try:
            with os.fdopen(fd, "wb") as target:
                target.write(payload)
        except BaseException:
            os.unlink(name, dir_fd=parent)
            raise
    finally:
        os.close(parent)


def _ratio(numerator, denominator, places=6):
    if not denominator:
        return None
    quantum = Decimal(1).scaleb(-places)
    with localcontext() as ctx:
        ctx.prec = 48
        value = Decimal(numerator) / Decimal(denominator)
        return format(value.quantize(quantum, rounding=ROUND_HALF_UP), "f")


def _amount(value):
    return format(value, ".2f")


def _finding(code, pointer, **details):
    return {"code": code, "source_pointer": pointer, "details": details,
            "review_status": "pending"}


class _PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.titles = []
        self.in_title = False
        self.h1_count = 0
        self.descriptions = []
        self.canonicals = []
        self.robots = []
        self.jsonld_count = 0
        self.jsonld_blocks = []
        self.in_jsonld = False

    def handle_starttag(self, tag, attrs):
        attrs = {key: (value if value is not None else "") for key, value in attrs}
        if tag == "title":
            self.titles.append("")
            self.in_title = True
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "meta":
            name = attrs.get("name", "").lower()
            if name == "description":
                self.descriptions.append(attrs.get("content", ""))
            elif name in {"robots", "googlebot"}:
                self.robots.append(attrs.get("content", "").lower())
        elif tag == "link" and "canonical" in attrs.get("rel", "").lower().split():
            self.canonicals.append(attrs.get("href", ""))
        elif tag == "script":
            self.in_jsonld = attrs.get("type", "").lower() == "application/ld+json"
            if self.in_jsonld:
                self.jsonld_count += 1
                self.jsonld_blocks.append("")

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        elif tag == "script":
            self.in_jsonld = False

    def handle_data(self, data):
        if self.in_title and self.titles:
            self.titles[-1] += data
        if self.in_jsonld and self.jsonld_blocks:
            self.jsonld_blocks[-1] += data


def _seo(page):
    _exact(page, {"url", "html"})
    _url(page["url"])
    html = _string(page["html"], MAX_HTML_BYTES)
    if len(html.encode("utf-8")) > MAX_HTML_BYTES:
        _fail()
    parser = _PageParser()
    parser.feed(html)
    parser.close()
    findings = []
    metrics = {
        "snapshot_bytes": len(html.encode("utf-8")),
        "title_count": len(parser.titles),
        "title_lengths": [len(title.strip()) for title in parser.titles[:20]],
        "description_count": len(parser.descriptions),
        "description_lengths": [len(text.strip()) for text in parser.descriptions[:20]],
        "h1_count": parser.h1_count,
        "canonical_count": len(parser.canonicals),
        "robots_meta_count": len(parser.robots),
        "jsonld_block_count": parser.jsonld_count,
    }
    for count, code in ((len(parser.titles), "title_count_review"),
                        (len(parser.descriptions), "description_count_review"),
                        (parser.h1_count, "h1_count_review"),
                        (len(parser.canonicals), "canonical_count_review")):
        if count != 1:
            findings.append(_finding(code, "/page/html", observed_count=count))
    if any(not title.strip() for title in parser.titles):
        findings.append(_finding("empty_title", "/page/html"))
    if any(not text.strip() for text in parser.descriptions):
        findings.append(_finding("empty_description", "/page/html"))
    valid_canonicals = []
    for canonical in parser.canonicals:
        try:
            _url(canonical)
            valid_canonicals.append(canonical)
        except InputError:
            pass
    metrics["canonical_https_syntax_valid_count"] = len(valid_canonicals)
    metrics["canonical_matches_submitted_url"] = (
        parser.canonicals[0] == page["url"] if len(parser.canonicals) == 1 else None)
    if len(valid_canonicals) != len(parser.canonicals):
        findings.append(_finding("canonical_syntax_review", "/page/html"))
    noindex = any("noindex" in re.split(r"[\s,;]+", text) or "none" in re.split(r"[\s,;]+", text)
                  for text in parser.robots)
    metrics["robots_noindex_observed"] = noindex
    if noindex:
        findings.append(_finding("robots_noindex_observed", "/page/html"))
    valid_jsonld = 0
    for block in parser.jsonld_blocks:
        try:
            parsed = json.loads(block, object_pairs_hook=_pairs, parse_constant=_constant)
            _validate_unicode(parsed)
            if type(parsed) in (dict, list):
                valid_jsonld += 1
        except (ValueError, RecursionError):
            pass
    metrics["jsonld_json_syntax_valid_count"] = valid_jsonld
    if valid_jsonld != parser.jsonld_count:
        findings.append(_finding("jsonld_syntax_review", "/page/html"))
    findings.append(_finding("snapshot_only_no_site_request", "/page/html"))
    return metrics, findings, [
        "html_parsed_as_data_only", "no_http_status_or_header_validation",
        "no_robots_txt_or_javascript_rendering", "no_core_web_vitals_or_ranking_measurement",
        "jsonld_syntax_does_not_establish_schema_validity",
    ]


def _rows(data):
    if type(data) is not list or not 1 <= len(data) <= MAX_ROWS:
        _fail()
    return data


def _search_console(rows):
    clicks = impressions = 0
    weighted = Decimal(0)
    findings = []
    opportunity_count = 0
    for index, row in enumerate(_rows(rows)):
        _exact(row, {"query", "page", "clicks", "impressions", "position"})
        _string(row["query"], 512, 1)
        _url(row["page"])
        row_clicks, row_impressions = _integer(row["clicks"]), _integer(row["impressions"])
        if row_clicks > row_impressions:
            _fail()
        position = _position(row["position"])
        clicks += row_clicks
        impressions += row_impressions
        weighted += position * row_impressions
        # Strictly below 2%; integer arithmetic avoids rounding at the threshold.
        if row_impressions >= 100 and row_clicks * 100 < row_impressions * 2:
            opportunity_count += 1
            if len(findings) < MAX_FINDINGS:
                findings.append(_finding("high_impressions_low_ctr_heuristic", f"/rows/{index}",
                                         impressions=row_impressions,
                                         ctr_percent=_ratio(row_clicks * 100, row_impressions)))
    return {
        "row_count": len(rows), "clicks": clicks, "impressions": impressions,
        "ctr_percent": _ratio(clicks * 100, impressions),
        "position_impression_weighted": _ratio(weighted, impressions),
        "heuristic_opportunity_count": opportunity_count,
    }, findings, ["submitted_rows_only_export_completeness_unverified",
                  "position_is_export_aggregate_not_rank_tracking",
                  "opportunity_rule_impressions_at_least_100_and_ctr_below_2_percent",
                  "no_causal_or_forecast_claim"]


def _paid(rows, context):
    groups = {}
    seen = set()
    for row in _rows(rows):
        _exact(row, {"id", "campaign", "channel", "currency", "spend", "revenue",
                     "conversions", "clicks", "impressions"})
        _identifier(row["id"])
        _identifier(row["campaign"])
        if row["id"] in seen:
            _fail()
        seen.add(row["id"])
        if type(row["channel"]) is not str or row["channel"] not in CHANNELS:
            _fail()
        if row["currency"] != context["currency"]:
            _fail()
        spend, revenue = _money(row["spend"]), _money(row["revenue"])
        conversions = _integer(row["conversions"])
        clicks, impressions = _integer(row["clicks"]), _integer(row["impressions"])
        if clicks > impressions:
            _fail()
        group = groups.setdefault(row["channel"], {"spend": Decimal(0), "revenue": Decimal(0),
                                                   "conversions": 0, "clicks": 0, "impressions": 0,
                                                   "row_count": 0})
        group["spend"] += spend
        group["revenue"] += revenue
        group["conversions"] += conversions
        group["clicks"] += clicks
        group["impressions"] += impressions
        group["row_count"] += 1
    channels = []
    for channel, group in sorted(groups.items()):
        channels.append({
            "channel": channel, "row_count": group["row_count"],
            "spend": _amount(group["spend"]), "reported_revenue": _amount(group["revenue"]),
            "reported_conversions": group["conversions"], "clicks": group["clicks"],
            "impressions": group["impressions"],
            "ctr_percent": _ratio(group["clicks"] * 100, group["impressions"]),
            "cpa": _ratio(group["spend"], group["conversions"], 2),
            "roas": _ratio(group["revenue"], group["spend"]),
        })
    return {
        "row_count": len(rows), "channel_count": len(channels), "currency": context["currency"],
        "spend": _amount(sum((group["spend"] for group in groups.values()), Decimal(0))),
        "channels": channels,
    }, [_finding("reported_conversion_and_revenue_require_review", "/rows"),
        _finding("no_cross_channel_blended_cpa_or_roas", "/rows")], [
            "reported_values_not_independently_audited",
            "global_definition_and_attribution_declared_by_submitter",
            "no_cross_channel_deduplication_or_attribution_verification",
            "cpa_and_roas_are_historical_arithmetic_not_forecasts",
            "no_budget_allocation_or_campaign_changes",
        ]


def _context(context, mode):
    fields = {"project_id", "date_start", "date_end"}
    if mode == "paid_media":
        fields |= {"currency", "conversion_definition", "attribution_window", "timezone", "data_as_of"}
    _exact(context, fields)
    _identifier(context["project_id"])
    if _date(context["date_start"]) > _date(context["date_end"]):
        _fail()
    if mode == "paid_media":
        if type(context["currency"]) is not str or context["currency"] not in CURRENCIES:
            _fail()
        if context["conversion_definition"] not in ("purchase", "lead", "signup", "custom"):
            _fail()
        if context["attribution_window"] not in ("1d_click", "7d_click", "30d_click", "platform_reported"):
            _fail()
        _string(context["timezone"], 64, 1)
        try:
            ZoneInfo(context["timezone"])
        except (ZoneInfoNotFoundError, ValueError):
            _fail()
        _string(context["data_as_of"], 20, 20)
        try:
            stamp = datetime.strptime(context["data_as_of"], "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            _fail()
        if stamp.strftime("%Y-%m-%dT%H:%M:%SZ") != context["data_as_of"]:
            _fail()


def analyze(raw):
    """Return a deterministic report. Accept raw bytes to bind the exact input hash."""
    data = parse_input(raw)
    if type(data) is not dict:
        _fail()
    mode = data.get("mode")
    if type(mode) is not str or mode not in ("seo_page", "search_console", "paid_media"):
        _fail()
    _exact(data, {"schema_version", "mode", "context", "page" if mode == "seo_page" else "rows"})
    if data["schema_version"] != INPUT_SCHEMA:
        _fail()
    _context(data["context"], mode)
    with localcontext() as ctx:
        ctx.prec = 48
        if mode == "seo_page":
            metrics, findings, limitations = _seo(data["page"])
        elif mode == "search_console":
            metrics, findings, limitations = _search_console(data["rows"])
        else:
            metrics, findings, limitations = _paid(data["rows"], data["context"])
    return {
        "schema_version": OUTPUT_SCHEMA, "mode": mode,
        "input_sha256": hashlib.sha256(raw).hexdigest(), "observed_metrics": metrics,
        "measurement_context": {key: value for key, value in data["context"].items()
                                if key != "project_id"} | {"source_pointer": "/context"},
        "findings": findings[:MAX_FINDINGS], "findings_truncated": len(findings) > MAX_FINDINGS
            or (mode == "search_console" and metrics["heuristic_opportunity_count"] > MAX_FINDINGS),
        "limitations": limitations, "review_status": "pending", "execution_allowed": False,
    }
