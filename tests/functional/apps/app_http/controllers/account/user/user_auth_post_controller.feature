Feature: UserAuthPostController

  Scenario: Auth User
    Given an existent user with
    """
    {
        "id": "6fdd4d5a-750f-4bcf-9dfd-942e91412235",
        "email": "6fdd4d5a750f4bcf9dfd942e91412235@example.com",
        "password": "example2020"
    }
    """
    When I send JSON "POST" request to "/public/users/auth" with body
    """
    {
        "data": {
            "type": "users",
            "attributes": {
                "email": "6fdd4d5a750f4bcf9dfd942e91412235@example.com",
                "password": "example2020"
            }
        }
    }
    """
    Then the response status code should be "200"
    And the response content should be contains
    """
     {
        "data": {
            "type": "users",
            "id": "6fdd4d5a-750f-4bcf-9dfd-942e91412235"
        },
        "meta": {}
    }
    """
