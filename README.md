# Lake Macquarie rainfall processing

This project calculates area-weighted annual R20mm values for Lake Macquarie from the supplied NetCDF files.

## Windows setup and use

### 1. Copy the project files

Copy this entire folder to a location on the colleague's computer, for example:

`C:\Users\YourName\Documents\LakeMacquarieRainfall`

The folder must include:

- `lake_macquarie_rainfall.py`
- `pyproject.toml`
- `uv.lock`
- `Rainfall2_Historical` (including all NetCDF files and subfolders)
- `LGA Boundary EPSG 4326.gpkg`

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

Replace the example path with the folder copied in step 1:

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

Open `lake_macquarie_rainfall.py` in a text editor. At the top of the file, replace the three path settings with the colleague's actual folder path.

For example, if the project is in `C:\Users\YourName\Documents\LakeMacquarieRainfall`, use:

```python
NETCDF_ROOT = Path(r"C:\Users\YourName\Documents\LakeMacquarieRainfall\Rainfall2_Historical")
LAKE_GPKG = Path(r"C:\Users\YourName\Documents\LakeMacquarieRainfall\LGA Boundary EPSG 4326.gpkg")
OUTPUT_XLSX = Path(r"C:\Users\YourName\Documents\LakeMacquarieRainfall\lake_macquarie_r20mm_by_year.xlsx")
```

Keep the `r` before each quoted path. It makes Windows backslashes safe in Python.

### 6. Run the processing

From PowerShell, while still in the project folder, run:

```powershell
uv run python lake_macquarie_rainfall.py
```

The output file will be created at the `OUTPUT_XLSX` path set in step 5.

## Troubleshooting

- **`uv` is not recognised:** Close and reopen PowerShell, then run `uv --version` again.
- **A path was not found:** Check the three paths at the top of `lake_macquarie_rainfall.py`, including the spelling of the GeoPackage filename.
- **No NetCDF files were found:** Confirm `NETCDF_ROOT` points to the folder that contains the `Rainfall2_Historical` subfolders.
- **Permission error writing Excel:** Set `OUTPUT_XLSX` to a folder the colleague can write to, such as their Documents folder.
