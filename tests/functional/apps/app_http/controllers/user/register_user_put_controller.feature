Feature: UserRegisterPutController

  Scenario: Register an User
    When I send JSON "PUT" request to "/public/users/register" with body
    """
    {
        "data": {
            "type": "users",
            "id": "a9f98679-d812-4fab-9437-6d4d03f32f36",
            "attributes": {
                "id": "a9f98679-d812-4fab-9437-6d4d03f32f36",
                "email": "a9f98679d8124fab94376d4d03f32f36@example.com",
                "password": "secret123456"
            }
        }
    }
    """
    Then the response status code should be "201"
    And the response content should be
    """
     {
        "data": {
            "type": "users",
            "id": "a9f98679-d812-4fab-9437-6d4d03f32f36"
        },
        "meta": {}
    }
    """

  Scenario: User already exists registering
    Given an existent user with
    """
    {
        "id": "11dfed28-5a63-4715-ad16-9ca594245961",
        "email": "11dfed285a634715ad169ca594245961@example.com",
        "password": "secret123456"
    }
    """
    When I send JSON "PUT" request to "/public/users/register" with body
    """
    {
        "data": {
            "type": "users",
            "id": "11dfed28-5a63-4715-ad16-9ca594245961",
            "attributes": {
                "email": "11dfed285a634715ad169ca594245961@example.com",
                "password": "secret123456"
            }
        }
    }
    """
    Then the response status code should be "409"
    And the response content should be contains
    """
     {
      "errors": [{
        "status": "409",
        "code": "user_already_exist",
        "title": "User already exist",
        "detail": "{\"id\": \"11dfed28-5a63-4715-ad16-9ca594245961\"}",
        "meta": {}
      }]
    }
    """
