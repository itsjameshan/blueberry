"""Redraw published HyLake metrics, not the original paper's plot appearance.

Source: He & Yang (2025), doi:10.5194/gmd-18-9257-2025
All values below are explicitly reported in the article.
"""
from pathlib import Path
import matplotlib.pyplot as plt

MLW_RMSE = {
    "LST (°C)": {"FLake": 1.76, "Baseline": 2.71, "HyLake": 1.08},
    "LE (W m^-2)": {"FLake": 42.73, "Baseline": 51.77, "HyLake": 24.65},
    "HE (W m^-2)": {"FLake": 7.24, "Baseline": 14.63, "HyLake": 7.15},
}
ERA5_MAE = {
    "LST (°C)": {"FLake": 1.46, "TaihuScene": 1.29, "HyLake": 0.90},
    "LE (W m^-2)": {"FLake": 50.94, "TaihuScene": 47.78, "HyLake": 35.02},
    "HE (W m^-2)": {"FLake": 9.68, "TaihuScene": 10.11, "HyLake": 7.97},
}

def draw_metric_figures(metric_table, metric_name, outdir="plots"):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    for variable, model_values in metric_table.items():
        fig, ax = plt.subplots(figsize=(5.6, 3.5))
        bars = ax.bar(list(model_values), list(model_values.values()), width=0.55)
        ax.set_ylabel(f"{metric_name} · {variable}")
        ax.set_ylim(0, max(model_values.values()) * 1.20)
        for bar, value in zip(bars, model_values.values()):
            ax.annotate(f"{value:.2f}",
                        (bar.get_x() + bar.get_width()/2, value),
                        xytext=(0, 4), textcoords="offset points", ha="center")
        ax.spines[["top", "right"]].set_visible(False)
        fig.tight_layout()
        slug = variable.split(" ")[0].lower()
        for ext in ("png", "pdf", "svg"):
            fig.savefig(outdir / f"{metric_name.lower()}_{slug}.{ext}", dpi=300)
        plt.close(fig)

if __name__ == "__main__":
    draw_metric_figures(MLW_RMSE, "RMSE")
    draw_metric_figures(ERA5_MAE, "MAE")
