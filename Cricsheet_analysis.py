import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
from streamlit_option_menu import option_menu
import sqlite3
from sqlalchemy import create_engine

st.markdown(
    """
    <style>
    .centered-title {
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 48px;
        font-weight: bold;
        color: green;
    }
    </style>
    <div class="centered-title">CRICSHEET MATCH ANALYSIS</div>
    """,
    unsafe_allow_html=True
)
with st.sidebar:
    selected = option_menu('Menu',["SQL Queries & Insights","Data Visualization (EDA)"])

# Test matches data
test_summary = pd.read_csv('test_matches_summary.csv',parse_dates=['start_date','end_date'])
test_innings = pd.read_csv('test_matches_innings.csv')

# ODI matches data
odi_summary = pd.read_csv('odi_matches_summary.csv',parse_dates=['start_date','end_date'])
odi_innings = pd.read_csv('odi_matches_innings.csv')

# T20 matches data
t20_summary = pd.read_csv('t20_matches_summary.csv',parse_dates=['start_date','end_date'])
t20_innings = pd.read_csv('t20_matches_innings.csv')

# create database
engine = create_engine('sqlite:///cricket_data.db', echo=True)

# Migrate to SQLite3
test_summary.to_sql('Test_Summary',con=engine,if_exists='replace',index=False)
test_innings.to_sql('Test_Innings',con=engine,if_exists='replace',index=False)

odi_summary.to_sql('ODI_Summary',con=engine,if_exists='replace',index=False)
odi_innings.to_sql('ODI_Innings',con=engine,if_exists='replace',index=False)

t20_summary.to_sql('T20_Summary',con=engine,if_exists='replace',index=False)
t20_innings.to_sql('T20_Innings',con=engine,if_exists='replace',index=False)

if selected=="SQL Queries & Insights":
    tab1,tab2,tab3,tab4 = st.tabs(["Test","ODI","T20","Common"])
    with tab1:
        quest = {
                 "Q1":"Who are the top 10 highest run scorers?",
                 "Q2":"Who are the top 10 most successful wicket-takers?",
                 "Q3":"Which batsmen have the best strike rate (ones who faced more than 500 balls)?",
                 "Q4":"What are the total runs scored by each team in each test match?",
                 "Q5":"What are the runs scored (or wicket taken) by the player of the match in each test match?",
                 "Q6":"Which test matches have happened for more than 4 days and the total overs for these matches?"}
        sl = st.selectbox("Select a query",tuple(quest.values()),index=None)
        if sl==quest["Q1"]:
            query_t1 = pd.read_sql_query('''select batsman, sum(runs_scored) AS total_runs_scored
                                from test_innings
                                group by batsman
                                order by total_runs_scored desc
                                limit 10;''',con=engine)
            st.dataframe(query_t1)
        if sl==quest["Q2"]:
            query = '''select bowler, count(*) as total_wickets
           from test_innings
           where wicket_type != "Not Out"
           group by bowler
           order by total_wickets desc
           limit 10;'''
            query_t2 = pd.read_sql_query(query,con=engine)
            st.dataframe(query_t2)
        if sl==quest["Q3"]:
            query = '''SELECT batsman, 
           SUM(runs_scored) * 100.0 / COUNT(*) AS strike_rate
           FROM test_innings
           GROUP BY batsman
           HAVING COUNT(*) >= 500
           ORDER BY strike_rate DESC
           LIMIT 10;'''
            query_t3 = pd.read_sql_query(query,con=engine)
            st.dataframe(query_t3)
        if sl==quest["Q4"]:
            query ="""SELECT tm.season,tm.start_date,tm.end_date, ti.inning_team, SUM(ti.runs_scored) AS total_runs_scored
          FROM test_summary tm
          JOIN test_innings ti ON tm.match_id = ti.match_id
          GROUP BY ti.match_id, ti.inning_team
          ORDER BY ti.match_id;"""
            query_t4 = pd.read_sql_query(query,con=engine)
            st.dataframe(query_t4)
        if sl==quest["Q5"]:
            query = '''SELECT tm.season,tm.start_date,tm.end_date,tm.team_1,
                       tm.team_2,tm.winner, tm.player_of_match, 
                   COALESCE(SUM(CASE WHEN ti.batsman = tm.player_of_match THEN ti.runs_scored ELSE 0 END), 0) AS total_runs,
                   COALESCE(COUNT(CASE WHEN ti.bowler = tm.player_of_match AND ti.wicket_type != 'Not Out' THEN 1 END), 0) AS total_wickets
            FROM test_summary tm
            LEFT JOIN test_innings ti ON tm.match_id = ti.match_id
            where tm.winner != 'No Result' and tm.player_of_match != 'None'
            GROUP BY tm.match_id, tm.player_of_match
            ORDER BY total_runs DESC, total_wickets DESC;'''
            query_t5 = pd.read_sql_query(query,con=engine)
            st.dataframe(query_t5)
        if sl==quest["Q6"]:
            query = '''select tm.season, tm.start_date, tm.duration_days, 
           tm.team_1, tm.team_2, count(distinct ti.over) as total_overs
           from test_summary tm
           join test_innings ti on tm.match_id=ti.match_id
           where tm.duration_days > 4
           group by tm.match_id;'''
            query_t6 = pd.read_sql_query(query,con=engine)
            st.dataframe(query_t6)
            
    with tab2:
        quest = {
                 "Q1":"What are the top 10 highest team total in ODI matches?",
                 "Q2":"What are the top 15 'fastest 50s' in ODI history?",
                 "Q3":"Who are the top 10 bowlers who have taken most number of wickets in lost ODI matches?",
                 "Q4":"Who are the top 10 highest run scorers in winning matches?",
                 "Q5":"Who are the top 5 batsmen with the most centuries in ODI matches?",
                 "Q6":"Which teams have won most of the matches (select top 5) when they were chasing teams?"}
        sl = st.selectbox("Select a query",tuple(quest.values()),index=None)
        if sl==quest["Q1"]:
            query = """SELECT om.season, om.start_date, om.team_1, om.team_2, team_tot.inning_team, team_tot.total_score
                       FROM odi_summary om
                       JOIN(SELECT match_id, inning_team, SUM(runs_scored) AS total_score
                       FROM odi_innings
                       GROUP BY match_id, inning_team
                       ORDER BY total_score DESC
                       LIMIT 10) AS team_tot ON om.match_id = team_tot.match_id;"""
            query_o1 = pd.read_sql_query(query,con=engine)
            st.dataframe(query_o1)
        if sl==quest["Q2"]:
            query = """SELECT om.season, om.start_date, om.team_1, om.team_2, 
                       fast_50.batsman, fast_50.balls_faced, fast_50.total_runs_scored
                       FROM odi_summary om
                       JOIN(SELECT match_id, batsman, COUNT(*) AS balls_faced, SUM(runs_scored) AS total_runs_scored
                       FROM odi_innings
                       GROUP BY match_id, batsman
                       HAVING total_runs_scored >= 50 AND balls_faced <= 25
                       ORDER BY balls_faced ASC, total_runs_scored DESC
                       LIMIT 15) AS fast_50 ON om.match_id = fast_50.match_id;"""
            query_o2 = pd.read_sql_query(query,con=engine)
            st.dataframe(query_o2)
        if sl==quest["Q3"]:
            query = """SELECT oi.bowler, COUNT(*) AS total_wickets
            FROM odi_summary om
            JOIN odi_innings oi ON om.match_id = oi.match_id
            WHERE oi.wicket_type != 'Not Out' 
            AND (
                (oi.inning_team = om.team_1 AND om.winner = om.team_2)  
                OR 
                (oi.inning_team = om.team_2 AND om.winner = om.team_1)
            )  
            GROUP BY oi.bowler
            ORDER BY total_wickets DESC
            LIMIT 10;"""
            query_o3 = pd.read_sql_query(query,con=engine)
            st.dataframe(query_o3)
        if sl==quest["Q4"]:
            query = """SELECT oi.batsman, SUM(oi.runs_scored) AS total_runs_scored
            FROM odi_summary om
            JOIN odi_innings oi ON om.match_id = oi.match_id
            WHERE om.winner = oi.inning_team
            GROUP BY oi.batsman
            ORDER BY total_runs_scored DESC
            LIMIT 10;"""
            query_o4 = pd.read_sql_query(query,con=engine)
            st.dataframe(query_o4)
        if sl==quest["Q5"]:
            query = """SELECT batsman, COUNT(*) AS centuries
            FROM (
                SELECT match_id, batsman, SUM(runs_scored) AS total_runs_scored
                FROM odi_innings
                GROUP BY match_id, batsman
                HAVING total_runs_scored >= 100  
            ) AS centuries_table
            GROUP BY batsman
            ORDER BY centuries DESC
            LIMIT 5;"""
            query_o5 = pd.read_sql_query(query,con=engine)
            st.dataframe(query_o5)
        if sl==quest["Q6"]:
            query = """SELECT winner, COUNT(*) AS chases_won
            FROM odi_summary
            WHERE toss_decision = 'field'
            GROUP BY winner
            ORDER BY chases_won DESC
            LIMIT 5;"""
            query_o6 = pd.read_sql_query(query,con=engine)
            st.dataframe(query_o6)
            
    with tab3:
        quest = {
                 "Q1":"What is the average strike rate of each team for each T20 match?",
                 "Q2":"What are the top 10 highest runs scored in the powerplay?",
                 "Q3":"How many teams have the team won while losing less than 5 wickets?",
                 "Q4":"Which teams have scored the most number of runs in death overs (last 5 overs)?",
                 "Q5":"Which top 10 bowlers had the worst economy in a single match?",
                 "Q6":"Who are the top 10 bowlers who bowled the most consecutive dot balls in a single T20 match?"}
        sl = st.selectbox("Select a query",tuple(quest.values()),index=None)
        if sl==quest["Q1"]:
            query = """SELECT tm.season, tm.start_date, tm.team_1, tm.team_2, str_rat.inning_team, str_rat.avg_strike_rate
                       FROM t20_summary tm
                       JOIN(SELECT match_id, inning_team,
                       SUM(runs_scored) * 100.0 / COUNT(*) AS avg_strike_rate
                       FROM t20_innings
                       GROUP BY match_id, inning_team) AS str_rat ON tm.match_id=str_rat.match_id;"""
            query_t20_1 = pd.read_sql_query(query,con=engine)
            st.dataframe(query_t20_1)
        if sl==quest["Q2"]:
            query = """SELECT tm.season, tm.start_date, tm.team_1, tm.team_2, pow_ply.inning_team, pow_ply.powerplay_runs
                       FROM t20_summary tm
                       JOIN(SELECT match_id, inning_team, SUM(runs_scored) AS powerplay_runs
                            FROM t20_innings
                            WHERE over < 6 
                            GROUP BY match_id, inning_team
                            ORDER BY powerplay_runs DESC
                            LIMIT 10) AS pow_ply ON tm.match_id=pow_ply.match_id;"""
            query_t20_2 = pd.read_sql_query(query,con=engine)
            st.dataframe(query_t20_2)
        if sl==quest["Q3"]:
            query = """SELECT tm.winner, COUNT(*) AS times_won
            FROM t20_summary tm
            JOIN (
                SELECT match_id, inning_team, COUNT(*) AS total_wickets_lost
                FROM t20_innings
                WHERE wicket_type != 'Not Out'
                GROUP BY match_id, inning_team
            ) AS wickets ON tm.match_id = wickets.match_id
            WHERE tm.winner = wickets.inning_team AND total_wickets_lost < 5
            GROUP BY tm.winner
            ORDER BY times_won DESC;"""
            query_t20_3 = pd.read_sql_query(query,con=engine)
            st.dataframe(query_t20_3)
        if sl==quest["Q4"]:
            query = """SELECT tm.season, tm.start_date, tm.team_1, tm.team_2, death_ov.inning_team, death_ov.death_overs_runs
                       FROM t20_summary tm
                       JOIN(SELECT match_id, inning_team, SUM(runs_scored) AS death_overs_runs
                       FROM t20_innings
                       WHERE over >= 15  
                       GROUP BY match_id, inning_team
                       ORDER BY death_overs_runs DESC
                       LIMIT 5) AS death_ov ON tm.match_id=death_ov.match_id;"""
            query_t20_4 = pd.read_sql_query(query,con=engine)
            st.dataframe(query_t20_4)
        if sl==quest["Q5"]:
            query = """SELECT tm.season, tm.start_date, tm.team_1, tm.team_2, worst_ec.bowler, worst_ec.runs_conceded
                       FROM t20_SUmmary tm
                       JOIN(SELECT match_id, bowler, SUM(total_runs) AS runs_conceded
                       FROM t20_innings
                       GROUP BY match_id, bowler
                       ORDER BY runs_conceded DESC
                       LIMIT 10) AS worst_ec on tm.match_id = worst_ec.match_id;"""
            query_t20_5 = pd.read_sql_query(query,con=engine)
            st.dataframe(query_t20_5)
        if sl==quest["Q6"]:
            query = """SELECT tm.season, tm.start_date, tm.team_1, tm.team_2, consec_dot.bowler, consec_dot.dot_balls
                       FROM t20_SUmmary tm
                       JOIN(SELECT match_id, bowler, COUNT(*) AS dot_balls
                            FROM t20_innings
                            WHERE runs_scored = 0 AND extras = 0 
                            GROUP BY match_id, bowler
                            ORDER BY dot_balls DESC
                            LIMIT 10) AS consec_dot ON tm.match_id=consec_dot.match_id;"""
            query_t20_6 = pd.read_sql_query(query,con=engine)
            st.dataframe(query_t20_6)
            
    with tab4:
        quest = {
                 "Q1":"List all the winners of the Test, ODI and T20 matches.",
                 "Q2":"Which are the top 10 teams that have won most matches in all the three formats?"}
        sl = st.selectbox("Select a query",tuple(quest.values()),index=None)
        if sl==quest["Q1"]:
            query1 = pd.read_sql_query('''select match_type, team_1, team_2, winner 
                              from Test_Summary
                              union all
                              select match_type, team_1, team_2, winner 
                              from ODI_Summary
                              union all
                              select match_type, team_1, team_2, winner 
                              from T20_Summary''',con=engine)
            st.dataframe(query1)
        if sl==quest["Q2"]:
            query2 = '''select winner, count(*) as total_wins
            from (
                  select winner from test_summary
                  union all
                  select winner from odi_summary
                  union all
                  select winner from t20_Summary
                  ) AS all_matches
            where winner != 'No Result'
            GROUP BY winner
            ORDER BY total_wins DESC limit 10;'''
            query_2 = pd.read_sql_query(query2,con=engine)
            st.dataframe(query_2)
            
if selected=="Data Visualization (EDA)":
    chart = [f"Chart {i}" for i in range(1,11)]
    ch = st.selectbox("Select a chart for visualization",tuple(chart),index=None)
    if ch=="Chart 1":
        matches_won = pd.concat([test_summary,odi_summary,t20_summary],axis=0)
        matches_won = matches_won[matches_won.winner!='No Result']
        match = pd.DataFrame(matches_won.groupby('winner')['winner'].count())
        match = match.rename(columns={'winner':'count'})
        match.reset_index(inplace=True)
        match = match.sort_values(by='count',ascending=False)
        match.reset_index(drop=True,inplace=True)
        match = match[0:10]
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(data=match,x='count',y='winner',hue='winner',palette='rocket',ax=ax)
        ax.set_title("Top 10 most successful teams in all formats")
        st.pyplot(fig)
    if ch=="Chart 2":
        # Create a figure
        fig = plt.figure(figsize=(12, 10))

        # Test Matches Histogram (Top-Left)
        ax1 = fig.add_subplot(2, 2, 1)  # First row, first column
        sns.histplot(test_innings["runs_scored"], bins=20, kde=True, color="blue", ax=ax1)
        ax1.set_title("Runs Distribution in Test Matches")
        ax1.set_xlabel("Runs Scored")
        ax1.set_ylabel("Frequency")

        # ODI Matches Histogram (Top-Right)
        ax2 = fig.add_subplot(2, 2, 2)  # First row, second column
        sns.histplot(odi_innings["runs_scored"], bins=20, kde=True, color="green", ax=ax2)
        ax2.set_title("Runs Distribution in ODI Matches")
        ax2.set_xlabel("Runs Scored")
        ax2.set_ylabel("Frequency")

        # T20 Matches Histogram (Bottom-Center, spanning both columns)
        ax3 = fig.add_subplot(2, 1, 2)  # Second row, spans full width
        sns.histplot(t20_innings["runs_scored"], bins=20, kde=True, color="red", ax=ax3)
        ax3.set_title("Runs Distribution in T20 Matches")
        ax3.set_xlabel("Runs Scored")
        ax3.set_ylabel("Frequency")

        # Adjust layout
        plt.tight_layout()
        st.pyplot(fig)
    if ch=="Chart 3":
        fig = plt.figure(figsize=(12, 10))
        # Plot for T20 Matches
        ax1 = fig.add_subplot(2, 2, 1)
        sns.lineplot(x=t20_innings["over"], y=t20_innings["runs_scored"], color="blue", ax=ax1)
        ax1.set_title("Runs Scored per Over in T20 Matches")
        ax1.set_xlabel("Over Number")
        ax1.set_ylabel("Runs Scored")

        # Plot for ODI Matches
        ax2 = fig.add_subplot(2, 2, 2)
        sns.lineplot(x=odi_innings["over"], y=odi_innings["runs_scored"], color="green", ax=ax2)
        ax2.set_title("Runs Scored per Over in ODI Matches")
        ax2.set_xlabel("Over Number")
        ax2.set_ylabel("Runs Scored")

        # Plot for Test Matches
        ax3 = fig.add_subplot(2, 1, 2)
        sns.lineplot(x=test_innings["over"], y=test_innings["runs_scored"], color="red", ax=ax3)
        ax3.set_title("Runs Scored per Over in Test Matches")
        ax3.set_xlabel("Over Number")
        ax3.set_ylabel("Runs Scored")

        plt.tight_layout()
        st.pyplot(fig)
    if ch=="Chart 4":
        fig,ax = plt.subplots(figsize=(12, 6))
        test_sumup = test_summary[test_summary.winner!='No Result']
        sns.countplot(x=test_sumup["toss_decision"], hue=test_sumup["winner"], palette="coolwarm",ax=ax)
        ax.set_title("Win % Based on Toss Decision in Test Matches")
        ax.set_xlabel("Toss Decision")
        ax.set_ylabel("Total Wins")
        ax.legend(title="Winning Team")
        st.pyplot(fig)
    if ch=="Chart 5":
        fig,ax = plt.subplots(figsize=(10, 6))
        sns.scatterplot(x=odi_innings["ball_number"], y=odi_innings["runs_scored"], alpha=0.5, color="green",ax=ax)
        ax.set_title("Balls Taken vs. Runs Scored in ODI Matches")
        ax.set_xlabel("Balls Faced")
        ax.set_ylabel("Runs Scored")
        st.pyplot(fig)
    if ch=="Chart 6":
        top_scorers = odi_innings.groupby("batsman")["runs_scored"].sum().reset_index()
        top_scorers = top_scorers.sort_values("runs_scored", ascending=False).head(10)

        fig = plt.figure(figsize=(12, 10))
        ax1 = fig.add_subplot(2, 2, 1)
        sns.barplot(x=top_scorers["runs_scored"], y=top_scorers["batsman"],hue=top_scorers["batsman"], palette="viridis",ax=ax1)
        ax1.set_title("Top 10 Run Scorers in ODI Matches")
        ax1.set_xlabel("Total Runs")
        ax1.set_ylabel("Batsman")

        top_scorers_t20 = t20_innings.groupby("batsman")["runs_scored"].sum().reset_index()
        top_scorers_t20 = top_scorers_t20.sort_values("runs_scored", ascending=False).head(10)
        ax2 = fig.add_subplot(2, 2, 2)
        sns.barplot(x=top_scorers_t20["runs_scored"], y=top_scorers_t20["batsman"],hue=top_scorers_t20["batsman"], palette="coolwarm",ax=ax2)
        ax2.set_title("Top 10 Run Scorers in T20 Matches")
        ax2.set_xlabel("Total Runs")
        ax2.set_ylabel("Batsman")

        top_scorers_test = test_innings.groupby("batsman")["runs_scored"].sum().reset_index()
        top_scorers_test = top_scorers_test.sort_values("runs_scored", ascending=False).head(10)
        ax3 = fig.add_subplot(2, 1, 2)
        sns.barplot(x=top_scorers_test["runs_scored"], y=top_scorers_test["batsman"],hue=top_scorers_test["batsman"], palette="Set2",ax=ax3)
        ax3.set_title("Top 10 Run Scorers in Test Matches")
        ax3.set_xlabel("Total Runs")
        ax3.set_ylabel("Batsman")

        plt.tight_layout()
        st.pyplot(fig)
    if ch=="Chart 7":
        # Filter different phases
        df_t20_powerplay = t20_innings[t20_innings["over"] <= 6]
        df_t20_middle = t20_innings[(t20_innings["over"] >= 6) & (t20_innings["over"] <= 16)]
        df_t20_death = t20_innings[t20_innings["over"] >= 16]

        fig, ax = plt.subplots(figsize=(12, 6))

        # Plot each phase separately
        sns.lineplot(x=df_t20_powerplay["over"], y=df_t20_powerplay["runs_scored"], label="Powerplay (0-6)", color="blue", marker="o",ax=ax)
        sns.lineplot(x=df_t20_middle["over"], y=df_t20_middle["runs_scored"], label="Middle Overs (6-15)", color="green", marker="o",ax=ax)
        sns.lineplot(x=df_t20_death["over"], y=df_t20_death["runs_scored"], label="Death Overs (16-20)", color="red", marker="o",ax=ax)

        # Titles and labels
        ax.set_title("Strike Rate Across Different Phases in T20s")
        ax.set_xlabel("Over Number")
        ax.set_ylabel("Runs Scored")
        ax.legend()
        st.pyplot(fig)
    if ch=="Chart 9":
        test_wickets = test_innings[test_innings['wicket_type']!='Not Out']
        top_bowlers_test = test_wickets["bowler"].value_counts().head(10)

        odi_wickets = odi_innings[odi_innings['wicket_type']!='Not Out']
        top_bowlers_odi = odi_wickets["bowler"].value_counts().head(10)

        t20_wickets = t20_innings[t20_innings['wicket_type']!='Not Out']
        top_bowlers_t20 = t20_wickets["bowler"].value_counts().head(10)

        fig = plt.figure(figsize=(12, 10))
        ax1 = fig.add_subplot(2, 2, 1)
        sns.barplot(x=top_bowlers_test.values,y=top_bowlers_test.index,hue=top_bowlers_test.index,palette='terrain_r',ax=ax1)
        ax1.set_xlabel('Total wickets')
        ax1.set_ylabel('Bowler')
        ax1.set_title('Top 10 Wicket Takers in Test')

        ax2 = fig.add_subplot(2, 2, 2)
        sns.barplot(x=top_bowlers_odi.values,y=top_bowlers_odi.index,hue=top_bowlers_odi.index,palette='deep',ax=ax2)
        ax2.set_xlabel('Total wickets')
        ax2.set_ylabel('Bowler')
        ax2.set_title('Top 10 Wicket Takers in ODI')

        ax3 = fig.add_subplot(2, 1, 2)
        sns.barplot(x=top_bowlers_t20.values,y=top_bowlers_t20.index,hue=top_bowlers_t20.index,palette='muted',ax=ax3)
        ax3.set_xlabel('Total wickets')
        ax3.set_ylabel('Bowler')
        ax3.set_title('Top 10 Wicket Takers in T20')

        plt.tight_layout()
        st.pyplot(fig)
    if ch=="Chart 8":
        # Create a 'wickets_lost' column: 1 if wicket_type is NOT "not out", else 0
        t20_innings["wickets_lost"] = (t20_innings["wicket_type"] != "Not Out").astype(int)
        test_innings["wickets_lost"] = (test_innings["wicket_type"] != "Not Out").astype(int)

        # Aggregate total runs and total wickets per over
        df_wickets_per_over_t20 = t20_innings.groupby("over").agg(
            total_runs=("runs_scored", "sum"),
            total_wickets=("wickets_lost", "sum")
        ).reset_index()

        df_wickets_per_over_test = test_innings.groupby("over").agg(
            total_runs=("runs_scored", "sum"),
            total_wickets=("wickets_lost", "sum")
        ).reset_index()

        # Scatter plot with aggregated values
        fig, ax = plt.subplots(2, 2, figsize=(10,8))
        sns.scatterplot(
            x=df_wickets_per_over_t20["total_runs"], 
            y=df_wickets_per_over_t20["total_wickets"], 
            hue=df_wickets_per_over_t20["over"], 
            palette="viridis",
            ax = ax[0,0]
        )
        ax[0,0].set_title("Runs vs. Wickets Lost per Over in T20")
        ax[0,0].set_xlabel("Total Runs Scored")
        ax[0,0].set_ylabel("Total Wickets Lost")
        ax[0,0].legend(title="Over Number")

        sns.scatterplot(
            x=df_wickets_per_over_test["total_runs"], 
            y=df_wickets_per_over_test["total_wickets"], 
            hue=df_wickets_per_over_test["over"], 
            palette="magma",
            ax = ax[0,1]
        )
        ax[0,1].set_title("Runs vs. Wickets Lost per Over in Test")
        ax[0,1].set_xlabel("Total Runs Scored")
        ax[0,1].set_ylabel("Total Wickets Lost")
        ax[0,1].legend(title="Over Number")

        fig.delaxes(ax[1,0])
        fig.delaxes(ax[1,1])

        plt.tight_layout()
        st.pyplot(fig)
    if ch=="Chart 10":
        test_worst = test_summary[test_summary.winner!='No Result'].groupby('winner').agg(wins=("winner","count"))
        test_worst.reset_index(inplace=True)
        test_worst = test_worst.sort_values(by='wins')
        test_worst = test_worst.head()
        test_worst.reset_index(drop=True,inplace=True)

        odi_worst = odi_summary[odi_summary.winner!='No Result'].groupby('winner').agg(wins=("winner","count"))
        odi_worst.reset_index(inplace=True)
        odi_worst = odi_worst.sort_values(by='wins')
        odi_worst = odi_worst.head()
        odi_worst.reset_index(drop=True,inplace=True)

        t20_worst = t20_summary[t20_summary.winner!='No Result'].groupby('winner').agg(wins=("winner","count"))
        t20_worst.reset_index(inplace=True)
        t20_worst = t20_worst.sort_values(by='wins')
        t20_worst = t20_worst.head(10)
        t20_worst.reset_index(drop=True,inplace=True)

        fig = plt.figure(figsize=(12, 10))
        ax1 = fig.add_subplot(2, 2, 1)
        ax1.bar(test_worst['winner'],test_worst['wins'],color='green')
        ax1.set_title("Top 5 Poorly Performing Teams - Test")
        ax1.set_xlabel("Teams")
        ax1.set_ylabel("Matches Won")
        ax1.tick_params(axis='x', rotation=45)

        ax2 = fig.add_subplot(2, 2, 2)
        ax2.bar(odi_worst['winner'],odi_worst['wins'],color='red')
        ax2.set_title("Top 5 Poorly Performing Teams - ODI")
        ax2.set_xlabel("Teams")
        ax2.set_ylabel("Matches Won")
        ax2.tick_params(axis='x', rotation=45)

        ax3 = fig.add_subplot(2, 1, 2)
        ax3.bar(t20_worst['winner'],t20_worst['wins'],color='blue')
        ax3.set_title("Top 10 Poorly Performing Teams - T20")
        ax3.set_xlabel("Teams")
        ax3.set_ylabel("Matches Won")
        ax3.tick_params(axis='x', rotation=45)

        plt.tight_layout()
        st.pyplot(fig)
        
            

        
        
        
        
        
            
        
        



