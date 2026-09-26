import argparse

import benchmark_charts.common as common
import benchmark_charts.complexity_chart as complexity
import benchmark_charts.speedup_chart as speedup


def main(argv) -> None:
    argparser = argparse.ArgumentParser(prog="benchmark-charts")
    subparsers = argparser.add_subparsers(dest="chart", required=True, metavar="CHART")

    common_argparser = common.build_default_argparser(add_help=False)
    complexity_argparser = subparsers.add_parser(
        "complexity", parents=[common_argparser], help="complexity chart"
    )
    speedup_argparser = subparsers.add_parser(
        "speedup", parents=[common_argparser], help="speedup chart"
    )

    complexity.extend_argparser(complexity_argparser)
    speedup.extend_argparser(speedup_argparser)

    args = argparser.parse_args(argv)

    match args.chart:
        case "speedup":
            return speedup.run(args)
        case "complexity":
            return complexity.run(args)
