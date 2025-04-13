import streamlit as st
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

st.set_page_config(page_title="BGMI Tournament Schedule Generator", layout="wide")

st.title("BGMI Tournament Schedule Generator")
st.markdown("Generate a custom tournament schedule for Battle Grounds Mobile India (BGMI).")

with st.expander("Tournament Settings", expanded=True):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Changed to only allow even numbers
        total_teams = st.number_input("Total Number of Teams (10-32, even numbers only)", 
                                      min_value=10, max_value=32, value=16, step=2)
        
        teams_per_match = st.number_input("Teams per Match (maximum 16)", 
                                         min_value=2, max_value=16, value=16)
    
    with col2:
        tournament_days = st.number_input("Tournament Duration (days, 1-7)", 
                                         min_value=1, max_value=7, value=3)
        
        matches_per_day = st.number_input("Matches per Day (maximum 6)", 
                                         min_value=1, max_value=6, value=4)
    
    with col3:
        matches_per_team = st.number_input("Matches per Team (maximum 6)", 
                                          min_value=1, max_value=6, value=3)
        
        # Add date picker for tournament start date
        start_date = st.date_input("Tournament Start Date", value=datetime.now().date())
        
        # Calculate and display end date
        end_date = start_date + timedelta(days=tournament_days - 1)
        st.info(f"Tournament End Date: {end_date.strftime('%d-%m-%y')}")

    # Calculate total matches
    total_matches = tournament_days * matches_per_day
    
    st.info(f"Total matches in tournament: {total_matches}")
    
# Team names input
with st.expander("Team Names", expanded=True):
    st.markdown(f"Enter names for all {total_teams} teams:")
    
    team_names = []
    cols = st.columns(4)
    
    for i in range(total_teams):
        with cols[i % 4]:
            team_name = st.text_input(f"Team {i+1}", value=f"Team {i+1}", key=f"team_{i}")
            team_names.append(team_name)
    
    if len(set(team_names)) != total_teams:
        st.error("Each team must have a unique name.")

# Function to generate schedule
def generate_schedule():
    # Create the teams
    teams = team_names.copy()
    
    # Track matches per team
    team_match_count = {team: a for team, a in zip(teams, [0] * len(teams))}
    
    # Create schedule structure
    schedule = []
    match_id = 1
    
    # Generate exactly the requested number of matches for each day
    for day in range(tournament_days):
        day_matches = []
        
        for match in range(matches_per_day):
            # Prioritize teams that have played fewer matches
            sorted_teams = sorted(teams, key=lambda t: team_match_count[t])
            
            # Select teams for this match, prioritizing those with fewer matches
            match_teams = sorted_teams[:teams_per_match]
            
            # If we need more teams than available with minimum matches, 
            # get the remaining teams randomly from the rest
            if len(match_teams) < teams_per_match:
                remaining_teams = [t for t in teams if t not in match_teams]
                additional_teams = random.sample(remaining_teams, teams_per_match - len(match_teams))
                match_teams.extend(additional_teams)
            
            # Update match counts
            for team in match_teams:
                team_match_count[team] += 1
            
            day_matches.append({
                "match_id": match_id,
                "teams": match_teams
            })
            
            match_id += 1
        
        schedule.append({
            "day": day + 1,
            "matches": day_matches
        })
    
    return schedule, team_match_count

# Generate button
if st.button("Generate Tournament Schedule", type="primary"):
    if len(set(team_names)) == total_teams:
        with st.spinner("Generating tournament schedule..."):
            schedule, team_match_count = generate_schedule()
            
            # Display the schedule
            st.subheader("Tournament Schedule")
            
            # Create list to store CSV data
            csv_rows = []
            
            for day_info in schedule:
                day_num = day_info["day"]
                matches = day_info["matches"]
                
                # Calculate the date for this day as a string
                current_date = start_date + timedelta(days=day_num-1)
                date_string = current_date.strftime('%d-%m-%Y')  # DD-MM-YYYY format
                
                st.markdown(f"### Day {day_num} - {current_date.strftime('%A, %B %d, %Y')}")
                
                match_data = []
                for match in matches:
                    match_data.append({
                        "Match ID": match["match_id"],
                        "Teams": ", ".join(match["teams"])
                    })
                    
                    # Add to CSV data as simple strings
                    csv_rows.append({
                        "Day": f"Day {day_num}",
                        "Date": date_string,
                        "Match ID": str(match["match_id"]),
                        "Teams": ", ".join(match["teams"])
                    })
                
                st.table(pd.DataFrame(match_data))
            
            # Team participation summary
            st.subheader("Team Participation Summary")
            team_summary = pd.DataFrame({
                "Team": list(team_match_count.keys()),
                "Matches": list(team_match_count.values())
            })
            st.dataframe(team_summary.sort_values("Matches", ascending=False))
            
            # Export options
            st.subheader("Export Schedule")
            
            # Create DataFrame from CSV rows
            csv_df = pd.DataFrame(csv_rows)
            
            # Preview the CSV
            st.write("CSV Preview (first 5 rows):")
            st.write(csv_df.head())
            
            # Convert DataFrame to CSV string with explicit string conversion
            csv_string = csv_df.to_csv(index=False)
            
            st.download_button(
                label="Download Schedule as CSV",
                data=csv_string,
                file_name="bgmi_tournament_schedule.csv",
                mime="text/csv"
            )
    else:
        st.error("Please fix the errors before generating the schedule.")

st.markdown("---")
st.markdown("### Instructions")
st.markdown("""
- Set the tournament parameters in the Tournament Settings section
- Select the tournament start date (end date will be calculated automatically)
- Enter unique names for all teams
- Click 'Generate Tournament Schedule' to create your custom schedule
- You can download the schedule as a CSV file for later use
""")