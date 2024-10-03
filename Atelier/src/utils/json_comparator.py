import logging
from typing import Dict, Any, List, Optional


class JsonComparator:
    def compare_match_data(self, old_data: Dict[str, Any], new_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            if not isinstance(old_data, dict) or not isinstance(new_data, dict):
                logging.error(f"Invalid data type: old_data is {type(old_data)}, new_data is {type(new_data)}")
                return None

            changes = {}
            old_aces_data = old_data.get('aces_data', {})
            new_aces_data = new_data.get('aces_data', {})

            # Check for added or removed markets
            all_markets = set(old_aces_data.keys()) | set(new_aces_data.keys())
            for market in all_markets:
                old_market = old_aces_data.get(market)
                new_market = new_aces_data.get(market)

                if old_market != new_market:
                    market_changes = self.compare_selections(old_market, new_market)
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

    def compare_selections(self, old_selections: Any, new_selections: Any) -> List[Dict[str, Any]]:
        try:
            changes = []

            if old_selections == "None" and new_selections != "None":
                return [{'change': 'Market added', 'new_value': new_selections}]
            elif old_selections != "None" and new_selections == "None":
                return [{'change': 'Market removed', 'old_value': old_selections}]

            if not isinstance(old_selections, list) or not isinstance(new_selections, list):
                return [{'change': 'Market format changed', 'old_value': old_selections, 'new_value': new_selections}]

            for new_selection in new_selections:
                if not isinstance(new_selection, dict):
                    continue
                old_selection = next(
                    (s for s in old_selections if isinstance(s, dict) and s.get('name') == new_selection.get('name')),
                    None)

                if old_selection is None:
                    changes.append({
                        'change': 'Selection added',
                        'name': new_selection.get('name'),
                        'new_odds': new_selection.get('odds')
                    })
                elif old_selection.get('odds') != new_selection.get('odds'):
                    changes.append({
                        'change': 'Odds changed',
                        'name': new_selection.get('name'),
                        'old_odds': old_selection.get('odds'),
                        'new_odds': new_selection.get('odds')
                    })

            for old_selection in old_selections:
                if isinstance(old_selection, dict) and not any(
                        s.get('name') == old_selection.get('name') for s in new_selections if isinstance(s, dict)):
                    changes.append({
                        'change': 'Selection removed',
                        'name': old_selection.get('name'),
                        'old_odds': old_selection.get('odds')
                    })

            return changes
        except Exception as e:
            logging.error(f"Error in compare_selections: {str(e)}")
            return []