from src.libs.shared.infrastructure.configurator.amqp.config import AMQPServiceConfig, AMQPServiceConfigData

RootAMQPServiceConfig = AMQPServiceConfig(AMQPServiceConfigData(
    exchange='example',
    queues_and_internal_queues_binds=[
    ],
    external_queues_binds=[
    ]
))
