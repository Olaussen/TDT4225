from pprint import pprint 
from DbConnector import DbConnector
from Preprocessor import Preprocessor
from json import load


class DbHandler:

    def __init__(self):
        self.connection = DbConnector()
        self.client = self.connection.client
        self.db = self.connection.db

    def create_coll(self, collection_name):
        collection = self.db.create_collection(collection_name)    
        print('Created collection: ', collection)

    def insert_documents(self, collection, data):
        collection = self.db[collection]
        collection.insert_many(data)
    
        
    def fetch_documents(self, collection_name):
        collection = self.db[collection_name]
        documents = collection.find({})
        return documents
        

    def drop_coll(self, collection_name):
        collection = self.db[collection_name]
        collection.drop()

        
    def show_coll(self):
        collections = self.client['test'].list_collection_names()
        print(collections)
         


def main():
    program = None
    try:
        p = Preprocessor()
        p.preprocess()
        program = DbHandler()
        #program.drop_coll(collection_name='users')
        #program.drop_coll(collection_name='trackpoints')
        #program.create_coll("users")
        #program.create_coll("trackpoints")
        #program.insert_documents("users", p.users)
        #program.insert_documents("trackpoints", p.trackpoints)
        #program.update_coordinated()
        #program.fetch_documents("users")
        # Check that the table is dropped
        #program.show_coll()
    except Exception as e:
        print("ERROR: Failed to use database:", e)
    finally:
        if program:
            program.connection.close_connection()


if __name__ == '__main__':
    main()
