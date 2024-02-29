import pandas as pd
import requests
from GlobalEntryCenters import ge_centers
import streamlit as st
from datetime import datetime, time
from streamlit_gsheets import GSheetsConnection
import time as tm

def count_down(ts, placeholder):
    while ts:
        mins, secs = divmod(ts, 60)
        time_now = '{:02d}:{:02d}'.format(mins, secs)
        placeholder.write(f"Next update in {ts}")
        tm.sleep(1)
        ts -= 1
    return ts

def fetch_slots():
    # API endpoint with parameters
    url = "https://ttp.cbp.dhs.gov/schedulerapi/slots?limit=500"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return []


df = pd.json_normalize(ge_centers)
st.title("Global Entry Appointment Scanner") 
enrolment_centers = df["name"].to_list()

# Create the multiselect dropdown
selected_options = st.multiselect("Select Enrolment Centers", enrolment_centers)
if(selected_options):
    st.write("Fetching appointment slots")

# Define the time range for the slider
start_time = time(8, 00)  # 8:00 AM
end_time = time(18, 00)  # 6:00 PM

# Create a slider for selecting a time window
time_window = st.slider(
    "Select a time window:",
    value=(start_time, end_time),
    format="HH:mm"  # Optional: format the display of the times
)

# Create a placeholder for the DataFrame
dataframe_placeholder = st.empty()
counter_placeholder = st.empty()

# while True:
#     found_slots = pd.json_normalize(fetch_slots())
#     final_df = pd.merge(found_slots, df, left_on='locationId', right_on='id', how='inner')[["locationId", "startTimestamp", "name"]]
#     final_df["startTimestamp"] = pd.to_datetime(final_df["startTimestamp"])
#     final_df["startTimestamp"] = final_df["startTimestamp"].dt.strftime('%B, %d %I:%M %p')
#     final_df["locationId"] = final_df["locationId"].astype(str)
#     final_df = final_df[["name", "locationId", "startTimestamp"]]
#     final_df.columns = ["Enrolment Center", "Location ID", "Start Time"]
#     filtered_df = final_df[final_df["Enrolment Center"].isin(selected_options)]
#     if(selected_options):
#         dataframe_placeholder.write(filtered_df)
#         counter_placeholder.write({count_down(300, counter_placeholder)})
        

st.write("Gsheets connection")  
conn = st.connection("gsheets", type=GSheetsConnection)
worksheet_url = "https://docs.google.com/spreadsheets/d/1G_-NCxfPZmYD7uuNxfcSObmGXn_aDSXKHy388GgHNTo/edit?hl=en&pli=1#gid=0"
existing_data = conn.read(spreadsheet= worksheet_url , usecols = list(range(6)), ttl = 5)
st.dataframe(existing_data)