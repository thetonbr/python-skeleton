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
