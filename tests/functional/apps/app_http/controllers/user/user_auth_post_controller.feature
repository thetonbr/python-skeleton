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

  Scenario: Auth user not found
    Given I send JSON "POST" request to "/public/users/auth" with body
    """
    {
        "data": {
            "type": "users",
            "attributes": {
                "email": "0101e9f780b740c69872d65570c4ccbc@example.com",
                "password": "secret123456"
            }
        }
    }
    """
    Then the response status code should be "401"
    And the response content should be contains
    """
    {
      "errors": [{
          "status": "401",
          "code": "user_unauthorized",
          "title": "User Unauthorized",
          "detail": "{\"email\": \"0101e9f780b740c69872d65570c4ccbc@example.com\"}"
      }]
    }
    """

  Scenario: Auth User password not match
    Given an existent user with
    """
    {
        "id": "35c2242f-3438-4f1c-ab52-205b19177265",
        "email": "35c2242f-3438-4f1c-ab52-205b19177265@example.com",
        "password": "success123"
    }
    """
    When I send JSON "POST" request to "/public/users/auth" with body
    """
    {
        "data": {
            "type": "users",
            "attributes": {
                "email": "35c2242f-3438-4f1c-ab52-205b19177265@example.com",
                "password": "fail12345"
            }
        }
    }
    """
    Then the response status code should be "401"
    And the response content should be contains
    """
    {
      "errors": [{
          "status": "401",
          "code": "user_unauthorized",
          "title": "User Unauthorized",
          "detail": "{\"email\": \"35c2242f-3438-4f1c-ab52-205b19177265@example.com\"}"
      }]
    }
    """
