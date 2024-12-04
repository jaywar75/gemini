import pymongo
import logging

class MongoPipeline:
    """
    Pipeline for storing scraped items in a MongoDB collection.
    """
    def __init__(self, mongo_uri, mongo_db, mongo_collection):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_collection = mongo_collection

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get("MONGO_URI"),
            mongo_db=crawler.settings.get("MONGO_DATABASE"),
            mongo_collection=crawler.settings.get("MONGO_COLLECTION"),
        )

    def open_spider(self, spider):
        """
        Called when the spider is opened.
        """
        try:
            self.client = pymongo.MongoClient(self.mongo_uri)
            self.db = self.client[self.mongo_db]
            self.collection = self.db[self.mongo_collection]
            logging.info("MongoDB connection established.")
        except pymongo.errors.ConnectionFailure as e:
            logging.critical(f"MongoDB connection failed: {e}")
            raise e

    def close_spider(self, spider):
        """
        Called when the spider is closed.
        """
        self.client.close()
        logging.info("MongoDB connection closed.")

    def process_item(self, item, spider):
        """
        Processes each scraped item.
        """
        try:
            self.collection.insert_one(dict(item))
            logging.info(f"Inserted item into MongoDB: {item['text']}")
        except pymongo.errors.PyMongoError as e:
            logging.error(f"Error inserting item into MongoDB: {e}")
        return item