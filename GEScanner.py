import pandas as pd
import requests
from GlobalEntryCenters import ge_centers
import streamlit as st
from datetime import datetime, time
from streamlit_gsheets import GSheetsConnection
import time as tm
import re

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

def is_valid_email(email):
    # Regular expression for validating an Email
    regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    # If the string matches the regex, it is a valid email
    if re.fullmatch(regex, email):
        return True
    else:
        return False
    
def add_user_info(existing_data, user_data, conn, worksheet_url):
    try:
        updated_df  = pd.concat([existing_data, user_data], ignore_index=True)
        conn.update(spreadsheet= worksheet_url, data=updated_df)
        st.success("Successfully updated user data!")
    except Exception as e:
        st.error(f"Failed to update user data due to {e}")

df = pd.json_normalize(ge_centers)
st.title("Global Entry Appointment Scanner") 
enrolment_centers = df["name"].to_list()

# Create the multiselect dropdown
selected_options = st.multiselect("Select Enrolment Centers", enrolment_centers)


# # Define the time range for the slider
# start_time = time(8, 00)  # 8:00 AM
# end_time = time(18, 00)  # 6:00 PM

# # Create a slider for selecting a time window
# time_window = st.slider(
#     "Select a time window:",
#     value=(start_time, end_time),
#     format="HH:mm"  # Optional: format the display of the times
# )

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


conn = st.connection("gsheets", type=GSheetsConnection)
worksheet_url = "https://docs.google.com/spreadsheets/d/1G_-NCxfPZmYD7uuNxfcSObmGXn_aDSXKHy388GgHNTo/"
existing_data = conn.read(spreadsheet= worksheet_url , usecols = list(range(6)), ttl = 5)
existing_data = existing_data.dropna(how="all")


# Create an input box where users can enter an email address
user_input = st.text_input("Enter your email address")

# Create a submit button
if st.button('Submit'):
    # Check if the email entered is valid
    if is_valid_email(user_input):
        st.success(f'You entered a valid email: {user_input}')
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")  # Format the timestamp as you like
        
        user_data = pd.DataFrame(
            [
                {
                    "UserEmail" : user_input,
                    "SelectedLocations": selected_options,
                    "NumLocations": len(selected_options),
                    "RegisteredOn": now	
                }

            ]

        )
        st.dataframe(user_data)

        if add_user_info(existing_data, user_data, conn, worksheet_url):
            st.dataframe(existing_data)
        

    else:
        st.error('This is not a valid email address. Please try again.')



