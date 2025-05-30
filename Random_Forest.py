import subprocess
import sys
subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib"])

import streamlit as st
import pickle
import pandas as pd
import matplotlib.pyplot as plt

teams = ['Sunrisers Hyderabad',
         'Mumbai Indians',
         'Royal Challengers Bengaluru',
         'Kolkata Knight Riders',
         'Punjab Kings',
         'Chennai Super Kings',
         'Rajasthan Royals',
         'Delhi Capitals',
         'Lucknow Super Giants',
         'Gujarat Titans']

team_colors = {
    'Sunrisers Hyderabad': '#F26522',
    'Mumbai Indians': '#004BA0',
    'Royal Challengers Bengaluru': '#DA1818',
    'Kolkata Knight Riders': '#3B0A45',
    'Punjab Kings': '#B2002D',
    'Chennai Super Kings': '#FDEE00',
    'Rajasthan Royals': '#EA1A8E',
    'Delhi Capitals': '#17449B',
    'Lucknow Super Giants': '#93DAFF',
    'Gujarat Titans': '#0F1A2C'
}
cities = [
    'Ahmedabad', 'Bengaluru', 'Chennai', 'Delhi', 'Dharamsala',
    'Guwahati', 'Hyderabad', 'Jaipur', 'Kolkata', 'Lucknow',
    'Mumbai', 'Mullanpur', 'Visakhapatnam'
]

pipe1 = pickle.load(open('pipe1.pkl', "rb"))

st.title('IPL Win Predictor')

col1, col2 = st.columns(2)

with col1:
    batting_team = st.selectbox('Select the batting team ', sorted(teams))
with col2:
    bowling_team = st.selectbox('Select the bowling team ', sorted(teams))

selected_city = st.selectbox('Select host city', sorted(cities))

target = st.number_input('Target', min_value=0, step=1, format="%d")

col3, col4, col5 = st.columns(3)

with col3:
    score = st.number_input('Score', min_value=0, step=1, format="%d")
with col4:
    overs = st.selectbox(
        'Overs completed',
        options=[round(over + ball / 10, 1) for over in range(0, 20) for ball in range(0, 6)] + [20.0]
    )
with col5:
    wickets_out = st.number_input('Wickets out', min_value=0, max_value=10, step=1)

# Validation and prediction logic
if st.button('Predict Probability'):
    if batting_team == bowling_team:
        st.error("Batting and Bowling teams cannot be the same.")
    elif overs > 20:
        st.error("Overs cannot be more than 20.")
    elif wickets_out > 10:
        st.error("Wickets out cannot be more than 10.")
    elif score > target:
        st.error("Score cannot be greater than the target.")
    else:
        runs_left = target - score
        over_int = int(overs)
        ball_fraction = round((overs - over_int) * 10)
        balls_bowled = over_int * 6 + ball_fraction
        balls_left = 120 - balls_bowled

        remaining_wickets = 10 - wickets_out
        crr = score / overs if overs != 0 else 0
        rrr = (runs_left * 6) / balls_left if balls_left != 0 else 0

        # Display CRR and RRR
        st.markdown(f"*Current Run Rate (CRR):* {crr:.2f}")
        st.markdown(f"*Required Run Rate (RRR):* {rrr:.2f}")

        # Prepare input and make prediction
        input_df = pd.DataFrame({
            'batting_team': [batting_team],
            'bowling_team': [bowling_team],
            'city': [selected_city],
            'runs_left': [runs_left],
            'balls_left': [balls_left],
            'wickets': [remaining_wickets],
            'total_runs_x': [target],
            'crr': [crr],
            'rrr': [rrr]
        })

        # result = pipe.predict_proba(input_df)
        # loss = result[0][0]
        # win = result[0][1]
        #
        # st.header(f"{batting_team} - {round(win * 100)}%")
        # st.header(f"{bowling_team} - {round(loss * 100)}%")
        result = pipe1.predict_proba(input_df)
        loss = result[0][0]
        win = result[0][1]
        st.subheader("Win Probability")

        st.header(f"{batting_team} - {round(win * 100)}%")
        st.header(f"{bowling_team} - {round(loss * 100)}%")

        # Win probability pie chart

        labels = [batting_team, bowling_team]
        sizes = [round(win * 100), round(loss * 100)]
        colors = [team_colors.get(batting_team, '#00cc99'), team_colors.get(bowling_team, '#ff6666')]

        explode = (0.05, 0.05)  # Slightly separate slices

        fig, ax = plt.subplots(figsize=(6, 6))  # Default white background

        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            autopct='%d%%',
            startangle=90,
            colors=colors,
            explode=explode,
            shadow=True,
            textprops={'fontsize': 14, 'color': 'black'}  # Use black text for visibility on white
        )

        ax.axis('equal')  # Pie circle
        plt.setp(autotexts, size=14, weight="bold", color='black')  # Bold black percentage text
        ax.set_title("", fontsize=16, weight='bold', color='black')

        # Remove transparency so background stays white
        # (No need for fig.patch.set_alpha or ax.set_facecolor here)

        st.pyplot(fig, clear_figure=True)
