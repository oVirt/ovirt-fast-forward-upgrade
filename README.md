# ovirt-fast-forward-upgrade

About
=====
The ovirt-fast-forward-upgrade is a wrapper tool to automate oVirt Engine upgrades.

**Supported versions**:  
4.0 or higher

**Description**:  
*First stage*, the tool detects the current version of RHVM running on the system and check if there are updates
available related to minor version detected. If there are updates available, update all ovirt-engine-\*setup
packages via yum and execute engine-setup to complete the update. After the update is completed, update the
entire system via yum update command.

*Second stage*, all system is up to date, enable the new channels required for the next major release via
subscription-manager and update all ovirt-engine-\*setup packages. As soon the packages are updated,
execute engine-setup to complete the major upgrade.

*Final stage*, as new channel were added into the system, execute, yum update, to have the system
up to date and disable previous major versions related channels not required anymore.

**Note**:  
The upgrades are **incremental**.  
Example: Systems running 4.0 version, require upgrade to 4.1 before upgrading to 4.2

**Options**:  
--backup
      Execute engine-backup before the upgrade

--backup-dir
      Directory where the engine-backup will save the backup file.  If not provided, it will use /tmp
