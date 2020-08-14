Feature: ConsumerOnInternalUserDeletedController

  Scenario: On Internal User deleted do something
    Given an existent user with id "2328180c-ee33-48ef-bc79-16acee98a059"
    When an existent published event with
    """
    {
      "attributes": {
        "id": "2328180c-ee33-48ef-bc79-16acee98a059",
        "email": "test@example.com"
      },
      "meta": {
        "message": "example.account.user.deleted"
      }
    }
    """
    Then I execute the "skeleton:account:consumer-on-internal-user-deleted --times=1" command for "1" seconds
    And the exit code should be "0"
