import os
import tomli  # For reading TOML files
from kubernetes import client, config
from src.utils.logging_util import get_logger

logger = get_logger(__name__)

class KubernetesClient:
    """
    Utility class to set up and provide a Kubernetes API client.
    """

    def __init__(self, config_file="config/settings.toml"):
        """
        Initializes the Kubernetes client based on configuration.

        Args:
            config_file (str): Path to the configuration file.
        """
        self.config_mode = self._load_config(config_file)
        self.client = None
        self._initialize_client()

    def _load_config(self, config_file):
        """
        Load the config_mode from the given TOML configuration file.

        Args:
            config_file (str): Path to the configuration file.

        Returns:
            str: The config_mode value from the configuration file.
        """
        logger.info(f"Loading configuration from {config_file}...")
        try:
            with open(config_file, "rb") as file:
                config_data = tomli.load(file)
                config_mode = config_data.get("k8s", {}).get("config_mode", "local")
                logger.info(f"Config mode loaded: {config_mode}")
                return config_mode
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_file}. Defaulting to 'local' mode.")
            return "local"
        except Exception as e:
            logger.exception(f"Failed to load configuration: {e}. Defaulting to 'local' mode.")
            return "local"

    def _initialize_client(self):
        """
        Initializes the Kubernetes client based on the configuration mode.
        """
        # Set proxy environment variables
        http_proxy = os.getenv("http_proxy")
        https_proxy = os.getenv("https_proxy")
        no_proxy = os.getenv("no_proxy")

        if http_proxy:
            os.environ["http_proxy"] = http_proxy
            logger.debug(f"HTTP proxy set to {http_proxy}")
        if https_proxy:
            os.environ["https_proxy"] = https_proxy
            logger.debug(f"HTTPS proxy set to {https_proxy}")
        if no_proxy:
            os.environ["no_proxy"] = no_proxy
            logger.debug(f"No proxy set to {no_proxy}")

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
