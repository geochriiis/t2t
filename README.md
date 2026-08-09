# Lake Macquarie rainfall processing

This project calculates area-weighted annual R20mm values for Lake Macquarie from supplied NetCDF files.

## Windows setup and use

### 1. Copy or clone the code repository

Copy or clone this repository to a location on your computer, for example:

`C:\Users\YourName\Documents\LakeMacquarieRainfall`

Your project folder should contain the following code and dependency files:

- `lake_macquarie_rainfall.py`
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

Open `lake_macquarie_rainfall.py` in a text editor. At the top of the file, set the three paths to the locations on your computer for the project, NetCDF folder, and GeoPackage. The source data does **not** need to sit inside the project folder.

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
uv run python lake_macquarie_rainfall.py
```

Your Excel output file will be created at the `OUTPUT_XLSX` path you set in step 5.

## Troubleshooting

- **`uv` is not recognised:** Close and reopen PowerShell, then run `uv --version` again.
- **A path was not found:** Check the three paths at the top of `lake_macquarie_rainfall.py`, including the spelling of the GeoPackage filename.
- **No NetCDF files were found:** Confirm `NETCDF_ROOT` points to the folder that contains the `Rainfall2_Historical` subfolders.
- **Permission error writing Excel:** Set `OUTPUT_XLSX` to a folder you can write to, such as your Documents folder.
