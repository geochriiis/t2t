# Lake Macquarie climate projections

This repository contains the reusable rainfall-processing script and the completed, client-facing Lake Macquarie climate-projections workbook.

## Completed projections workbook

`T2T Data updates_projections_clean.xlsx` is the clean workbook prepared for sharing. It includes:

- Rainfall 2: annual days with rainfall of at least 20 mm;
- Bushfire: annual days with severe fire weather (FFDI > 50);
- Heat: annual days with maximum temperature of at least 35°C;
- Rainfall 1: retained from the previously completed work.

The updated climate values are LGA-wide area-weighted annual averages from the supplied NARCliM NetCDF data. The workbook presents the requested model spread as 10th, 50th and 90th percentiles for the baseline, 2050 and 2090 periods.

The original datasets, local boundary GeoPackage, project instructions and internal calculation/QA workbook are deliberately not included in this repository.

## Windows setup and use

### 1. Copy or clone the code repository

Copy or clone this repository to a location on your computer, for example:

`C:\Users\YourName\Documents\LakeMacquarieRainfall`

Your project folder should contain the following code and dependency files:

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

### 3. Navigate to the project folder

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

### 6. Run the processing

From PowerShell, while still in the project folder, run:

```powershell
uv run python lake_macquarie_rainfall_liza.py
```

Your Excel output file will be created at the `OUTPUT_XLSX` path you set in step 5.

## Troubleshooting

- **`uv` is not recognised:** Close and reopen PowerShell, then run `uv --version` again.
- **A path was not found:** Check the three paths at the top of `lake_macquarie_rainfall_liza.py`, including the spelling of the GeoPackage filename.
- **No NetCDF files were found:** Confirm `NETCDF_ROOT` points to the folder that contains the `Rainfall2_Historical` subfolders.
- **Permission error writing Excel:** Set `OUTPUT_XLSX` to a folder you can write to, such as your Documents folder.
