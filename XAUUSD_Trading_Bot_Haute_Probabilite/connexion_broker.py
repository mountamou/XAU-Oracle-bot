# connexion_broker.py - Exemple de connexion a un broker reel
# A adapter selon votre broker (OANDA, IG, Interactive Brokers, etc.)

import requests

class OANDAConnector:
    """Exemple de connexion API OANDA"""

    def __init__(self, api_key, account_id, practice=True):
        self.api_key = api_key
        self.account_id = account_id
        self.base_url = "https://api-fxpractice.oanda.com/v3" if practice else "https://api-fxtrade.oanda.com/v3"

    def get_price(self, instrument="XAU_USD"):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        r = requests.get(
            f"{self.base_url}/accounts/{self.account_id}/pricing?instruments={instrument}",
            headers=headers
        )
        data = r.json()
        price = data['prices'][0]
        return {
            'open': float(price['closeoutBid']),
            'high': float(price['closeoutAsk']),
            'low': float(price['closeoutBid']),
            'close': float(price['closeoutBid']),
            'timestamp': price['time']
        }

    def place_order(self, instrument, units, stop_loss, take_profit):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        order = {
            "order": {
                "type": "MARKET",
                "instrument": instrument,
                "units": str(units),
                "stopLossOnFill": {"price": str(stop_loss)},
                "takeProfitOnFill": {"price": str(take_profit)}
            }
        }
        r = requests.post(
            f"{self.base_url}/accounts/{self.account_id}/orders",
            headers=headers,
            json=order
        )
        return r.json()
