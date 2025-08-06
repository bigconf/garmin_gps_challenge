# 🗺️ Garmin_GPS_Challenge

**Garmin_GPS_Challenge** is a Streamlit-based web app for downloading and analyzing Garmin GPS activity data and visualizing intersections with Dutch postcode regions (CBS PC4). Designed for cyclists and runners, the app combines geospatial analysis with a user-friendly interface. The app uses cbs_pc4_2023.gpkg for postcode region analysis.

## 🚀 Features

- 📥 Download and process Garmin FIT files (prevents from downloading fit files more then once)
- 🧭 Analyze GPS tracks and detect postcode intersections
- 🗂️ Store all GPS data in a single CSV file including sport type
- 🗺️ Visualize activities and progress on interactive Folium maps
- 🏃 Multi-sport support (cycling, running, walking)
- 📊 Stats panel showing progress toward postcode coverage

## Dependencies

This project uses the following Python libraries:

- Garth: A Python wrapper for Garmin Connect authentication.
- Garminconnect: A Python client for accessing Garmin connect data.

These libraries are listed in `requirements.txt` and are required to run the app.


## 📁 Project Structure
```text
POSTCODECHALLENGE/ 
├── app.py # Main Streamlit app
├── file_utils.py # File handling and path management 
├── garmin_utils.py # Garmin Connect API logic 
├── gps_processing.py # GPS data parsing and intersection analysis 
├── gps_utils.py # FIT file GPS extraction 
├── map_utils.py # Folium map generation with stats 
├── garmin_sessions/ # Saved Garmin login sessions 
├── postcodes/ 
    └── cbs_pc4_2023.gpkg # CBS PC4 postcode boundaries 
├── user_data/ # User-specific GPS and FIT data 
├── requirements.txt # Python dependencies 
├── .gitignore # Files excluded from version control 
└── .env # Garmin credentials (not tracked)
```

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/bigconf/garmin_gps_challenge.git
   cd garmin_gps_challenge

2. **Create a virtual environment (recommended)**:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate


3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt

4. **Create a .env file with your Garmin credentials (optional)**:
    ```bash
    GARMIN_USERNAME=your_email_or_username
    GARMIN_PASSWORD=your_password

5. **Run the app**:
    '''bash
   streamlit run app.py

📈 **Roadmap**
 - Public deployment (e.g., Streamlit Cloud)
 - Additional layers (e.g. administrative units EU)
 
🤝 **Contributing**
Contributions are welcome! Please open an issue or submit a pull request.

📄 **License**
MIT License

**Credits**

Special thanks to the developers of garth and garminconnect for making Garmin data accessible via Python.
