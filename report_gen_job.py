import yaml
import requests
import json

# Read config file
with open('config.yml', 'r') as file:
    config_params = yaml.safe_load(file)

# Initialize databricks environment variables
token = config_params['databricks_config']['databricks_token']
host  = 'https://' + config_params['databricks_config']['databricks_host']
cluster_id  = config_params['databricks_config']['databricks_clusterId']

# API Call to create run 
api_endpoint = "/api/2.1/jobs/runs/submit"
submit_url = f"{host}{api_endpoint}"

#Request Payload
job_payload = {

    "run_name": "test_run",
    "email_notifications": {
        "no_alert_for_skipped_runs": False
    },
    "webhook_notifications": {},
    "timeout_seconds": 0,
    "max_concurrent_runs": 1,
    "tasks": [
        {
            "task_key": "build_and_test",
            "run_if": "ALL_SUCCESS",
            "notebook_task": {
                "notebook_path": "src/report_gen/generate_report",
                "source": "GIT"
            },
            "existing_cluster_id": cluster_id,
            "timeout_seconds": 0,
            "email_notifications": {},
            "notification_settings": {
                "no_alert_for_skipped_runs": False,
                "no_alert_for_canceled_runs": False,
                "alert_on_last_attempt": False
            }
        }
    ],
    "git_source": {
        "git_url": "https://github.com/haripurnapatre/xcel_databricks_llm_earnings.git",
        "git_provider": "gitHub",
        "git_branch": "main"
    },
    "format": "MULTI_TASK"
}

# Create run with generate_report
resp = requests.post(submit_url, json=job_payload, headers={'Authorization': f"Bearer {token}"})

# Print Run Status
print(resp.text)
