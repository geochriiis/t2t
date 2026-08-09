"""Area-weighted annual R20mm values for the Lake Macquarie LGA.

Before running, change the three paths in the CONFIGURATION section to the
locations on your computer, then run:
    uv run python lake_macquarie_rainfall_liza.py

The calculation constructs the NetCDF grid's exact rectangular cells from the
coordinate midpoints (a fishnet), intersects only cells that meet the LGA, and
uses intersection_area / lga_area as the weight. The weights are made in an
equal-area CRS and cached per grid definition, so they are accurate and are
calculated only once even when there are many NetCDF files.
"""

from __future__ import annotations

import hashlib
import logging
import sys
from dataclasses import dataclass
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr


# ------------------------------ CONFIGURATION -----------------------------
# Replace each example with the matching location on your computer.
NETCDF_ROOT = Path(r"C:\path\to\Rainfall2_Historical")
LAKE_GPKG = Path(r"C:\path\to\LGA Boundary EPSG 4326.gpkg")
OUTPUT_XLSX = Path(r"C:\path\to\lake_macquarie_r20mm_by_year.xlsx")

# Use None to automatically select the first data variable in each NetCDF.
RAINFALL_VARIABLE: str | None = "R20mm"
# EPSG:3577 is the Australian Albers equal-area CRS, used only for areas.
AREA_CRS = "EPSG:3577"
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GridWeights:
    """Indices and Lake-area fractions for cells touching the Lake polygon."""

    lat_index: np.ndarray
    lon_index: np.ndarray
    lake_fraction: np.ndarray


def require_path(path: Path, description: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"{description} was not found: {path}")


def coordinate_edges(values: np.ndarray, name: str) -> np.ndarray:
    """Return cell edges from regular, centre-point coordinates."""
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or len(values) < 2:
        raise ValueError(f"{name} must be a one-dimensional coordinate with at least two values.")
    diffs = np.diff(values)
    if not np.allclose(diffs, diffs[0], rtol=1e-7, atol=1e-10):
        raise ValueError(f"{name} is not a regular grid; explicit bounds are required.")
    half_step = abs(diffs[0]) / 2
    values = np.sort(values)
    return np.concatenate(([values[0] - half_step], (values[:-1] + values[1:]) / 2, [values[-1] + half_step]))


def load_lake() -> gpd.GeoDataFrame:
    lake = gpd.read_file(LAKE_GPKG)
    if lake.empty or lake.geometry.is_empty.all():
        raise ValueError("The GeoPackage contains no usable Lake Macquarie geometry.")
    if lake.crs is None:
        raise ValueError("The GeoPackage has no CRS. Define its CRS before processing.")
    geometry = lake.geometry.union_all()
    if not geometry.is_valid:
        geometry = geometry.buffer(0)
    return gpd.GeoDataFrame(geometry=[geometry], crs=lake.crs)


def grid_key(lat: np.ndarray, lon: np.ndarray, source_crs: str) -> str:
    digest = hashlib.sha256()
    for value in (np.asarray(lat), np.asarray(lon)):
        digest.update(np.ascontiguousarray(value).tobytes())
    digest.update(source_crs.encode())
    return digest.hexdigest()


def make_weights(lat: np.ndarray, lon: np.ndarray, lake: gpd.GeoDataFrame) -> GridWeights:
    """Create fishnet polygons and Lake fractions for the cells that intersect it."""
    lat_order = np.argsort(lat)
    lon_order = np.argsort(lon)
    lat_sorted, lon_sorted = np.asarray(lat)[lat_order], np.asarray(lon)[lon_order]
    lat_edges, lon_edges = coordinate_edges(lat_sorted, "latitude"), coordinate_edges(lon_sorted, "longitude")
    minx, miny, maxx, maxy = lake.total_bounds
    candidate_lats = np.where((lat_edges[:-1] < maxy) & (lat_edges[1:] > miny))[0]
    candidate_lons = np.where((lon_edges[:-1] < maxx) & (lon_edges[1:] > minx))[0]
    if not len(candidate_lats) or not len(candidate_lons):
        raise ValueError("The Lake polygon does not overlap the NetCDF grid extent.")

    cells, source_indices = [], []
    for sorted_lat_i in candidate_lats:
        for sorted_lon_i in candidate_lons:
            cells.append(gpd.GeoSeries.from_wkt([
                f"POLYGON (({lon_edges[sorted_lon_i]} {lat_edges[sorted_lat_i]}, "
                f"{lon_edges[sorted_lon_i + 1]} {lat_edges[sorted_lat_i]}, "
                f"{lon_edges[sorted_lon_i + 1]} {lat_edges[sorted_lat_i + 1]}, "
                f"{lon_edges[sorted_lon_i]} {lat_edges[sorted_lat_i + 1]}, "
                f"{lon_edges[sorted_lon_i]} {lat_edges[sorted_lat_i]}))"
            ], crs="EPSG:4326").iloc[0])
            source_indices.append((lat_order[sorted_lat_i], lon_order[sorted_lon_i]))

    fishnet = gpd.GeoDataFrame({"source_index": source_indices}, geometry=cells, crs="EPSG:4326")
    fishnet_equal_area = fishnet.to_crs(AREA_CRS)
    lake_equal_area = lake.to_crs(AREA_CRS).geometry.iloc[0]
    fractions = fishnet_equal_area.geometry.intersection(lake_equal_area).area.to_numpy() / lake_equal_area.area
    keep = fractions > 0
    if not np.any(keep):
        raise ValueError("No fishnet cell has a positive Lake intersection area.")
    indices, fractions = np.asarray(source_indices, dtype=int)[keep], fractions[keep]
    if not np.isclose(fractions.sum(), 1.0, rtol=1e-8, atol=1e-8):
        raise RuntimeError(f"Lake weights must sum to 1; got {fractions.sum():.12f}.")
    logging.info("%d rainfall cells intersect the Lake polygon.", len(fractions))
    return GridWeights(indices[:, 0], indices[:, 1], fractions)


def rainfall_variable(ds: xr.Dataset) -> str:
    if RAINFALL_VARIABLE and RAINFALL_VARIABLE in ds.data_vars:
        return RAINFALL_VARIABLE
    candidates = [name for name, value in ds.data_vars.items() if {"time", "lat", "lon"}.issubset(value.dims)]
    if len(candidates) != 1:
        raise ValueError(f"Could not identify one rainfall variable. Candidates: {candidates}")
    return candidates[0]


def process_file(path: Path, lake: gpd.GeoDataFrame, cache: dict[str, GridWeights]) -> pd.Series:
    with xr.open_dataset(path, decode_times=True, mask_and_scale=True) as ds:
        if not {"lat", "lon", "time"}.issubset(ds.coords):
            raise ValueError("Expected lat, lon and time coordinates.")
        variable = rainfall_variable(ds)
        values = ds[variable].transpose("time", "lat", "lon")
        if values.ndim != 3:
            raise ValueError(f"{variable} must have dimensions (time, lat, lon); got {values.dims}")
        key = grid_key(ds.lat.values, ds.lon.values, "EPSG:4326")
        if key not in cache:
            cache[key] = make_weights(ds.lat.values, ds.lon.values, lake)
        weights = cache[key]
        selected = values.values[:, weights.lat_index, weights.lon_index]
        annual = np.where(np.isnan(selected).any(axis=1), np.nan, selected @ weights.lake_fraction)
        years = np.asarray(ds.time.dt.year.values, dtype=int)
        if pd.Index(years).duplicated().any():
            raise ValueError("More than one time step has the same year.")
        logging.info("%s: %s to %s (%d annual records, %s).", path.name, years.min(), years.max(), len(years), variable)
        return pd.Series(annual, index=years, name=path.parent.name.rsplit("-", 1)[-1])


def write_workbook(table: pd.DataFrame) -> None:
    OUTPUT_XLSX.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(OUTPUT_XLSX, engine="xlsxwriter") as writer:
        table.to_excel(writer, sheet_name="Lake Macquarie R20mm", index_label="Year")
        workbook, worksheet = writer.book, writer.sheets["Lake Macquarie R20mm"]
        header = workbook.add_format({"bold": True, "bg_color": "#1F4E78", "font_color": "#FFFFFF", "align": "center"})
        number = workbook.add_format({"num_format": "0.000", "align": "right"})
        worksheet.set_row(0, None, header)
        worksheet.set_column(0, 0, 12)
        worksheet.set_column(1, len(table.columns), 16, number)
        worksheet.freeze_panes(1, 1)
        worksheet.autofilter(0, 0, len(table), len(table.columns))


def main() -> None:
    require_path(NETCDF_ROOT, "NetCDF root folder")
    require_path(LAKE_GPKG, "Lake GeoPackage")
    files = sorted(NETCDF_ROOT.rglob("*.nc"))
    if not files:
        raise FileNotFoundError(f"No .nc files were found below {NETCDF_ROOT}")
    lake, cache, results = load_lake(), {}, []
    for path in files:
        try:
            results.append(process_file(path, lake, cache))
        except Exception as exc:
            logging.exception("Skipping %s because it could not be processed: %s", path, exc)
    if not results:
        raise RuntimeError("No NetCDF files were processed successfully.")
    write_workbook(pd.concat(results, axis=1).sort_index())
    logging.info("Processing complete: %s", OUTPUT_XLSX)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    try:
        main()
    except Exception as error:
        logging.critical("Processing failed: %s", error)
        sys.exit(1)
