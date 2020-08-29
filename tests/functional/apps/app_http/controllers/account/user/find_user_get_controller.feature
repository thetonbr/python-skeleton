Feature: UserFinderGetController

  Scenario: Find User
    Given an existent authenticated user with
    """
    {
        "id": "6c124e3d-cba4-48b6-8d7e-abeef51d8c96",
        "email": "6c124e3dcba448b68d7eabeef51d8c96@example.com",
        "password": "secret123456"
    }
    """
    When I send JSON "GET" request to "/private/users/6c124e3d-cba4-48b6-8d7e-abeef51d8c96"
    Then the response status code should be "200"
    And the response content should be
    """
     {
        "data": {
            "type": "users",
            "id": "6c124e3d-cba4-48b6-8d7e-abeef51d8c96",
            "attributes": {
              "id": "6c124e3d-cba4-48b6-8d7e-abeef51d8c96",
              "email": "6c124e3dcba448b68d7eabeef51d8c96@example.com"
            }
        },
        "meta": {}
    }
    """
