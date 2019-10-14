import firebase_admin
from firebase_admin import credentials, firestore


class FirestoreManager:
    def __init__(self, cred, col_name):
        self.col_ref = firestore.client().collection(col_name)
        self.doc_ref = None
        firebase_admin.initialize_app(credentials.Certificate(cred))

    def retrieve_doc(self, doc_id=None):
        self.doc_ref = self.col_ref.document(doc_id)
        return self.doc_ref

    def set(self, data, merge=True):
        self.doc_ref.set(data, merge=merge)

    def get(self):
        return self.doc_ref.get().to_dict()

    def on_snapshot(self, handler):
        self.doc_ref.on_snapshot(handler)
