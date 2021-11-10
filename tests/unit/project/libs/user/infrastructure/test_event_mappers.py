from typing import final

from project.libs.user.domain.events import (
    UserDeleted,
    UserPasswordChanged,
    UserPasswordForgotten,
    UserPasswordResetted,
    UserRegistered,
    UserRegisteredNotified,
)
from project.libs.user.infrastructure.event_mappers import (
    UserDeletedEventMapper,
    UserPasswordChangedEventMapper,
    UserPasswordForgottenEventMapper,
    UserPasswordResettedEventMapper,
    UserRegisteredEventMapper,
    UserRegisteredNotifiedEventMapper,
)
from tests.unit.project.libs.user.domain.properties_mothers import (
    UserEmailMother,
    UserIdMother,
    UserRefreshTokenExpirationInMother,
    UserRefreshTokenMother,
)


@final
class TestUserEventMappers:
    @staticmethod
    def test_user_registered_event_mapper() -> None:
        mapper = UserRegisteredEventMapper()
        msg = UserRegistered(UserRegistered.Attributes(UserIdMother.random(), UserEmailMother.random()))
        assert mapper.belongs_to(msg)
        assert mapper.service_name == 'project.account'
        assert mapper.event_name == 'users.registered'
        data = {
            'id': msg.attributes.id.value(),
            'email': msg.attributes.email.value(),
        }
        evt: UserRegistered = mapper.decode(data)
        assert evt.attributes.id.value() == data['id']
        assert evt.attributes.email.value() == data['email']
        assert mapper.map_attributes(msg.attributes) == data

    @staticmethod
    def test_user_deleted_event_mapper() -> None:
        mapper = UserDeletedEventMapper()
        msg = UserDeleted(UserDeleted.Attributes(UserIdMother.random(), UserEmailMother.random()))
        assert mapper.belongs_to(msg)
        assert mapper.service_name == 'project.account'
        assert mapper.event_name == 'users.deleted'
        data = {
            'id': msg.attributes.id.value(),
            'email': msg.attributes.email.value(),
        }
        evt: UserDeleted = mapper.decode(data)
        assert evt.attributes.id.value() == data['id']
        assert evt.attributes.email.value() == data['email']
        assert mapper.map_attributes(msg.attributes) == data

    @staticmethod
    def test_user_password_changed_event_mapper() -> None:
        mapper = UserPasswordChangedEventMapper()
        msg = UserPasswordChanged(UserPasswordChanged.Attributes(UserIdMother.random(), UserEmailMother.random()))
        assert mapper.belongs_to(msg)
        assert mapper.service_name == 'project.account'
        assert mapper.event_name == 'users.password_changed'
        data = {
            'id': msg.attributes.id.value(),
            'email': msg.attributes.email.value(),
        }
        evt: UserPasswordChanged = mapper.decode(data)
        assert evt.attributes.id.value() == data['id']
        assert evt.attributes.email.value() == data['email']
        assert mapper.map_attributes(msg.attributes) == data

    @staticmethod
    def test_user_password_forgotten_event_mapper() -> None:
        mapper = UserPasswordForgottenEventMapper()
        msg = UserPasswordForgotten(
            UserPasswordForgotten.Attributes(
                UserIdMother.random(),
                UserEmailMother.random(),
                UserRefreshTokenMother.random(),
                UserRefreshTokenExpirationInMother.random(),
            )
        )
        assert mapper.belongs_to(msg)
        assert mapper.service_name == 'project.account'
        assert mapper.event_name == 'users.password_forgotten'
        data = {
            'id': msg.attributes.id.value(),
            'email': msg.attributes.email.value(),
            'refresh_token': msg.attributes.refresh_token.value(),
            'refresh_token_expiration_in': msg.attributes.refresh_token_expiration_in.value(),
        }
        evt: UserPasswordForgotten = mapper.decode(data)
        assert evt.attributes.id.value() == data['id']
        assert evt.attributes.email.value() == data['email']
        assert evt.attributes.refresh_token.value() == data['refresh_token']
        assert evt.attributes.refresh_token_expiration_in.value() == data['refresh_token_expiration_in']
        assert mapper.map_attributes(msg.attributes) == data

    @staticmethod
    def test_user_password_resetted_event_mapper() -> None:
        mapper = UserPasswordResettedEventMapper()
        msg = UserPasswordResetted(
            UserPasswordResetted.Attributes(
                UserIdMother.random(),
                UserEmailMother.random(),
                UserRefreshTokenMother.random(),
                UserRefreshTokenExpirationInMother.random(),
            )
        )
        assert mapper.belongs_to(msg)
        assert mapper.service_name == 'project.account'
        assert mapper.event_name == 'users.password_resetted'
        data = {
            'id': msg.attributes.id.value(),
            'email': msg.attributes.email.value(),
            'refresh_token': msg.attributes.refresh_token.value(),
            'refresh_token_expiration_in': msg.attributes.refresh_token_expiration_in.value(),
        }
        evt: UserPasswordResetted = mapper.decode(data)
        assert evt.attributes.id.value() == data['id']
        assert evt.attributes.email.value() == data['email']
        assert evt.attributes.refresh_token.value() == data['refresh_token']
        assert evt.attributes.refresh_token_expiration_in.value() == data['refresh_token_expiration_in']
        assert mapper.map_attributes(msg.attributes) == data

    @staticmethod
    def test_user_registered_notified_event_mapper() -> None:
        mapper = UserRegisteredNotifiedEventMapper()
        msg = UserRegisteredNotified(UserRegisteredNotified.Attributes(UserIdMother.random(), UserEmailMother.random()))
        assert mapper.belongs_to(msg)
        assert mapper.service_name == 'project.account'
        assert mapper.event_name == 'users.user_registered_notified'
        data = {
            'id': msg.attributes.id.value(),
            'email': msg.attributes.email.value(),
        }
        evt: UserRegisteredNotified = mapper.decode(data)
        assert evt.attributes.id.value() == data['id']
        assert evt.attributes.email.value() == data['email']
        assert mapper.map_attributes(msg.attributes) == data
