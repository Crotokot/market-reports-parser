from pydantic import BaseModel


class Options(BaseModel):
    model: str
    compress_coef: float = 0.5


class SummarizeBody(BaseModel):
    content: str
    options: Options