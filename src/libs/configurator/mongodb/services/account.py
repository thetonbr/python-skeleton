from src.libs.configurator.mongodb.config import MongoDBServiceConfigData, Database, Collection

AccountMongoDBServiceConfigData = [
    MongoDBServiceConfigData(
        database=Database(name='example'),
        collections=[
            Collection(name='domain_events'),
            Collection(name='users'),
        ]
    )
]
