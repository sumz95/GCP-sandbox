import tomli  # For reading TOML files
from kubernetes import client, config
from kubernetes.client.configuration import Configuration
from kubernetes.client.api_client import ApiClient
from src.utils.logging_util import get_logger
import urllib3

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
            elif config_mode == "in-cluster":
                logger.debug("Loading in-cluster Kubernetes configuration.")
                config.load_incluster_config()
            else:
                logger.error(f"Invalid config_mode: {config_mode}")
                raise ValueError(f"Invalid config_mode: {config_mode}. Use 'local' or 'in-cluster'.")

            # Get proxy configuration from the settings
            http_proxy = self.config.get("proxy", {}).get("http_proxy")
            https_proxy = self.config.get("proxy", {}).get("https_proxy")
            verify_ssl = self.config.get("proxy", {}).get("verify_ssl", True)

            # Get the default Kubernetes configuration
            k8s_config = Configuration.get_default_copy()

            # Configure SSL verification
            k8s_config.verify_ssl = verify_ssl
            logger.info(f"SSL verification set to: {verify_ssl}")

            # Initialize the ApiClient with the configuration
            api_client = ApiClient(configuration=k8s_config)

            # Set the proxy in the ApiClient if provided
            if https_proxy:
                logger.info(f"Configuring HTTPS proxy: {https_proxy}")
                api_client.rest_client.pool_manager = urllib3.ProxyManager(
                    proxy_url=https_proxy,
                    cert_reqs="CERT_REQUIRED" if verify_ssl else "CERT_NONE",
                )
            elif http_proxy:
                logger.info(f"Configuring HTTP proxy: {http_proxy}")
                api_client.rest_client.pool_manager = urllib3.ProxyManager(
                    proxy_url=http_proxy,
                    cert_reqs="CERT_REQUIRED" if verify_ssl else "CERT_NONE",
                )

            # Initialize the Kubernetes API client
            self.client = client.AppsV1Api(api_client)
            logger.info("Kubernetes client initialized successfully.")

        except Exception as e:
            logger.exception(f"Failed to initialize Kubernetes client: {e}")
            raise

    def get_client(self):
        """
        Returns the Kubernetes API client instance.

        Returns:
            client.AppsV1Api: Configured Kubernetes API client.
        """
        return self.client
