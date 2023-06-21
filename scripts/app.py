import csv
import datetime
import pandas as pd
from enum import Enum


class Result(Enum):
    HomeWin = 1
    Draw = 2
    AwayWin = 3


class Games:
    def __init__(self, comp, home_team, away_team, date, h_prob, d_prob, a_prob, xg, d_odds, h_score, a_score):
        self.Comp = comp
        self.HomeTeam = home_team
        self.AwayTeam = away_team
        self.Date = date
        self.HProb = h_prob
        self.DProb = d_prob
        self.AProb = a_prob
        self.MinHAProb = None
        self.XG = xg
        self.DOdds = d_odds
        self.HScore = h_score
        self.AScore = a_score
        self.Result = None


def main():
    csv_file_path = "./ForebetDatabase.csv"

    csv_data = pd.read_csv(csv_file_path)
    all_games = []

    for _, row in csv_data.iterrows():
        date = datetime.datetime.strptime(row[3], "%d/%m/%Y %H:%M")
        game = Games(
            row[0],
            row[1],
            row[2],
            date,
            int(row[4]),
            int(row[5]),
            int(row[6]),
            float(row[7]),
            float(row[11]),
            int(row[13]),
            int(row[14])
        )
        all_games.append(game)

    for game in all_games:
        if game.HScore > game.AScore:
            game.Result = Result.HomeWin
        elif game.AScore > game.HScore:
            game.Result = Result.AwayWin
        else:
            game.Result = Result.Draw

    for game in all_games:
        game.MinHAProb = game.HProb if game.HProb < game.AProb else game.AProb

    min_draw_percent = 35
    prob_range = 2
    xg_range = 0.2
    min_combo_games_ratio = 1875
    min_odds = 2.9

    iterations = 0

    sim_start_date = datetime.datetime(2021, 1, 1)
    sim_end_date = datetime.datetime(2021, 1, 7)

    cumulative_rois = []

    while prob_range <= 5:
        while min_draw_percent <= 39:
            iterations += 1
            print(f"Iteration: {iterations} | MinDraw%: {min_draw_percent} | ProbRange: {prob_range} | xGRange: {xg_range} | SampleRatio: {min_combo_games_ratio}")

            date_in_play = sim_start_date
            daily_rois = []
            weekly_rois = []

            while date_in_play <= sim_end_date:
                sim_past_games = [g for g in all_games if g.Date < date_in_play - datetime.timedelta(days=1)]
                sim_play_games = [g for g in all_games if date_in_play <= g.Date < date_in_play + datetime.timedelta(days=1)]
                sim_total_past_games = len(sim_past_games)
                min_combo_games = sim_total_past_games / (min_combo_games_ratio * prob_range * xg_range)
                good_combos = []

                for past_game in sim_past_games:
                    ha_prob_max = past_game.MinHAProb + prob_range
                    ha_prob_min = past_game.MinHAProb - prob_range
                    d_prob_max = past_game.DProb + prob_range
                    d_prob_min = past_game.DProb - prob_range
                    xg_max = past_game.XG + xg_range
                    xg_min = past_game.XG - xg_range
                    combo_game_count = 0
                    combo_draw_count = 0

                    for combo_game in sim_past_games:
                        if (
                            ha_prob_min <= combo_game.MinHAProb <= ha_prob_max and
                            d_prob_min <= combo_game.DProb <= d_prob_max and
                            xg_min <= combo_game.XG <= xg_max
                        ):
                            combo_game_count += 1
                            if combo_game.Result == Result.Draw:
                                combo_draw_count += 1

                    combo_draw_percent = (combo_draw_count / combo_game_count) * 100 if combo_game_count > 0 else 0

                    if combo_game_count >= min_combo_games and combo_draw_percent >= min_draw_percent:
                        good_combos.append(past_game)

                tot_bet_games = 0
                tot_bet_draws = 0
                tot_bet_odd_games = 0
                tot_bet_odd_draws = 0
                tot_bet_min_odd_games = 0
                tot_bet_min_odd_draws = 0
                bank = 0
                min_odds_bank = 0

                for game in sim_play_games:
                    match_combo_count = 0

                    for good_combo in good_combos:
                        if (
                            match_combo_count > 0 or
                            not (good_combo.MinHAProb - prob_range <= game.MinHAProb <= good_combo.MinHAProb + prob_range) or
                            not (good_combo.DProb - prob_range <= game.DProb <= good_combo.DProb + prob_range) or
                            not (good_combo.XG - xg_range <= game.XG <= good_combo.XG + xg_range)
                        ):
                            break

                        match_combo_count += 1
                        tot_bet_games += 1

                        if game.Result == Result.Draw:
                            tot_bet_draws += 1

                        if game.DOdds > 0:
                            tot_bet_odd_games += 1

                            if game.Result == Result.Draw:
                                tot_bet_odd_draws += 1
                                bank += game.DOdds

                        if game.DOdds >= min_odds:
                            tot_bet_min_odd_games += 1

                            if game.Result == Result.Draw:
                                tot_bet_min_odd_draws += 1
                                min_odds_bank += game.DOdds

                draw_percent = (tot_bet_draws / tot_bet_games) * 100 if tot_bet_games > 0 else 0
                roi = bank / tot_bet_odd_games if tot_bet_odd_games > 0 else 0
                min_odds_roi = min_odds_bank / tot_bet_min_odd_games if tot_bet_min_odd_games > 0 else 0

                daily_rois.append({
                    "DateInPlay": date_in_play.strftime("%d/%m/%Y"),
                    "TotBetGames": tot_bet_games,
                    "TotBetDraws": tot_bet_draws,
                    "DrawPercent": draw_percent,
                    "TotBetOddGames": tot_bet_odd_games,
                    "TotBetOddDraws": tot_bet_odd_draws,
                    "TotBetMinOddGames": tot_bet_min_odd_games,
                    "TotBetMinOddDraws": tot_bet_min_odd_draws,
                    "Bank": bank,
                    "ROI": roi,
                    "MinOddsBank": min_odds_bank,
                    "MinOddsROI": min_odds_roi
                })

                past_week_roi = [p for p in daily_rois if date_in_play - datetime.timedelta(days=6) <= datetime.datetime.strptime(p["DateInPlay"], "%d/%m/%Y") < date_in_play + datetime.timedelta(days=1)]

                week_bet_games = sum(p["TotBetGames"] for p in past_week_roi)
                week_bet_draws = sum(p["TotBetDraws"] for p in past_week_roi)
                week_draw_percent = (week_bet_draws / week_bet_games) * 100 if week_bet_games > 0 else 0
                week_bet_odd_games = sum(p["TotBetOddGames"] for p in past_week_roi)
                week_bank = sum(p["Bank"] for p in past_week_roi)
                week_roi = week_bank / week_bet_odd_games if week_bet_odd_games > 0 else 0
                week_bet_min_odd_games = sum(p["TotBetMinOddGames"] for p in past_week_roi)
                week_min_odds_bank = sum(p["MinOddsBank"] for p in past_week_roi)
                week_min_odds_roi = week_min_odds_bank / week_bet_min_odd_games if week_bet_min_odd_games > 0 else 0

                cumulative_rois.append({
                    "DateInPlay": date_in_play.strftime("%d/%m/%Y"),
                    "TotBetGames": sum(p["TotBetGames"] for p in daily_rois),
                    "TotBetDraws": sum(p["TotBetDraws"] for p in daily_rois),
                    "DrawPercent": (sum(p["TotBetDraws"] for p in daily_rois) / sum(p["TotBetGames"] for p in daily_rois)) * 100 if sum(p["TotBetGames"] for p in daily_rois) > 0 else 0,
                    "TotBetOddGames": sum(p["TotBetOddGames"] for p in daily_rois),
                    "TotBetOddDraws": sum(p["TotBetOddDraws"] for p in daily_rois),
                    "TotBetMinOddGames": sum(p["TotBetMinOddGames"] for p in daily_rois),
                    "TotBetMinOddDraws": sum(p["TotBetMinOddDraws"] for p in daily_rois),
                    "Bank": sum(p["Bank"] for p in daily_rois),
                    "ROI": sum(p["Bank"] for p in daily_rois) / sum(p["TotBetOddGames"] for p in daily_rois) if sum(p["TotBetOddGames"] for p in daily_rois) > 0 else 0,
                    "MinOddsBank": sum(p["MinOddsBank"] for p in daily_rois),
                    "MinOddsROI": sum(p["MinOddsBank"] for p in daily_rois) / sum(p["TotBetMinOddGames"] for p in daily_rois) if sum(p["TotBetMinOddGames"] for p in daily_rois) > 0 else 0,
                })

                if date_in_play >= sim_start_date + datetime.timedelta(days=6):
                    weekly_rois.append({
                        "DateInPlay": date_in_play.strftime("%d/%m/%Y"),
                        "TotBetGames": week_bet_games,
                        "TotBetDraws": week_bet_draws,
                        "DrawPercent": week_draw_percent,
                        "TotBetOddGames": week_bet_odd_games,
                        "TotBetOddDraws": sum(p["TotBetOddDraws"] for p in past_week_roi),
                        "TotBetMinOddGames": week_bet_min_odd_games,
                        "TotBetMinOddDraws": sum(p["TotBetMinOddDraws"] for p in past_week_roi),
                        "Bank": week_bank,
                        "ROI": week_roi,
                        "MinOddsBank": week_min_odds_bank,
                        "MinOddsROI": week_min_odds_roi
                    })
                    print(f"{date_in_play.strftime('%d/%m/%Y')} Cumulative Daily - Matched Games: {cumulative_rois[-1]['TotBetGames']} | Draws: {cumulative_rois[-1]['DrawPercent']:.1f}% | With Odds: {cumulative_rois[-1]['TotBetOddGames']} | ROI: {cumulative_rois[-1]['ROI']:.2f} | Odds > {min_odds}: {cumulative_rois[-1]['TotBetMinOddGames']} | ROI: {cumulative_rois[-1]['MinOddsROI']:.2f} |")
                    print(f"{date_in_play.strftime('%d/%m/%Y')}           Weekly - Matched Games: {weekly_rois[-1]['TotBetGames']} | Draws: {weekly_rois[-1]['DrawPercent']:.1f}% | With Odds: {weekly_rois[-1]['TotBetOddGames']} | ROI: {weekly_rois[-1]['ROI']:.2f} | Odds > {min_odds}: {weekly_rois[-1]['TotBetMinOddGames']} | ROI: {weekly_rois[-1]['MinOddsROI']:.2f} |")
                else:
                    print(f"{date_in_play.strftime('%d/%m/%Y')} Cumulative Daily - Matched Games: {cumulative_rois[-1]['TotBetGames']} | Draws: {cumulative_rois[-1]['DrawPercent']:.1f}% | With Odds: {cumulative_rois[-1]['TotBetOddGames']} | ROI: {cumulative_rois[-1]['ROI']:.2f} | Odds > {min_odds}: {cumulative_rois[-1]['TotBetMinOddGames']} | ROI: {cumulative_rois[-1]['MinOddsROI']:.2f} |")

                date_in_play += datetime.timedelta(days=1)

            week_ave_bet_games = sum(p["TotBetGames"] for p in weekly_rois) / len(weekly_rois)
            week_ave_draw_percent = sum(p["DrawPercent"] for p in weekly_rois) / len(weekly_rois)
            week_ave_bet_odd_games = sum(p["TotBetOddGames"] for p in weekly_rois) / len(weekly_rois)
            week_ave_roi = sum(p["ROI"] for p in weekly_rois) / len(weekly_rois)
            week_ave_bet_min_odd_games = sum(p["TotBetMinOddGames"] for p in weekly_rois) / len(weekly_rois)
            week_ave_min_odds_roi = sum(p["MinOddsROI"] for p in weekly_rois) / len(weekly_rois)

            print("-----------------------------------------------------------------------------------------------------")
            print(f"Average Weekly - Matched Games: {week_ave_bet_games:.2f} | Draws: {week_ave_draw_percent:.1f}% | With Odds: {week_ave_bet_odd_games:.2f} | ROI: {week_ave_roi:.2f} | Odds > {min_odds}: {week_ave_bet_min_odd_games:.2f} | ROI: {week_ave_min_odds_roi:.2f} |")
            print("-----------------------------------------------------------------------------------------------------")

            min_draw_percent += 1
        prob_range += 1


if __name__ == "__main__":
    main()
