import re
from pathlib import Path
import yaml
from typing import Union

from kbib_lib.bib_classes import BibStandards, BibTypes, PreprintBib, BookBib, ThesisBib, ArticleBib, ProceedingsBib

kbib_lib_out_lang = "en"
INCLUDE_DOI = True
DOI_AS_URL = False
MAX_AUTHORS = None


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
            "proceedings_of_the": "Proceedings of the",
        }
    elif kbib_lib_out_lang == "ru":
        return {
            "etal": "и др",
            "vol": "Т",
            "no": "№",
            "pp": "С",
            "proceedings_of_the": "Тез. докл.",
        }
    else:
        raise ValueError(f"lang must be only: {kbib_lib_out_lang}.")


def remove_dot_and_strip(s: str) -> str:
    res = s.strip()
    while res[-1] == ".":
        res = res.strip()
        res = res[:-1]
    res = res.strip()
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
        elif s == words["etal"]:
            return True
        elif s[-1] == "." and s[:-1] == words["etal"]:
            return True
        else:
            return False

    if is_at_al(authors[-1]):
        authors[-1] = words["etal"]

    if MAX_AUTHORS is not None:
        if len(authors) <= MAX_AUTHORS:
            pass
        else:
            authors = authors[:MAX_AUTHORS]
            authors.append(words["etal"])

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
    if doi is not None and INCLUDE_DOI:
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


def form_preprint_4(standard: BibStandards,
                    item: PreprintBib) -> str:
    return form_preprint(standard=standard, title=item.title, authors=item.authors,
                         year=item.year, publisher_and_id=item.publisher_and_id, doi=item.doi)


def form_book(standard: BibStandards,
              title: str, authors: list[str],
              year: int, city: str | None, publisher: str | None,
              pages: str | None) -> str:
    words = get_words_by_lang()
    authors_str = form_authors_str(standard, authors)
    title = remove_dot_and_strip(title)
    if city is not None:
        city = remove_dot_and_strip(city)
    if publisher is not None:
        publisher = remove_dot_and_strip(publisher)
    if pages is not None:
        pages = remove_dot_and_strip(pages)

    if standard == BibStandards.APA:
        if city is not None and publisher is not None:
            city_publisher_str = f" {city}: {publisher}."
        elif city is not None and publisher is None:
            city_publisher_str = f" {city}."
        elif city is None and publisher is not None:
            city_publisher_str = f" {publisher}."
        else:
            city_publisher_str = ""

        res = f"{authors_str} ({year}) {title}.{city_publisher_str}"
    elif standard == BibStandards.GOST:
        if city is not None and publisher is not None:
            city_publisher_str = f" {city}: {publisher},"
        elif city is not None and publisher is None:
            city_publisher_str = f" {city},"
        elif city is None and publisher is not None:
            city_publisher_str = f" {publisher},"
        else:
            city_publisher_str = ""
        res = f"{authors_str} {title}.{city_publisher_str} {year}."
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


def form_book_4(standard: BibStandards,
                item: BookBib) -> str:
    return form_book(standard=standard, title=item.title, authors=item.authors,
                     year=item.year, city=item.city, publisher=item.publisher, pages=item.pages)


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


def form_thesis_4(standard: BibStandards,
                  item: ThesisBib) -> str:
    return form_thesis(standard=standard, title=item.title, authors=item.authors,
                       year=item.year, city=item.city, publisher=item.publisher, extra_text=item.extra_text)


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

    if doi is not None and INCLUDE_DOI:
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


def form_article_4(standard: BibStandards,
                   item: ArticleBib) -> str:
    return form_article(standard=standard, title=item.title,
                        authors=item.authors, year=item.year, journal=item.journal,
                        volume=item.volume, issue=item.issue, pages=item.pages, doi=item.doi)


def form_proceedings(standard: BibStandards,
                     title: str, authors: list[str],
                     year: int, conference: str,
                     place_and_date: str | None,
                     city: str | None,
                     publisher: str | None,
                     volume: int | None,
                     issue: int | None,
                     pages: str | None,
                     doi: str | None) -> str:
    words = get_words_by_lang()
    authors_str = form_authors_str(standard, authors)
    title = remove_dot_and_strip(title)
    conference = remove_dot_and_strip(conference)

    if doi is not None and INCLUDE_DOI:
        doi = remove_dot_and_strip(doi)
        doi_str = f" {form_doi_str(doi)}."
    else:
        doi_str = ""

    if city is not None:
        city = remove_dot_and_strip(city)
    if publisher is not None:
        publisher = remove_dot_and_strip(publisher)

    if standard == BibStandards.APA:
        proceedings_of_the_str = f"{words['proceedings_of_the']} "
        place_and_date_str = f", {remove_dot_and_strip(place_and_date)}" if place_and_date is not None else ""

        if city is not None and publisher is not None:
            city_publisher_str = f" {city}: {publisher},"
        elif city is not None and publisher is None:
            city_publisher_str = f" {city},"
        elif city is None and publisher is not None:
            city_publisher_str = f" {publisher},"
        else:
            city_publisher_str = ""

        volume_str = "" if volume is None else f" {words['vol']}. {volume},"
        issue_str = "" if issue is None else f" {words['no']}. {issue},"
        pages_str = "" if pages is None else f" {words['pp']}. {pages},"

        res = f"{authors_str} ({year}) {title}. {proceedings_of_the_str}{conference}{place_and_date_str}.{city_publisher_str}"
        res += f"{volume_str}{issue_str}{pages_str}"
        res = res if res[-1] != "," else res[:-1] + "."
        res += f"{doi_str}"
    elif standard == BibStandards.GOST:
        proceedings_of_the_str = f"{words['proceedings_of_the']} "
        place_and_date_str = f", {remove_dot_and_strip(place_and_date)}" if place_and_date is not None else ""

        city_str = "" if city is None else f" – {city}"
        if city_str == "":
            publisher_str = "" if publisher is None else f" – {publisher}"
        else:
            publisher_str = "" if publisher is None else f": {publisher}"

        volume_str = "" if volume is None else f" – {words['vol']}. {volume}."
        issue_str = "" if issue is None else f" – {words['no']}. {issue}."
        pages_str = "" if pages is None else f" – {words['pp']}. {pages}."

        res = f"{authors_str} {title} // {proceedings_of_the_str}{conference}{place_and_date_str}.{city_str}{publisher_str} – {year}.{volume_str}{issue_str}{pages_str}{doi_str}"
    else:
        raise get_raise_if_miss_standard()

    return res


def form_proceedings_4(standard: BibStandards,
                       item: ProceedingsBib) -> str:
    return form_proceedings(standard=standard, title=item.title, authors=item.authors,
                            year=item.year, conference=item.conference,
                            place_and_date=item.place_and_date, city=item.city, publisher=item.publisher,
                            volume=item.volume, issue=item.issue, pages=item.pages, doi=item.doi)


def dict_to_bibs(d: dict, needed: list[str] | None) -> list[Union[PreprintBib, BookBib, ThesisBib, ArticleBib, ProceedingsBib]]:

    res: list[Union[PreprintBib, BookBib,
                    ThesisBib, ArticleBib, ProceedingsBib]] = []
    if needed is None:
        needed = list(d.keys())

    for k_i in needed:
        if k_i not in d:
            raise ValueError(f"\"{k_i}\" does not exists. ")
        if "type" not in d[k_i]:
            raise ValueError(f"bib \"{d[k_i]}\" must contains \"type\". ")
        else:
            type_i = str(d[k_i]["type"]).strip().lower()
            value = d[k_i]

            el: Union[PreprintBib, BookBib,
                      ThesisBib, ArticleBib, ProceedingsBib]
            if type_i == BibTypes.PREPRINT.value:
                el = PreprintBib(id=k_i, **value)
            elif type_i == BibTypes.BOOK.value:
                el = BookBib(id=k_i, **value)
            elif type_i == BibTypes.THESIS.value:
                el = ThesisBib(id=k_i, **value)
            elif type_i == BibTypes.ARTICLE.value:
                el = ArticleBib(id=k_i, **value)
            elif type_i == BibTypes.PROCEEDINGS.value:
                el = ProceedingsBib(id=k_i, **value)
            else:
                raise ValueError(
                    f"Undefined type=\"{type_i}\" from \"{d[k_i]}\". Only can be: {[el.value for el in BibTypes]}")

            res.append(el)

    return res


def bibs_to_str(bibs: list[Union[PreprintBib, BookBib, ThesisBib, ArticleBib, ProceedingsBib]], standard: BibStandards) -> list[str]:
    res: list[str] = []
    for bib_i in bibs:
        if isinstance(bib_i, PreprintBib):
            bib_text = form_preprint_4(standard=standard, item=bib_i)
        elif isinstance(bib_i, BookBib):
            bib_text = form_book_4(standard=standard, item=bib_i)
        elif isinstance(bib_i, ThesisBib):
            bib_text = form_thesis_4(standard=standard, item=bib_i)
        elif isinstance(bib_i, ArticleBib):
            bib_text = form_article_4(standard=standard, item=bib_i)
        elif isinstance(bib_i, ProceedingsBib):
            bib_text = form_proceedings_4(standard=standard, item=bib_i)
        else:
            raise TypeError(f"Unknown class: {bib_i}")

        res.append(bib_text)

    return res


def form_bibs_from_yaml(yaml_path: Path, needed: list[str] | None = None) -> list[str]:
    with open(yaml_path, "r", encoding="utf-8") as fd:
        data = yaml.safe_load(fd)

    settings = data["global"]

    if needed is None:
        if "needed" in settings and settings["needed"].strip() != "":
            buff = Path(settings["needed"])
            with open(buff, "r", encoding="utf-8") as fd:
                s = fd.read()
            needed = [line for line in s.split("\n") if line]
        else:
            needed = None

    standard_set = str(settings["standard"]).strip().upper()
    for existing_standard_i in BibStandards:
        if existing_standard_i.name == standard_set:
            standard = existing_standard_i
            break
    if not isinstance(standard, BibStandards):
        raise ValueError(
            f"standard must be only from {[el.name for el in BibStandards]}.")
    global INCLUDE_DOI
    INCLUDE_DOI = settings["include_doi"]
    global DOI_AS_URL
    DOI_AS_URL = settings["doi_as_url"]
    global kbib_lib_out_lang
    kbib_lib_out_lang = str(settings["target_lang"]).strip().lower()
    global MAX_AUTHORS
    if "max_authors" not in settings or settings["max_authors"] is None or str(settings["max_authors"]).strip() == "":
        MAX_AUTHORS = None
    else:
        MAX_AUTHORS = int(settings.get("max_authors", None))

    bibs_dict = data["items"]
    bibs: list[Union[PreprintBib, BookBib, ThesisBib,
                     ArticleBib, ProceedingsBib]] = dict_to_bibs(bibs_dict, needed)
    res = bibs_to_str(bibs, standard)

    return res
