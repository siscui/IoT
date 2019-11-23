import spidev
import json
import codecs
import RPi.GPIO as GPIO
from uuid import getnode
from time import sleep

import firebase_admin
from firebase_admin import credentials

from power_supply_sensor import PowerSupplySensor
from humidity_sensor import HumiditySensor
from photo_sensor import PhotoSensor
from temperature_sensor import TemperatureSensor
from image_processor import ImageProcessor
from db_connection import DbConnection
from firestore_manager import FirestoreManager
from sensor_data_uploader import SensorDataUploader


if __name__ == '__main__':

    def on_snapshot(doc_snapshot, changes, read_time):
        for doc in doc_snapshot:
            data = doc.to_dict()
            lamp_state = data['lamp']['state']
            heater_state = data['heater']['state']
            pump_state = data['pump']['state']
            print(f'Received document snapshot: {doc.id}. Pump: {pump_state} Lamp: {lamp_state} Heater: {heater_state}')
            humidity_sensor.set_pump_state(pump_state)
            photo_sensor.set_lamp_state(lamp_state)
            temperature_sensor.set_heater_state(heater_state)

    spi = spidev.SpiDev()
    spi.open(0, 0)
    spi.max_speed_hz = 1000000
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    # LED Azul de Prendido
    GPIO.setup(38, GPIO.OUT, initial=1)

    min_max_per_plant = json.load(codecs.open('min_max.json', 'r', 'utf-8-sig'))
    cred = './credentials.json'
    firebase_admin.initialize_app(credentials.Certificate(cred))
    conn = DbConnection(db_name='local.db')
    fsm = FirestoreManager(cred=cred, col_name='crops')
    mnt = FirestoreManager(cred=cred, col_name='monitor')

    power_sensor = PowerSupplySensor(pin=36, conn=conn)
    image_processor = ImageProcessor(conn=conn)
    photo_sensor = PhotoSensor(spi=spi, conn=conn, lamp_pin=22, pin=0)
    humidity_sensor = HumiditySensor(spi=spi, conn=conn, pump_pin=18, pin=1)
    temperature_sensor = TemperatureSensor(conn=conn, heater_pin=11, pin=22)
    sensor_data_uploader = SensorDataUploader(conn=conn, fsm=fsm)
    query_watch = None
    species = None

    while True:
        prev_species = species
        species, _, _ = image_processor.run()

        if species != 'vacio':

            if prev_species != species:
                mnt.retrieve_doc(doc_id='plants')
                data = mnt.get()
                data['values'].append(species)
                mnt.set(data)

            # If it's the first run, or species changed
            if query_watch is None or (species != prev_species and prev_species is not None):
                if query_watch is not None:
                    photo_sensor.unset_min_max()
                    humidity_sensor.unset_min_max()
                    temperature_sensor.unset_min_max()
                   ## query_watch.unsubscribe()
                    query_watch = None

                min_temperature, max_temperature = min_max_per_plant[species]['temperature'].values()
                min_humidity, max_humidity = min_max_per_plant[species]['humidity'].values()
                min_illumination, max_illumination = min_max_per_plant[species]['illumination'].values()

                photo_sensor.set_min_max(min_illumination=min_illumination, max_illumination=max_illumination)
                humidity_sensor.set_min_max(min_humidity=min_humidity, max_humidity=max_humidity)
                temperature_sensor.set_min_max(min_temperature=min_temperature, max_temperature=max_temperature)

                power_sensor.run()
                power_sensor.log() # Comentar para PROD

                results = conn.get('firestore_docs', f"PLANT = '{species}' ORDER BY ID DESC LIMIT 1")
                if len(results) == 0:
                    doc_id = fsm.retrieve_doc()
                    fsm.set({
                        'device_id': getnode(),
                        'pump': {
                            'state': humidity_sensor.get_pump_state(),
                            'force': False
                        },
                        'lamp': {
                            'state': photo_sensor.get_lamp_state(),
                            'force': False
                        },
                        'heater': {
                            'state': temperature_sensor.get_heater_state(),
                            'force': False
                        },
                        'temperature': {
                            'min': min_temperature,
                            'max': max_temperature,
                            'values': []
                        },
                        'humidity': {
                            'min': min_humidity,
                            'max': max_humidity,
                            'values': []
                        },
                        'illumination': {
                            'min': min_illumination,
                            'max': max_illumination,
                            'values': []
                        },
                        'plant': []
                    })
                    conn.save('firestore_docs', {'doc_id': doc_id, 'plant': species})
                else:
                    fsm.retrieve_doc(doc_id=results[0][1])
                query_watch = fsm.on_snapshot(on_snapshot)

            doc_dict = fsm.get()
            power_sensor.run()
            power_sensor.log() # Comentar en PROD
            pump_state = humidity_sensor.run(force=doc_dict['pump']['force'])
            lamp_state = photo_sensor.run(force=doc_dict['lamp']['force'])
            heater_state = temperature_sensor.run(force=doc_dict['heater']['force'])
            sensor_data_uploader.run(pump_state=pump_state,
                                     lamp_state=lamp_state,
                                     heater_state=heater_state)
        else:
            if query_watch is not None:
                photo_sensor.unset_min_max()
                humidity_sensor.unset_min_max()
                temperature_sensor.unset_min_max()
                ## query_watch.unsubscribe()
                query_watch = None

        sleep(2)
