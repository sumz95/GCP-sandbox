Feature: Scale deployment to 1000 replicas

  Scenario: Successfully scale an existing deployment to 1000 replicas
    Given a Kubernetes cluster is running
    And a deployment named "scale-test" exists
    When I scale "scale-test" to 1000 replicas
    Then the deployment should have exactly 1000 replicas
    And all replicas should be running and available
