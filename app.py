from flask import Flask, request, jsonify

app = Flask(__name__)
@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/release-gate")
def release_gate():
    data = request.get_json(silent=True) or {}

    target = data.get("target")
    event = data.get("event")
    ref = data.get("ref")

    workflow = data.get("workflow") or {}
    image = data.get("image") or {}

    violations = []

    expected_permissions = {
        "contents": "read",
        "packages": "write",
        "id-token": "none"
    }

    if workflow.get("permissions") != expected_permissions:
        violations.append("EXCESS_PERMISSION")

    if event == "pull_request":
        if workflow.get("trigger") != "pull_request":
            violations.append("UNSAFE_PR_TRIGGER")

    if (
        workflow.get("testsPassed") is not True
        or workflow.get("matrixComplete") is not True
        or workflow.get("failFast") is not False
    ):
        violations.append("TESTS_INCOMPLETE")

    for action in workflow.get("actions", []):
        owner = action.get("owner", "")
        action_ref = action.get("ref", "")

        if owner != "actions":
            valid_sha = (
                len(action_ref) == 40
                and all(c in "0123456789abcdef" for c in action_ref)
            )

            if not valid_sha:
                violations.append("MUTABLE_ACTION")
                break

    if image.get("multiStage") is not True:
        violations.append("SINGLE_STAGE_IMAGE")

    if image.get("runsAsRoot") is not False:
        violations.append("ROOT_RUNTIME")

    if image.get("secretMode") not in ("none", "buildkit"):
        violations.append("SECRET_IN_LAYER")

    if image.get("criticalVulnerabilities") != 0:
        violations.append("CRITICAL_CVE")

    if image.get("digestPinned") is not True:
        violations.append("UNPINNED_IMAGE")

    if target == "production":
        if event != "push" or ref != "refs/heads/main":
            violations.append("INVALID_PRODUCTION_REF")

        if workflow.get("environmentApproval") is not True:
            violations.append("APPROVAL_REQUIRED")

    decision = "promote" if not violations else "block"

    return jsonify({
        "decision": decision,
        "violations": violations
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
