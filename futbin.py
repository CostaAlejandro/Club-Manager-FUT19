import requests
from datos import plataforma

def getPrecio(name, id):
	player_ids = {name: id}
	for (name,id) in player_ids.items():
		r = requests.get('https://www.futbin.com/19/playerPrices?player={0}'.format(id))
		data = r.json()
		price = data[format(id)]["prices"][plataforma]["LCPrice"]
		return price

def getMinPrecio(name, id):
	player_ids = {name: id}
	for (name,id) in player_ids.items():
		r = requests.get('https://www.futbin.com/19/playerPrices?player={0}'.format(id))
		data = r.json()
		price = data[format(id)]["prices"][plataforma]["MinPrice"]
		return price