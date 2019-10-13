import firebase_admin
from firebase_admin import credentials, firestore


class FirestoreManager:
    def __init__(self, cred, doc_id):
        firebase_admin.initialize_app(credentials.Certificate(cred))
        self.doc_ref = firestore.client().collection(u'cultivos').document(doc_id)

    def set(self, data, merge=True):
        self.doc_ref.set(data, merge=merge)

    def on_snapshot(self, handler):
        self.doc_ref.on_snapshot(handler)
