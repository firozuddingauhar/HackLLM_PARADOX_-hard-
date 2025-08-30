import json
import os
import re
import csv

# The standard ownership of supply centers at the beginning of a game in 1901.
INITIAL_OWNERSHIP_1901 = {
  "Par": "France", "Mar": "France", "Bre": "France",
  "Smy": "Turkey", "Con": "Turkey", "Ank": "Turkey",
  "Lon": "England", "Lvp": "England", "Edi": "England",
  "Nap": "Italy", "Ven": "Italy", "Rom": "Italy",
  "Mun": "Germany", "Kie": "Germany", "Ber": "Germany",
  "War": "Russia", "Mos": "Russia", "Stp": "Russia", "Sev": "Russia",
  "Tri": "Austria", "Vie": "Austria", "Bud": "Austria"
}

def update_ownership(current_ownership, moves_data):
    """Updates the ownership of supply centers based on a turn's moves."""
    new_ownership = current_ownership.copy()
    supply_centers = set(current_ownership.keys())
    
    for country, orders in moves_data.get('orders', {}).items():
        for _, order_details in orders.items():
            if order_details.get('type') == 'MOVE' and order_details.get('result') == 'SUCCEEDS':
                target_province = order_details.get('to')
                if target_province in supply_centers:
                    new_ownership[target_province] = country
    return new_ownership

def generate_strategic_commentary(game_data, previous_territories):
    """Generates semantically rich commentary paragraphs."""
    commentaries = {}
    
    for country, orders in game_data.get('orders', {}).items():
        attacks = {'succeeded': [], 'failed': []}
        expansions = []
        holds = []
        supports = {'offensive': [], 'defensive': [], 'failed': []}
        builds = []
        disbands = []
        convoys = []

        for unit_loc, details in orders.items():
            order_type = details.get('type')
            result = details.get('result')

            if order_type == 'MOVE':
                target = details.get('to')
                owner = previous_territories.get(target, 'neutral')
                if owner != 'neutral' and owner != country:
                    (attacks['succeeded'] if result == 'SUCCEEDS' else attacks['failed']).append(f"{target} (from {owner})")
                elif owner == 'neutral' and result == 'SUCCEEDS':
                    expansions.append(target)
            elif order_type == 'SUPPORT':
                supp_from = details.get('from')
                supp_owner = previous_territories.get(supp_from, country)
                if result != 'SUCCEEDS':
                    supports['failed'].append(f"an action at {details.get('to') or supp_from}")
                elif supp_owner == country:
                    supports['defensive'].append(f"its own unit at {supp_from}")
                else:
                    supports['offensive'].append(f"{supp_owner}'s efforts")
            elif order_type == 'HOLD':
                holds.append(unit_loc)
            elif order_type == 'CONVOY':
                convoys.append(f"an army from {details.get('from')} to {details.get('to')}")
            elif order_type == 'BUILD':
                unit_type = "an Army" if details.get('unit_type') == 'A' else "a Fleet"
                builds.append(f"{unit_type} in {unit_loc}")
            elif order_type == 'DISBAND':
                disbands.append(unit_loc)

        themes = []
        if any(attacks.values()): themes.append("aggression")
        if expansions: themes.append("expansion")
        if holds or supports['defensive']: themes.append("consolidation")
        if builds: themes.append("reinforcement")
        if disbands: themes.append("a reduction of forces")
        
        paragraph_parts = [f"In this turn, {country}'s strategy involved {', '.join(themes) or 'holding positions'}."]
        
        if attacks['succeeded']:
            paragraph_parts.append(f"It launched successful assaults, capturing {', '.join(attacks['succeeded'])}.")
        if attacks['failed']:
            paragraph_parts.append(f"However, its attempted attacks on {', '.join(attacks['failed'])} were repelled.")
        if expansions:
            paragraph_parts.append(f"The nation expanded into neutral territories, claiming {', '.join(expansions)}.")
        if supports['offensive']:
            paragraph_parts.append(f"It projected power by providing key support for {', '.join(set(supports['offensive']))}.")
        if convoys:
            paragraph_parts.append(f"Logistically, it executed important convoys, including moving {', '.join(convoys)}.")
        if builds:
            paragraph_parts.append(f"During the build phase, it strengthened its military by creating {', '.join(builds)}.")
        if disbands:
            paragraph_parts.append(f"It was forced to disband units at {', '.join(disbands)}.")
            
        commentaries[country] = " ".join(paragraph_parts)
            
    return commentaries

def create_dataset_from_directory(directory_path, output_csv_path):
    """
    Processes all game files in a directory to create a structured dataset.
    """
    all_files = [f for f in os.listdir(directory_path) if f.endswith('.json')]
    
    # Using regex to parse filenames and prepare for sorting
    file_details = []
    season_order = {'spring': 0, 'fall': 1, 'winter': 2}
    for filename in all_files:
        match = re.match(r"DiplomacyGame(\d+)_(\d+)_(\w+)\.json", filename)
        if match:
            game_id, year, season = match.groups()
            file_details.append({
                'game_id': int(game_id),
                'year': int(year),
                'season_order': season_order.get(season.lower(), 99),
                'season_name': season,
                'path': os.path.join(directory_path, filename)
            })

    # Sorting files by game, then year, then season to process in order
    sorted_files = sorted(file_details, key=lambda x: (x['game_id'], x['year'], x['season_order']))
    
    game_states = {} # Stores the latest territory ownership for each game_id
    final_dataset = []

    for file_info in sorted_files:
        game_id = file_info['game_id']
        
        # Getting the territory ownership from the previous turn for this game
        # If it's the first turn, use the initial 1901 layout
        previous_territories = game_states.get(game_id, INITIAL_OWNERSHIP_1901)
        
        try:
            with open(file_info['path'], 'r') as f:
                game_data = json.load(f)
        except Exception as e:
            print(f"Skipping file {file_info['path']} due to error: {e}")
            continue

        # Generating the commentary paragraphs for the current turn
        commentaries = generate_strategic_commentary(game_data, previous_territories)
        
        for player, commentary in commentaries.items():
            final_dataset.append({
                'game_id': game_id,
                'year': file_info['year'],
                'season': file_info['season_name'],
                'player': player,
                'commentary': commentary
            })
        
        # If the turn was a Fall turn, update the ownership state for the next turn
        if file_info['season_name'].lower() == 'fall':
            new_ownership = update_ownership(previous_territories, game_data)
            game_states[game_id] = new_ownership

    # Writing the final dataset to a CSV file
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['game_id', 'year', 'season', 'player', 'commentary'])
        writer.writeheader()
        writer.writerows(final_dataset)
        
    print(f"Dataset successfully created with {len(final_dataset)} records.")
    print(f"Output saved to: {output_csv_path}")


if __name__ == "__main__":
    INPUT_DIRECTORY = "moves"
    OUTPUT_CSV = "commentary.csv"

    create_dataset_from_directory(INPUT_DIRECTORY, OUTPUT_CSV)