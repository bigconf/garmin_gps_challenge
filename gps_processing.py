import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import folium
import os
from fitparse import FitFile
from shapely.geometry import LineString
from streamlit_folium import st_folium
import pandas as pd
from shapely.geometry import Point

def load_gps_csv_to_geodataframe(csv_path: str) -> gpd.GeoDataFrame:
    """Load GPS points from CSV and convert to GeoDataFrame."""
    df = pd.read_csv(csv_path, header=None, names=["lat", "lon", "activity_id"])
    geometry = [Point(lon, lat) for lat, lon in zip(df["lat"], df["lon"])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
    return gdf


def load_postcode_data(path):
    gdf_postcode = gpd.read_file(path)
    gdf_postcode = gdf_postcode[['postcode', 'geometry']]
    gdf_postcode = gdf_postcode.to_crs(epsg=4326)
    return gdf_postcode


def find_intersections(gdf_gps, gdf_postcode):
    intersected_postcode = gpd.sjoin(gdf_postcode, gdf_gps, how="inner", predicate="intersects")
    return intersected_postcode


def mark_crossed_areas(gdf, intersected, id_column):
    gdf["crossed"] = gdf[id_column].isin(intersected[id_column])
    gdf["crossed"] = gdf["crossed"].fillna(False).astype(bool)
    return gdf


def calculate_crossing_stats(gdf, column="crossed"):
    crossed = int(gdf[column].sum())
    uncrossed = int((~gdf[column]).sum())
    total = crossed + uncrossed
    crossedpct = float(crossed / total * 100) if total > 0 else 0
    return crossed, uncrossed, crossedpct





