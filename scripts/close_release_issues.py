import json
import subprocess

issue_ids = [21, 22, 23]

for issue_id in issue_ids:
    print(f"Processing issue #{issue_id}...")
    try:
        # Get body
        res = subprocess.run(
            ["gh", "issue", "view", str(issue_id), "--json", "body"],
            capture_output=True,
            text=True,
            check=True,
        )
        data = json.loads(res.stdout)
        body = data.get("body", "")

        # Check all checkboxes
        new_body = body.replace("[ ]", "[x]")

        # Update body
        subprocess.run(["gh", "issue", "edit", str(issue_id), "--body", new_body], check=True)
        print(f"Updated body for issue #{issue_id}.")

        # Close issue
        subprocess.run(["gh", "issue", "close", str(issue_id)], check=True)
        print(f"Closed issue #{issue_id}.")
    except Exception as e:
        print(f"Error on issue #{issue_id}: {e}")
