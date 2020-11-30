from typing import final

from aioddd import ConflictError, ForbiddenError, NotFoundError, UnauthorizedError


@final
class UserUnauthorizedError(UnauthorizedError):
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
class UserNotSavedError(ConflictError):
    _code = 'user_not_saved'
    _title = 'User not saved'


@final
class UserNotDeletedError(ConflictError):
    _code = 'user_not_deleted'
    _title = 'User not user_not_deleted'


@final
class UserRefreshTokenNotValidError(ConflictError):
    _code = 'user_refresh_token_not_valid'
    _title = 'User refresh token not valid'


@final
class UserRefreshTokenExpirationInNotValidError(ConflictError):
    _code = 'user_refresh_token_expiration_in_not_valid'
    _title = 'User refresh token expiration in not valid'


@final
class UserRefreshTokenExpirationInExpiredError(ForbiddenError):
    _code = 'user_refresh_token_expiration_in_expired'
    _title = 'User refresh token expiration in expired'
