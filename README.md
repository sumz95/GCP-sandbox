
# GKE Scaling Tests

This repository contains tests for scaling Kubernetes deployments, implemented using `pytest` and `pytest-bdd`. It provides functionality for scaling deployments up and down and ensures their proper behavior through integration tests.

## **Features**
- **Scale Up Deployment**: Tests to scale a deployment to a high number of replicas (e.g., 10,000).
- **Scale Down Deployment**: Tests to scale a deployment down to a minimal number of replicas (e.g., 1).

## **Directory Structure**
```
├── config/             # Configuration files (e.g., settings.yaml)
├── features/           # Gherkin feature files for behavior-driven testing
├── k8s_manifests/      # kubernetes Deployments that are used for testing.
├── src/                # Source code for utilities and helpers
│   └── utils/          # Kubernetes client utility and other shared modules
├── tests/              # Test files using pytest-bdd for Gherkin scenarios
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

## **Setup Instructions**

### **1. Prerequisites**
- Python 3.9 or higher
- `kubectl` installed and configured for your cluster
- Access to a Kubernetes cluster (local or GKE)
- `pip` for installing Python dependencies

### **2. Install Dependencies**
Create a virtual environment and install the required dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### **3. Configuration**
- Modify the `config/settings.yaml` file to specify the desired `config_mode`:
  - Use `local` for local execution.
  - Use `in-cluster` for running inside a Kubernetes cluster.
- Example `settings.yaml`:
```yaml
k8s:
  config_mode: local
  namespace: default
  deployment_name: scale-test

scaling:
  timeout: 600
  interval: 10
```

## **Developer Guide**

### **Running Locally**
1. Ensure the `config_mode` in `settings.yaml` is set to `local`.
2. Ensure `kubectl` is properly configured and can access your cluster:
   ```bash
   kubectl get nodes
   ```
3. Run the tests:
   ```bash
   pytest -v tests/
   ```

## **Running the Tests**

### **1. Running All Tests**
Execute all tests in the `tests/` directory:
```bash
pytest -v --log-cli-level=INFO tests/
pytest -v tests/
```

### **2. Running Specific Tests**
To run a single test file (e.g., `test_scale_down_deployment.py`):
```bash
pytest -v tests/test_scale_down_deployment.py
pytest -v --log-cli-level=INFO tests/test_scale_down_deployment.py
```

### **3. Running Feature-Specific Tests**
To run tests for a specific feature (e.g., `scale_deployment.feature`):
```bash
pytest -v -k "scale deployment"
```

### **4. Running with Coverage**
Install `pytest-cov` if not already installed:
```bash
pip install pytest-cov
```

Run tests with coverage reporting:
```bash
pytest --cov=src tests/
```

Generate an HTML report for coverage:
```bash
pytest --cov=src --cov-report=html tests/
```

The coverage report will be available in the `htmlcov/` directory.

## **Extending the Tests**
- Add new Gherkin scenarios to `features/` for additional functionality.
- Implement corresponding step definitions in `tests/`.
- Follow the existing patterns for reusable utilities and configuration.

## **Contact**
For issues or suggestions, feel free to submit a pull request or open an issue.
