import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from time import sleep

# Create a callback on_snapshot function to capture changes
def on_snapshot(doc_snapshot, changes, read_time):
    for doc in doc_snapshot:
        print(u'Received document snapshot: {}'.format(doc.to_dict()))

# Configure credentials and initalize database
cred = credentials.Certificate('siscui-firebase-adminsdk-qzw3h-981046b404.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Get document
cultivos_ref = db.collection(u'cultivos')
doc_ref = cultivos_ref.document(u'9gOhABtBYIToU5N4RRxV')

# Watch the document
doc_watch = doc_ref.on_snapshot(on_snapshot)

input()