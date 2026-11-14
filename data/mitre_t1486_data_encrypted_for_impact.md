# T1486 Data Encrypted for Impact

Tactic: Impact
Platforms: Windows, Linux, macOS, ESXi, cloud storage

## Summary

Adversaries encrypt data on target systems or across a network to interrupt
the availability of systems and data. This is the core action of ransomware:
files, databases or whole virtual machine disks are encrypted, and the victim
is told to pay a ransom, usually in cryptocurrency, to receive a decryption
key. Modern ransomware groups frequently combine encryption with data theft
before encryption, then threaten to publish the stolen data if the victim does
not pay. This is called double extortion.

Encryption is normally the final stage of an intrusion. Before it, attackers
typically gain initial access (for example through phishing, exposed RDP or an
unpatched VPN), escalate privileges, move laterally, steal data and disable
defences, so that encryption can be launched across as many systems as
possible at the same time, often at night or over a weekend. Attacks against
VMware ESXi hypervisors are common because encrypting one host takes down many
virtual machines at once.

## Related techniques

- **T1490 Inhibit System Recovery.** Ransomware usually deletes Windows Volume
  Shadow Copies, for example with "vssadmin delete shadows /all /quiet" or
  wmic shadowcopy delete, and disables Windows recovery options, so that
  victims cannot simply roll back.
- **T1489 Service Stop.** Database and backup services are stopped so their
  files are no longer locked and can be encrypted.
- **T1567 Exfiltration Over Web Service.** Data is often copied to cloud
  storage before encryption to support double extortion.

## Detection

- Watch for a single process rapidly reading, writing and renaming large
  numbers of files, and for many files gaining a new, unusual extension.
- Alert on ransom note files (for example README or HOW_TO_DECRYPT text files)
  appearing in many directories.
- Alert on shadow copy deletion, use of bcdedit to disable recovery, and
  sudden stopping of backup or database services.
- Canary files placed in shared folders can give early warning when they are
  modified.

## Mitigations

- **M1053 Data Backup.** Keep regular backups that follow the 3-2-1 rule (three
  copies, two media types, one offsite), with at least one copy offline or
  immutable so that ransomware cannot reach it. Test restores regularly.
- **M1040 Behavior Prevention on Endpoint.** Use endpoint protection that
  detects and blocks ransomware-like behaviour such as mass file encryption.
- Reduce the blast radius with network segmentation, least-privilege admin
  accounts and MFA on remote access, since these limit how far the attacker
  can spread before encryption.
