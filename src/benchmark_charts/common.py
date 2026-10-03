import json
from argparse import ArgumentParser, ArgumentTypeError
from datetime import datetime
from fnmatch import fnmatch
from functools import partial
from pathlib import Path

import pandas as pd


def parse_complexity_file(path_to_json: Path, wildcard: str = None) -> dict:
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

    complexity = {}

    for benchmark in df["benchmark"]:
        if benchmark not in complexity:
            if wildcard is not None and not fnmatch(benchmark, wildcard):
                continue

            complexity[benchmark] = (
                df[df["benchmark"] == benchmark]
                .sort_values("size")
                .reset_index(drop=True)
            )

    if len(complexity) == 0:
        raise ValueError("Data not found")

    return complexity


def parse_complexity_many_files(paths_to_jsons: list, wildcard: str = None) -> dict:
    complexity = {}

    for path_to_json in paths_to_jsons:
        complexity |= parse_complexity_file(path_to_json, wildcard)

    return complexity


def show_chart(fig, path_to_chart: str | Path):
    try:
        from google.colab import output  # noqa
        from IPython.display import display, HTML

        display(HTML(fig.to_html()))
    except ImportError:
        import webbrowser

        if not path_to_chart.is_file():
            export_chart_to_html(fig, path_to_chart)

        webbrowser.open(str(path_to_chart))


def range_limited_int(min_value, max_value, value) -> int:
    ivalue = int(value)
    if not min_value <= ivalue <= max_value:
        raise ArgumentTypeError(
            f"Value must be between {min_value} and {max_value}, got {ivalue}"
        )
    return ivalue


def resolve_input_paths(*str_paths: str, wildcard: str = "*.json") -> list[Path]:
    endpoints = []

    for p in str_paths:
        path = Path(p)

        if path.is_file():
            if path.suffix != ".json":
                print(f"Warning: skipping non-JSON file: {p}")
                continue

            endpoints.append(path)
            continue

        if path.is_dir():
            endpoints.extend(path.rglob(wildcard))
            continue

        print(f"Warning: path not found, skipping: {p}")

    return endpoints


def ensure_html_filename(path: str) -> str:
    return path if path.endswith(".html") else path + ".html"


def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def resolve_output_path(str_path: str, fname_prefix: str = "chart") -> Path:
    path = Path(str_path)

    if str_path.endswith(("/", "\\")):
        path.mkdir(parents=True, exist_ok=True)
        output = path / f"{fname_prefix}_{timestamp()}"
        return Path(ensure_html_filename(str(output)))

    if len(path.parts) > 1:
        path.parent.mkdir(parents=True, exist_ok=True)

    return Path(ensure_html_filename(str(path)))


def export_chart_to_html(fig, output_path):
    fig.write_html(
        output_path,
        full_html=True,
        include_plotlyjs="cdn",
        config={"responsive": True},
    )

    print(f"The chart file has been saved to {output_path}.")


def build_default_argparser(add_help=True):
    argparser = ArgumentParser(add_help=add_help)

    argparser.add_argument(
        "-i",
        "--input",
        nargs="+",
        required=True,
        default=[],
        help="One or more paths to JSON benchmark result files "
        "or directories to scan recursively.",
    )

    argparser.add_argument(
        "--cpu",
        action="store_true",
        default=False,
        help="Plot CPU time instead of real (wall-clock) time.",
    )

    argparser.add_argument(
        "--xlog",
        action="store_true",
        default=False,
        help="Use a logarithmic scale on the X axis.",
    )

    argparser.add_argument(
        "--ylog",
        action="store_true",
        default=False,
        help="Use a logarithmic scale on the Y axis.",
    )

    argparser.add_argument(
        "-wx",
        "--width",
        type=partial(range_limited_int, min_value=400, max_value=1920),
        default=1000,
        help="Chart width in pixels. Must be between 400 and 1920. Default: 1000.",
    )

    argparser.add_argument(
        "-hy",
        "--height",
        type=partial(range_limited_int, min_value=400, max_value=1080),
        default=600,
        help="Chart height in pixels. Must be between 400 and 1080. Default: 600.",
    )

    argparser.add_argument(
        "--fullscreen",
        action="store_true",
        default=False,
        help="Stretch the chart to fill the entire browser window or Colab cell. "
        "Overrides --width and --height.",
    )

    argparser.add_argument(
        "--dark",
        action="store_true",
        default=False,
        help="Render the chart using a dark theme.",
    )

    argparser.add_argument(
        "--show",
        action="store_true",
        default=True,
        help="Open the generated chart in the default browser after rendering.",
    )

    argparser.add_argument(
        "-f",
        "--filter",
        type=str,
        default=None,
        help="Filter benchmarks by name using a wildcard pattern (e.g. 'sort_*'). "
        "Only matching benchmarks will be included in the chart.",
    )

    return argparser


def cli_run(entrypoint: callable):
    raise SystemExit(entrypoint())
