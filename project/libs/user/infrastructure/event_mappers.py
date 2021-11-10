from typing import Any, Dict, final

from aioddd import Event, EventMapper

from project.libs.user.domain.events import (
    UserDeleted,
    UserPasswordChanged,
    UserPasswordForgotten,
    UserPasswordResetted,
    UserRegistered,
    UserRegisteredNotified,
)
from project.libs.user.domain.properties import (
    UserEmail,
    UserId,
    UserRefreshToken,
    UserRefreshTokenExpirationIn,
)


@final
class UserRegisteredEventMapper(EventMapper):
    event_type = UserRegistered
    service_name = 'project.account'
    event_name = 'users.registered'

    def decode(self, data: Dict[str, Any]) -> Event:
        return UserRegistered(UserRegistered.Attributes(UserId(data['id']), UserEmail(data['email'])))

    @staticmethod
    def map_attributes(msg: UserRegistered.Attributes) -> Dict[str, Any]:
        return {
            'id': msg.id.value(),
            'email': msg.email.value(),
        }


@final
class UserDeletedEventMapper(EventMapper):
    event_type = UserDeleted
    service_name = 'project.account'
    event_name = 'users.deleted'

    def decode(self, data: Dict[str, Any]) -> Event:
        return UserDeleted(UserDeleted.Attributes(UserId(data['id']), UserEmail(data['email'])))

    @staticmethod
    def map_attributes(msg: UserDeleted.Attributes) -> Dict[str, Any]:
        return {
            'id': msg.id.value(),
            'email': msg.email.value(),
        }


@final
class UserPasswordChangedEventMapper(EventMapper):
    event_type = UserPasswordChanged
    service_name = 'project.account'
    event_name = 'users.password_changed'

    def decode(self, data: Dict[str, Any]) -> Event:
        return UserPasswordChanged(UserPasswordChanged.Attributes(UserId(data['id']), UserEmail(data['email'])))

    @staticmethod
    def map_attributes(msg: UserPasswordChanged.Attributes) -> Dict[str, Any]:
        return {
            'id': msg.id.value(),
            'email': msg.email.value(),
        }


@final
class UserPasswordForgottenEventMapper(EventMapper):
    event_type = UserPasswordForgotten
    service_name = 'project.account'
    event_name = 'users.password_forgotten'

    def decode(self, data: Dict[str, Any]) -> Event:
        return UserPasswordForgotten(
            UserPasswordForgotten.Attributes(
                UserId(data['id']),
                UserEmail(data['email']),
                UserRefreshToken(data['refresh_token']),
                UserRefreshTokenExpirationIn(data['refresh_token_expiration_in']),
            )
        )

    @staticmethod
    def map_attributes(msg: UserPasswordForgotten.Attributes) -> Dict[str, Any]:
        return {
            'id': msg.id.value(),
            'email': msg.email.value(),
            'refresh_token': msg.refresh_token.value(),
            'refresh_token_expiration_in': msg.refresh_token_expiration_in.value(),
        }


@final
class UserPasswordResettedEventMapper(EventMapper):
    event_type = UserPasswordResetted
    service_name = 'project.account'
    event_name = 'users.password_resetted'

    def decode(self, data: Dict[str, Any]) -> Event:
        return UserPasswordResetted(
            UserPasswordResetted.Attributes(
                UserId(data['id']),
                UserEmail(data['email']),
                UserRefreshToken(data['refresh_token']),
                UserRefreshTokenExpirationIn(data['refresh_token_expiration_in']),
            )
        )

    @staticmethod
    def map_attributes(msg: UserPasswordResetted.Attributes) -> Dict[str, Any]:
        return {
            'id': msg.id.value(),
            'email': msg.email.value(),
            'refresh_token': msg.refresh_token.value(),
            'refresh_token_expiration_in': msg.refresh_token_expiration_in.value(),
        }


@final
class UserRegisteredNotifiedEventMapper(EventMapper):
    event_type = UserRegisteredNotified
    service_name = 'project.account'
    event_name = 'users.user_registered_notified'

    def decode(self, data: Dict[str, Any]) -> Event:
        return UserRegisteredNotified(UserRegisteredNotified.Attributes(UserId(data['id']), UserEmail(data['email'])))

    @staticmethod
    def map_attributes(msg: UserRegisteredNotified.Attributes) -> Dict[str, Any]:
        return {
            'id': msg.id.value(),
            'email': msg.email.value(),
        }
