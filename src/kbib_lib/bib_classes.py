from pydantic import BaseModel, Field, ConfigDict, field_validator
from enum import Enum


class BibStandards(Enum):
    GOST = 1
    APA = 2


class BibTypes(Enum):
    PREPRINT = "preprint"
    BOOK = "book"
    THESIS = "thesis"
    ARTICLE = "article"
    PROCEEDINGS = "proceedings"


def check_str_for_non_value(v) -> str | None:
    if isinstance(v, str) and not v.strip():
        return None
    return str(v)


def process_authors(authors: list[str]):
    if isinstance(authors, list):
        for el in authors:
            if not isinstance(el, str):
                raise ValueError(
                    f"authors=\"{authors}\" must be list[str], but \"{el}\" is not str")
            if not el.strip():
                raise ValueError(f"\"{el}\" must be not empty str")
        return authors
    else:
        raise ValueError(f"authors=\"{authors}\" must be list[str]")


class PreprintBib(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    title: str
    authors: list[str]
    year: int
    publisher_and_id: str
    doi: str | None = Field(default=None)

    @field_validator("id", "title", "publisher_and_id", mode="before")
    @classmethod
    def it_must_be_not_none(cls, v):
        return check_str_for_non_value(v)

    @field_validator("authors", mode="before")
    @classmethod
    def check_authors(cls, v):
        return process_authors(v)

    @field_validator("doi", mode="before")
    @classmethod
    def empty_string_to_none(cls, v):
        return check_str_for_non_value(v)


class BookBib(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    title: str
    authors: list[str]
    year: int
    city: str | None = Field(default=None)
    publisher: str | None = Field(default=None)
    pages: str | None = Field(default=None)

    @field_validator("id", "title", mode="before")
    @classmethod
    def it_must_be_not_none(cls, v):
        return check_str_for_non_value(v)

    @field_validator("authors", mode="before")
    @classmethod
    def check_authors(cls, v):
        return process_authors(v)

    @field_validator("pages", "city", "publisher", mode="before")
    @classmethod
    def empty_string_to_none(cls, v):
        return check_str_for_non_value(v)


class ThesisBib(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    title: str
    authors: list[str]
    extra_text: str | None = Field(default=None)
    year: int
    city: str
    publisher: str

    @field_validator("id", "title", mode="before")
    @classmethod
    def it_must_be_not_none(cls, v):
        return check_str_for_non_value(v)

    @field_validator("authors", mode="before")
    @classmethod
    def check_authors(cls, v):
        return process_authors(v)

    @field_validator("extra_text", mode="before")
    @classmethod
    def empty_string_to_none(cls, v):
        return check_str_for_non_value(v)


class ArticleBib(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    title: str
    authors: list[str]
    year: int
    journal: str
    volume: int | None = Field(default=None)
    issue: int | None = Field(default=None)
    pages: str | None = Field(default=None)
    doi: str | None = Field(default=None)

    @field_validator("id", "title", "journal", mode="before")
    @classmethod
    def it_must_be_not_none(cls, v):
        return check_str_for_non_value(v)

    @field_validator("authors", mode="before")
    @classmethod
    def check_authors(cls, v):
        return process_authors(v)

    @field_validator("volume", "issue", mode="before")
    @classmethod
    def preprocess_int(cls, v):
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return None
            try:
                return int(v)
            except ValueError:
                raise ValueError(f"Cannot convert year=\"{v}\" to int")
        elif isinstance(v, int):
            return v
        else:
            raise ValueError(f"year=\"{v}\" must be int or str")

    @field_validator("pages", "doi", mode="before")
    @classmethod
    def empty_string_to_none(cls, v):
        return check_str_for_non_value(v)


class ProceedingsBib(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    title: str
    authors: list[str]
    year: int
    conference: str
    place_and_date: str | None = Field(default=None)
    city: str | None = Field(default=None)
    publisher: str | None = Field(default=None)
    volume: int | None = Field(default=None)
    issue: int | None = Field(default=None)
    pages: str | None = Field(default=None)
    doi: str | None = Field(default=None)

    @field_validator("id", "title", "conference", mode="before")
    @classmethod
    def it_must_be_not_none(cls, v):
        return check_str_for_non_value(v)

    @field_validator("authors", mode="before")
    @classmethod
    def check_authors(cls, v):
        return process_authors(v)

    @field_validator("volume", "issue", mode="before")
    @classmethod
    def preprocess_int(cls, v):
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return None
            try:
                return int(v)
            except ValueError:
                raise ValueError(f"Cannot convert year=\"{v}\" to int")
        elif isinstance(v, int):
            return v
        else:
            raise ValueError(f"year=\"{v}\" must be int or str")

    @field_validator("pages", "place_and_date", "city", "publisher", "doi", mode="before")
    @classmethod
    def empty_string_to_none(cls, v):
        return check_str_for_non_value(v)
