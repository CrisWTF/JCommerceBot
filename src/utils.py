from json import loads, dumps
from requests import post
from pymongo import MongoClient
client = MongoClient("mongodb+srv://CrisWTF:%2FCristianagama1@cluster0.uz5sa.mongodb.net/?retryWrites=true&w=majority")
collection_users = client.get_database('JCommerce').get_collection('Users')

async def update_one(id_dictionary, data_dictionary):
    try:
        collection_users.update_one(id_dictionary,{'$set':data_dictionary})
        return True
    except:
        return False

async def find_all():
    users = None
    try:
        users = collection_users.find()
        return users
    except:
        return users

def discount(price):
    return price - ((price * 30)/100)

async def groupPayment(id_user, amount, Retry = True, Token=""):
    user = collection_users.find_one({'id':str(344287947337629697)})
    response = post('https://groups.roblox.com/v1/groups/14907345/payouts',
    data=dumps({
        "PayoutType": "FixedAmount",
        "Recipients": [
        {
            "recipientId": id_user,
            "recipientType": "User",
            "amount": amount
        }
        ]
    }),
    headers={
    "Content-Type":"application/json",
    "X-CSRF-TOKEN" : Token,
    "Cookie":f".ROBLOSECURITY={user['security']}"
    })
    if response.status_code == 403:
        try:
            JSON = loads(response.text)
            ResponseCode = JSON["errors"][0]["code"]
            if ResponseCode == 0: # And Roblox response is 0...
                if Retry == True: # If retry is enabled...
                    return await groupPayment(id_user, amount, Retry=False, Token=response.headers["x-csrf-token"]) # Re-do the request, but this time, with the `x-csrf-token` supplied as well.
        except:
            return response
    return response, Token

async def vipPayment(id_user, id_universe, amount, Retry = True, Token=""):
    user = collection_users.find_one({'id':str(344287947337629697)})
    response = post(f'https://games.roblox.com/v1/games/vip-servers/{id_universe}',
    data=dumps({
        'name':'Payment JCommerce',
        'expectedPrice':amount
    }),
    headers={
    "Content-Type":"application/json",
    "X-CSRF-TOKEN" : Token,
    "Cookie":f".ROBLOSECURITY={user['security']}"
    })
    if response.status_code == 403:
        try:
            JSON = loads(response.text)
            ResponseCode = JSON["errors"][0]["code"]
            if ResponseCode == 0: # And Roblox response is 0...
                if Retry == True: # If retry is enabled...
                    return await vipPayment(id_user, id_universe, amount, Retry=False, Token=response.headers["x-csrf-token"]) # Re-do the request, but this time, with the `x-csrf-token` supplied as well.
        except:
            return response
    return response, Token

'''
HACER UN FETCH A LA BASE DE DATOS MONGO
url = "https://data.mongodb-api.com/app/data-zpnlj/endpoint/data/beta/action/findOne"
payload = json.dumps({
"collection": "Seller",
"database": "JCommercie",
"dataSource": "Cluster0",
"projection": {
    "_id": 1
}
})
headers = {
'Content-Type': 'application/json',
'Access-Control-Request-Headers': '*',
'api-key': 'LtA3ubNot8FxxSbOp6w90dYAwfHuCBxKboTQ5Ev1lQf4PqZ7Ta0PwzznIgHBCugb'
}
response = requests.request("POST", url, headers=headers, data=payload)
print(response.text)
---------------------------------------------------------------------------------------------------------El de abajo es para la api de webhooks discord
import requests
import json
data = json.dumps({
    'embeds':[{
        'title':'Donation',
        'description':'Una donacion ha llegado',
        'color':10181046
    }]
})
request = requests.post('https://discord.com/api/v10/webhooks/986493239215398992/ZsmJjTPzZErN7aIf8kCdX5UIJ6-UE3p9OhdP4N49MglGR5YZ-rrJdD6FJnCehUlmdmP_',data=data, headers={"Content-Type":"application/json"})
print(request.status_code)

'''
