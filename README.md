# AWS Session Interface

## Overview

The `DezSessionInterface` class is designed to simplify and enhance the usage of temporary AWS session tokens, particularly when Multi-Factor Authentication (MFA) is involved. This interface extends the functionality provided by the `boto3.Session` class to handle the caching and validation of AWS credentials, making it convenient for daily tasks within a DevOps team.

## Why Use This Class?

When managing multiple AWS accounts and regularly performing tasks using the AWS SDK for Python (`boto3`), it's common to encounter scenarios where temporary session tokens are required. This often involves using MFA to authenticate and obtain short-lived credentials. The `DezSessionInterface` streamlines this process, ensuring that cached credentials are utilized whenever possible, minimizing the need for repeated MFA prompts during daily operations.

## Features

- **Credential Caching**: The interface intelligently caches AWS credentials to avoid unnecessary MFA challenges on each run.
- **Automatic Expiry Handling**: The class verifies the validity of cached credentials and fetches new ones when necessary, providing a seamless experience.
- **Logging and Debugging**: Utilizes the Python `logging` module for structured and informative logs, aiding in debugging and monitoring activities.

## Example Usage

```python
from aws_session_interface import DezSessionInterface

# Initialize the session interface
session = DezSessionInterface(cache_creds=True, profile_name='your_aws_profile')

# Use the session to create AWS clients
ecs_client = session.client('ecs', region_name='your_preferred_region')

# Perform AWS operations using the client
response = ecs_client.list_clusters()

# Further operations with the same session do not trigger unnecessary MFA prompts
```

## Dependencies

- `boto3`: The AWS SDK for Python.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
