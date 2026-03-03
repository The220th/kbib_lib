import re
from enum import Enum
from pathlib import Path

kbib_lib_out_lang = "en"
INCLUDE_DOI = True
DOI_AS_URL = False


class BibStandards(Enum):
    GOST = 1
    APA = 2


def get_standard_vars() -> list[str]:
    return [el.name for el in BibStandards]


def get_raise_if_miss_standard() -> ValueError:
    return ValueError(f"standard must be in {get_standard_vars()}. ")


def get_words_by_lang() -> dict[str, str]:
    global kbib_lib_out_lang
    if kbib_lib_out_lang == "en":
        return {
            "etal": "et al",
            "vol": "vol",
            "no": "no",
            "pp": "pp",
        }
    elif kbib_lib_out_lang == "ru":
        return {
            "etal": "и др",
            "vol": "Т",
            "no": "№",
            "pp": "С",
        }
    else:
        raise ValueError(f"lang must be only: {kbib_lib_out_lang}.")


def remove_dot_and_strip(s: str) -> str:
    res = s.strip()
    while res[-1] == ".":
        res = s.strip()
        res = res[:-1]
    res = s.strip()
    return res


def form_authors_str(standard: BibStandards,
                     authors: list[str]) -> str:
    authors = [el.strip() for el in authors]
    apa_del = "&"  # and
    words = get_words_by_lang()

    def is_at_al(s: str) -> bool:
        s = s.strip()
        if s == "et al":
            return True
        elif s[-1] == "." and s[:-1] == "et al":
            return True
        else:
            return False

    def add_dot_if_not(s: str) -> str:
        return s + "." if s[-1] != "." else s

    if standard == BibStandards.APA:
        if len(authors) == 1:
            last = add_dot_if_not(authors[-1])
            res = f"{last}"
        elif is_at_al(authors[-1]):
            res = ", ".join(authors) + "."
        else:
            last = add_dot_if_not(authors[-1])
            res = ", ".join(authors[:-1]) + f", {apa_del} " + last
    elif standard == BibStandards.GOST:
        if is_at_al(authors[-1]):
            authors = authors[:-1]
        if len(authors) == 1:
            last = add_dot_if_not(authors[-1])
            res = f"{last}"
        elif len(authors) > 3:
            res = f"{authors[0]} {words['etal']}."
        else:
            last = add_dot_if_not(authors[-1])
            res = ", ".join(authors[:-1]) + ", " + last
    else:
        raise get_raise_if_miss_standard()

    return res


def form_doi_str(doi: str) -> str:
    doi = doi.strip()
    global DOI_AS_URL

    def is_doi_url(doi: str) -> bool:
        doi_regex = r'https?://(www\.)?doi\.org/.+?'
        return re.match(doi_regex, doi) is not None

    def get_doi_from_url(doi_url_src: str) -> str:
        doi_url = doi_url_src.strip()
        assert is_doi_url(doi_url), f"\"{doi_url}\" must be DOI url"
        doi_regex = r'^https?://(www\.)?doi\.org/(.+)$'
        match = re.search(doi_regex, doi_url)
        if match:
            return str(match.group(2))
        else:
            raise ValueError(f"Cannot extract DOI from: \"{doi_url_src}\".")

    if DOI_AS_URL:
        if is_doi_url(doi):
            res = f"{doi}"
        else:
            res = f"https://doi.org/{doi}"
    else:
        if is_doi_url(doi):
            doi_src = get_doi_from_url(doi)
            res = f"DOI: {doi_src}"
        else:
            res = f"DOI: {doi}"

    return res


def form_preprint(standard: BibStandards,
                  title: str, authors: list[str],
                  year: int, publisher_and_id: str, doi: str | None) -> str:
    # words = get_words_by_lang()
    authors_str = form_authors_str(standard, authors)
    title = remove_dot_and_strip(title)
    publisher_and_id = remove_dot_and_strip(publisher_and_id)
    if doi is not None:
        doi = remove_dot_and_strip(doi)
        doi_str = f" {form_doi_str(doi)}."
    else:
        doi_str = ""
    if standard == BibStandards.APA:
        res = f"{authors_str} ({year}). {title}. {publisher_and_id}.{doi_str}"
    elif standard == BibStandards.GOST:
        res = f"{authors_str} {title} // {publisher_and_id}. – {year}.{doi_str}"
    else:
        raise get_raise_if_miss_standard()

    return res


def form_book(standard: BibStandards,
              title: str, authors: list[str],
              year: int, city: str, publisher: str,
              pages: str | None) -> str:
    words = get_words_by_lang()
    authors_str = form_authors_str(standard, authors)
    title = remove_dot_and_strip(title)
    city = remove_dot_and_strip(city)
    publisher = remove_dot_and_strip(publisher)
    if pages is not None:
        pages = remove_dot_and_strip(pages)

    if standard == BibStandards.APA:
        res = f"{authors_str} ({year}) {title}. {city}: {publisher}."
    elif standard == BibStandards.GOST:
        res = f"{authors_str} {title}. {city}: {publisher}, {year}."
    else:
        raise get_raise_if_miss_standard()

    if pages is not None:
        pp = words["pp"]
        if standard == BibStandards.APA:
            res = res[:-1] + f", {pp}. {pages}."
        elif standard == BibStandards.GOST:
            res += f" {pp}. {pages}."
        else:
            raise get_raise_if_miss_standard()

    return res


def form_thesis(standard: BibStandards,
                title: str, authors: list[str],
                year: int, city: str, publisher: str | None,
                extra_text: str | None) -> str:
    # words = get_words_by_lang()
    authors_str = form_authors_str(standard, authors)
    title = remove_dot_and_strip(title)
    city = remove_dot_and_strip(city)
    if publisher is None:
        publisher = ""
    else:
        publisher = remove_dot_and_strip(publisher)
        publisher = f": {publisher}"

    if standard == BibStandards.APA:
        res = f"{authors_str} ({year}) {title} (PhD Thesis). {city}{publisher}."
    elif standard == BibStandards.GOST:
        if extra_text is None:
            extra_text = ""
        else:
            extra_text = remove_dot_and_strip(extra_text)
            extra_text = f" {extra_text}."
        res = f"{authors_str} {title}.{extra_text} {city}{publisher}, {year}."
    else:
        raise get_raise_if_miss_standard()

    return res


def form_article(standard: BibStandards,
                 title: str, authors: list[str],
                 year: int, journal: str,
                 volume: int | None,
                 issue: int | None,
                 pages: str | None,
                 doi: str | None) -> str:
    words = get_words_by_lang()
    authors_str = form_authors_str(standard, authors)
    title = remove_dot_and_strip(title)
    journal = remove_dot_and_strip(journal)

    if doi is not None:
        doi = remove_dot_and_strip(doi)
        doi_str = f" {form_doi_str(doi)}."
    else:
        doi_str = ""

    if standard == BibStandards.APA:
        volume_str = "" if volume is None else f", {words['vol']}. {volume}"
        issue_str = "" if issue is None else f", {words['no']}. {issue}"
        pages_str = "" if pages is None else f", {words['pp']}. {pages}"
        res = f"{authors_str} ({year}) {title}. {journal}{volume_str}{issue_str}{pages_str}.{doi_str}"
    elif standard == BibStandards.GOST:
        volume_str = "" if volume is None else f" – {words['vol']}. {volume}."
        issue_str = "" if issue is None else f" – {words['no']}. {issue}."
        pages_str = "" if pages is None else f" – {words['pp']}. {pages}."
        res = f"{authors_str} {title} // {journal}. – {year}.{volume_str}{issue_str}{pages_str}{doi_str}"
    else:
        raise get_raise_if_miss_standard()

    return res


def form_proceedings(standard: BibStandards,
                     title: str, authors: list[str],
                     year: int, conference: str,
                     city: str | None,
                     publisher: str | None,
                     volume: str | None,
                     issue: str | None,
                     pages: str | None,
                     doi: str | None) -> str:
    words = get_words_by_lang()
    authors_str = form_authors_str(standard, authors)
    title = remove_dot_and_strip(title)
    conference = remove_dot_and_strip(conference)

    if doi is not None:
        doi = remove_dot_and_strip(doi)
        doi_str = f" {form_doi_str(doi)}."
    else:
        doi_str = ""

    if standard == BibStandards.APA:
        if city is not None and publisher is not None:
            city_publisher_str = " {city}: {publisher},"
        elif city is not None and publisher is None:
            city_publisher_str = " {city},"
        elif city is None and publisher is not None:
            city_publisher_str = " {publisher},"
        else:
            city_publisher_str = ""

        volume_str = "" if volume is None else f" {words['vol']}. {volume},"
        issue_str = "" if issue is None else f" {words['no']}. {issue},"
        pages_str = "" if pages is None else f" {words['pp']}. {pages},"

        res = f"{authors_str} ({year}) {title}. {conference}.{city_publisher_str}"
        res += f"{volume_str}{issue_str}{pages_str}"
        res = res if res[-1] != "," else res[:-1] + "."
        res += f"{doi_str}"
    elif standard == BibStandards.GOST:
        city_str = "" if city is None else f" – {city}"
        if city_str == "":
            publisher_str = "" if publisher is None else f" – {publisher}"
        else:
            publisher_str = "" if publisher is None else f": {publisher}"

        volume_str = "" if volume is None else f" – {words['vol']}. {volume}."
        issue_str = "" if issue is None else f" – {words['no']}. {issue}."
        pages_str = "" if pages is None else f" – {words['pp']}. {pages}."

        res = f"{authors_str} {title} // {conference}.{city_str}{publisher_str} – {year}.{volume_str}{issue_str}{pages_str}{doi_str}"
    else:
        raise get_raise_if_miss_standard()

    return res


def form_bibs_from_yaml(yaml_path: Path, needed: list[str]) -> list[str]:
    return []
