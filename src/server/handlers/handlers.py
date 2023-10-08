import typing

import transformers

from . import data, config


models_dict = {}


async def init_nlp_pipelines():
    for alias, model_options in config.available_models.items():
        models_dict[alias] = config.ModelOptions(
            model=transformers.pipeline(
                task="summarization", model=model_options.model
            ),
            batch_size=model_options.batch_size
        )


def summarize(
    content: str,
    model_name: str,
    compress_coef: float
) -> typing.Generator[str, str, None]:
    if model_name not in models_dict:
        raise ValueError("bad model")
    model, batch_size = models_dict[model_name]
    text_data = data.TextData(content, [data.remove_extra_spaces])
    max_length = int(compress_coef * batch_size)
    for batch in data.batch_split(text_data, batch_size):
        summary = model(batch, max_length=max_length)
        yield summary