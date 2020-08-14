from typing import final

from aioddd import ConflictError, NotFoundError


@final
class UserUnauthorizedError(ConflictError):
    _code = 'user_unauthorized'
    _title = 'User Unauthorized'


@final
class UserEmailNotValidError(ConflictError):
    _code = 'user_email_not_valid'
    _title = 'User email not valid'


@final
class UserPasswordNotValidError(ConflictError):
    _code = 'user_password_not_valid'
    _title = 'User password not valid'


@final
class UserPasswordNotMatchError(ConflictError):
    _code = 'user_password_not_match'
    _title = 'User password not match'


@final
class UserAlreadyExistError(ConflictError):
    _code = 'user_already_exist'
    _title = 'User already exist'


@final
class UserNotFoundError(NotFoundError):
    _code = 'user_not_found'
    _title = 'User not found'


@final
class UserNotCreatedError(ConflictError):
    _code = 'user_not_created'
    _title = 'User not created'


@final
class UserNotUpdatedError(ConflictError):
    _code = 'user_not_updated'
    _title = 'User not updated'


@final
class UserNotDeletedError(ConflictError):
    _code = 'user_not_deleted'
    _title = 'User not user_not_deleted'
