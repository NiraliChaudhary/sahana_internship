# import pandas as pd
#
#
# df = pd.read_excel('IPL.xls')
#
# print("="*100)
# print("Total Matches by year and winner type(2008-2015")
# print("="*100)
#
# q1_res = []
# years = sorted(df['Year'].unique())
#
# for y in years:
#     year_data = df[df['Year'] == y]
#     total_matches = len(year_data)
#
#     bat_first_wins = len(year_data[year_data['Winning_Team'] == 'FirstBatting'])
#
#     chase_wins = len(year_data[year_data['Winning_Team'] == 'Chasing'])
#
#     tied_matches = len(year_data[year_data['Winning_Team'] == 'Match Tied'])
#
#     q1_res.append({
#         'Year':y,
#         'Total Matches':total_matches,
#         'Batting First Won':bat_first_wins,
#         'Chasing Won':chase_wins,
#         'Match Tied':tied_matches
#     })
#
# q1_df = pd.DataFrame(q1_res)
# print("\n" + q1_df.to_string(index=False))
#
# print("Statistics :")
# print(f"Total Matches (2008-2015) : {q1_df['Total Matches'].sum()}")
# print(f"Total Chasing Wins: {q1_df['Chasing Won'].sum()}")
# print(f"Total Tied Matches: {q1_df['Match Tied'].sum()}")


#==============================================================================

import pandas as pd

file_path = "EASY_IPL.xlsx"
SheetName = "All_IPL_Data"

def load_data(fp: str,sn:str) -> pd.DataFrame:
    return pd.read_excel(fp,sheet_name=sn)

def year_wise_match_stats(df: pd.DataFrame) -> pd.DataFrame:
    result = (
        df.groupby("Year").agg(
            total_matches = ("Match_Number","count"),
            batting_first_wins = ("Winning_Team",lambda x: (x == "FirstBatting").sum()),
            chasing_wins=("Winning_Team",lambda x: (x=="Chasing").sum()),
            tied_matches=("Winning_Team",lambda x:(x == "Match Tied").sum())
        ).reset_index()
    )

    return result

def venue_with_most_matches(df:pd.DataFrame) -> pd.Series:
    return df["Venue"].value_counts().head(1)

def highest_batting_first_run_rate(df: pd.DataFrame) -> pd.Series:
    return df.loc[df["Bat_First_Run_Rate"].idxmax()]

def main() -> None:
    df = load_data(file_path,SheetName)

    print("==========Year Wise Match Statistics=========")

    yearly_stats = year_wise_match_stats(df)
    print(yearly_stats.to_string(index=False))

    #2=========
    print("=======Venue with maximum matches=========")
    top_venue = venue_with_most_matches(df)
    print(top_venue)

    #3==========
    print("=======Highest batting first run rate=======")

    highest_rr = highest_batting_first_run_rate(df)

    print(highest_rr[["Match_Number","Team_Batting_First","Bat_First_Runs_Scored","Bat_First_Overs_Consumed","Bat_First_Run_Rate"]])


if __name__ == "__main__":
    main()