import tomli
from kubernetes import client, config
from kubernetes.client.api_client import ApiClient
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
        self.config = self._load_config(config_file)
        self.client = None
        self._initialize_client()

    def _load_config(self, config_file):
        """
        Load the configuration from the given TOML file.

        Args:
            config_file (str): Path to the configuration file.

        Returns:
            dict: Parsed configuration data.
        """
        logger.info(f"Loading configuration from {config_file}...")
        try:
            with open(config_file, "rb") as file:
                config_data = tomli.load(file)
                logger.info("Configuration loaded successfully.")
                return config_data
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_file}.")
            raise
        except Exception as e:
            logger.exception(f"Failed to load configuration: {e}")
            raise

    def _initialize_client(self):
        """
        Initializes the Kubernetes client based on the configuration.
        """
        try:
            logger.info("Initializing Kubernetes client...")

            # Load Kubernetes configuration
            config_mode = self.config.get("k8s", {}).get("config_mode", "local")
            if config_mode == "local":
                logger.debug("Loading kubeconfig for local setup.")
                config.load_kube_config()
                self._configure_local_settings()
            elif config_mode == "in-cluster":
                logger.debug("Loading in-cluster Kubernetes configuration.")
                config.load_incluster_config()
                self._configure_in_cluster_settings()
            else:
                logger.error(f"Invalid config_mode: {config_mode}")
                raise ValueError(f"Invalid config_mode: {config_mode}. Use 'local' or 'in-cluster'.")

            # Initialize the Kubernetes API client
            self.client = client.AppsV1Api()
            logger.info("Kubernetes client initialized successfully.")

        except Exception as e:
            logger.exception(f"Failed to initialize Kubernetes client: {e}")
            raise

    def _configure_local_settings(self):
        """
        Configure settings for the local environment.
        """
        logger.info("Applying local environment settings...")

        # Disable SSL verification for local environments if specified
        verify_ssl = self.config.get("local", {}).get("verify_ssl", False)
        client.Configuration.get_default_copy().verify_ssl = verify_ssl
        logger.info(f"SSL verification set to: {verify_ssl}")

        # Configure proxy settings if specified
        proxy_url = self.config.get("local", {}).get("proxy")
        if proxy_url:
            logger.info(f"Configuring proxy: {proxy_url}")
            api_client = ApiClient()
            api_client.rest_client.pool_manager.proxy = proxy_url

    def _configure_in_cluster_settings(self):
        """
        Configure settings for the in-cluster environment.
        """
        logger.info("Applying in-cluster environment settings...")

        # For in-cluster environments, SSL verification is typically required
        client.Configuration.get_default_copy().verify_ssl = True

        # No proxy required for in-cluster environments
        logger.info("No proxy settings applied for in-cluster environment.")

    def get_client(self):
        """
        Returns the Kubernetes API client instance.

        Returns:
            client.AppsV1Api: Configured Kubernetes API client.
        """
        return self.client
