from abc import ABCMeta, abstractmethod
import io

from bs4 import BeautifulSoup
import pdfplumber


class IParser(metaclass=ABCMeta):
    """
    Interface for all parsers.
    """
    @abstractmethod
    def parse(cls, data: str | bytes) -> str:
        ...


class HtmlParser(IParser):
    def parse(self, markup: str | bytes) -> str:
        if isinstance(markup, bytes):
            markup = io.BytesIO(markup)

        soup = BeautifulSoup(markup, features='html.parser')
        data = soup.find('body')
        for script_tag in data.select('script'):
            script_tag.extract()
        text = data.get_text()
        return text


class PDFParser(IParser):
    def parse(self, data: str | bytes) -> str:
        if isinstance(data, bytes):
            data = io.BytesIO(data)

        with pdfplumber.open(data) as pdf:
            text = '\n'.join(page.extract_text() for page in pdf.pages)
        return text


class PlainTextParser(IParser):
    def parse(self, data: str | bytes) -> str:
        if isinstance(data, bytes):
            data = data.decode()
        return data


def parser_factory(label: str) -> IParser:
    match label.lower():
        case "html":
            return HtmlParser()
        case "pdf":
            return PDFParser()
        case "text" | "txt":
            return PlainTextParser()