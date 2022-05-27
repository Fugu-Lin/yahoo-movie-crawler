import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

class FirebaseOperation:
    def __init__(self, cred):
        self.cred = credentials.Certificate(cred)
        firebase_admin.initialize_app(self.cred)
        self.db = firestore.client()

    def update(self, collectionName, documentName, value):
        doc = self.db.collection("%s" %(collectionName)).document("%s" %(documentName))
        doc.update(value)
        
    def create(self, collectionName, documentName, value):
        doc = self.db.collection("%s" %(collectionName)).document("%s" %(documentName))
        doc.create(value)

    def setSubCollection(self, collectionName, documentName, subCollectionName, subDocumentName, value):
        doc = self.db.collection("%s" %(collectionName)).document("%s" %(documentName)).collection("%s" %(subCollectionName)).document("%s" %(subDocumentName))
        doc.set(value)

    def deleteCollection(self, collRef, batchSize):
        docs = collRef.limit(batchSize).get()
        deleted = 0
        for doc in docs:
            doc.reference.delete()
            deleted = deleted + 1

        if deleted >= batchSize:
            return self.delete_collection(collRef, batchSize)

    def retrieveAllDocument(self, collectionName):
        docs = self.db.collection(collectionName).stream()
        return [doc.id for doc in docs]