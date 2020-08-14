Feature: UserPasswordChangerPostController

  Scenario: Change user password
    Given an existent authenticated user with
    """
    {
        "id": "59b76b5b-41eb-4061-a2f4-ec8fd65a315d",
        "email": "59b76b5b41eb4061a2f4ec8fd65a315d@example.com",
        "password": "secret123456"
    }
    """
    When I send JSON "POST" request to "/private/users/change-password" with body
    """
    {
        "data": {
            "type": "users",
            "id": "59b76b5b-41eb-4061-a2f4-ec8fd65a315d",
            "attributes": {
                "oldPassword": "secret123456",
                "newPassword": "123456secret"
            }
        }
    }
    """
    Then the response status code should be "200"
    And the response content should be
    """
     {
        "data": {
            "type": "users",
            "id": "59b76b5b-41eb-4061-a2f4-ec8fd65a315d"
        },
        "meta": {}
    }
    """
