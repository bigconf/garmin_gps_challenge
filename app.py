import streamlit as st
from garmin_utils import resume_session, download_activities, filter_activities_by_sport, download_fit_files, SPORT_TYPE_GROUPS
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
from file_utils import cleanup_fit_folder

st.set_page_config(page_title="Postcode Challenge", layout="wide")
st.title("🚴‍♂️ Postcode Challenge")

st.header("User Login")
username = st.text_input("Enter your Garmin username", key="username")

# Check if session exists before asking for password
session_dir = os.path.join("garmin_sessions", username)
session_exists = os.path.exists(session_dir)

if username:
    if session_exists:
        resume_session(username)
    else:
        password = st.text_input("Enter your Garmin password", type="password", key="password")
        if password:
            resume_session(username, password)
        else:
            st.warning("Session not found. Please enter your password to log in.")
            st.stop()
else:
    st.warning("Please enter your Garmin username to continue.")
    st.stop()


# Step 1: Select sport
st.header("Step 1: Select sport")
selected_sport = st.selectbox("Choose sport", list(SPORT_TYPE_GROUPS.keys()))


# Step 2: Garmin Download
st.header("Step 2: Download Garmin Activities")
activity_count = st.number_input("Number of latest activities to download (leave 0 for all)", min_value=0, value=50)
if st.button("Download Activities"):
    df_all = download_activities(None if activity_count == 0 else activity_count)
    df_filtered = filter_activities_by_sport(df_all, selected_sport)
    st.success(f"Found {len(df_filtered)} {selected_sport} activities with GPS")
    download_fit_files(selected_sport, df_filtered, username)
   
    #df_cycling = filter_cycling_activities(df_all)
    #st.success(f"Found {len(df_cycling)} cycling activities with GPS")
    #download_fit_files("cycling", df_cycling, username)

# Step 3: Extract GPS Data
st.header("Step 3: Extract GPS Data")
if st.button("Extract GPS from FIT files"):
    unzip_fit_files(selected_sport, username)
    #unzip_fit_files("cycling", username)  # Optional if files are zipped
    user_fit_folder = os.path.join("user_data", username, f"{selected_sport}_fit_files", "unzipped")
    #user_fit_folder = os.path.join("user_data", username, "cycling_fit_files", "unzipped")
    process_fit_folder(user_fit_folder, username)
    st.success("GPS data extracted and saved to gps_points.csv")
    cleanup_fit_folder(username, selected_sport)
    #cleanup_fit_folder(username)


# Step 4: Analyze GPS Tracks
st.header("Step 4: Analyze GPS Tracks")
if st.button("Analyze Tracks"):
    gps_csv_path = os.path.join("user_data", username, "gps_points.csv")
    if os.path.exists(gps_csv_path):
        with st.spinner("Loading GPS data..."):
            gdf_gps = load_gps_csv_to_geodataframe(gps_csv_path)

        with st.spinner("Loading postcode data..."):
            gdf_postcode = load_postcode_data("postcodes/cbs_pc4_2023.gpkg")

        with st.spinner("Finding intersections..."):
            intersected_postcode = find_intersections(gdf_gps, gdf_postcode)

        with st.spinner("Marking crossed postcode areas..."):
            gdf_postcode = mark_crossed_areas(gdf_postcode, intersected_postcode, "postcode")

        with st.spinner("Calculating crossing statistics..."):
            crossed, uncrossed, crossedpct = calculate_crossing_stats(gdf_postcode)

        st.metric("Crossed Postcodes", crossed)
        st.metric("Remaining", uncrossed)
        st.progress(crossedpct / 100)
        st.success(f"You've crossed {crossed} postcode areas!")

        st.session_state["gdf_postcode"] = gdf_postcode
        st.session_state["crossed"] = crossed
        st.session_state["uncrossed"] = uncrossed
        st.session_state["crossedpct"] = crossedpct
    else:
        st.error("GPS CSV file not found. Please extract GPS data first.")


# Step 5: Generate Map with stats
st.header("Step 5: Generate map with stats")

if st.button("Generate HTML Map with Stats"):
    gdf_postcode = st.session_state.get("gdf_postcode")
    crossed = st.session_state.get("crossed", 0)
    uncrossed = st.session_state.get("uncrossed", 0)
    crossedpct = st.session_state.get("crossedpct", 0.0)

    if gdf_postcode is not None:
        with st.spinner("Generating interactive map..."):
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
        st.success("Map generated successfully!")
    else:
        st.warning("No postcode data available to generate the map.")





