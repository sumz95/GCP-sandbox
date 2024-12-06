import time
from pytest_bdd import given, when, then, scenarios
from src.utils.logging_util import get_logger
from src.utils.config_util import load_config

logger = get_logger(__name__)
# Load configuration once at module level
CONFIG = load_config()
# Link the Gherkin feature file
scenarios("../features/scale_deployment_node_tracking.feature")

@given("a Kubernetes cluster is running")
def verify_cluster_running(k8s_client):
    assert k8s_client is not None, "Kubernetes client could not be initialized."

@given('a deployment named "scale-test" exists in the "scale-test" namespace')
def verify_deployment_exists(k8s_client):
    namespace = CONFIG["k8s"]["namespace"]
    deployment_name = CONFIG["k8s"]["deployment_name"]

    # Retrieve AppsV1Api client
    apps_api = k8s_client("AppsV1Api")
    response = apps_api.read_namespaced_deployment(name=deployment_name, namespace=namespace)
    assert response is not None, f"Deployment {deployment_name} does not exist in namespace {namespace}."

@when('I scale "scale-test" to 1000 replicas')
def scale_deployment(k8s_client):
    namespace = CONFIG["k8s"]["namespace"]
    deployment_name = CONFIG["k8s"]["deployment_name"]
    replicas = 1000

    # Retrieve AppsV1Api client
    apps_api = k8s_client("AppsV1Api")
    body = {"spec": {"replicas": replicas}}
    apps_api.patch_namespaced_deployment_scale(name=deployment_name, namespace=namespace, body=body)
    logger.info(f"Scaling deployment {deployment_name} in namespace {namespace} to {replicas} replicas.")

@then("new nodes should become ready within 240 seconds")
def verify_nodes_ready(k8s_client):
    # Retrieve CoreV1Api client
    core_api = k8s_client("CoreV1Api")
    start_time = time.time()
    timeout = 240  # seconds
    interval = 10  # seconds
    nodes_ready = False

    while not nodes_ready and (time.time() - start_time) < timeout:
        nodes = core_api.list_node().items
        nodes_ready = all(
            any(condition.type == "Ready" and condition.status == "True" for condition in node.status.conditions)
            for node in nodes
        )
        if nodes_ready:
            break
        time.sleep(interval)

    assert nodes_ready, "New nodes did not become ready within the timeout."
    logger.info(f"Nodes became ready in {time.time() - start_time:.2f} seconds.")

@then("all replicas of the deployment should be running and available within 240 seconds")
def verify_pods_ready(k8s_client):
    namespace = CONFIG["k8s"]["namespace"]
    deployment_name = CONFIG["k8s"]["deployment_name"]

    # Retrieve AppsV1Api client
    apps_api = k8s_client("AppsV1Api")
    start_time = time.time()
    timeout = 240  # seconds
    interval = 10  # seconds
    pods_ready = False

    while not pods_ready and (time.time() - start_time) < timeout:
        response = apps_api.read_namespaced_deployment(name=deployment_name, namespace=namespace)
        pods_ready = (
            response.status.replicas == 1000
            and response.status.available_replicas == 1000
        )
        if pods_ready:
            break
        time.sleep(interval)

    assert pods_ready, f"Deployment did not scale to 1000 replicas within {timeout} seconds."
    logger.info(f"Pods became ready in {time.time() - start_time:.2f} seconds.")

@then("I log the node readiness and pod readiness times")
def log_timing():
    logger.info("Timing metrics have been logged in the previous steps.")
