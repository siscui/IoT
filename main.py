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
from picamera import PiCamera
from datetime import datetime

# ------------------------ Settings & Variables ------------------------
spi = spidev.SpiDev() # SPI para leer entradas analogicas
spi.open(0,0)
spi.max_speed_hz = 1000000
camera = PiCamera()
# camera.rotation = 180
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4 # GPIO 4
TABLAS = ('SENSORES', 'CAMARA', )
RASPY_DB = 'sensordata.db'
DEVICE_ID = 'ea6d2946-a89c-490a-ae18-d23f29c752f5'
# ---------------------------------------------------------------

""" ----------- Definicion de metodos utiles -------------- """
def create_structures_db(connection):
	tables = ('dht22', 'fotoresistor', 'ds1820')
	try:
		c = connection.cursor()
		c.execute(''' 
			CREATE TABLE IF NOT EXISTS '''+ TABLAS[0] +''' (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				temp NUMERIC,
				hume NUMERIC,
				luz  NUMERIC,
				temp_status TEXT,
				hume_status TEXT,
				luz_status TEXT,
				fecha TEXT); ''')
		c.execute(''' 
			CREATE TABLE IF NOT EXISTS '''+ TABLAS[1] +''' (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				file BLOB,
				plant_type TEXT,
				plant_name TEXT,
				status TEXT,
				fecha TEXT); ''')
	except Error as e:
		print(e)


def create_connection(db_file):
	# Se crea o si existe se conecta a la base
	try:
		conn = sqlite3.connect(db_file)
		conn.row_factory = sqlite3.Row
		print(sqlite3.version)
		create_structures_db(conn)
	except Error as e:
		print(e)
	finally:
		conn.close();


# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
def readadc(adcnum):
	r = spi.xfer2([1, 8 + adcnum << 4, 0])
	data = ((r[1]&3) << 8) + r[2]
	return data

def save_sensors_data():
	x, temp = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN, 5)
	luz = readadc(0)
	hume = readadc(1)
	err1 = 'OK'
	err2 = 'OK'
	err3 = 'OK'

	# Validaciones de lecturas
	if temp is not None:
		temp = round(temp, 1)
		if temp > 80 or temp < -40:
			err1 = 'ERR_TEMP_2' # Temperatura incoherente del DHT22
	else:
		err1 = 'ERR_TEMP_1' # Failed to retrieve data from humidity sensor
		temp = 'XXXX' # Sacar para no mostrar en el print

	if luz is not None:
		if luz > 1023 or luz < 0:
			err2 = 'ERR_LUZ_2' # Lectura incoherente
		else:
			luz = round(50 * (math.cos(math.pi * luz / 1023) + 1))
	else:
		err2 = 'ERR_LUZ_1' # No se pudo leer el LDR
		luz = 'XXXX' # Sacar para no mostrar en el print

	if hume is not None:
		if hume > 1023 or hume < 0:
			err3 = 'ERR_HUME_2' # Lectura incoherente
		else:
			hume = round(50 * (math.cos(math.pi * hume / 1023) + 1))
	else:
		err3 = 'ERR_HUME_1' # No se puede leer el Soil Moisture
		hume = 'XXXX' # Sacar para no mostrar en el print

	print("================================================")
	print("Temp: {:4}  - STATUS: {}".format(temp, err1))
	print("Hume: {:4}  - STATUS: {}".format(hume, err2))
	print("Luz: {:5}  - STATUS: {}".format(luz, err3))

	fecha = time.strftime('%Y%m%d%H%M%S')

	conn = sqlite3.connect(RASPY_DB)
	conn.row_factory = sqlite3.Row
	conn.cursor().execute(''' insert into '''+ TABLAS[0] + '''(temp, 
		hume, luz, temp_status, hume_status, luz_status, fecha) values 
		(?, ?, ?, ?, ?, ?, ?)''', (temp, hume, luz, err1, err2, err3, fecha))
	conn.commit()
	conn.close()


def active_actuators():
	print('TODO = Desarrollar este metodo.')

def manage_sensors_and_actuators():
	while True:
		save_sensors_data();
		active_actuators();
		time.sleep(5)

def take_and_analyze_photo():
	while True:
		filename = './fotos/' + datetime.now().strftime("%Y%m%d%H%M%S") + '.jpg'
		my_file = open(filename, 'wb')
		camera.start_preview()
		# prender lampara como flash
		time.sleep(2)
		camera.capture(my_file)
		camera.stop_preview()
		my_file.close()
		time.sleep(10)

""" ---------------------------------------------------------------- """

create_connection(RASPY_DB)

try:
   _thread.start_new_thread( manage_sensors_and_actuators, () )
   _thread.start_new_thread( take_and_analyze_photo, () )
except:
   print ("Error: unable to start thread")

while 1:
   pass
