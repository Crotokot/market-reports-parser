from collections import namedtuple


ModelOptions = namedtuple("ModelOptions", ("model", "batch_size"))
available_models = {
    "BART": ModelOptions(model="facebook/bart-large-cnn", batch_size=512)
}