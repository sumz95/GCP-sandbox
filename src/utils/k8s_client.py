import os
import tomli
from kubernetes import client, config
from kubernetes.client.api_client import ApiClient
from urllib3 import ProxyManager
from src.utils.logging_util import get_logger

logger = get_logger(__name__)

class KubernetesClient:
    """
    Utility class to set up and provide Kubernetes API clients.
    """

    def __init__(self, config_file="config/settings.toml"):
        """
        Initializes the Kubernetes client based on configuration.

        Args:
            config_file (str): Path to the configuration file.
        """
        self.config = self._load_config(config_file)
        self.api_clients = {}  # Cache for API clients
        self.proxy_manager = None  # ProxyManager instance
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
                self._configure_proxy()
                self._configure_ssl_settings()
            elif config_mode == "in-cluster":
                logger.debug("Loading in-cluster Kubernetes configuration.")
                config.load_incluster_config()
                self._configure_ssl_settings()
            else:
                logger.error(f"Invalid config_mode: {config_mode}")
                raise ValueError(f"Invalid config_mode: {config_mode}. Use 'local' or 'in-cluster'.")

            logger.info("Kubernetes configuration initialized successfully.")
        except Exception as e:
            logger.exception(f"Failed to initialize Kubernetes client: {e}")
            raise

    def _configure_proxy(self):
        """
        Configure HTTP and HTTPS proxy settings using ProxyManager.
        """
        http_proxy = self.config.get("local", {}).get("http_proxy")
        https_proxy = self.config.get("local", {}).get("https_proxy")
        no_proxy = self.config.get("local", {}).get("no_proxy")

        if http_proxy or https_proxy:
            proxy_url = https_proxy or http_proxy
            logger.info(f"Configuring proxy: {proxy_url}, NO_PROXY: {no_proxy}")
            self.proxy_manager = ProxyManager(
                proxy_url=proxy_url,
                proxy_headers=None,  # Add custom headers if necessary
            )

            # Apply ProxyManager to Kubernetes client
            api_client = ApiClient()
            api_client.rest_client.pool_manager = self.proxy_manager

            # Optionally, set environment variables for external tools
            if http_proxy:
                os.environ["http_proxy"] = http_proxy
            if https_proxy:
                os.environ["https_proxy"] = https_proxy
            if no_proxy:
                os.environ["no_proxy"] = no_proxy

            logger.info("Proxy settings applied successfully.")
        else:
            logger.info("No proxy settings provided. Skipping proxy configuration.")

    def _configure_ssl_settings(self):
        """
        Configure SSL verification settings for the Kubernetes client.
        """
        verify_ssl = self.config.get("local", {}).get("verify_ssl", True)
        client.Configuration.get_default_copy().verify_ssl = verify_ssl
        logger.info(f"SSL verification set to: {verify_ssl}")

    def get_client(self, api_type):
        """
        Retrieve the specified Kubernetes API client.

        Args:
            api_type (str): Type of Kubernetes API client (e.g., "AppsV1Api", "CoreV1Api").

        Returns:
            object: The requested Kubernetes API client instance.
        """
        if api_type not in self.api_clients:
            logger.info(f"Initializing API client for: {api_type}")
            if api_type == "AppsV1Api":
                self.api_clients[api_type] = client.AppsV1Api()
            elif api_type == "CoreV1Api":
                self.api_clients[api_type] = client.CoreV1Api()
            else:
                logger.error(f"Unsupported API client type: {api_type}")
                raise ValueError(f"Unsupported API client type: {api_type}")
        return self.api_clients[api_type]
