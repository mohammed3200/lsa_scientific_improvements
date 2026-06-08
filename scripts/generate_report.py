#!/usr/bin/env python3
"""
Master script to generate complete LSA v2.0 analysis report.
Usage: python scripts/generate_report.py --mode v2 --output results/reports
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.data_generator import DataGenerator
from pipeline.plot_engine import PlotEngine
from pipeline.report_builder import ReportBuilder


def main():
    parser = argparse.ArgumentParser(description="Generate LSA v2.0 complete analysis report")
    parser.add_argument('--mode', choices=['v2', 'legacy'], default='v2')
    parser.add_argument('--output', default='results/reports')
    parser.add_argument('--skip-data', action='store_true', help='Skip data generation')
    parser.add_argument('--skip-figures', action='store_true', help='Skip figure generation')
    args = parser.parse_args()

    print("=" * 70)
    print("LSA v2.0 Report Generation Pipeline")
    print("=" * 70)

    # Step 1: Generate all data
    if not args.skip_data:
        print("\n[Step 1/3] Generating datasets...")
        gen = DataGenerator(mode=args.mode)
        gen.run_all()
    else:
        print("\n[Step 1/3] Skipping data generation (--skip-data)")

    # Step 2: Generate all figures
    if not args.skip_figures:
        print("\n[Step 2/3] Generating figures...")
        plot = PlotEngine()
        plot.generate_all()
    else:
        print("\n[Step 2/3] Skipping figure generation (--skip-figures)")

    # Step 3: Build dashboard
    print("\n[Step 3/3] Building dashboard...")
    builder = ReportBuilder()
    dashboard_path = builder.build_dashboard()

    print("\n" + "=" * 70)
    print("✅ Report generation complete!")
    print(f"   Dashboard: {dashboard_path}")
    print(f"   Figures:   results/figures/")
    print(f"   Raw data:  results/raw_data/")
    print("=" * 70)


if __name__ == '__main__':
    main()
