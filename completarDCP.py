#!/usr/bin/python
# -*- coding: utf-8 -*-

import fut
from datos import email, password, respuesta, plataforma
from bs4 import BeautifulSoup
import time
import requests
import re

futbin = "https://www.futbin.com"
futbinDcp = "/squad-building-challenges/ALL/"

print ("Iniciando sesion...")

session = fut.Core(email, password, respuesta, plataforma)

if plataforma == "xbox":
    precioPlataforma = "data-xone-price"
    plataformaFutbin = "xone"
    precioJugadorBuscar = "data-price-xbl"
elif plataforma == "ps":
    precioPlataforma = "data-ps-price"
    plataformaFutbin = "ps4"
    precioJugadorBuscar = "data-price-ps3"
elif plataforma=="pc":
    precioPlataforma = "data-pc-price"
    plataformaFutbin = "pc"
    precioJugadorBuscar = "data-price-pc"

def getDcp():
    for dcp in listaDcp['sets']:
        if format(dcp['repeatable']) == "True":
                print "- " + dcp['description']
        else:
            if format(dcp['timesCompleted']) == "0":
                print "- "+ dcp['description']

print "Obteniendo los DCP activos."

categoria = []
x = 0

for listaDcp in session.sbsSets()['categories']:
    print "\n" + format(x+1) + ".- "+format(listaDcp['name'])
    getDcp()
    categoria.append(format(listaDcp['name']))
    x = x + 1

ans = input("\nSelecciona la categoria. ")
buscar = ans - 1
categoriaSeleccionada = (categoriaSelected for categoriaSelected in session.sbsSets()['categories'] if categoriaSelected['name'] == categoria[buscar])
print "\nMostrando los DCP de la categoria: " + categoria[buscar]

idDcp = []
desafios = []
i = 1
for categoriaSelected in categoriaSeleccionada:
    for c in categoriaSelected['sets']:
        if format(c['repeatable']) == "True":
            print format(i)+".- " + c['description']
            desafios.append(format(c['challengesCount']))
            idDcp.append(format(c['setId']))
            i = i + 1
        elif format(c['timesCompleted']) == "0":
            print format(i)+".- " + c['description']
            desafios.append(format(c['challengesCount']))
            idDcp.append(format(c['setId']))
            i = i + 1
ans = input("\nSelecciona el DCP a buscar. ")
buscar = ans - 1
numeroDesafios = desafios[buscar]
dcpBuscar = futbin + futbinDcp + idDcp[buscar]
pagina_desafios = requests.get(dcpBuscar, timeout=5)
pagina_desafios_contenido = BeautifulSoup(pagina_desafios.content, "html.parser")

desafios = pagina_desafios_contenido.find_all('div', class_ = "main_chal_box")
numDesafios = len(desafios)
costeTotal = 0
y = 1
urlDesafios = []
print "\nEl DCP seleccionado tiene " + format(numDesafios) + " desafios:\n"

for desafio in desafios:
    nombreDesafio = desafio.find('div', class_= 'chal_name').text.strip()
    descDesafio = desafio.find('div', class_= 'chal_desc').text.strip()
    recompensaDesafio = nombreDesafio
    if desafio.find('div', class_= 'coins_text_value') != None:
        cantidadRecompensa = desafio.find('div', class_='coins_text_value').text.strip()
        queRecompensa = desafio.find('div', class_='coins_text').text.strip()
    elif desafio.find('div', class_='pack_small_reward_count_right') != None:
        cantidadRecompensa = desafio.find('div', class_='pack_small_reward_count_right').text.strip()
        queRecompensa = desafio.find('div', class_='pack_small_reward_name_right').text.strip()
    costeDesafio = desafio.find('div', class_= 'est_chal_prices_holder')
    costeDesafio = int(costeDesafio[precioPlataforma])
    costeTotal = costeTotal + costeDesafio
    print format(y) + ".- " + nombreDesafio + ": " + descDesafio + " - RECOMPENSA: " + recompensaDesafio  + " - COSTE: " + format(costeDesafio) + "."
    urlDesafio = desafio.find('div', class_='btn_holder')
    urlDesafio = urlDesafio.find('a')
    urlDesafio = futbin + urlDesafio.get('href') + "?page=1&lowest="+plataformaFutbin
    y = y + 1
    urlDesafios.append(urlDesafio)

print "\nCompletarlo cuesta " + format(costeTotal) + " monedas aproximadamente."
ans = input("Que desafio quieres realizar? ")
buscar = ans - 1
completarDesafio = urlDesafios[buscar]
completarDesafio = requests.get(completarDesafio, timeout=5)
completarDesafio_contenido = BeautifulSoup(completarDesafio.content, "html.parser")
plantillas = completarDesafio_contenido.find('a', class_='squad_url')
urlPlantilla = futbin + plantillas.get('href')
contador = 0
plantilla = requests.get(urlPlantilla, timeout=5)
plantilla_contenido = BeautifulSoup(plantilla.content, "html.parser")
listajugadores = plantilla_contenido.find_all('div', attrs={'style':'z-index:22;'})
comprado = False
for jugador in listajugadores:
    idJugadorBuscar = jugador['data-resource-id']
    precioJugador = jugador[precioJugadorBuscar]
    print "Vamos a buscar al jugador " + format(idJugadorBuscar) + " a un precio de " + format(precioJugador) + " monedas"
    comprado = False
    while comprado == False:
        print "Durmiendo 15 segundos antes de realizar la busqueda."
        time.sleep(15)
        listSearchedPlayer = session.searchAuctions('player', assetId=idJugadorBuscar, max_buy=precioJugador)
        for jugadorComprar in listSearchedPlayer:
            tradeId = jugadorComprar.get("tradeId")
            print tradeId
            try:
                print "Comprando jugador..."
                session.bid(tradeId, precioJugador)
                print "Jugador comprado!! "
                estadoJugador = session.tradeStatus(format(tradeId))
                for estado in estadoJugador:
                    idJugador = estado.get("id")
                    session.sendToTradepile(tradeId)
                comprado = True
                time.sleep(15)
                break
            except:
                print "No se ha podido comprar al jugador. "

raw_input("")