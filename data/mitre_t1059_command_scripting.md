# T1059 Command and Scripting Interpreter

Tactic: Execution
Platforms: Windows, Linux, macOS, network devices, cloud environments

## Summary

Adversaries abuse command and script interpreters to execute commands,
scripts or binaries. Almost every operating system ships with at least one
interpreter, so attackers can run code without dropping custom executables,
a style often called "living off the land". Interpreters are used throughout
an intrusion: to run the first payload after phishing, to download further
tools, to perform discovery, to move laterally and to execute ransomware.
Because administrators use the same tools every day, telling malicious use
apart from normal use requires context such as the parent process, the
command-line arguments and the user account.

## Sub-techniques

- **T1059.001 PowerShell.** A powerful Windows shell and scripting language
  with direct access to .NET and Windows APIs. Attackers use encoded commands
  (the -EncodedCommand parameter), download cradles that fetch and run code in
  memory, and frameworks built on PowerShell.
- **T1059.002 AppleScript.** macOS scripting used to control applications and,
  through osascript, to run shell commands.
- **T1059.003 Windows Command Shell.** cmd.exe and batch files, used for simple
  commands, scripts and chaining other tools.
- **T1059.004 Unix Shell.** sh, bash and zsh on Linux and macOS, often used
  after exploiting a web server or with stolen SSH credentials.
- **T1059.005 Visual Basic.** VBScript and VBA macros inside Office documents,
  a classic follow-on from Spearphishing Attachment (T1566.001).
- **T1059.006 Python.** Python scripts and the interpreter, available on most
  Linux systems and many developer workstations.
- **T1059.007 JavaScript.** JScript run by Windows Script Host, and JavaScript
  in browsers or Node.js.
- **T1059.008 Network Device CLI.** The command line of routers, switches and
  firewalls, abused to change configuration or capture traffic.
- Further sub-techniques cover cloud APIs and other interpreters such as Lua
  and AutoHotKey.

## Detection

- Enable PowerShell Script Block Logging, which records the content of
  executed script blocks in Event ID 4104, including decoded versions of
  obfuscated commands.
- Enable command-line auditing for process creation (Windows Event ID 4688 with
  command line, or Sysmon Event ID 1) and look for unusual parent-child pairs,
  such as winword.exe launching powershell.exe.
- Flag long Base64 strings, hidden windows, execution policy bypass flags and
  scripts that download from the internet.
- On Linux, collect shell history and auditd execve records.

## Mitigations

- **M1038 Execution Prevention.** Use application control such as AppLocker or
  Windows Defender Application Control to block scripts and interpreters that
  users do not need.
- **M1042 Disable or Remove Feature or Program.** Remove interpreters that are
  not required, such as old PowerShell version 2, which lacks modern logging.
- **M1045 Code Signing.** Allow only signed PowerShell scripts to run.
- **M1026 Privileged Account Management.** Limit who can run interpreters with
  administrative rights, and use PowerShell Constrained Language Mode or Just
  Enough Administration.
