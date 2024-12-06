Feature: Scale Deployment with Timing Metrics
  As a Kubernetes user
  I want to measure the time taken to scale a deployment
  So that I can analyze node readiness and pod scheduling times

  Scenario: Successfully scale a deployment to 1000 replicas and track timing
    Given a Kubernetes cluster is running
    And a deployment named "scale-test" exists in the "scale-test" namespace
    When I scale "scale-test" to 1000 replicas
    Then new nodes should become ready within 240 seconds
    And all replicas of the deployment should be running and available within 240 seconds
    And I log the node readiness and pod readiness times
