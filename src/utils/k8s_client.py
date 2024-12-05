import os
from kubernetes import client, config
from src.utils.logging_util import get_logger

logger = get_logger(__name__)

class KubernetesClient:
    """
    Utility class to set up and provide a Kubernetes API client.
    """

    def __init__(self, config_file="config/settings.toml"):
        self.config_mode = "local"  # Default to local mode
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """
        Initializes the Kubernetes client based on the configuration mode.
        """
        try:
            logger.info("Initializing Kubernetes client...")
            if self.config_mode == "local":
                logger.debug("Loading kubeconfig for local setup.")
                config.load_kube_config()
            elif self.config_mode == "in-cluster":
                logger.debug("Loading in-cluster Kubernetes configuration.")
                config.load_incluster_config()
            else:
                logger.error(f"Invalid config_mode: {self.config_mode}")
                raise ValueError(f"Invalid config_mode: {self.config_mode}. Use 'local' or 'in-cluster'.")
            self.client = client.AppsV1Api()
            logger.info("Kubernetes client initialized successfully.")
        except Exception as e:
            logger.exception(f"Failed to initialize Kubernetes client: {e}")
            raise

    def get_client(self):
        """
        Returns the Kubernetes API client instance.
        """
        return self.client
