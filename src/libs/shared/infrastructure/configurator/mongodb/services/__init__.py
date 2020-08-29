from src.libs.shared.infrastructure.configurator.mongodb.config import MongoDBServiceConfigData, Database, Collection

RootMongoDBServiceConfigData = [
    MongoDBServiceConfigData(
        database=Database(name='example'),
        collections=[
            Collection(name='domain_events'),
        ]
    )
]
