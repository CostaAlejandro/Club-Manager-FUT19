#!/usr/bin/python
# -*- coding: utf-8 -*-

import fut
import os
import urllib, json
import time
from rarityPlayers import rarityCards
from futbin import getPrecio, getMinPrecio
from redondear import formatearPrecio, precioPuja
from datos import email, password, respuesta, plataforma

url = "https://www.easports.com/fifa/ultimate-team/api/fut/item?jsonParamObject="

def menu():
	print (u"Tienes un total de {} monedas. ¿Qué deseas hacer?: ".format(session.keepalive()))
	print ("""1. Buscar jugadores
2. Ver mi lista de transferibles
3. Salir""")

def limpiarLista():
	try:
		session.tradepileClear()
		print u"\nLista de transferibles limpia. Ya no hay ningún artículo vendido. "
		dormir(2)
	except:
		print u"\nNo se puede limpiar la lista, no hay artículos para limpiar. Volviendo al menú... "
		dormir(2)

def relist():
	try:
		session.relist()
		print u"\nArtículos añadidos correctamente. "
		dormir(2)
	except:
		print u"\nNo hay artículos vendidos. Volviendo al menú... "
		dormir(2)

def dormir(x):
	print "......................................................................."
	time.sleep(x)

def buscarJugador():
	listaCount = len(session.tradepile())
	listaTotal = session.tradepile_size
	if listaCount < listaTotal:
		jugador = raw_input("Introduce el nombre del jugador a buscar: ")
		fifaurl = url + '{"name":"' + jugador + '"}'
		response = urllib.urlopen(fifaurl)
		busqueda = json.loads(response.read())
		print u"Estamos realizando una búsqueda sobre " + jugador
		totalEncontrados = busqueda["count"]
		totalEncontradosF = format(totalEncontrados)
		print("Se han encontrado " + totalEncontradosF + " jugadores con el nombre buscado. ")
		contadorJugadores = 0
		if totalEncontrados > 0:
			selJugador = []
			for x in range (totalEncontrados):
				rating = busqueda["items"][x]["rating"]
				rarity = busqueda["items"][x]["rarityId"]
				if format(rarity) != "18":
					contadorJugadores = contadorJugadores + 1
					rarity = rarityCards.get(format(rarity))
					idJugador = busqueda["items"][x]["id"]
					print (format(contadorJugadores) + ". " + busqueda["items"][x]["firstName"] + " " + busqueda["items"][x]["lastName"] + " (" + \
						  busqueda["items"][x]["position"]+ " " + format(rating) + " - " +busqueda["items"][x]["quality"] + " " + \
						  rarity + ") " + busqueda["items"][x]["club"]["name"] + " - " + busqueda["items"][x]["league"]["name"]).encode('utf8')
					selJugador.append(idJugador)
		else:
			print "No se han encontrado jugadores. Vuelve a probar. "
			dormir(2)
			menu()
		buscar = input("Selecciona la carta a buscar. ")
		buscar = buscar - 1
		print "Has seleccionado al jugador " + format(buscar+1)
		jugadoresAComprar = input("¿Cuantos jugadores vas a querer comprar? ")
		precioJugador = getPrecio(jugador, selJugador[buscar])
		precioJugador = formatearPrecio(precioJugador)
		print (busqueda["items"][buscar]["name"] + " segun Futbin, vale " + format(precioJugador) + " monedas.").encode('utf8')
		porcentaje = input("¿A que porcentaje del precio vas a querer comprar el jugador? 100 = precio marcado por futbin ")
		precioPujar = precioPuja(precioJugador, porcentaje)
		precioMinimo = getMinPrecio(jugador, selJugador[buscar])
		precioMinimo = int(precioMinimo)
		precioPujar = int(precioPujar)
		comprados = 0
		if precioPujar < precioMinimo:
			precioPujar = precioMinimo
		x = 0
		#print contadorJ


		while comprados < jugadoresAComprar:
			x = x + 1
			listSearchedPlayer = session.search(ctype="player", defId=selJugador[buscar], max_price=precioPujar)
			tradeId = listSearchedPlayer[0]["tradeId"]
			segundosRestantes = listSearchedPlayer[0]["expires"]
			current = listSearchedPlayer[0]["currentBid"]
			current = int(current)

			print "Intento n. " + format(x) + " - puja actual: " + format(current)
			if current < precioPujar:
				print "Realizando puja por " + format(precioPujar) + " monedas quedando " + format(segundosRestantes) + " segundos para que acabe la puja"
				session.bid(tradeId,precioPujar,True)
				print "Se ha pujado correctamente..."
				print "Esperando el tiempo restante que le queda a la puja... (" + format(segundosRestantes) + " segundos)"
				dormir(segundosRestantes)
				print "Esperando 30 segundos para dar tiempo a que se actualice el estado del tradeo."
				dormir(30)
				estadoJugador = session.tradeStatus(format(tradeId))
				for estado in estadoJugador:
					bidState = estado.get("bidState")
					tradeState = estado.get("tradeState")
					idJugador = estado.get("id")
					if bidState == "highest" and tradeState == "closed":
						comprados = comprados + 1
						print ("Se ha comprado correctamente a " + busqueda["items"][buscar]["name"] + " a " + format(precioPujar) + " monedas").encode('utf8')
						try:
							session.sendToTradepile(idJugador)
							print "Jugador enviado a la lista de transferibles"
						except:
							print u"Error al enviar el jugador a la lista de transferibles. Quizá esté llena."
					else:
						print "No se ha comprado al jugador, vamos a intentar pujar otro... "
			else:
				print "El precio de la puja actual supera al precio a pujar. Buscando otro jugador"
			print "\nEn espera 10 segundos para parecer normal."
			dormir(10)
		menu()
	else:
		print "Lista de transferibles llena. "

def mandarClub():
	totalArticulosLista = len(session.tradepile())
	if totalArticulosLista > 0:
		contadorJugadores = 0
		print "\n"
		selJugador = []
		for player in session.tradepile():
			estado = player.get("tradeState")
			estado = format(estado)
			if estado != "active" or estado != "closed":
				contadorJugadores = contadorJugadores + 1
				playerId = player.get("resourceId")
				playerId = str(playerId)
				fifaurl = url + '{"id":"' + playerId + '"}'
				response = urllib.urlopen(fifaurl)
				playerInfo = json.loads(response.read())
				rating = playerInfo["items"][0]["rating"]
				rarity = playerInfo["items"][0]["rarityId"]
				rarity = rarityCards.get(format(rarity))
				idJugador = player.get("id")
				selJugador.append(idJugador)
				print (format(contadorJugadores) + ". " + playerInfo["items"][0]["name"] + " (" + \
					  playerInfo["items"][0]["position"]+ " " + format(rating) + " - " +playerInfo["items"][0]["quality"] + " " + rarity + ") ").encode('utf8')
		respuesta = input("\n¿Qué jugador deseas mandar al club? ")
		respuesta = respuesta - 1
		print "Has seleccionado al jugador " + format(respuesta + 1)
		id = selJugador[respuesta]
		try:
			session.sendToClub(id)
			print "Jugador envíado al club correctamente... "
		except:
			print "No se ha podido enviar el jugador al club. Seguramente ya lo tengas en el club. "

def listaTransferibles():
	totalArticulosLista = len(session.tradepile())
	print "\nViendo la lista de transferibles"
	print "\nTienes {} articulos en la lista de transferibles.".format(totalArticulosLista)
	print u"\nEl tamaño de tu lista de transferibles es " + format(session.tradepile_size)
	if totalArticulosLista > 0:
		contadorJugadores = 0
		selJugador = []
		for player in session.tradepile():
			contadorJugadores = contadorJugadores + 1
			estado = player.get("tradeState")
			monedas = ""
			if estado == "active":
				estado = "EN VENTA"
			elif estado == "expired":
				estado = "NO VENDIDO"
			elif estado == "closed":
				estado = "VENDIDO"
				vendido = player.get("currentBid")
				monedas = " POR " + format(vendido) + " MONEDAS"
			else:
				estado = ""
			playerId = player.get("resourceId")
			playerId = str(playerId)
			fifaurl = url + '{"id":"' + playerId + '"}'
			response = urllib.urlopen(fifaurl)
			playerInfo = json.loads(response.read())
			rating = playerInfo["items"][0]["rating"]
			rarity = playerInfo["items"][0]["rarityId"]
			rarity = rarityCards.get(format(rarity))
			print (format(contadorJugadores) + ". " + playerInfo["items"][0]["name"] + " (" + \
				  playerInfo["items"][0]["position"]+ " " + format(rating) + " - " +playerInfo["items"][0]["quality"] + " " + rarity + ") " + estado).encode('utf8')
		print "\n"
		
#EMPIEZA

print (u"Iniciando sesión...")

session = fut.Core(email, password, respuesta, plataforma)

while True:
	os.system("cls")
	menu()
	ans = raw_input("Elige una opción para continuar: ").encode('utf8')
	if ans=="1":
		listaCount = len(session.tradepile())
		listaTotal = session.tradepile_size
		if listaCount == listaTotal:
			print "Lista de transferibles llena. Intentando limpiar... "
			limpiarLista()
			dormir(2)
			listaCount = len(session.tradepile())
			print "La lista sigue llena, espera a que se vendan los jugadores... "
			menu()
		buscarJugador()
		ans=raw_input("""¿Qué quieres hacer ahora?
1. Buscar otro jugador. 
2. Volver al menu. """)
		if ans == "1":
			buscarJugador()
		elif ans=="2":
			menu()
	elif ans=="2":
		listaTransferibles()
		ans=raw_input("""¿Qué quieres hacer ahora?
1. Vender un jugador en el mercado.  
2. Venta rápida de un jugador. 
3. Enviar al club un jugador. 
4. Limpiar lista de transferibles. 
5. Volver a vender un jugador. 
6. Ver articulos sin asignar. 
7. Vender todos los artículos.
8. Volver al menú. """).encode('utf8')
		if ans == "1":
			totalArticulosLista = len(session.tradepile())
			listaTransferibles = session.tradepile()
			if totalArticulosLista > 0:
				idFutbin = []
				listaJugadores = []
				contarJugadores = 0
				totalGanado = 0
				totalGastado = 0
				totalBeneficios = 0
				print "\n"
				otroJugador = False
				for jugador in listaTransferibles:
					estado = jugador.get("tradeState")
					if estado != "active":
					#	print jugador
						idBuscar = jugador.get("resourceId")
						id = jugador.get("id")
						idBuscar = str(idBuscar)
						fifaurl = url + '{"id":"' + idBuscar + '"}'
						response = urllib.urlopen(fifaurl)
						playerInfo = json.loads(response.read())
						rating = playerInfo["items"][0]["rating"]
						rarity = playerInfo["items"][0]["rarityId"]
						rarity = rarityCards.get(format(rarity))
						idJugador = playerInfo["items"][0]["id"]
						precioJugador = getPrecio("buscar", idJugador)
						precioJugador = formatearPrecio(precioJugador)
						precioCompra = jugador.get("lastSalePrice")
						contarJugadores = contarJugadores + 1
						totalGastado = totalGastado + precioCompra
						totalGanado = totalGanado + precioJugador
						print (format(contarJugadores) + ". " + playerInfo["items"][0]["name"] + " (" + \
							  playerInfo["items"][0]["position"]+ " " + format(rating) + " - " +playerInfo["items"][0]["quality"] + " " + rarity + ")	VALOR COMPRA: " + format(precioCompra) + "VALOR ACTUAL: " + format(precioJugador) + " monedas").encode('utf8')
						listaJugadores.append(id)
				for x in range (contarJugadores):
					buscar = input("\n¿Qué jugador quieres poner a la venta en el mercado? ")
					buscar = buscar - 1
					print "Has seleccionado al " + format(buscar + 1)
 					jugadorVender = listaJugadores[buscar]
					precioVender = input("¿A qué precio deseas poner el jugador a la venta? ")
					precioCompraYa = input("¿Y precio de compra ya?")
					try:
						session.sell(jugadorVender,precioVender,precioCompraYa,3600,True)
						print "Jugador puesto a la venta a " + format(precioVender) + " monedas y " + format(precioCompraYa) + " en compra ya "
					except:
						print "\nHa ocurrido un problema a la hora de poner el jugador en venta. "
					otro = raw_input("\n¿Quieres vender otro jugador? (S/N)")
					if otro == "N" or otro == "n":
						otroJugador = True
					if otroJugador == True:
						break
				totalBeneficios = totalGanado - totalGastado
				print "Habiendo gastado " + format(totalGastado) + " monedas, tu lista de transferibles tiene un valor de " + format(totalGanado) + " monedas, lo que significa que tienes unas ganancias potenciales de " + format(totalBeneficios) + " monedas"
				if len(listaJugadores) < 1:
					print "No hay jugadores disponibles para vender. Volviendo al menú..."
					dormir(2)
			else:
				print "\nNo hay jugadores en la lista de transferibles. "
				print "Volviendo al menú..."
				dormir(2)
				menu()
		elif ans=="2":
			totalArticulosLista = len(session.tradepile())
			listaTransferibles = session.tradepile()
			if totalArticulosLista > 0:
				listaJugadores = []
				contarJugadores = 0
				print "\n"
				otroJugador = False
				for jugador in listaTransferibles:
					estado = jugador.get("tradeState")
					idBuscar = jugador.get("resourceId")
					id = jugador.get("id")
					fifaurl = url + '{"id":"' + format(idBuscar) + '"}'
					response = urllib.urlopen(fifaurl)
					playerInfo = json.loads(response.read())
					rating = playerInfo["items"][0]["rating"]
					rarity = playerInfo["items"][0]["rarityId"]
					rarity = rarityCards.get(format(rarity))
					if estado != "closed" or estado != "active":
						contarJugadores = contarJugadores + 1
						print (format(contarJugadores) + ". " + playerInfo["items"][0]["name"] + \
							  " (" +playerInfo["items"][0]["position"]+ " " + format(rating) + " - " + \
							  playerInfo["items"][0]["quality"] + " " + rarity + ")").encode('utf8')
						listaJugadores.append(id)
			else:
				print "No hay jugadores para vender, volviendo al menú"
				break
			for x in range (contarJugadores):
				buscar = input("\n¿Qué jugador quieres descartar? ")
				buscar = buscar - 1
				print "Has seleccionado al " + format(buscar +1)
				jugadorVender = listaJugadores[buscar]
				try:
					session.quickSell(jugadorVender)
					print "Jugador vendido"
				except:
					print "\nEl jugador no se ha vendido "
				otro = raw_input("\n¿Quieres vender otro jugador? (S/N)")
				if otro == "N" or otro == "n":
					otroJugador = True
				if otroJugador == True:
					break
		elif ans=="3":
			mandarClub()
			dormir(2)
		elif ans=="4":
			limpiarLista()
			dormir(2)
		elif ans=="5":
			relist()
			dormir(2)
		elif ans=="6":
			sinAsignar = session.watchlist()
			listaJugadores = []
			contarJugadores = 0
			print "\n"
			for articulo in sinAsignar:
				bidState = articulo.get("bidState")
				tradeId = articulo.get("tradeId")
				if bidState == "highest":
					estado = articulo.get("tradeState")
					if estado == "closed":
						idBuscar = articulo.get("resourceId")
						id = articulo.get("id")
						fifaurl = url + '{"id":"' + format(idBuscar) + '"}'
						response = urllib.urlopen(fifaurl)
						playerInfo = json.loads(response.read())
						rating = playerInfo["items"][0]["rating"]
						rarity = playerInfo["items"][0]["rarityId"]
						rarity = rarityCards.get(format(rarity))
						contarJugadores = contarJugadores + 1
						print (format(contarJugadores) + ". " + playerInfo["items"][0]["name"] + " (" + \
							playerInfo["items"][0]["position"] + " " + format(rating) + " - " + \
							playerInfo["items"][0]["quality"] + " " + rarity + ")").encode('utf8')
						listaJugadores.append(id)
				else:
					session.watchlistDelete(tradeId)

			otroJugador = False
			if contarJugadores>0:
				for x in range(contarJugadores):
					buscar = input("\n¿Qué jugador quieres enviar a la lista de transferibles? ")
					buscar = buscar - 1
					print "Has seleccionado al " + format(buscar + 1)
					jugadorEnviar = listaJugadores[buscar]
					try:
						session.sendToTradepile(jugadorEnviar)
						print "Jugador envíado correctamente"
					except:
						print u"\nHa habido un error: El jugador no se ha envíado. Quizá tienes la lista llena. "
					otro = raw_input("\n¿Quieres vender otro jugador? (S/N)")
					if otro == "N" or otro == "n":
						otroJugador = True
					if otroJugador == True:
						break
			else:
				print "No hay jugadores para añadir a la lista de transferibles, volviendo al menú"
				dormir(2)
		elif ans=="7":
			totalArticulosLista = len(session.tradepile())
			listaTransferibles = session.tradepile()
			if totalArticulosLista > 0:
				listaJugadores = []
				listaPrecios = []
				listaNombres = []
				x = 0
				contarJugadores = 0
				print "\n"
				for jugador in listaTransferibles:
					estado = jugador.get("tradeState")
					if estado != "active":
						idBuscar = jugador.get("resourceId")
						id = jugador.get("id")
						idBuscar = str(idBuscar)
						contarJugadores = contarJugadores + 1
						fifaurl = url + '{"id":"' + idBuscar + '"}'
						response = urllib.urlopen(fifaurl)
						playerInfo = json.loads(response.read())
						idJugador = playerInfo["items"][0]["id"]
						nombre = (playerInfo["items"][0]["name"]).encode('utf8')
						listaNombres.append(nombre)
						listaJugadores.append(id)
						listaPrecios.append(idJugador)
				for x in range(contarJugadores):
					nombreJugador = listaNombres[x]
					jugadorVender = listaJugadores[x]
					precioJugador = getPrecio("buscar", listaPrecios[x])
					precioJugador = formatearPrecio(precioJugador)
					vender = raw_input ("¿Quieres vender a " + nombreJugador + " por " + format(precioJugador) + " monedas? S/N" ).encode('utf8')
					if vender == "S" or vender == "s":
						try:
							session.sell(jugadorVender, precioJugador-100, precioJugador+100, 3600, True)
							print listaNombres[x] + " puesto a la venta a " + format(precioJugador-100) + " monedas y " + format(
								precioJugador+100) + " en compra ya "
						except:
							print "\nHa ocurrido un problema a la hora de poner los jugadores en venta. "
					dormir(10)
				if len(listaJugadores) < 1:
					print "No hay jugadores disponibles para vender. Volviendo al menú..."
					dormir(2)
			else:
				print "\nNo hay jugadores en la lista de transferibles. "
				print "Volviendo al menú..."
				dormir(2)
				menu()
		elif ans=="8":
			menu()
	elif ans=="3":
		print "\nAdios!!"
		break
	else:
		"\nNo reconozco lo que has dicho"
