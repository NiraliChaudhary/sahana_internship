import pandas as pd


file_path = "IPL.xls"

def load_data(fp: str) -> pd.DataFrame:
    return pd.read_excel(fp)

def close_matches_by_year(df: pd.DataFrame) -> pd.DataFrame:

    tied_match = df["Winner"] == "Match tied"

    low_balls_remaining = df["Balls_Remaining"] <= 3

    close_wicket_win = ((df["Winning_Team"] == "Chasing") & (df["Win_Type"] == "wicket") & (df["Winning_Margin"] <= 1))

    close_run_loss = ((df["Winning_Team"] == "FirstBatting") & (df["Win_Type"] == "run") & (df["Winning_Margin"] <= 5))

    close_match = (tied_match | low_balls_remaining | close_wicket_win | close_run_loss)

    close_match_df = df[close_match]

    result = (close_match_df.groupby("Year")["Match_Number"].count().reset_index(name="No_of_Close_Matches"))

    return result

def batting_first_win_percent(df: pd.DataFrame) -> pd.DataFrame:

    batting_first_wins = (df[df["Winning_Team"] == "FirstBatting"].groupby("Winner").size())

    team_wins = df["Winner"].value_counts()

    top_teams = team_wins.head(4)

    percent_first_bat = (batting_first_wins.reindex(top_teams.index,fill_value=0) / top_teams) * 100

    res = percent_first_bat.reset_index()

    res.columns = ["Team","Percent_Won_Batting_First"]

    return res

def main() -> None:
    df = load_data(file_path)

    cm = close_matches_by_year(df)
    print(cm)

    batting_percent = batting_first_win_percent(df)

    print(batting_percent)

if __name__ == "__main__":
    main()