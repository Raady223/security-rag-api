# Incident Response Playbook: Ransomware

Related ATT&CK techniques: T1486 Data Encrypted for Impact, T1490 Inhibit
System Recovery. Structure follows the NIST SP 800-61 incident response phases.

## 1. Preparation

- Maintain offline or immutable backups and test restores at least quarterly.
- Keep an up-to-date asset inventory and network diagram, so responders know
  which systems are critical.
- Pre-arrange contacts: legal counsel, cyber insurance provider, an external
  incident response firm and law enforcement.
- Store this playbook and contact list outside the corporate network, because
  encrypted file servers and email may be unavailable during an attack.

## 2. Detection and Analysis

- Typical signals: ransom notes, files with a new extension, users unable to
  open documents, endpoint alerts for mass file modification, or shadow copy
  deletion.
- Identify the ransomware variant from the ransom note and file extension;
  check public resources such as the No More Ransom project for a free
  decryptor.
- Determine scope: which hosts, file shares and accounts are affected, and
  whether data was exfiltrated before encryption.
- Find patient zero and the initial access vector, such as a phishing email,
  exposed RDP or an unpatched VPN appliance.
- Declare the incident, assign an incident commander and start a timeline log
  of every action taken.

## 3. Containment

- Isolate infected hosts from the network immediately, using EDR network
  isolation or by unplugging the cable. Do not power them off: memory may
  contain encryption keys and other evidence.
- Disable compromised accounts and reset passwords for privileged accounts,
  including domain administrators and service accounts.
- Block known attacker IP addresses, domains and command-and-control channels
  at the firewall and proxy.
- Disconnect backups from the network to protect them from encryption.
- Preserve evidence: take memory captures and disk images of key systems
  before rebuilding them.

## 4. Eradication

- Remove persistence mechanisms such as scheduled tasks, new services, new
  admin accounts and remote access tools installed by the attacker.
- Patch the vulnerability or close the access path used for initial access.
- Reset the KRBTGT account password twice if domain controllers were
  compromised, to invalidate forged Kerberos tickets.

## 5. Recovery

- Rebuild affected systems from known-good images rather than trying to clean
  them.
- Restore data from backups only after confirming the backups are clean and
  the attacker no longer has access.
- Bring systems back in priority order, starting with identity infrastructure
  such as Active Directory, then business-critical services.
- Monitor restored systems closely for signs of re-infection.

## 6. Post-Incident Activity

- Hold a blameless lessons-learned meeting within two weeks.
- Decisions about paying a ransom involve executives, legal counsel and law
  enforcement. Payment does not guarantee working decryption and may be
  restricted by sanctions law.
- Meet regulatory notification obligations if personal data was stolen.
- Update detections, backup strategy and this playbook based on findings.
