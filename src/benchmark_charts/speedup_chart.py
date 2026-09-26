from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

import benchmark_charts.common as common

PATH_TO_SPEEDUP_CHART = f"speedup_chart_{common.timestamp()}.html"


def calc_speedup(
    complexity: dict, benchmark_target: str, benchmark_reference: str, cpu_time=False
) -> pd.DataFrame:
    target_df = complexity[benchmark_target]
    reference_df = complexity[benchmark_reference]

    target_df["reference"] = reference_df["benchmark"].values

    time_key = "cpu_time" if cpu_time else "real_time"
    target_df["speedup"] = reference_df[time_key].values / target_df[time_key].values

    return target_df


def make_speedup_chart(
    target_df: pd.DataFrame,
    path=PATH_TO_SPEEDUP_CHART,
    cpu_time=False,
    width=1000,
    height=600,
    xaxis_log=True,
    yaxis_log=True,
    dark=False,
    baseline=False,
) -> go.Figure:
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=target_df["size"],
            y=target_df["speedup"],
            mode="lines+markers",
            marker=dict(size=6),
            name="Speedup",
        )
    )

    if baseline:
        fig.add_trace(
            go.Scatter(
                x=target_df["size"],
                y=[1] * len(target_df),
                mode="lines",
                line=dict(dash="dash", color="red"),
                name="Baseline",
            )
        )

    title = f"Speedup: {target_df['benchmark'].values[0]} vs {
        target_df['reference'].values[0]
    }"

    fig.update_layout(
        title=title,
        title_x=0.5,
        xaxis_title="N",
        yaxis_title="Speedup",
        xaxis_type="log" if xaxis_log else "linear",
        yaxis_type="log" if yaxis_log else "linear",
        hovermode="x unified",
        template="plotly_dark" if dark else "plotly_white",
        width=width,
        height=height,
        autosize=False,
    )

    fig.write_html(path)
    print(f"The chart file has been saved to {path}.")

    return fig


def extend_argparser(argparser=None):
    if argparser is None:
        argparser = common.build_default_argparser()

    argparser.add_argument(
        "-o",
        "--output",
        type=str,
        default=str(PATH_TO_SPEEDUP_CHART),
        help="Output path for the speedup chart file",
    )

    argparser.add_argument(
        "-r",
        "--reference",
        required=True,
        type=str,
        help="Reference result",
    )

    argparser.add_argument(
        "-t",
        "--target",
        required=True,
        type=str,
        help="Target result",
    )

    argparser.add_argument(
        "--baseline",
        action="store_true",
        default=False,
        help="Add baseline (y = 1)",
    )


def run(args):
    target_df = calc_speedup(
        common.parse_complexity_many_files([Path(p) for p in args.json]),
        args.target,
        args.reference,
    )

    figure = make_speedup_chart(
        target_df,
        args.output,
        args.cpu,
        args.width,
        args.height,
        args.xlog,
        args.ylog,
        args.dark,
        args.baseline,
    )

    if args.show:
        common.show_chart(
            figure,
            args.output,
        )


def main(argv):
    run(extend_argparser().parse_args(argv))


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
