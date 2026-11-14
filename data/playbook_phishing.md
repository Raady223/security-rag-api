# Incident Response Playbook: Phishing Email

Related ATT&CK techniques: T1566 Phishing, T1059 Command and Scripting
Interpreter. Structure follows the NIST SP 800-61 incident response phases.

## 1. Preparation

- Provide a one-click "report phishing" button in the mail client and a clear
  process for the security team to receive reports.
- Make sure email gateway logs, mailbox audit logs and endpoint telemetry are
  retained long enough to investigate, at least 90 days.
- Prepare the ability to search all mailboxes for a message and purge it.

## 2. Detection and Analysis

- Collect the original message with full headers, not a forwarded copy,
  because forwarding loses the header information.
- Analyse the headers: sender address, Reply-To, Return-Path, the originating
  IP address and the SPF, DKIM and DMARC results.
- Extract indicators: sender domains, URLs, attachment file names and file
  hashes. Check them against threat intelligence and detonate attachments in
  a sandbox.
- Search mail logs to find every recipient of the same campaign.
- Determine impact: who clicked the link, who opened the attachment, and who
  entered credentials. Check proxy logs for visits to the phishing URL and
  endpoint logs for processes started by the attachment.

## 3. Containment

- Purge the message from all mailboxes and block the sender, domain and URLs
  at the email gateway and web proxy.
- For users who entered credentials: reset the password, revoke all active
  sessions and refresh tokens, and review MFA methods for any that the
  attacker may have added.
- For users who opened a malicious attachment: isolate the endpoint and
  follow the malware response process.
- Check affected mailboxes for malicious inbox rules, such as rules that
  forward mail externally or hide replies, which attackers create to keep
  access and to run business email compromise fraud.
- Review OAuth application consents granted by affected users and remove
  unknown applications.

## 4. Eradication and Recovery

- Remove any malware found on endpoints, or reimage the machine.
- Confirm no further sign-ins from attacker IP addresses after the reset.
- Restore normal mail flow and unblock any legitimate senders caught by
  overly broad blocks.

## 5. Post-Incident Activity

- Notify affected users and thank the reporter; fast reporting shortens
  incidents.
- Use the real phishing email, with indicators removed, in awareness training.
- Tune email filtering rules and add detections for the indicators observed.
- Record time to detect and time to contain as metrics for improvement.
