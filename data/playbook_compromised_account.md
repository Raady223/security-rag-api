# Incident Response Playbook: Compromised Account and Password Attacks

Related ATT&CK techniques: T1110 Brute Force (including Password Spraying and
Credential Stuffing), T1078 Valid Accounts. Structure follows the NIST SP
800-61 incident response phases.

## 1. Preparation

- Enforce multi-factor authentication for all users, and phishing-resistant
  MFA for administrators.
- Centralise authentication logs from the identity provider, VPN and critical
  servers in the SIEM.
- Create alert rules for password spraying, impossible travel and many failed
  logins followed by a success.

## 2. Detection and Analysis

- Typical signals: a spike in failed logins, sign-ins from new countries or
  anonymising services, MFA push requests the user did not start, or a user
  reporting that their password no longer works.
- Distinguish the attack pattern. Many failures against one account suggest
  password guessing; a small number of failures across many accounts from one
  source suggests password spraying; many attempts with unknown usernames
  suggest credential stuffing from leaked lists.
- Identify which accounts had a successful login during the attack window;
  those are the confirmed compromises.
- For each compromised account, review what the attacker did: mailbox access,
  file downloads, new MFA devices, password changes, new inbox rules and
  privilege changes.
- Be alert to MFA fatigue, where the attacker sends repeated push
  notifications until the user approves one.

## 3. Containment

- Disable or lock compromised accounts, or reset their passwords and revoke
  all sessions and refresh tokens so existing logins stop working.
- Remove any MFA methods or devices the attacker registered.
- Block the attacking IP addresses or ranges and enable stricter conditional
  access, such as blocking legacy authentication protocols.
- If an administrator or service account is affected, treat the incident as
  high severity and review all actions performed with that account.

## 4. Eradication and Recovery

- Remove attacker persistence: inbox forwarding rules, OAuth app consents, API
  keys, new accounts and changed permissions.
- Return the account to the user only after the password is reset and MFA is
  re-registered with a trusted method.
- Monitor the account and the source IP ranges for at least 30 days.

## 5. Post-Incident Activity

- Check whether the compromised passwords appear in public breach data; if so,
  require password changes for all users who reused them.
- Ban common and breached passwords in the password policy.
- Review account lockout thresholds so they slow attackers without allowing
  them to lock everyone out.
- Report credential stuffing to affected users and recommend password managers.
