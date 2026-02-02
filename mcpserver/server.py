from mcp.server.fastmcp import FastMCP
import os
import time
import requests
import logging

# Initialize FastMCP
mcp = FastMCP("Jenkins-Manager")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-jenkins")

# Default settings
DEFAULT_JOB = "ocp-common/job/Flexy-install"

def get_auth():
    user = os.environ.get("JENKINS_USER")
    token = os.environ.get("JENKINS_TOKEN")
    url = os.environ.get("JENKINS_URL", "<https://<actual-jenkins-user-url>")
    if not user or not token:
        raise ValueError("JENKINS_USER and JENKINS_TOKEN environment variables must be set")
    return url.rstrip('/'), (user, token)

@mcp.tool()
def trigger_job(parameters: dict = None, job_name: str = DEFAULT_JOB) -> str:
    """
    Trigger a Jenkins job with optional parameters.
    
    Args:
        parameters: A dictionary of key-value pairs for job parameters.
        job_name: Jenkins job path. Defaults to ocp-common/job/Flexy-install.
    """
    base_url, auth = get_auth()
    trigger_url = f"{base_url}/job/{job_name}/buildWithParameters"
    
    logger.info(f"Triggering job {job_name} with params {parameters}")
    resp = requests.post(trigger_url, params=parameters, auth=auth, verify=False)
    resp.raise_for_status()

    if 'Location' not in resp.headers:
        return "Error: Job triggered but no Location header returned."

    queue_url = resp.headers['Location'].rstrip('/') + "/api/json"
    
    # Poll for build URL
    for _ in range(30):
        q_data = requests.get(queue_url, auth=auth, verify=False).json()
        if 'executable' in q_data:
            build_url = q_data['executable']['url']
            return f"Job started successfully. Build URL: {build_url}"
        time.sleep(10)
        
    return f"Job is still in queue. Check later at: {queue_url}"

@mcp.tool()
def trigger_azure_hcp_install(version: str) -> str:
    """
    Jenkins tool to trigger an Azure management cluster installation for a specific version,and install hcp in the management cluster.
    
    Args:
        version: OpenShift version (e.g., '4.21')
    """
    version_underscore = version.replace('.', '_')
    version_dir = f"aos-{version_underscore}"
    user = os.environ.get("JENKINS_USER", "user")
    random_suffix = str(int(time.time()))[-4:]
    
    parameters = {
        "OPENSHIFT_VERSION": version,
        "INSTANCE_NAME_PREFIX": f"{user}-{random_suffix}",
        "VARIABLES_LOCATION": f"private-templates/functionality-testing/{version_dir}/ipi-on-azure/versioned-installer-ci"
    }
    
    job_result = trigger_job(parameters=parameters)
    return f"{job_result}\n\nNote: The cluster will be ready in about 50 minutes. You can use the 'download_kubeconfig' tool later to retrieve the kubeconfig."

@mcp.tool()
def get_build_status(build_id_or_url: str) -> dict:
    """
    Check the status of a specific Jenkins build job'
    
    Args:
        build_id_or_url: Jenkins build ID (e.g. '370172') or full build URL.
    """
    base_url, auth = get_auth()
    if build_id_or_url.isdigit() or not build_id_or_url.startswith("http"):
        build_url = f"{base_url}/job/{DEFAULT_JOB}/{build_id_or_url}/"
    else:
        build_url = build_id_or_url
        
    api_url = f"{build_url.rstrip('/')}/api/json"
    
    resp = requests.get(api_url, auth=auth, verify=False)
    data = resp.json()
    
    return {
        "building": data.get("building"),
        "result": data.get("result"),
        "displayName": data.get("fullDisplayName"),
        "url": data.get("url")
    }

@mcp.tool()
def download_kubeconfig(build_id_or_url: str, output_path: str = "mgmt-kubeconfig") -> str:
    """
    Download the kubeconfig artifact from a completed Flexy build of jenkins.
    
    Args:
        build_id_or_url: Jenkins build ID (e.g. '370172') or full build URL.
        output_path: Local path to save the kubeconfig.
    """
    base_url, auth = get_auth()
    if build_id_or_url.isdigit() or not build_id_or_url.startswith("http"):
        build_url = f"{base_url}/job/{DEFAULT_JOB}/{build_id_or_url}/"
    else:
        build_url = build_id_or_url

    artifact_urls = [
        f"{build_url.rstrip('/')}/artifact/workdir/install-dir/auth/kubeconfig"
    ]
    
    for url in artifact_urls:
        try:
            resp = requests.get(url, auth=auth, verify=False, stream=True)
            if resp.status_code == 200:
                with open(output_path, 'wb') as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        f.write(chunk)
                return f"Successfully downloaded kubeconfig to {output_path}"
        except Exception:
            continue
            
    return "Error: Kubeconfig artifact not found."

if __name__ == "__main__":
    mcp.run()
