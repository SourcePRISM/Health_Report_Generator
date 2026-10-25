#!/usr/bin/env python3
"""Compatibility entry point: analyse once and render with provenance."""
import argparse
from pathlib import Path

from analyse import analyse, load_config
from publish import build_provenance, package, render

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--stakeholder",
        default=str(HERE / "config/stakeholders/public_health_expert.json"),
    )
    parser.add_argument(
        "--classes", default=str(HERE / "config/pathogen_class.csv")
    )
    parser.add_argument("--out", default="out")
    parser.add_argument("--quarto", default="quarto")
    args = parser.parse_args()
    config = load_config(args.stakeholder)
    bundle = Path(args.out) / "reports" / config["id"] / "data"
    analyse(args.out, args.stakeholder, args.classes, bundle)
    provenance = build_provenance(bundle, "html", args.quarto)
    package(bundle, bundle.parent / "app")
    render(
        bundle, bundle.parent / "report.html", "html", args.quarto,
        provenance=provenance,
        provenance_out=bundle.parent / "provenance.json",
    )


if __name__ == "__main__":
    main()
