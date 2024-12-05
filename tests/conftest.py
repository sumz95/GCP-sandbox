import pytest
import time
import logging
from src.utils.k8s_client import KubernetesClient

# Configure global logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_protocol(item):
    """
    Hook to log the start, end, and duration of each test.
    """
    logger.info(f"Starting test: {item.name}")
    start_time = time.time()
    yield  # Execute the test
    end_time = time.time()
    duration = end_time - start_time
    logger.info(f"Finished test: {item.name} in {duration:.3f} seconds.")

@pytest.fixture(scope="module")
def k8s_client():
    """
    Fixture to set up Kubernetes API client based on configuration.
    """
    config_file = "config/settings.toml"  # Path to the TOML configuration file
    logger.info(f"Initializing Kubernetes client with config file: {config_file}")
    return KubernetesClient(config_file=config_file).get_client()    
