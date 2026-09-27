import plotly.graph_objects as go

import benchmark_charts.common as common

PATH_TO_COMPLEXITY_CHART = "complexity.html"


def make_complexity_chart(
    complexity: dict,
    cpu_time=False,
    xaxis_log=True,
    yaxis_log=True,
    height=600,
    width=1000,
    fullscreen=False,
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
        width=None if fullscreen else width,
        height=None if fullscreen else height,
        autosize=fullscreen,
    )

    return fig


def extend_argparser(argparser=None):
    if argparser is None:
        argparser = common.build_default_argparser()

    argparser.add_argument(
        "-o",
        "--output",
        type=str,
        default=str(PATH_TO_COMPLEXITY_CHART),
        help="Output path for the generated chart. "
        "If the path ends with '/', it is treated as a directory and "
        "the filename will be generated automatically. "
        "Otherwise, it is treated as a file path. "
        "The .html extension will be added if not specified. "
        f"Default: {PATH_TO_COMPLEXITY_CHART}",
    )

    return argparser


def run(args):
    input_paths = common.resolve_input_paths(*args.input)
    output_path = common.resolve_output_path(args.output, "complexity")

    figure = make_complexity_chart(
        complexity=common.parse_complexity_many_files(input_paths, args.filter),
        cpu_time=args.cpu,
        width=args.width,
        height=args.height,
        fullscreen=args.fullscreen,
        xaxis_log=args.xlog,
        yaxis_log=args.ylog,
        dark=args.dark,
    )

    common.export_chart_to_html(figure, output_path)

    if args.show:
        common.show_chart(figure, output_path)


def main(argv):
    run(extend_argparser().parse_args(argv))


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
