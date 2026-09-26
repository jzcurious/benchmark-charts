import json
from argparse import ArgumentParser, ArgumentTypeError
from datetime import datetime
from functools import partial
from pathlib import Path

import pandas as pd


def parse_complexity_file(path_to_json: Path, complexity=None) -> dict:
    if not path_to_json.exists():
        raise FileNotFoundError("File not found")

    with open(path_to_json) as f:
        data = json.load(f)

    def parse_benchmark_and_size(x: str):
        tokens = x.split("/")
        i = 0 if tokens[1].isdigit() else 1
        return tokens[i], int(tokens[i + 1])

    df = pd.DataFrame(data["benchmarks"])
    df["benchmark"] = df["name"].apply(lambda x: parse_benchmark_and_size(x)[0])
    df["size"] = df["name"].apply(lambda x: parse_benchmark_and_size(x)[1])

    if complexity is None:
        complexity = {}

    for benchmark in df["benchmark"]:
        if benchmark not in complexity:
            complexity[benchmark] = df[df["benchmark"] == benchmark].sort_values("size")

    if len(complexity) == 0:
        raise ValueError("Data not found")

    return complexity


def parse_complexity_many_files(paths_to_jsons) -> dict:
    complexity = {}
    for path_to_json in paths_to_jsons:
        parse_complexity_file(path_to_json, complexity)
    return complexity


def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def show_chart(fig, path_to_chart):
    try:
        from google.colab import output  # noqa
        from IPython.display import display, HTML

        display(HTML(fig.to_html()))
    except ImportError:
        import webbrowser

        webbrowser.open(path_to_chart)


def range_limited_int(min_value, max_value, value) -> int:
    ivalue = int(value)
    if not min_value <= ivalue <= max_value:
        raise ArgumentTypeError(
            f"Value must be between {min_value} and {max_value}, got {ivalue}"
        )
    return ivalue


def build_default_argparser(add_help=True):
    argparser = ArgumentParser(add_help=add_help)

    argparser.add_argument(
        "-j",
        "--json",
        nargs="+",
        required=True,
        default=[],
        help="Path to benchmark results (JSON)",
    )

    argparser.add_argument(
        "--cpu",
        action="store_true",
        default=False,
        help="CPU Time Chart",
    )

    argparser.add_argument(
        "--xlog",
        action="store_true",
        default=False,
        help="Log scale on X axis",
    )

    argparser.add_argument(
        "--ylog",
        action="store_true",
        default=False,
        help="Log scale on Y axis",
    )

    argparser.add_argument(
        "-wx",
        "--width",
        type=partial(range_limited_int, min_value=100, max_value=1920),
        default=1000,
        help="Width of the chart in pixels",
    )

    argparser.add_argument(
        "-hy",
        "--height",
        type=partial(range_limited_int, min_value=100, max_value=1080),
        default=600,
        help="Height of the chart in pixels",
    )

    argparser.add_argument(
        "--dark",
        action="store_true",
        default=False,
        help="Use dark theme",
    )

    argparser.add_argument(
        "--show",
        action="store_true",
        default=True,
        help="Show chart",
    )

    return argparser
