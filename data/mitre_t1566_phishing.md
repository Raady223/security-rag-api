# T1566 Phishing

Tactic: Initial Access
Platforms: Windows, Linux, macOS, SaaS, Office suites, identity providers

## Summary

Phishing is the sending of deceptive electronic messages to trick a victim
into running malicious code, opening a malicious link, or handing over
credentials, giving the adversary a first foothold in the target environment.
It is one of the most common initial access techniques in reported incidents.
Phishing can be targeted at specific people (spearphishing) or sent in broad
campaigns. Messages often impersonate trusted senders such as colleagues,
suppliers, banks, delivery services or IT support, and use urgency, such as an
unpaid invoice or an account about to be disabled, to make the victim act
without thinking.

## Sub-techniques

- **T1566.001 Spearphishing Attachment.** The message carries a malicious file,
  such as an Office document with macros, a PDF, an archive, an ISO or LNK
  file, or an HTML file that rebuilds a payload in the browser (HTML
  smuggling). The victim must open the attachment for the code to run.
- **T1566.002 Spearphishing Link.** The message contains a link instead of a
  file. The link may lead to a credential-harvesting page that imitates a real
  login portal, to a download of malware, or to an OAuth consent screen that
  asks the victim to grant a malicious application access to their mailbox
  (consent phishing).
- **T1566.003 Spearphishing via Service.** The adversary uses a third-party
  service instead of corporate email, for example social media direct
  messages, personal webmail or collaboration chat, where enterprise email
  filtering does not apply.
- **T1566.004 Spearphishing Voice.** Also called vishing. The adversary calls
  the victim, often posing as help desk staff, and persuades them to reveal
  credentials, approve an MFA prompt, or install remote access software.

## Detection

- Inspect email gateway logs for messages that fail SPF, DKIM or DMARC checks,
  use look-alike domains, or carry risky attachment types.
- Detonate attachments and URLs in a sandbox before delivery.
- Watch endpoints for Office applications spawning command interpreters such as
  cmd.exe or powershell.exe, which links phishing to Command and Scripting
  Interpreter (T1059).
- Encourage users to report suspicious messages with a single "report phishing"
  button, and treat user reports as a detection source.

## Mitigations

- **M1017 User Training.** Teach users to recognise phishing and to report it
  quickly; run regular simulated phishing exercises.
- **M1054 Software Configuration.** Enforce SPF, DKIM and DMARC to make sender
  spoofing harder, and disable Office macros from internet sources.
- **M1049 Antivirus/Antimalware** and **M1031 Network Intrusion Prevention**
  scan attachments and block known malicious content.
- **M1021 Restrict Web-Based Content.** Block known malicious domains and
  newly registered domains, and restrict risky file types at the gateway.
- Phishing-resistant MFA, such as FIDO2 security keys, prevents stolen
  passwords from credential-harvesting pages being reused.
