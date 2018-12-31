import math

def precioPuja(precio, porcentaje):
	porcentaje = float(porcentaje)
	if precio < 1000:
		pujaformateada = porcentaje / 100 * precio
		pujaformateada = math.floor(pujaformateada / 50) * 50
		pujaformateada = int(pujaformateada)
	elif precio >1000 and precio< 10000:
		pujaformateada = porcentaje / 100 * precio
		pujaformateada = math.floor(pujaformateada / 100) * 100
		pujaformateada = int(pujaformateada)
	elif precio > 10000 and precio < 50000:
		pujaformateada = porcentaje / 100 * precio
		pujaformateada = math.floor(pujaformateada / 250) * 250
		pujaformateada = int(pujaformateada)
	elif precio > 50000 and precio < 100000:
		pujaformateada = porcentaje / 100 * precio
		pujaformateada = math.floor(pujaformateada / 500) * 500
		pujaformateada = int(pujaformateada)
	else:
		pujaformateada = porcentaje / 100 * precio
		pujaformateada = math.floor(pujaformateada / 1000) * 1000
		pujaformateada = int(pujaformateada)
	return pujaformateada

def formatearPrecio(precio):
	precio = precio.replace(",","")
	precio = int(precio)
	return precio
