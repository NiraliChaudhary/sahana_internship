import pandas as pd

df = pd.read_excel('IPL.xls')

df['bat2_wkts_remain'] =10-df['Bat_Second_15_ov_wkts_lost']
df['run_needed'] = df['Bat_First_15_ov_score']-df['Bat_Second_15_ov_score']

df['bat1_run_last5'] = df["Bat_First_20_ov_score"]-df['Bat_First_15_ov_score']

#1
result_a = df[(df['bat2_wkts_remain'] >= 6) & (df['run_needed'] <= 3) & (df["run_needed"] > 0) & (df["Winning_Team"] != df["Team_Batting_Second"])
][['Match_Number', 'Date', 'Team_Batting_Second', 'Team_Batting_First']].reset_index(drop=True)

result_b = df[
    (df['Bat_First_15_ov_wkts_lost'] <= 2) &
    (df['bat1_run_last5'] < 25) &
    (df["bat1_run_last5"] > 0)
][['Match_Number', 'Date', 'Team_Batting_First', 'Team_Batting_Second']].reset_index(drop=True)

print("=" * 80)
print("IPL ODD SCORING PATTERNS ANALYSIS")
print("=" * 80)

print("\n(a) Favorable position at 15 overs but LOST:")
print(f"    Found: {len(result_a)} matches\n")
print(result_a.to_string(index=False))

print("\n\n(b) Strong start (≤2 wkts lost) but weak finish (<25 runs in last 5):")
print(f"    Found: {len(result_b)} matches\n")
print(result_b.to_string(index=False))