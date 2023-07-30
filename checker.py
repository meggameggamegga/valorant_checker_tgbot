import asyncio

# Остальной код
import json
from datetime import datetime

from valo_lib import Auth

import requests

class ClientAcc:
    def __init__(self,username:str=None,password:str=None):
        self.username = username
        self.password = password
        self.cookie = None
        self.access_token = None
        self.token_id = None
        self.entitlements_token = None
        self.puuid = None
        self.name = None
        self.tag =None
        self.region = None
        self.player_name = None

    async def autheticate(self):
        auth = Auth()
        authenticate = await auth.authenticate(self.username, self.password)
        #Если ответ произошел
        if not authenticate:
            return None
        else:
            if authenticate['auth'] == 'response':
                auth_data = authenticate['data']
                self.cookie = auth_data['cookie']['cookie']
                self.access_token = auth_data['access_token']
                self.token_id = auth_data['token_id']
                self.entitlements_token = await auth.get_entitlements_token(self.access_token)
                self.puuid, self.name, self.tag = await auth.get_userinfo(self.access_token)
                self.region = await auth.get_region(self.access_token, self.token_id)
                self.player_name = f'{self.name}#{self.tag}' if self.tag is not None and self.name is not None else 'no_username'
                print(self.puuid)
                return {'cookies':self.cookie,'access_token':self.access_token,'token_id':self.token_id,'entitlements_token':self.entitlements_token,
                        'puuid':self.puuid,'name':self.name,'tag':self.tag,'region':self.region,'player_name':self.player_name}
            else:
                return False

#---------------Получить нужные вещи-----------------#
    def get_items(self,item:str):
        headers = {
            "X-Riot-Entitlements-JWT": self.entitlements_token,
            "Authorization":f"Bearer {self.access_token}"
        }
        #Добавить список items скинов по которым надо сделать запроос
        request = requests.get(
            f'https://pd.{self.region}.a.pvp.net/store/v1/entitlements/{self.puuid}/{item}', #region,puuid,code_items
            headers=headers)
        return request.json()

    def get_store(self):
        headers = {
            "X-Riot-Entitlements-JWT": self.entitlements_token,
            "Authorization": f"Bearer {self.access_token}"
        }
        # Добавить список items скинов по которым надо сделать запроос
        request = requests.get(
            url=f'https://pd.eu.a.pvp.net/store/v2/storefront/{self.puuid}',  # region,puuid,code_items
            headers=headers)
        with open('store.json','w') as file:
            json.dump(request.json(),file,indent=4)
        return request.json()

    def get_mathes(self):
        headers = {
            'Content-Type': 'application/json',
            "X-Riot-Entitlements-JWT": self.entitlements_token,
            "Authorization": f"Bearer {self.access_token}"
        }
        # Получить баланс игрока
        request = requests.get(
            url=f'https://pd.{self.region}.a.pvp.net/match-history/v1/history/{self.puuid}',
            headers=headers)

        print(request.json())


    def get_my_account(self):
        headers = {
            'Content-Type':'application/json',
            "X-Riot-Entitlements-JWT": self.entitlements_token,
            "Authorization": f"Bearer {self.access_token}"
        }
        #Получить баланс игрока
        request = requests.get(
            url=f'https://pd.{self.region}.a.pvp.net/store/v1/wallet/{self.puuid}',
            headers=headers)
        VP = request.json()['Balances']['85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741']
        Kingdom = request.json()['Balances']['85ca954a-41f2-ce94-9b45-8ca3dd39a00d']
        RP = request.json()['Balances']['e59aa87c-4cbf-517a-5983-6e81511be9b7']


        #Получить ранг
        headers = {
            'X-Riot-ClientPlatform':'ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9',
            'X-Riot-ClientVersion': "release-07.01-shipping-28-925799",
            'X-Riot-Entitlements-JWT':self.entitlements_token,
            'Authorization': f'Bearer {self.access_token}'
        }
        request = requests.get(
            url=f'https://pd.{self.region}.a.pvp.net/mmr/v1/players/{self.puuid}',
            headers=headers)
        with open('account.json','w') as file:
            json.dump(request.json(),file,indent=4)
        try:
            rank =request.json()['QueueSkills']["competitive"]['SeasonalInfoBySeasonID']['0981a882-4e7d-371a-70c4-c3b4f46c504a']['Rank']#Seson ID mb change
        except:
            rank = request.json()['LatestCompetitiveUpdate']['TierAfterUpdate']
        print(rank)
        last_match = request.json()['LatestCompetitiveUpdate']['MatchStartTime']
        formatted_time = datetime.fromtimestamp(last_match / 1000).strftime('%Y-%m-%d %H:%M:%S')
        return {'VP':VP,'Kingdom':Kingdom,'RadiantPoints':RP,'Rank':rank,'last_match':formatted_time}


    async def start(self,items=None,store:bool=None,account:bool=None):
        if items:
            await self.autheticate()
            return self.get_items(items)
        elif store:
            await self.autheticate()
            return self.get_store()
        elif account:
            await self.autheticate()
            return self.get_my_account()

        else:
            return await self.autheticate()

