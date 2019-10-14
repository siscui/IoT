import spidev
from uuid import getnode

from humidity_sensor import HumiditySensor
from photo_sensor import PhotoSensor
from temperature_sensor import TemperatureSensor
from image_processor import ImageProcessor
from db_connection import DbConnection
from firestore_manager import FirestoreManager
from ai_model_manager import AIModelManager
from camera_controller import CameraController
from sensor_data_uploader import SensorDataUploader


def handle_changes(doc_snapshot, changes, read_time):
    for doc in doc_snapshot:
        print(u'Received document snapshot: {}'.format(doc.id))


if __name__ == '__main__':
    spi = spidev.SpiDev()
    spi.open(0, 0)
    spi.max_speed_hz = 1000000
    device_id = getnode()
    cred = './credentials.json'

    conn = DbConnection(db_name='localdb')
    fsm = FirestoreManager(cred=cred, col_name='cultivos')
    ai = AIModelManager()
    camera = CameraController()
    filename = camera.take_photo()
    plant, _ = ai.analyze(filename)

    results = conn.get('firestore_docs', f"WHERE PLANT = '{plant}' ORDER BY ID DESC LIMIT 1")
    if len(results) == 0:
        doc_id = fsm.get_doc()
        conn.save('firestore_docs', {'doc_id': doc_id, 'plant': plant})
    else:
        fsm.get_doc(doc_id=results[1])

    HumiditySensor(spi=spi, conn=conn, interval=60, pin=1).start()
    PhotoSensor(spi=spi, conn=conn, interval=60, pin=0).start()
    TemperatureSensor(conn=conn, interval=60, pin=4, retries=5).start()
    ImageProcessor(conn=conn, interval=120, camera=camera, ai=ai).start()
    SensorDataUploader(conn=conn, interval=120, fsm=fsm).start()

    fsm.on_snapshot(handle_changes)

    input()
