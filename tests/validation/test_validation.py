import sys
import json
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from app.models.betting_adviser import BettingAdviser

SOCCER_JSON = 'data/soccer_matches.json'
BASKET_JSON = 'data/basketball_games.json'

def load_data(path):
    """Load match data from JSON file."""
    full_path = os.path.join(os.path.dirname(__file__), path)
    with open(full_path, encoding='utf-8') as f:
        return json.load(f)

def evaluate(matches, sport):
    """Evaluate the accuracy of predictions for a sport."""
    adviser = BettingAdviser(sport)
    correct = 0
    total_processed = 0
    
    for m in matches:
        try:
            actual = m['result']  # 'home_win' or 'away_win'
            
            # Filter out metadata fields and create facts list
            excluded_fields = {'result', 'home_team', 'away_team', 'date'}
            facts_dict = {k: v for k, v in m.items() if k not in excluded_fields}
            
            # Process all facts at once to get final recommendation
            facts_list = [facts_dict]  # Wrap in list as expected by the system
            
            res = adviser.get_betting_advice(facts_list)
            
            if 'message' not in res:
                print(f"Warning: No message in response for {m.get('home_team', 'Unknown')} vs {m.get('away_team', 'Unknown')}")
                continue
                
            msg = res['message']
            
            # Determine prediction based on message content
            pred = 'segura' if 'segura' in msg else 'arriesgada'
            
            # Check if prediction matches actual result
            # segura = safe bet = expect home win
            # arriesgada = risky bet = expect away win or upset
            if (pred == 'segura' and actual == 'home_win') or (pred == 'arriesgada' and actual != 'home_win'):
                correct += 1
                
            total_processed += 1
            
            # Debug output for first few matches
            if total_processed <= 3:
                print(f"Debug: {m.get('home_team', 'Home')} vs {m.get('away_team', 'Away')}")
                print(f"  Prediction: {pred}, Actual: {actual}, Correct: {(pred == 'segura' and actual == 'home_win') or (pred == 'arriesgada' and actual != 'home_win')}")
                print(f"  Message: {msg[:100]}...")
                
        except Exception as e:
            print(f"Error processing match {m.get('home_team', 'Unknown')} vs {m.get('away_team', 'Unknown')}: {e}")
            continue
    
    if total_processed == 0:
        return 0, 0, 0.0
        
    accuracy = (correct / total_processed) * 100
    return total_processed, correct, accuracy

def main():
    """Main validation function."""
    try:
        print("Loading data...")
        soccer = load_data(SOCCER_JSON)
        basket = load_data(BASKET_JSON)
        
        print("Evaluating soccer matches...")
        soc_total, soc_corr, soc_rate = evaluate(soccer, 'soccer')
        
        print("Evaluating basketball games...")
        bb_total, bb_corr, bb_rate = evaluate(basket, 'basketball')

        print("\n" + "="*40)
        print("=== INFORME DE VALIDACIÓN ===")
        print("="*40)
        print(f"Fútbol     : {soc_corr}/{soc_total} aciertos -> {soc_rate:.2f}%")
        print(f"Baloncesto : {bb_corr}/{bb_total} aciertos -> {bb_rate:.2f}%")
        print("="*40)
        
        # Overall statistics
        total_matches = soc_total + bb_total
        total_correct = soc_corr + bb_corr
        overall_rate = (total_correct / total_matches * 100) if total_matches > 0 else 0
        
        print(f"Total      : {total_correct}/{total_matches} aciertos -> {overall_rate:.2f}%")
        
    except FileNotFoundError as e:
        print(f"Error: Could not find data file. {e}")
        print("Make sure the data files exist in the correct location.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()