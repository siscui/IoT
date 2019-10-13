# https://pimylifeup.com/raspberry-pi-humidity-sensor-dht22/
# https://randomnerdtutorials.com/sqlite-database-on-a-raspberry-pi/
# https://scienceprog.com/working-with-sqlite-in-raspberry-pi-using-python-3/
# https://stackoverflow.com/questions/10104662/is-there-uid-datatype-in-sqlite-if-yes-then-how-to-generate-value-for-that
# http://www.sqlitetutorial.net/sqlite-python/creating-database/
# https://pythonexamples.org/python-sqlite3-check-if-table-exists/
# https://www.tutorialspoint.com/python/time_strftime
# https://www.instructables.com/id/Soil-Moisture-Sensor-Raspberry-Pi/
# https://computers.tutsplus.com/tutorials/build-a-raspberry-pi-moisture-sensor-to-monitor-your-plants--mac-52875
# https://www.youtube.com/watch?v=qw29egj5o9w
# http://www.pibits.net/code/read-ldr-raspberry-pi-using-mcp3008.php
# https://www.raspberrypi-spy.co.uk/2013/10/analogue-sensors-on-the-raspberry-pi-using-an-mcp3008/
# https://geekytheory.com/tutorial-raspberry-pi-uso-de-picamera-con-python

import _thread
import spidev
import Adafruit_DHT
import os
import time
import math
import sqlite3
import sys
from uuid import getnode
from picamera import PiCamera
from datetime import datetime
import firebase-admin
from firebase_admin import credentials
from firebase_admin import firestorm

# ------------------------ Settings & Variables ------------------------
spi = spidev.SpiDev() # SPI para leer entradas analogicas
spi.open(0,0)
spi.max_speed_hz = 1000000
DEVICE_ID = getnode()
# ---------------------------------------------------------------

class DbConnection:
	def __init__(self):
		self.file = 'sensordata.db'
		self.conn = sqlite3.connect(self.file)
		try:
			c = self.conn.cursor()
			c.execute("""CREATE TABLE IF NOT EXISTS TEMPERATURAS (
				ID INTEGER AUTOINCREMENT, VALOR NUMERIC, ESTADO TEXT, FECHA TEXT);""")
			c.execute("""CREATE TABLE IF NOT EXISTS HUMEDADES (
				ID INTEGER AUTOINCREMENT, VALOR NUMERIC, ESTADO TEXT, FECHA TEXT);""")
			c.execute("""CREATE TABLE IF NOT EXISTS ILUMINACIONES (
				ID INTEGER AUTOINCREMENT, VALOR NUMERIC, ESTADO TEXT, FECHA TEXT);""")
			c.execute("""CREATE TABLE IF NOT EXISTS FOTOS ( ID INTEGER AUTOINCREMENT, 
				FILENAME TEXT, NAME TEXT, MADURITY INTEGER, ESTADO TEXT, FECHA TEXT);""")
		except Error as e:
			sys.exit(e)
	
	def save_sensor(table, value, status):
		fecha = time.strftime('%Y%m%d%H%M%S')
		with self.conn:
			self.conn.cursor().execute(""" INSERT INTO """+ table +""" 
				(VALOR, ESTADO, FECHA) VALUES (?, ?, ?);""", (self.value, self.status, fecha))

class SensorLuz:
	def __init__(self):
		self.pin = 0

	def read:
		# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
		r = spi.xfer2([1, 8 + self.pin << 4, 0])
		self.value = ((r[1]&3) << 8) + r[2]
		if self.value is not None:
			if self.value > 1023 or self.value < 0:
				self.status = "ERR_LUZ_2"
			else:
				self.status = "OK"
				self.value = round(50 * (math.cos(math.pi * self.value / 1023) + 1))
		else:
			self.status = 'ERR_LUZ_1' # No se pudo leer el LDR
		conn.save_sensor("ILUMINACIONES", self.value, self.status)
		return (self.value, self.status)
	
	def mostrar:
		print(f"Luz: {self.value:5}  - STATUS: {self.status}")

class SensorHumedad:
	def __init__(self):
		self.pin = 1

	def read:
		# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
		r = spi.xfer2([1, 8 + self.pin << 4, 0])
		self.value = ((r[1]&3) << 8) + r[2]
		if self.value is not None:
			if self.value > 1023 or self.value < 0:
				self.status = 'ERR_HUME_2' # Lectura incoherente
			else:
				self.value = round(50 * (math.cos(math.pi * self.value / 1023) + 1))
				self.status = "OK"
		else:
			self.status = 'ERR_HUME_1' # No se puede leer el Soil Moisture
		conn.save_sensor("HUMEDADES", self.value, self.status)
		return (self.value, self.status)
	
	def mostrar:
		print(f"Hume: {self.value:4}  - STATUS: {self.status}")

class SensorTemperatura:
	def __init__(self):
		self.pin = 4 # GPIO 4
		self.sensor = Adafruit_DHT.DHT22
	
	def read:
		x, self.value = Adafruit_DHT.read_retry(self.sensor, self.pin, 5) # 5 Reintentos
		if self.value is not None:
			self.value = round(self.value, 1)
			if self.value > 80 or self.value < -40:
				self.status = 'ERR_TEMP_2' # Temperatura incoherente del DHT22
		else:
			self.status = 'ERR_TEMP_1' # Failed to retrieve data from humidity sensor
		conn.save_sensor("TEMPERATURAS", self.value, self.status)
		return (self.value, self.status)

	def mostrar:
		print(f"Temp: {self.value:4}  - STATUS: {self.status}")


class ProcesadorImagen:
	def __init__(self):
		self.camera = PiCamera()
		self.camera.rotation = 180

	def tomar_foto:
		self.filename = './fotos/' + datetime.now().strftime("%Y%m%d%H%M%S") + '.jpg'
		my_file = open(filename, 'wb')
		self.camera.start_preview()
		time.sleep(0.5)
		self.camera.capture(my_file)
		self.camera.stop_preview()
		# Agregar en la base de datos
		my_file.close()

	def analizar_foto:
		tomar_foto()
        # run IA recognizer with filename's path {self.filename}
        # detect plant and madurity
        # set ranges of light, temperature and humidity.
		return (plant, madurity)

def read_sensors:
	self.luz = SensorLuz()
	self.hume = SensorHume()
	self.temp = SensorTemperatura()
	while True:
		sLuz.read()
		sHume.read()
		sTemp.read()
		sLuz.print() # log
		sHume.print() # log
		sTemp.print() # log
		sleep(self.period)


class MessageManagement:
	def __init__(self):
		self.wait = 60

	def sendPost:
		while True:
			# Obtener las lecturas de los sensores
			# Obtener los estados de los sensores
			# Obtener los estados de los actuadores
			# Armar el Post para enviar 
			sleep(self.wait)

	def recivePost:
		# Recibir las ordenes del frontend
		# Desactivar algun actuador.
		pass


conn = DbConnection()
message = MessageManagement()
ia = ProcesadorImagen()

try:
   _thread.start_new_thread( read_sensors, () )
   _thread.start_new_thread( message.send, () )
   _thread.start_new_thread( ia.analizar_foto, () )
except:
   print ("Error: unable to start thread")

while 1:
   pass
