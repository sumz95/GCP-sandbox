import pytest
from pytest_bdd import given, when, then, scenarios
from src.utils.k8s_client import KubernetesClient
from src.utils.logging_util import get_logger
import tomli  # To parse TOML configuration files
import time

logger = get_logger(__name__)

# Link the Gherkin feature file
scenarios("../features/scale_deployment.feature")


def load_config(config_file="config/settings.toml"):
    """
    Load configuration from a TOML file.

    Args:
        config_file (str): Path to the configuration file.

    Returns:
        dict: Parsed configuration data.
    """
    logger.info(f"Loading configuration from {config_file}...")
    try:
        with open(config_file, "rb") as file:
            config = tomli.load(file)
        logger.info("Configuration loaded successfully.")
        return config
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        raise


# Load configuration once at module level
CONFIG = load_config()


@pytest.fixture(scope="module")
def k8s_client():
    """
    Fixture to set up Kubernetes API client based on configuration.
    """
    config_file = "config/settings.toml"  # Path to the TOML configuration file
    logger.info(f"Initializing Kubernetes client with config file: {config_file}")
    return KubernetesClient(config_file=config_file).get_client()


@given("a Kubernetes cluster is running")
def verify_cluster_running(k8s_client):
    """
    Verify that the Kubernetes cluster is accessible.
    """
    logger.info("Verifying Kubernetes cluster is running...")
    assert k8s_client is not None, "Kubernetes client could not be initialized."
    logger.info("Kubernetes cluster verification successful.")


@given('a deployment named "scale-test" exists')
def verify_deployment_exists(k8s_client):
    """
    Ensure the deployment exists in the specified namespace.
    """
    namespace = CONFIG["k8s"]["namespace"]
    deployment_name = CONFIG["k8s"]["deployment_name"]
    logger.info(f"Checking if deployment '{deployment_name}' exists in namespace '{namespace}'...")
    response = k8s_client.read_namespaced_deployment(name=deployment_name, namespace=namespace)
    assert response is not None, f"Deployment '{deployment_name}' does not exist in namespace '{namespace}'."
    logger.info(f"Deployment '{deployment_name}' exists.")


@when('I scale "scale-test" to 1000 replicas')
def scale_deployment_to_1000(k8s_client):
    """
    Scale the deployment to 1000 replicas and monitor the progress.
    """
    namespace = CONFIG["k8s"]["namespace"]
    deployment_name = CONFIG["k8s"]["deployment_name"]
    replicas = 1000
    timeout = 600  # Timeout in seconds
    interval = 10  # Polling interval in seconds

    logger.info(f"Scaling deployment '{deployment_name}' in namespace '{namespace}' to {replicas} replicas.")
    body = {"spec": {"replicas": replicas}}
    k8s_client.patch_namespaced_deployment_scale(name=deployment_name, namespace=namespace, body=body)

    logger.info(f"Waiting for deployment '{deployment_name}' to reach {replicas} replicas...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        response = k8s_client.read_namespaced_deployment(name=deployment_name, namespace=namespace)
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


@then("the deployment should have exactly 1000 replicas")
def verify_replicas(k8s_client):
    """
    Verify that the deployment has scaled to the desired number of replicas.
    """
    namespace = CONFIG["k8s"]["namespace"]
    deployment_name = CONFIG["k8s"]["deployment_name"]
    logger.info(f"Verifying deployment '{deployment_name}' has exactly 1000 replicas...")
    response = k8s_client.read_namespaced_deployment(name=deployment_name, namespace=namespace)
    assert response.status.replicas == 1000, f"Expected 1000 replicas but got {response.status.replicas}."
    logger.info(f"Deployment '{deployment_name}' has the correct number of replicas: {response.status.replicas}.")


@then("all replicas should be running and available")
def verify_available_replicas(k8s_client):
    """
    Verify that all replicas are running and available.
    """
    namespace = CONFIG["k8s"]["namespace"]
    deployment_name = CONFIG["k8s"]["deployment_name"]
    logger.info(f"Checking if all replicas for deployment '{deployment_name}' are running and available...")
    response = k8s_client.read_namespaced_deployment(name=deployment_name, namespace=namespace)
    assert response.status.available_replicas == 1000, (
        f"Not all replicas are available. Only {response.status.available_replicas} are available."
    )
    logger.info(f"All replicas for deployment '{deployment_name}' are running and available.")
