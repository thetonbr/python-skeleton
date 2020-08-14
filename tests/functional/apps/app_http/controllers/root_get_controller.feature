Feature: RootGetController

  Scenario: RootGetController
    Given I send JSON "GET" request to "/"
    Then the response status code should be "200"
    And the response content should be
    """
    {
       "data": {
          "type": "service",
          "id": "example"
       },
       "meta": {}
    }
    """

