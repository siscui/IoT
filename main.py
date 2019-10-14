import spidev
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
            pump_state = doc_dict['pump']['active']
            lamp_state = doc_dict['lamp']['active']
            print(f'Received document snapshot: {doc.id}. Pump: {pump_state} Lamp: {lamp_state}')
            pump.set_state(pump_state)
            lamp.set_state(lamp_state)


    spi = spidev.SpiDev()
    spi.open(0, 0)
    spi.max_speed_hz = 1000000
    cred = './credentials.json'

    conn = DbConnection(db_name='local_db')
    fsm = FirestoreManager(cred=cred, col_name='crops')
    ai = AIModelManager()
    camera = Camera()
    lamp = DeviceController(pin=26)
    pump = DeviceController(pin=29)
    filename = camera.take_photo()
    plant, _ = ai.analyze(filename)

    results = conn.get('firestore_docs', f"WHERE PLANT = '{plant}' ORDER BY ID DESC LIMIT 1")
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
                'values': []
            },
            'humidity': {
                'values': []
            },
            'illumination': {
                'values': []
            },
            'plant': {
                'values': []
            }
        })
        conn.save('firestore_docs', {'doc_id': doc_id, 'plant': plant})
    else:
        fsm.retrieve_doc(doc_id=results[1])

    PhotoSensor(spi=spi, conn=conn, lamp=lamp, interval=60, pin=0, min=0, max=1).start()
    HumiditySensor(spi=spi, conn=conn, pump=pump, interval=60, pin=1, min=0, max=1).start()
    TemperatureSensor(conn=conn, lamp=lamp, interval=60, pin=4, retries=5, min=0, max=1).start()
    ImageProcessor(conn=conn, interval=120, camera=camera, ai=ai).start()
    SensorDataUploader(conn=conn, interval=120, fsm=fsm).start()

    fsm.on_snapshot(on_snapshot)

    input()
