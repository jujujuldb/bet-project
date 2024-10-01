import logging

class JsonComparator:
    def compare_match_data(self, old_data, new_data):
        try:
            if not isinstance(old_data, dict) or not isinstance(new_data, dict):
                logging.error(f"Invalid data type: old_data is {type(old_data)}, new_data is {type(new_data)}")
                return None

            changes = {}
            for market, new_selections in new_data.get('aces_data', {}).items():
                if market in old_data.get('aces_data', {}):
                    market_changes = self.compare_selections(old_data['aces_data'][market], new_selections)
                    if market_changes:
                        changes[market] = market_changes

            if changes:
                return {
                    'match_id': new_data.get('match_id'),
                    'joueur_1': new_data.get('contestants', {}).get('joueur 1'),
                    'joueur_2': new_data.get('contestants', {}).get('joueur 2'),
                    'changes': changes
                }
        except Exception as e:
            logging.error(f"Error in compare_match_data: {str(e)}")
        return None

    def compare_selections(self, old_selections, new_selections):
        try:
            changes = []
            for new_selection in new_selections:
                if not isinstance(new_selection, dict):
                    continue
                old_selection = next((s for s in old_selections if isinstance(s, dict) and s.get('name') == new_selection.get('name')), None)
                if old_selection and old_selection.get('odds') != new_selection.get('odds'):
                    changes.append({
                        'name': new_selection.get('name'),
                        'old_odds': old_selection.get('odds'),
                        'new_odds': new_selection.get('odds')
                    })
            return changes
        except Exception as e:
            logging.error(f"Error in compare_selections: {str(e)}")
            return []