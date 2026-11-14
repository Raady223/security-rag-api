# T1110 Brute Force

Tactic: Credential Access
Platforms: Windows, Linux, macOS, cloud identity providers, SaaS, network devices, containers

## Summary

Brute Force covers attacks where an adversary obtains access to accounts by
systematically trying many credentials when the real password is unknown, or
when only a password hash is available. Attackers use it against services
exposed to the network, such as SSH, RDP, VPN portals, Outlook Web Access,
single sign-on pages and cloud administration consoles. Successful brute force
usually gives the attacker a valid account, which then supports later steps
such as Initial Access, Persistence and Lateral Movement through Valid Accounts
(T1078).

Brute force can be done online, against a live login service, or offline,
against password hashes the attacker has already stolen. Online attacks are
noisy and often limited by account lockout and rate limiting. Offline attacks
are invisible to the defender because they run on the attacker's own hardware.

## Sub-techniques

- **T1110.001 Password Guessing.** The attacker tries common or likely
  passwords against a single account or a small set of accounts. Without
  knowing the password, they rely on lists of weak passwords, default
  passwords and patterns such as season plus year (for example "Summer2024!").
- **T1110.002 Password Cracking.** The attacker already holds password hashes,
  for example dumped from a domain controller or a breached database, and
  recovers the plaintext offline using wordlists, rules and GPU hardware.
  Account lockout does not help here because no login attempts reach the
  target.
- **T1110.003 Password Spraying.** The attacker tries one or a few very common
  passwords against many different accounts. Because each account only sees
  one or two failures, this approach stays under typical lockout thresholds.
  It is a frequent technique against Microsoft 365 and other cloud identity
  providers.
- **T1110.004 Credential Stuffing.** The attacker reuses username and password
  pairs leaked from breaches of unrelated websites, betting that people reuse
  the same password across services. Large credential lists and automated
  tools make this cheap to run at scale.

## Detection

- Monitor authentication logs for many failed logins. A burst of failures
  against one account suggests password guessing; one failure each across
  many accounts from the same source suggests password spraying.
- On Windows, failed logons generate Event ID 4625 and Kerberos
  pre-authentication failures generate Event ID 4771. Successful logons after
  a run of failures (Event ID 4624) deserve priority review.
- In cloud identity providers, review sign-in logs for failures from unusual
  countries, anonymising proxies, or legacy authentication protocols that do
  not support MFA.
- Credential stuffing often shows a high ratio of unknown usernames, because
  many leaked accounts do not exist in your organisation.

## Mitigations

- **M1032 Multi-factor Authentication.** The most effective control: a correct
  password alone is no longer enough to log in.
- **M1036 Account Use Policies.** Configure account lockout or progressive
  delays after a number of failed attempts, balanced so that attackers cannot
  easily lock out every user.
- **M1027 Password Policies.** Require long passwords, block known-breached
  and common passwords, and avoid forced periodic changes that push users
  toward predictable patterns.
- **M1018 User Account Management.** Remove unused accounts and disable
  legacy authentication protocols that bypass MFA.
