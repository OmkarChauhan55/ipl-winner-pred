import streamlit as st
import pickle
import pandas as pd
import matplotlib.pyplot as plt

# Custom CSS for styling
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .stSelectbox, .stNumberInput {
        background-color: white;
        border-radius: 10px;
        padding: 8px;
    }
    .stButton>button {
        background: linear-gradient(to right, #ff8a00, #da1b60);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 10px 24px;
        font-weight: bold;
        font-size: 16px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    .header-text {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(to right, #da1b60, #ff8a00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 30px;
    }
    .team-card {
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        text-align: center;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .metric-box {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Team and city lists
teams = [
    'Sunrisers Hyderabad',
    'Mumbai Indians',
    'Royal Challengers Bengaluru',
    'Kolkata Knight Riders',
    'Punjab Kings',
    'Chennai Super Kings',
    'Rajasthan Royals',
    'Delhi Capitals',
    'Lucknow Super Giants',
    'Gujarat Titans'
]

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

# Load trained prediction pipeline
pipe = pickle.load(open('pipe.pkl', "rb"))

# App Header
st.markdown('<p class="header-text">IPL Win Predictor</p>', unsafe_allow_html=True)

# Team Selection Columns
col1, col2 = st.columns(2)
with col1:
    st.markdown("### Batting Team")
    batting_team = st.selectbox('', sorted(teams), label_visibility="collapsed", key="batting_team_selectbox")
with col2:
    st.markdown("### Bowling Team")
    bowling_team = st.selectbox('', sorted(teams), label_visibility="collapsed", key="bowling_team_selectbox")


# City Selection
st.markdown("### Match Location")
selected_city = st.selectbox('', sorted(cities), label_visibility="collapsed")

# Target and Current Score Inputs
st.markdown("### Match Progress")
col3, col4 = st.columns(2)
with col3:
    target = st.number_input('Target Score', min_value=0, step=1, format="%d")
with col4:
    score = st.number_input('Current Score', min_value=0, step=1, format="%d")

# Match Details: Overs Completed, Wickets Fallen, and Balls Remaining
st.markdown("### Match Details")
col5, col6, col7 = st.columns(3)
with col5:
    overs = st.selectbox(
        'Overs Completed',
        options=[round(over + ball / 10, 1) for over in range(0, 20) for ball in range(0, 6)] + [20.0]
    )
with col6:
    wickets_out = st.number_input('Wickets Fallen', min_value=0, max_value=10, step=1)
with col7:
    # Calculate balls remaining for display
    if overs < 20:
        over_int = int(overs)
        ball_fraction = round((overs - over_int) * 10)
        balls_bowled_temp = over_int * 6 + ball_fraction
        balls_remaining_display = 120 - balls_bowled_temp
    else:
        balls_remaining_display = 0

    st.markdown(
        "<div class='metric-box'>"
        f"<div style='font-size: 0.9rem; color: #666;'>Balls Remaining</div>"
        f"<div style='font-size: 1.5rem; font-weight: bold;'>{balls_remaining_display}</div>"
        "</div>",
        unsafe_allow_html=True
    )

# Prediction Button
predict_button = st.button('Predict Win Probability', use_container_width=True)

if predict_button:
    # Validation
    if batting_team == bowling_team:
        st.error("⚠ Batting and Bowling teams cannot be the same.")
    elif overs > 20:
        st.error("⚠ Overs cannot be more than 20.")
    elif wickets_out > 10:
        st.error("⚠ Wickets out cannot be more than 10.")
    elif score > target:
        st.error("⚠ Current score cannot be greater than the target.")
    else:
        # Recalculate numeric match-state features
        runs_left = target - score
        over_int = int(overs)
        ball_fraction = round((overs - over_int) * 10)
        balls_bowled = over_int * 6 + ball_fraction
        balls_left = 120 - balls_bowled

        remaining_wickets = 10 - wickets_out
        crr = score / overs if overs != 0 else 0
        rrr = (runs_left * 6) / balls_left if balls_left != 0 else 0

        # Display Current Run Rate and Required Run Rate
        col8, col9 = st.columns(2)
        with col8:
            st.markdown(
                f"<div class='metric-box'>"
                f"<div style='font-size: 0.9rem; color: #666;'>Current Run Rate</div>"
                f"<div style='font-size: 1.5rem; font-weight: bold; color: #4CAF50;'>{crr:.2f}</div>"
                "</div>",
                unsafe_allow_html=True
            )
        with col9:
            st.markdown(
                f"<div class='metric-box'>"
                f"<div style='font-size: 0.9rem; color: #666;'>Required Run Rate</div>"
                f"<div style='font-size: 1.5rem; font-weight: bold; color: #F44336;'>{rrr:.2f}</div>"
                "</div>",
                unsafe_allow_html=True
            )

        # Prepare input DataFrame for the model
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

        # Predict probabilities
        result = pipe.predict_proba(input_df)
        loss_prob = result[0][0]
        win_prob = result[0][1]

        # Display Win Probability cards
        st.markdown("## Win Probability")
        col10, col11 = st.columns(2)
        with col10:
            st.markdown(
                f"<div class='team-card' style='background-color: {team_colors.get(batting_team, '#00cc99')}80;'>"
                f"{batting_team}<br><span style='font-size: 2rem;'>{round(win_prob * 100)}%</span>"
                "</div>",
                unsafe_allow_html=True
            )
        with col11:
            st.markdown(
                f"<div class='team-card' style='background-color: {team_colors.get(bowling_team, '#ff6666')}80;'>"
                f"{bowling_team}<br><span style='font-size: 2rem;'>{round(loss_prob * 100)}%</span>"
                "</div>",
                unsafe_allow_html=True
            )

        # Win probability donut chart
        labels = [batting_team, bowling_team]
        sizes = [round(win_prob * 100), round(loss_prob * 100)]
        colors = [team_colors.get(batting_team, '#00cc99'), team_colors.get(bowling_team, '#ff6666')]
        explode = (0.05, 0.05)

        fig, ax = plt.subplots(figsize=(8, 8))
        fig.patch.set_facecolor('none')
        ax.set_facecolor('none')

        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors,
            explode=explode,
            shadow=True,
            textprops={'fontsize': 14, 'color': 'black', 'weight': 'bold'}
        )

        # Draw white circle in the center for a donut effect
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        fig.gca().add_artist(centre_circle)

        ax.axis('equal')
        plt.setp(autotexts, size=16, weight="bold")
        ax.set_title("Win Probability", fontsize=18, weight='bold', pad=20)

        st.pyplot(fig, clear_figure=True)
