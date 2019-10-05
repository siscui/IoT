import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("siscui-firebase-adminsdk-qzw3h-981046b404.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

users_ref = db.collection(u'cultivos')
docs = users_ref.stream()

for doc in docs:
    print(u'{} => {}'.format(doc.id, doc.to_dict()))