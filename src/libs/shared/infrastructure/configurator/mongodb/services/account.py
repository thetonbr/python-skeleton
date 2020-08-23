from src.libs.shared.infrastructure.configurator.mongodb.config import MongoDBServiceConfigData, Database, Collection

AccountMongoDBServiceConfigData = [
    MongoDBServiceConfigData(
        database=Database(name='example_account'),
        collections=[
            Collection(name='domain_events'),
            Collection(name='users'),
        ]
    )
]
