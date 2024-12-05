Feature: Scale deployment down to 1 replica

  Scenario: Successfully scale an existing deployment down to 1 replica
    Given a Kubernetes cluster is running
    And a deployment named "scale-test" exists in the "scale-test" namespace
    When I scale "scale-test" to 1 replica in the "scale-test" namespace
    Then the deployment should have exactly 1 replica
