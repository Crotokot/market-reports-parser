from argparse import ArgumentParser
import json
from pathlib import Path

import uvicorn


def parse_options() -> dict:
    parser = ArgumentParser()
    parser.add_argument(
        "--server", type=str, required=False,
        help="Path to uvicorn json config"
    )
    args = dict(parser.parse_args()._get_kwargs())
    options = {}
    if args.get("server") is not None:
        options |= json.loads(Path.read_text(args["server"]))
    return options


if __name__ == "__main__":
    options = parse_options()
    uvicorn.run("app:app", **options)