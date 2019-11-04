import spidev
import json
import codecs
import RPi.GPIO as GPIO
from uuid import getnode
from time import sleep

from humidity_sensor import HumiditySensor
from photo_sensor import PhotoSensor
from temperature_sensor import TemperatureSensor
from image_processor import ImageProcessor
from db_connection import DbConnection
from firestore_manager import FirestoreManager
from sensor_data_uploader import SensorDataUploader
from device_controller import DeviceController

if __name__ == '__main__':

    def on_snapshot(doc_snapshot, changes, read_time):
        for doc in doc_snapshot:
            data = doc.to_dict()
            pump_state = data['pump']['state']
            lamp_state = data['lamp']['state']
            print(f'Received document snapshot: {doc.id}. Pump: {pump_state} Lamp: {lamp_state}')
            pump.set_state(pump_state)
            lamp.set_state(lamp_state)


    spi = spidev.SpiDev()
    spi.open(0, 0)
    spi.max_speed_hz = 1000000
    GPIO.setmode(GPIO.BOARD)

    min_max_per_plant = json.load(codecs.open('min_max.json', 'r', 'utf-8-sig'))
    cred = './credentials.json'

    conn = DbConnection(db_name='local.db')
    fsm = FirestoreManager(cred=cred, col_name='crops')

    heater = DeviceController(pin=11)
    lamp = DeviceController(pin=22)
    pump = DeviceController(pin=18)

    image_processor = ImageProcessor(conn=conn)
    photo_sensor = PhotoSensor(spi=spi, conn=conn, lamp=lamp, pin=0)
    humidity_sensor = HumiditySensor(spi=spi, conn=conn, pump=pump, pin=1)
    temperature_sensor = TemperatureSensor(conn=conn, lamp=lamp, pin=22)
    sensor_data_uploader = SensorDataUploader(conn=conn, fsm=fsm)
    query_watch = None

    while True:
        species, _, _ = image_processor.run()

        if species != 'vacio':

            if query_watch is None:
                min_temperature, max_temperature = min_max_per_plant[species]['temperature'].values()
                min_humidity, max_humidity = min_max_per_plant[species]['humidity'].values()
                min_illumination, max_illumination = min_max_per_plant[species]['illumination'].values()

                photo_sensor.set_min_max(min_illumination=min_illumination, max_illumination=max_illumination)
                humidity_sensor.set_min_max(min_humidity=min_humidity, max_humidity=max_humidity)
                temperature_sensor.set_min_max(min_temperature=min_temperature, max_temperature=max_temperature)

                results = conn.get('firestore_docs', f"PLANT = '{species}' ORDER BY ID DESC LIMIT 1")
                if len(results) == 0:
                    doc_id = fsm.retrieve_doc()
                    fsm.set({
                        'device_id': getnode(),
                        'pump': {
                            'state': pump.get_state(),
                            'force': False
                        },
                        'lamp': {
                            'state': lamp.get_state(),
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
            photo_sensor.run()
            humidity_sensor.run()
            temperature_sensor.run()
            sensor_data_uploader.run()
        else:
            photo_sensor.unset_min_max()
            humidity_sensor.unset_min_max()
            temperature_sensor.unset_min_max()
            query_watch.unsubscribe()
            query_watch = None

        sleep(2000)
