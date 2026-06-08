"""
Layer 3: Report Builder
=======================
Builds HTML dashboard from generated data and figures using Jinja2.
"""

import json
import pandas as pd
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


class ReportBuilder:
    def __init__(self, data_dir: str = "results/raw_data",
                 figures_dir: str = "results/figures",
                 template_dir: str = "pipeline/templates",
                 output_dir: str = "results/reports"):
        self.data_dir = Path(data_dir)
        self.figures_dir = Path(figures_dir)
        self.template_dir = Path(template_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.env = Environment(loader=FileSystemLoader(self.template_dir))

    def build_dashboard(self, output_file: str = "lsa_v2_dashboard.html") -> str:
        """Build the HTML dashboard."""
        template = self.env.get_template("dashboard_template.html")

        # Load NIST results
        nist_df = pd.read_csv(self.data_dir / "nist_results.csv")
        nist_pass = len(nist_df[nist_df['status'] == 'PASS'])
        nist_rows = nist_df.to_dict('records')

        # Load avalanche results
        with open(self.data_dir / "avalanche_results.json") as f:
            avalanche = json.load(f)
        avalanche_sac = round(avalanche.get('sac_mean', 0) * 100, 1)
        avalanche_items = [
            ("SAC Mean", f"{avalanche.get('sac_mean', 0):.4f}"),
            ("SAC StdDev", f"{avalanche.get('sac_std', 0):.4f}"),
            ("BIC Mean", f"{avalanche.get('bic_mean', 0):.4f}"),
            ("NPCR Mean", f"{avalanche.get('npcr_mean', 0):.2f}%"),
            ("UACI Mean", f"{avalanche.get('uaci_mean', 0):.2f}%"),
        ]

        # Load side-channel results
        with open(self.data_dir / "side_channel.json") as f:
            sc = json.load(f)
        side_channel_items = [
            ("Timing CV (v2)", f"{sc['lsa_v2']['timing_cv']:.3f}"),
            ("DPA Correlation (v2)", f"{sc['lsa_v2']['dpa_correlation']:.3f}"),
            ("Fault Detection (v2)", f"{sc['lsa_v2']['fault_detection_rate']:.2%}"),
            ("Entropy Bits (v2)", f"{sc['lsa_v2']['entropy_bits']}"),
            ("Timing CV (Legacy)", f"{sc['lsa_legacy']['timing_cv']:.3f}"),
            ("DPA Correlation (Legacy)", f"{sc['lsa_legacy']['dpa_correlation']:.3f}"),
        ]

        # Collect figures
        figures = []
        figure_names = [
            ("fig01_key_expansion_time.png", "Key Expansion Time Comparison"),
            ("fig02_security_level.png", "Security Level vs Key Size"),
            ("fig03_energy_consumption.png", "Energy Consumption vs Network Size"),
            ("fig04_pdr.png", "Packet Delivery Ratio"),
            ("fig05_nist_heatmap.png", "NIST Test Results Heatmap"),
            ("fig06_avalanche_distribution.png", "Avalanche Effect Distribution"),
            ("fig07_operation_counts.png", "Operation Count Comparison"),
            ("fig08_side_channel_radar.png", "Side-Channel Resistance Radar"),
            ("fig09_before_after.png", "Baseline vs Improved vs Upgraded"),
            ("fig10_complexity_pie.png", "Operation Distribution"),
        ]
        for fname, title in figure_names:
            fig_path = self.figures_dir / fname
            if fig_path.exists():
                figures.append({"path": f"../figures/{fname}", "title": title})

        html = template.render(
            nist_pass=nist_pass,
            nist_rows=nist_rows,
            avalanche_sac=avalanche_sac,
            avalanche_items=avalanche_items,
            side_channel_items=side_channel_items,
            figures=figures,
            figures_count=len(figures),
        )

        output_path = self.output_dir / output_file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"[ReportBuilder] Dashboard saved to {output_path}")
        return str(output_path)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="results/raw_data")
    parser.add_argument("--figures", default="results/figures")
    parser.add_argument("--output", default="results/reports")
    parser.add_argument("--file", default="lsa_v2_dashboard.html")
    args = parser.parse_args()

    builder = ReportBuilder(
        data_dir=args.data,
        figures_dir=args.figures,
        output_dir=args.output,
    )
    builder.build_dashboard(output_file=args.file)
