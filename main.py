import spidev
import json
import codecs
import RPi.GPIO as GPIO
from uuid import getnode

from humidity_sensor import HumiditySensor
from photo_sensor import PhotoSensor
from temperature_sensor import TemperatureSensor
from image_processor import ImageProcessor
from db_connection import DbConnection
from firestore_manager import FirestoreManager
from ai_model_manager import AIModelManager
from camera import Camera
from sensor_data_uploader import SensorDataUploader
from device_controller import DeviceController

if __name__ == '__main__':

    def on_snapshot(doc_snapshot, changes, read_time):
        for doc in doc_snapshot:
            doc_dict = doc.to_dict()
            pump_state = doc_dict['pump']['state']
            lamp_state = doc_dict['lamp']['state']
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
    ai = AIModelManager()
    camera = Camera()
    lamp = DeviceController(pin=26)
    pump = DeviceController(pin=29)
    filename = camera.take_photo()
    plant, _ = ai.analyze(filename)
    min_temperature, max_temperature = min_max_per_plant[plant]['temperature'].values()
    min_humidity, max_humidity = min_max_per_plant[plant]['humidity'].values()
    min_illumination, max_illumination = min_max_per_plant[plant]['illumination'].values()

    results = conn.get('firestore_docs', f"PLANT = '{plant}' ORDER BY ID DESC LIMIT 1")
    if len(results) == 0:
        doc_id = fsm.retrieve_doc()
        fsm.set({
            'device_id': getnode(),
            'pump': {
                'state': pump.get_state()
            },
            'lamp': {
                'state': lamp.get_state()
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
        conn.save('firestore_docs', {'doc_id': doc_id, 'plant': plant})
    else:
        fsm.retrieve_doc(doc_id=results[0][1])

    PhotoSensor(spi=spi, conn=conn, lamp=lamp, interval=60, pin=0, min_illumination=min_illumination,
                max_illumination=max_illumination).start()
    HumiditySensor(spi=spi, conn=conn, pump=pump, interval=60, pin=1, min_humidity=min_humidity,
                   max_humidity=max_humidity).start()
    TemperatureSensor(conn=conn, lamp=lamp, interval=60, pin=23, min_temperature=min_temperature,
                      max_temperature=max_temperature).start()
    ImageProcessor(conn=conn, interval=120, camera=camera, ai=ai).start()
    SensorDataUploader(conn=conn, interval=120, fsm=fsm).start()

    fsm.on_snapshot(on_snapshot)

    input()
