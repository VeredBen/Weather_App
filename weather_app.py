import json
import requests
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv('api_key')

# Load states and cities from CSV file
states_cities_df = pd.read_csv('states_cities.csv')
states_cities = states_cities_df.groupby('state')['city'].apply(list).to_dict()

# Streamlit app
st.title("Weather Forecast App")

# State selection
state = st.selectbox("Select a state", list(states_cities.keys()))

# City selection
city = st.selectbox("Select a city", states_cities[state])

# Units selection
units = st.selectbox("Select units", ["Metric", "Imperial"])

def plot_wind(df, midnight_timestamps, units):
    st.subheader("Wind")
    fig, ax = plt.subplots()
    ax.plot(df["Timestamp"], df["Wind Speed"], label="Speed")
    ax.plot(df["Timestamp"], df["Wind Gust"], label="Gust")
    ax.set_ylabel(f"Wind ({'m/s' if units == 'Metric' else 'mph'})")
    ax.set_xticks(midnight_timestamps)
    ax.set_xticklabels(midnight_timestamps, rotation=45, ha="right")
    ax.legend()
    st.pyplot(fig)

def plot_temperature(df, units, midnight_timestamps):
    temp_label = "Temperature (°C)" if units == "Metric" else "Temperature (°F)"
    temp_data = df["Temperature"]
    feels_like_data = df["Feels Like"]

    # Plot Temperature
    st.subheader("Temperature")
    fig, ax = plt.subplots()
    ax.plot(df["Timestamp"], temp_data, label="Temperature")
    ax.plot(df["Timestamp"], feels_like_data, label="Feels Like")
    ax.set_ylabel(temp_label)
    ax.set_xticks(midnight_timestamps)
    ax.set_xticklabels(midnight_timestamps, rotation=45, ha="right")
    ax.legend()
    st.pyplot(fig)

def plot_precipitation(df, midnight_timestamps):
    st.subheader("Precipitation")
    fig, ax = plt.subplots()
    ax.plot(df["Timestamp"], df["Precipitation Probability"], label="Probability")
    ax.plot(df["Timestamp"], df["Precipitation Volume"], label="Volume")
    ax.set_ylabel("Precipitation")
    ax.set_xticks(midnight_timestamps)
    ax.set_xticklabels(midnight_timestamps, rotation=45, ha="right")
    ax.legend()
    st.pyplot(fig)

if st.button("Show Weather"):
    # Fetch weather data from OpenWeatherMap
    units_param = "metric" if units == "Metric" else "imperial"
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city},{state},US&appid={API_KEY}&units={units_param}"
    response = requests.get(url)
    data = response.json()

    # Check if the response contains the 'list' key
    if 'list' not in data:
        st.error("Failed to fetch weather data. Please check the city and state combination.")
        st.write(data)  # Print the response for debugging
    else:
        # Extract relevant data
        timestamps = [item['dt_txt'] for item in data['list']]
        temperatures = [item['main']['temp'] for item in data['list']]
        feels_like = [item['main']['feels_like'] for item in data['list']]
        precipitation_prob = [item.get('pop', 0) for item in data['list']]
        precipitation_volume = [item.get('rain', {}).get('3h', 0) for item in data['list']]
        wind_speed = [item['wind']['speed'] for item in data['list']]
        wind_gust = [item['wind'].get('gust', 0) for item in data['list']]

        # Create a DataFrame
        df = pd.DataFrame({
            "Timestamp": timestamps,
            "Temperature": temperatures,
            "Feels Like": feels_like,
            "Precipitation Probability": precipitation_prob,
            "Precipitation Volume": precipitation_volume,
            "Wind Speed": wind_speed,
            "Wind Gust": wind_gust
        })

        # Save data to CSV
        df.to_csv("weather_data.csv", index=False)

        # Filter timestamps to include only midnight times
        global midnight_timestamps
        midnight_timestamps = [ts for ts in timestamps if ts.endswith("00:00:00")]

        # Plot Wind
        plot_wind(df, midnight_timestamps, units)

        # Plot Temperature
        plot_temperature(df, units, midnight_timestamps)

        # Plot Precipitation
        plot_precipitation(df, midnight_timestamps)