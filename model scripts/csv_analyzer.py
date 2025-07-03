# csv_analyzer.py

import pandas as pd

def analyze_match_csv(csv_file='match_data.csv'):
    df = pd.read_csv(csv_file)

    analysis = {}

    for player in df['player'].unique():
        player_data = df[df['player'] == player]
        for shot in ['forehand', 'backhand']:
            total = player_data[player_data['shot_type'] == shot].shape[0]
            successful = player_data[
                (player_data['shot_type'] == shot) & (player_data['success'] == 1)
            ].shape[0]
            success_rate = (successful / total) * 100 if total > 0 else 0

            if player not in analysis:
                analysis[player] = {}

            analysis[player][shot] = round(success_rate, 1)

    # Print Feedback
    for player, stats in analysis.items():
        print(f"\n🔍 {player.upper()} Analysis:")
        for shot, rate in stats.items():
            if rate >= 70:
                print(f"✅ {shot.capitalize()} Success: {rate}%")
            elif rate >= 40:
                print(f"⚠️ {shot.capitalize()} Success: {rate}% — Needs improvement")
            else:
                print(f"❌ {shot.capitalize()} Success: {rate}% — Major weakness")
