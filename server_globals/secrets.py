import boto3
import json

# Global cache for secrets
secrets = {}  

async def get_secret(secret_name, region_name="ap-south-1"):
    """
    Fetches a secret from AWS Secrets Manager.
    Uses caching to avoid unnecessary API calls.
    """
    global secrets  # Declare global before using

    if secrets:
        return secrets  # Return cached secrets if available

    try:
        # Create a Secrets Manager client
        client = boto3.client("secretsmanager", region_name=region_name)
        response = client.get_secret_value(SecretId=secret_name)

        # Check if the secret is stored as a string
        if "SecretString" in response:
            secret = response["SecretString"]
            try:
                secrets = json.loads(secret)  # Convert to dictionary if JSON
            except json.JSONDecodeError:
                secrets = secret  # Keep as string if not JSON
            return secrets  # Return cached secret

        return None  # Secret not found

    except Exception as e:
        print(f"Error retrieving secret {secret_name}: {str(e)}")
        return None
