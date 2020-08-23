from src.libs.shared.infrastructure.configurator.amqp.config import AMQPServiceConfig, AMQPServiceConfigData

AccountAMQPServiceConfig = AMQPServiceConfig(AMQPServiceConfigData(
    exchange='example.account',
    queues_and_internal_queues_binds=[
        # User
        'user.registered',
        'user.password_changed',
        'user.deleted',
    ],
    external_queues_binds=[
    ]
))
