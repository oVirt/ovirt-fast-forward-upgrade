#!/usr/bin/python

import subprocess

class Subscriptions(object):
    RHV_40_REPOS = [
        "rhel-7-server-supplementary-rpms",
        "rhel-7-server-rpms",
        "rhel-7-server-rhv-4.0-rpms",
        "jb-eap-7-for-rhel-7-server-rpms"
    ]

    RHV_41_REPOS = [
        "rhel-7-server-supplementary-rpms",
        "rhel-7-server-rpms",
        "rhel-7-server-rhv-4.1-rpms",
        "jb-eap-7-for-rhel-7-server-rpms"
    ]

    def __init__(self):
        super(Subscriptions, self).__init__()
        self.repos = []

    def get_enabled_repos(self):
        self.repos = []
        output = subprocess.check_output(
            "env LC_ALL=C subscription-manager repos --list-enabled",
            shell=True
        ).splitlines()
        for line in output:
            if(':' in line):
                key, value = line.split(':')
                if key == 'Repo ID':
                    self.repos.append(value)
        return self.repos

    def check_rhv_40_repos(self):
        enabled = set(self.repos)
        required = set(self.RHV_40_REPOS)
        unknown = enabled.difference(required)
        missing = required.difference(enabled)
        if missing:
            print("The following repositories are required for RHV 4.0:")
            for repo in missing:
                print(" - {repo}".format(repo=repo))
        if unknown:
            print("The following repositories are enabled and not supported "
                  "for RHV 4.0")
        if missing or unknown:
            return False
        return True

    def check_rhv_41_repos(self):
        enabled = set(self.repos)
        required = set(self.RHV_41_REPOS)
        unknown = enabled.difference(required)
        missing = required.difference(enabled)
        if missing:
            print("The following repositories are required for RHV 4.1:")
            for repo in missing:
                print(" - {repo}".format(repo=repo))
        if unknown:
            print("The following repositories are enabled and not supported "
                  "for RHV 4.1")
        if missing or unknown:
            return False
        return True

    def enable_repo(self, repo):
        output = subprocess.check_output(
            "env LC_ALL=C ubscription-manager repos --enable={repo}".format(
                repo=repo
            ),
            shell=True
        )
        return output

    def disable_repo(self, repo):
        output = subprocess.check_output(
            "env LC_ALL=C ubscription-manager repos --disable={repo}".format(
                repo=repo
            ),
            shell=True
        )
        return output

def UpgradeHelper(object):
    def __init__(self):
        super(UpgradeHelper, self).__init__()

    def is_upgrade_available(self):
        output = subprocess.check_output(
            "env LC_ALL=C engine-upgrade-check",
            shell=True
        )
        return output

    def upgrade_engine_setup(self):
        output = subprocess.check_output(
            "env LC_ALL=C yum update ovirt-engine-setup\*",
            shell=True
        )
        return output

    def run_engine_setup(self):
        output = subprocess.check_output(
            "env LC_ALL=C engine-setup",
            shell=True
        )
        return output

    def update_system(self):
        output = subprocess.check_output(
            "env LC_ALL=C yum update",
            shell=True
        )
        return output

def main():
    c = Subscriptions()
    print(c.get_enabled_repos())
    if c.check_rhv_40_repos():
        u = UpgradeHelper()
        if u.is_upgrade_available():
            print("An upgrade is available, upgrading to latest 4.0.z")
            u.upgrade_engine_setup()
            u.run_engine_setup()
            updated = u.update_system()
            if "kernel" in updated:
                print("A kernel update has been installed, please reboot the "
                    "system to complete the update.")
                return
        c.enable_repo("rhel-7-server-rhv-4.1-rpms")
        u.upgrade_engine_setup()
        u.run_engine_setup()
        updated = u.update_system()
        c.disable_repo("rhel-7-server-rhv-4.0-rpms")
        print("Please reboot the system to complete the update.")
        print("Once rebooted, please change the cluster and datacenter "
            "compatibility level to 4.1.\n"
            "See Chapter 4, Post-Upgrade Tasks: "
            "https://access.redhat.com/documentation/en/red-hat-virtualization/"
            "4.1/single/upgrade-guide#chap-Post-Upgrade_Tasks")
    if c.check_rhv_41_repos():
        u = UpgradeHelper()
        if u.is_upgrade_available():
            print("An upgrade is available, upgrading to latest 4.1.z")
            u.upgrade_engine_setup()
            u.run_engine_setup()
            updated = u.update_system()
            if "kernel" in updated:
                print("A kernel update has been installed, please reboot the "
                    "system to complete the update.")
                return
        c.enable_repo("rhel-7-server-rhv-4.2-rpms")
        u.upgrade_engine_setup()
        u.run_engine_setup()
        updated = u.update_system()
        c.disable_repo("rhel-7-server-rhv-4.1-rpms")
        print("Please reboot the system to complete the update.")
        print("Once rebooted, please change the cluster and datacenter "
            "compatibility level to 4.2.\n"
            "See Chapter 4, Post-Upgrade Tasks: "
            "https://access.redhat.com/documentation/en/red-hat-virtualization/"
            "4.2/single/upgrade-guide#chap-Post-Upgrade_Tasks")

main()
