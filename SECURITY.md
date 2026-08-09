# Security policy

Probe Scent is a research benchmark and analysis package. It does not operate a hosted service or process secrets during ordinary offline use.

## Supported version

Security and integrity fixes are accepted for the current `1.x` code line. The frozen v1 canonical evidence is preserved as an auditable historical artifact; a security fix that changes scientific outputs must create a new protocol/version rather than silently rewriting canonical evidence.

## Reporting a vulnerability

For non-sensitive issues, open a GitHub issue with a minimal reproduction and affected version.

For a vulnerability that would be unsafe to disclose publicly, use GitHub private vulnerability reporting for this repository if that option is available in the repository Security tab. Do not include credentials, private model artifacts, or unrelated sensitive data in a public issue.

## Scope

Examples of security-relevant reports include:

- unsafe command or path handling in the CLI;
- evidence-verification bypasses;
- provenance or manifest checks that can be trivially forged;
- dependency or workflow behavior that could expose secrets;
- malicious-file handling that causes unintended execution.

Scientific disagreements, alternative interpretations, and requests for new experiments are not security vulnerabilities and should use ordinary issues or pull requests.
