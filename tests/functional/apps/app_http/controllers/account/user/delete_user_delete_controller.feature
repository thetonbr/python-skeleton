Feature: UserDeleterDeleteController

  Scenario: Delete User
    Given an existent authenticated user with
    """
    {
        "id": "ca488d50-d383-4c08-95ec-7e876a0a77ef",
        "email": "ca488d50d3834c0895ec7e876a0a77ef@example.com",
        "password": "secret123456"
    }
    """
    When I send JSON "DELETE" request to "/private/users/ca488d50-d383-4c08-95ec-7e876a0a77ef"
    Then the response status code should be "200"
    And the response content should be
    """
     {
        "data": {
            "type": "users",
            "id": "ca488d50-d383-4c08-95ec-7e876a0a77ef"
        },
        "meta": {}
    }
    """
