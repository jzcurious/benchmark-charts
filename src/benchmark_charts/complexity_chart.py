from pathlib import Path

import plotly.graph_objects as go

import benchmark_charts.common as common

PATH_TO_COMPLEXITY_CHART = f"complexity_chart_{common.timestamp()}.html"


def make_complexity_chart(
    complexity: dict,
    path=PATH_TO_COMPLEXITY_CHART,
    cpu_time=False,
    width=1000,
    height=600,
    xaxis_log=True,
    yaxis_log=True,
    dark=False,
) -> go.Figure:
    fig = go.Figure()

    for benchmark, df in complexity.items():
        fig.add_trace(
            go.Scatter(
                x=df["size"],
                y=df["cpu_time"] if cpu_time else df["real_time"],
                mode="lines+markers",
                name=benchmark,
                marker=dict(size=6),
            )
        )

    fig.update_layout(
        title="Real Complexity",
        title_x=0.5,
        xaxis_title="N",
        yaxis_title=f"Time, {list(complexity.values())[0].time_unit[0]}",
        xaxis_type="log" if xaxis_log else "linear",
        yaxis_type="log" if yaxis_log else "linear",
        legend=dict(
            title="Benchmarks:",
            orientation="v",
            yanchor="top",
            y=-0.3,
            xanchor="left",
            x=0,
        ),
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
        default=str(PATH_TO_COMPLEXITY_CHART),
        help="Output path for the complexity chart file",
    )

    return argparser


def run(args):
    figure = make_complexity_chart(
        common.parse_complexity_many_files([Path(p) for p in args.json]),
        args.output,
        args.cpu,
        args.width,
        args.height,
        args.xlog,
        args.ylog,
        args.dark,
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
