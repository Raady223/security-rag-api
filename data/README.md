# Sample documents

Short summaries written for this project, based on the public
[MITRE ATT&CK](https://attack.mitre.org/) knowledge base and common incident
response practice (NIST SP 800-61 phases). They are paraphrased study notes,
not copies of the official text. For authoritative details always check
attack.mitre.org.

MITRE ATT&CK® is a registered trademark of The MITRE Corporation.

Upload them all with:

    for f in data/mitre_*.md data/playbook_*.md; do curl -s -F "file=@$f" localhost:8000/documents; echo; done
