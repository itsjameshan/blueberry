# HyLake v1.0 reading notes

DOI: 10.5194/gmd-18-9257-2025

## Source and scientific question
He, Y. and Yang, X. (2025), Geoscientific Model Development 18:9257–9277. DOI https://doi.org/10.5194/gmd-18-9257-2025. CC BY full text: https://gmd.copernicus.org/articles/18/9257/2025/gmd-18-9257-2025.pdf. Code: https://doi.org/10.5281/zenodo.15289113.

The authors combine physical lake-surface energy-balance equations with a Bayesian-optimized bidirectional LSTM surrogate for lake surface temperature. They train using Lake Taihu MLW observations and compare FLake, Baseline and TaihuScene across sites and ERA5 forcing.

## Writing lessons
The argument progresses from a specific process-model vs data-model gap to the hybrid architecture, observation-based calibration, in-site validation, temporal diagnostics, spatial transfer, forcing transfer, and acknowledged limits. Preserve model weaknesses and exceptions in Results/Discussion.

## Figure learning
Figures 2–3: physical model + surrogate architecture and coupling. Figures 4–5: surrogate and model performance. Figures 6–8: complete time series plus local close-ups. Figure 9: cross-site errors. Figures 10–11: ERA5-driven model performance and spatial patterns. Use separate figures for separate scientific questions. Clearly label RMSE/MAE units and distinguish training from spatial validation. Avoid inventing unprovided time-series data.

## Verified numerical example
MLW RMSE (FLake / Baseline / HyLake): LST 1.76/2.71/1.08 °C; LE 42.73/51.77/24.65 W m^-2; HE 7.24/14.63/7.15 W m^-2. Some stations favor TaihuScene. Model run time in the MLW experiment is approximately nine times FLake.

## Source cautions
Section 3.3 contains a LE/HE ordering inconsistency. The surrogate test RMSE differs between section 3.1 and the conclusion. The original figure appearance was not directly inspected in this run; any new figure is a numeric redraw or an explicitly labeled schematic, not a copy of original figure styling.
