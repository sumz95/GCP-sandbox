from pytest_bdd import given, when, then, scenarios
from src.utils.logging_util import get_logger
import time
from src.utils.config_util import load_config

logger = get_logger(__name__)

# Link the feature file
scenarios("../features/scale_down_deployment.feature")

# Load configuration once at module level
CONFIG = load_config()


@given("a Kubernetes cluster is running")
def verify_cluster_running(k8s_client):
    """Verify that the Kubernetes cluster is accessible."""
    logger.info("Verifying Kubernetes cluster is running...")
    assert k8s_client is not None, "Kubernetes client could not be initialized."
    logger.info("Kubernetes cluster verification successful.")


@given('a deployment named "scale-test" exists in the "scale-test" namespace')
def verify_deployment_exists(k8s_client):
    """Ensure the specified deployment exists."""
    namespace = CONFIG["k8s"]["namespace"]
    deployment_name = CONFIG["k8s"]["deployment_name"]

    # Retrieve AppsV1Api client for deployment operations
    apps_api = k8s_client("AppsV1Api")
    logger.info(f"Checking if deployment '{deployment_name}' exists in namespace '{namespace}'...")
    response = apps_api.read_namespaced_deployment(name=deployment_name, namespace=namespace)
    assert response is not None, f"Deployment {deployment_name} does not exist in namespace {namespace}."
    logger.info(f"Deployment '{deployment_name}' exists.")


@when('I scale "scale-test" to 1 replica in the "scale-test" namespace')
def scale_deployment_to_1(k8s_client):
    """Scale the deployment to 1 replica."""
    namespace = CONFIG["k8s"]["namespace"]
    deployment_name = CONFIG["k8s"]["deployment_name"]
    replicas = 1
    timeout = CONFIG["scaling"]["timeout"]
    interval = CONFIG["scaling"]["interval"]

    # Retrieve AppsV1Api client for deployment operations
    apps_api = k8s_client("AppsV1Api")
    logger.info(f"Scaling deployment '{deployment_name}' in namespace '{namespace}' to {replicas} replicas.")
    body = {"spec": {"replicas": replicas}}
    apps_api.patch_namespaced_deployment_scale(name=deployment_name, namespace=namespace, body=body)

    logger.info(f"Waiting for deployment '{deployment_name}' to scale to {replicas} replicas...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        response = apps_api.read_namespaced_deployment(name=deployment_name, namespace=namespace)
        logger.debug(f"Current replicas: {response.status.replicas}, Available replicas: {response.status.available_replicas}")
        if (
            response.status.replicas == replicas
            and response.status.available_replicas == replicas
        ):
            logger.info(f"Deployment '{deployment_name}' successfully scaled to {replicas} replicas.")
            return
        time.sleep(interval)

    logger.error(f"Deployment '{deployment_name}' did not scale to {replicas} replicas within {timeout} seconds.")
    raise RuntimeError(f"Deployment '{deployment_name}' did not scale to {replicas} replicas within {timeout} seconds.")


@then("the deployment should have exactly 1 replica")
def verify_single_replica(k8s_client):
    """Verify that the deployment has scaled to 1 replica."""
    namespace = CONFIG["k8s"]["namespace"]
    deployment_name = CONFIG["k8s"]["deployment_name"]

    # Retrieve AppsV1Api client for deployment operations
    apps_api = k8s_client("AppsV1Api")
    logger.info(f"Verifying deployment '{deployment_name}' has exactly 1 replica...")
    response = apps_api.read_namespaced_deployment(name=deployment_name, namespace=namespace)
    assert response.status.replicas == 1, f"Expected 1 replica but got {response.status.replicas}."
    assert response.status.available_replicas == 1, (
        f"Not all replicas are available. Only {response.status.available_replicas} are available."
    )
    logger.info(f"Deployment '{deployment_name}' verification successful.")
