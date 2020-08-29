Feature: ConsumerOnInternalUserDeletedController

  Scenario: On Internal User deleted delete User
    Given an existent user with
    """
    {
      "id": "2328180c-ee33-48ef-bc79-16acee98a059",
      "email": "2328180c-ee33-48ef-bc79-16acee98a059@example.com"
    }
    """
    When an existent published event with
    """
    {
      "attributes": {
        "id": "2328180c-ee33-48ef-bc79-16acee98a059",
        "email": "2328180c-ee33-48ef-bc79-16acee98a059@example.com"
      },
      "meta": {
        "message": "example.account.user.deleted"
      }
    }
    """
    Then I execute the "example:account:consumer-on-internal-user-deleted --times=1 --stop" command for "1" seconds
    And the exit code should be "0"
