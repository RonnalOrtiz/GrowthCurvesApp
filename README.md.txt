# GrowthCurveApp — Livestock Growth Dashboard

This repository contains the GrowthCurveApp (Streamlit / Colab) for visualizing livestock growth curves,
uploading user records, and comparing them to Gompertz reference curves.

## Contents
- `dashboard_growth_v0.py` — Main app script (currently Colab-ready; contains loader + UI)
- `default_parameters.xlsx` — Default parameter set used if no file is uploaded
- `requirements.txt` — Python dependencies
- `README.md` — This file

## Parameter file format
If uploading a custom parameter file, it must be **Excel (.xlsx or .xls)** or **CSV** with at least these columns:

- `ID` (region name / identifier)
- `b0` (numeric)
- `b1` (numeric)
- `b2` (numeric)

Example header: `ID, b0, b1, b2`

## Quick local test (Colab-style)
1. Install dependencies (if running locally):
```bash
pip install -r requirements.txt
