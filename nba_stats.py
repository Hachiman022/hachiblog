import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class NBAStatsAnalyzer:
    def __init__(self, api_key: str):
        self.base_url = "https://www.balldontlie.io/api/v1"
        self.headers = {
            'Authorization': f'Bearer {api_key}'
        }
        self.current_season = datetime.now().year
    
    def search_player(self, player_name: str) -> List[Dict]:
        """Search for a player by name."""
        url = f"{self.base_url}/players"
        params = {"search": player_name}
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            if response.status_code == 200:
                return response.json()["data"]
            elif response.status_code == 401:
                raise Exception("Invalid API key. Please check your API key.")
            elif response.status_code == 429:
                raise Exception("Rate limit exceeded. Please try again later.")
            else:
                raise Exception(f"API request failed with status code {response.status_code}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")

    def get_player_stats(self, player_id: int, season: Optional[int] = None) -> Dict:
        """Get player statistics for a specific season."""
        if season is None:
            season = self.current_season
            
        url = f"{self.base_url}/season_averages"
        params = {
            "player_ids[]": player_id,
            "season": season
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            if response.status_code == 200:
                return response.json()["data"]
            else:
                raise Exception(f"Failed to get player stats. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get player stats: {str(e)}")

    def calculate_advanced_stats(self, basic_stats: Dict) -> Dict:
        """Calculate advanced statistics from basic statistics."""
        try:
            advanced_stats = {}
            
            # True Shooting Percentage (TS%)
            if basic_stats['fga'] > 0 and basic_stats['fta'] > 0:
                advanced_stats['ts_pct'] = (basic_stats['pts'] / (2 * (basic_stats['fga'] + 0.44 * basic_stats['fta']))) * 100
            else:
                advanced_stats['ts_pct'] = 0
            
            # Usage Rate (estimated)
            if basic_stats['min'] > 0:
                advanced_stats['usage_rate'] = ((basic_stats['fga'] + 0.44 * basic_stats['fta'] + basic_stats['turnover']) / basic_stats['min']) * 100
            else:
                advanced_stats['usage_rate'] = 0
            
            # Assist to Turnover Ratio
            if basic_stats['turnover'] > 0:
                advanced_stats['ast_to_ratio'] = basic_stats['ast'] / basic_stats['turnover']
            else:
                advanced_stats['ast_to_ratio'] = basic_stats['ast']
            
            # Points per Shot Attempt
            if basic_stats['fga'] > 0:
                advanced_stats['pts_per_shot'] = basic_stats['pts'] / basic_stats['fga']
            else:
                advanced_stats['pts_per_shot'] = 0
            
            return advanced_stats
            
        except KeyError as e:
            raise Exception(f"Missing required statistics: {str(e)}")

    def display_player_stats(self, player_name: str, season: Optional[int] = None):
        """Display player statistics in a formatted way."""
        try:
            players = self.search_player(player_name)
            
            if not players:
                print(f"No players found matching '{player_name}'")
                return
            
            for player in players:
                player_id = player['id']
                stats = self.get_player_stats(player_id, season)
                
                print(f"\nPlayer: {player['first_name']} {player['last_name']}")
                print(f"Team: {player['team']['full_name']}")
                print(f"Position: {player['position']}")
                
                if stats:
                    stats = stats[0]
                    stats_df = pd.DataFrame([{
                        'Games Played': stats['games_played'],
                        'Minutes': round(stats['min'], 1),
                        'Points': round(stats['pts'], 1),
                        'Rebounds': round(stats['reb'], 1),
                        'Assists': round(stats['ast'], 1),
                        'Steals': round(stats['stl'], 1),
                        'Blocks': round(stats['blk'], 1),
                        'FG%': f"{round(stats['fg_pct'] * 100, 1)}%",
                        '3P%': f"{round(stats['fg3_pct'] * 100, 1)}%",
                        'FT%': f"{round(stats['ft_pct'] * 100, 1)}%"
                    }])
                    
                    print("\nSeason Averages:")
                    print(stats_df.to_string(index=False))
                    
                    # Calculate and display advanced stats
                    advanced_stats = self.calculate_advanced_stats(stats)
                    print("\nAdvanced Statistics:")
                    for stat, value in advanced_stats.items():
                        print(f"{stat.replace('_', ' ').title()}: {value:.2f}")
                else:
                    print(f"No statistics found for season {season}")
                    
        except Exception as e:
            print(f"Error: {str(e)}")

def main():
    try:
        api_key = input("Please enter your balldontlie API key: ").strip()
        analyzer = NBAStatsAnalyzer(api_key)
        
        while True:
            print("\nNBA Stats Analyzer")
            print("1. View Player Stats")
            print("2. Calculate Advanced Stats")
            print("3. Quit")
            
            choice = input("\nSelect an option (1-3): ").strip()
            
            if choice == '3':
                break
                
            player_name = input("Enter player name: ").strip()
            
            if choice == '1':
                season = input("Enter season year (press Enter for current season): ").strip()
                season = int(season) if season else None
                analyzer.display_player_stats(player_name, season)
            elif choice == '2':
                analyzer.display_player_stats(player_name)
                
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
