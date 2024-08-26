import os
import requests

class T14Manager():
    def get_all_items(self):
        url = f'{os.getenv("T14_API_BASE_URL")}/items/fitment?page=1'
        token = os.getenv("TURN14_ACCESS_TOKEN")
        headers = {
            'Authorization': f'Bearer {token}'
        }       
        try:
            res = requests.get(url,headers=headers)
            res.raise_for_status()  
            return res.json().get('data')
        except requests.exceptions.RequestException as e:
            print(f"Error fetching items: {e}")
            return None  

    def get_single_item_data(self,item_id):
        url = f'{os.getenv("T14_API_BASE_URL")}/items/data/{item_id}'
        token = os.getenv("TURN14_ACCESS_TOKEN")
        headers = {
            'Authorization': f'Bearer {token}'
        }       
        try:
            res = requests.get(url,headers=headers)
            res.raise_for_status()  
            return res.json().get('data')[0]
        except requests.exceptions.RequestException as e:
            raise e

    def get_single_item_price(self,item_id):
        url = f'{os.getenv("T14_API_BASE_URL")}/pricing/{item_id}'
        token = os.getenv("TURN14_ACCESS_TOKEN")
        headers = {
            'Authorization': f'Bearer {token}'
        }       

        try:
            res = requests.get(url, headers=headers)
            res.raise_for_status()  
            pricelist = res.json().get('data').get('attributes').get('pricelists')

            # Check for Retail, then MAP, then Jobber
            retail_price = next((p['price'] for p in pricelist if p['name'] == "Retail"), None)
            if retail_price is not None:
                return str(retail_price)
            
            map_price = next((p['price'] for p in pricelist if p['name'] == "MAP"), None)
            if map_price is not None:
                return str(map_price)
            
            jobber_price = next((p['price'] for p in pricelist if p['name'] == "Jobber"), None)
            return str(jobber_price)

        except requests.exceptions.RequestException as e:
            raise e

    def refresh_token(self):
        client_id=os.getenv('TURN14_CLIENT_ID')
        client_secret=os.getenv('TURN14_CLIENT_SECRET')

        url = f'{os.getenv("T14_API_BASE_URL")}/token'

        body={
          "grant_type": "client_credentials",
          "client_id": client_id,
          "client_secret": client_secret
        }

        headers={
            "Content-Type": "application/json",
        }
        res=requests.post(url,headers=headers,json=body)
        print(res.json())



