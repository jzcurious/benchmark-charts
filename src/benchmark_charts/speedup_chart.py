import pandas as pd
import plotly.graph_objects as go

import benchmark_charts.common as common

PATH_TO_SPEEDUP_CHART = "speedup.html"


def calc_speedup(
    complexity: dict, target_name: str, reference_name: str, cpu_time=False
) -> pd.DataFrame:

    target_df = complexity[target_name]
    reference_df = complexity[reference_name]

    target_df["reference"] = reference_df["benchmark"].values

    time_key = "cpu_time" if cpu_time else "real_time"
    target_df["speedup"] = target_df[time_key].values / reference_df[time_key].values

    return target_df


def make_speedup_chart(
    target_df: pd.DataFrame,
    xaxis_log=True,
    yaxis_log=True,
    baseline=False,
    width=1000,
    height=600,
    fullscreen=False,
    dark=False,
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
        default=str(PATH_TO_SPEEDUP_CHART),
        help="Output path for the generated chart. "
        "If the path ends with '/', it is treated as a directory and "
        "the filename will be generated automatically. "
        "Otherwise, it is treated as a file path. "
        "The .html extension will be added if not specified. "
        f"Default: {PATH_TO_SPEEDUP_CHART}",
    )

    argparser.add_argument(
        "-r",
        "--reference",
        required=True,
        type=str,
        help="Name of the benchmark result to use as a reference (denominator) "
        "for speedup calculation.",
    )

    argparser.add_argument(
        "-t",
        "--target",
        required=True,
        type=str,
        help="Name of the benchmark result to compare against the "
        "reference (numerator) for speedup calculation.",
    )

    argparser.add_argument(
        "--baseline",
        action="store_true",
        default=False,
        help="Add a horizontal baseline at y=1, representing no "
        "speedup (equal performance).",
    )


def run(args):
    input_paths = common.resolve_input_paths(*args.input)
    output_path = common.resolve_output_path(args.output, "speedup")

    target_df = calc_speedup(
        common.parse_complexity_many_files(input_paths),
        args.target,
        args.reference,
        args.cpu,
    )

    figure = make_speedup_chart(
        target_df=target_df,
        width=args.width,
        height=args.height,
        fullscreen=args.fullscreen,
        xaxis_log=args.xlog,
        yaxis_log=args.ylog,
        dark=args.dark,
        baseline=args.baseline,
    )

    common.export_chart_to_html(figure, output_path)

    if args.show:
        common.show_chart(figure, output_path)


def main(argv):
    run(extend_argparser().parse_args(argv))


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
