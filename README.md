# Lake Macquarie climate projections

This repository contains the client-facing Lake Macquarie climate-projections workbook and a reusable script for processing historical R20mm rainfall data.

## Completed projections workbook

`T2T Data updates_projections_clean.xlsx` is the clean workbook prepared for sharing. It includes:

- Rainfall 2: annual days with rainfall of at least 20 mm;
- Bushfire: annual days with severe fire weather (FFDI > 50);
- Heat: annual days with maximum temperature of at least 35°C;
- Rainfall 1: retained from the previously completed work.

## Projection processing method

The completed updates were prepared from the supplied NARCliM NetCDF datasets using this process:

1. Create source-grid cell polygons directly from the NetCDF latitude and longitude coordinates. This preserves the original grid resolution and boundaries; no resampling is used.
2. Intersect the cells with the Lake Macquarie LGA boundary in an equal-area Australian CRS (EPSG:3577).
3. For each model and year, calculate the LGA-wide annual value as the sum of each intersecting cell's annual value multiplied by `intersection area / full LGA area`.
4. Calculate a 20-year average for each model for the requested periods: 1990–2009 (where a modelled historical baseline was required), 2040–2059 (2050), and 2080–2099 (2090).
5. Calculate the 10th, 50th and 90th percentiles across the model-level 20-year averages, then calculate relative change from the relevant baseline.

This produces LGA-wide spatial averages, not totals. Fractional days are therefore expected. Rainfall 2 is the number of days with rainfall of at least 20 mm, rather than total rainfall or storm intensity. The percentile range shows variation across the available model configurations; it is not a probability forecast.

For Heat, the future modelled values are compared with the existing observed historical average already in the workbook, as requested in the project instructions.

The original datasets, local boundary GeoPackage, project instructions and internal calculation/QA workbook are deliberately not included in this repository.

## Re-run the historical R20mm script on Windows

`lake_macquarie_rainfall_liza.py` is a standalone script for producing the historical Rainfall 2 annual LGA values. It does not recreate the full Bushfire, Heat and projection-summary workflow in the completed workbook.

### 1. Download or clone the repository

Copy or clone this repository to a location on your computer, for example:

`C:\Users\YourName\Documents\LakeMacquarieRainfall`

Your project folder should contain these processing files:

- `lake_macquarie_rainfall_liza.py`
- `pyproject.toml`
- `uv.lock`

The large input datasets are intentionally not included in this repository. Make sure you have received them separately, then save them anywhere convenient on your computer:

- a `Rainfall2_Historical` folder, including all NetCDF files and subfolders;
- the `LGA Boundary EPSG 4326.gpkg` file.

### 2. Install uv (one time only)

Open **PowerShell** and run:

```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

Close PowerShell, then open a new PowerShell window. Confirm the installation:

```powershell
uv --version
```

### 3. Open the project folder in PowerShell

Replace the example path with the location of the project folder on your computer:

```powershell
cd "C:\Users\YourName\Documents\LakeMacquarieRainfall"
```

### 4. Install Python and the required packages

Run this once from the project folder:

```powershell
uv sync
```

`uv` will install the correct Python environment and all required packages automatically.

### 5. Update the three paths in the Python script

Open `lake_macquarie_rainfall_liza.py` in a text editor. At the top of the file, replace the three example paths with the locations on your computer for the NetCDF folder, GeoPackage, and Excel output. The source data does **not** need to sit inside the project folder.

For example, if your project is in `C:\Users\YourName\Documents\LakeMacquarieRainfall`, your NetCDF files are on `D:\ClimateData`, and your GeoPackage is in `D:\Boundaries`, use:

```python
NETCDF_ROOT = Path(r"D:\ClimateData\Rainfall2_Historical")
LAKE_GPKG = Path(r"D:\Boundaries\LGA Boundary EPSG 4326.gpkg")
OUTPUT_XLSX = Path(r"C:\Users\YourName\Documents\LakeMacquarieRainfall\lake_macquarie_r20mm_by_year.xlsx")
```

Keep the `r` before each quoted path. It makes Windows backslashes safe in Python.

### 6. Run the historical R20mm processing

From PowerShell, while still in the project folder, run:

```powershell
uv run python lake_macquarie_rainfall_liza.py
```

Your Excel output file will be created at the `OUTPUT_XLSX` path you set in step 5. The output has one row per year and one column per source NetCDF/model folder.

## Troubleshooting

- **`uv` is not recognised:** Close and reopen PowerShell, then run `uv --version` again.
- **A path was not found:** Check the three paths at the top of `lake_macquarie_rainfall_liza.py`, including the spelling of the GeoPackage filename.
- **No NetCDF files were found:** Confirm `NETCDF_ROOT` points to the `Rainfall2_Historical` folder that contains the NetCDF files or its subfolders.
- **Permission error writing Excel:** Set `OUTPUT_XLSX` to a folder you can write to, such as your Documents folder.
