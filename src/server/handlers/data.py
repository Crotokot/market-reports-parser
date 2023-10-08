import functools
import re
import typing


Cleaner = typing.Callable[[str], str]


class TextData(object):
    def __init__(
        self,
        text: str,
        cleaners: typing.Optional[list[Cleaner]] = None
    ) -> None:
        if cleaners is None:
            cleaners = []

        # add spliting function
        cleaners.append(lambda txt: list(map(str.strip, txt.split('.'))))
        self._sentences = self._split_and_clean(text, cleaners)

    @property
    def sentences(self):
        return self._sentences

    def __iter__(self):
        return iter(self.sentences)

    def __str__(self):
        return '. '.join(self.sentences)

    def __repr__(self):
        return str(self)

    def _split_and_clean(self, text: str, cleaners: list[Cleaner]):
        return functools.reduce(lambda txt, clean: clean(txt), cleaners, text)


def batch_split(data: TextData, batch_size: int):
    """
    Split all text data on batches.

    As NLP transformers can take no more than some number
    of tokens at a time we should split all data on batches.
    This function select data batches of size no more than
    ``batch_size`` and iterate through this batches.

    Parameters
    ----------
    data: ``TextData``
        Text extracted from document.
    batch_size: int
        Number of tokens which choosen transformer accepted.
    ----------

    Yields
    ------
    str
        Some piece of text consist of no more than
        ``batch_size`` tokens.
    ------
    """
    def glue_batch(batch):
        return '. '.join(batch)

    batch, curr_batch_size = [], 0
    for tokens_count, sentence in map(lambda s: (s.count(' ') + 1, s), data):
        if curr_batch_size + tokens_count > batch_size:
            yield glue_batch(batch)
            batch, curr_batch_size = [], 0
        batch.append(sentence)
        curr_batch_size += tokens_count
    if batch:
        yield glue_batch(batch)


def remove_extra_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()