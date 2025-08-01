import streamlit as st
from garmin_utils import resume_session, download_activities, filter_cycling_activities, download_fit_files
from gps_utils import process_fit_folder
from gps_processing import (
    load_gps_csv_to_geodataframe,
    load_postcode_data,
    find_intersections,
    mark_crossed_areas,
    calculate_crossing_stats
)
from unzip_utils import unzip_fit_files
from streamlit_folium import st_folium
import folium
import os
from map_utils import generate_map_with_stats

st.set_page_config(page_title="Postcode Challenge", layout="wide")
st.title("🚴‍♂️ Postcode Challenge")

# Step 1: Garmin Download
st.header("Step 1: Download Garmin Activities")
resume_session()
activity_count = st.number_input("Number of latest activities to download (leave 0 for all)", min_value=0, value=50)
if st.button("Download Activities"):
    df_all = download_activities(None if activity_count == 0 else activity_count)
    df_cycling = filter_cycling_activities(df_all)
    st.success(f"Found {len(df_cycling)} cycling activities with GPS")
    download_fit_files("cycling", df_cycling)

# Step 2: Extract GPS Data
st.header("Step 2: Extract GPS Data")
if st.button("Extract GPS from FIT files"):
    unzip_fit_files("cycling")  # Optional if files are zipped
    process_fit_folder("cycling_fit_files/unzipped")
    st.success("GPS data extracted and saved to gps_points.csv")

# Step 3: Analyze GPS Tracks
st.header("Step 3: Analyze GPS Tracks")
if st.button("Analyze Tracks"):
    if os.path.exists("gps_points.csv"):
        gdf_gps = load_gps_csv_to_geodataframe("gps_points.csv")
        gdf_postcode = load_postcode_data("postcodes/cbs_pc4_2023.gpkg")
        intersected_postcode = find_intersections(gdf_gps, gdf_postcode)
        gdf_postcode = mark_crossed_areas(gdf_postcode, intersected_postcode, "postcode")
        crossed, uncrossed, crossedpct = calculate_crossing_stats(gdf_postcode)

        st.metric("Crossed Postcodes", crossed)
        st.metric("Remaining", uncrossed)
        st.progress(crossedpct / 100)
        st.success(f"You've crossed {crossed} postcode areas!")
        st.session_state["gdf_postcode"]= gdf_postcode
        st.session_state["crossed"] = crossed
        st.session_state["uncrossed"] = uncrossed
        st.session_state["crossedpct"] = crossedpct

        
# Step 4: Generate Map with stats
st.header("Step 4: Generate map with stats")

if st.button("Generate HTML Map with Stats"):
    gdf_postcode = st.session_state.get("gdf_postcode")
    crossed = st.session_state.get("crossed", 0)
    uncrossed = st.session_state.get("uncrossed", 0)
    crossedpct = st.session_state.get("crossedpct", 0.0)

    if gdf_postcode is not None:
        map_file = generate_map_with_stats(
            gdf_postcode,
            tooltip_field="postcode",
            alias="Postcode:",
            crossed=crossed,
            uncrossed=uncrossed,
            crossedpct=crossedpct
        )
        with open(map_file, "rb") as f:
            st.download_button("Download Map with Stats as HTML", f, file_name=map_file, mime="text/html")
    else:
        st.warning("No postcode data available to generate the map.")

