#!/usr/bin/python
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
import argparse
import subprocess
import sys


def execute_cmd(command):
    """
    Execute cmd, use ['cmd' 'argument'] format for command argument
    Returns: output or raise an error
    """
    p = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False
    )
    out, err = p.communicate()
    if p.returncode != 0:
        raise RuntimeError("Command %s failed, rc=%s, out=%r, err=%r",
                           command, p.returncode, out, err)
    return out


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

    SUBSCRIPTION_MANAGER_GET_ENABLED_REPOS = [
        'env', 'LC_ALL=C', 'subscription-manager', 'repos', '--list-enabled'
    ]

    SUBSCRIPTION_MANAGER_ENABLE_REPO = [
        'env', 'LC_ALL=C', 'subscription-manager', 'repos', '--enable='
    ]

    SUBSCRIPTION_MANAGER_DISABLE_REPO = [
        'env', 'LC_ALL=C', 'subscription-manager', 'repos', '--disable='
    ]

    def __init__(self):
        super(Subscriptions, self).__init__()
        self.repos = []

    def get_enabled_repos(self):
        '''
        Get enabled repos

        Returns: All repos or subsription-manager error output
        '''
        self.repos = []

        output = execute_cmd(
             self.SUBSCRIPTION_MANAGER_GET_ENABLED_REPOS
        ).splitlines()

        for line in output:
            if(':' in line):
                key, value = line.split(':')
                if key == 'Repo ID':
                    self.repos.append(value)

        # If not output found, print message
        # join() to convert to str
        if not self.repos:
            return ''.join(output)

        return self.repos

    def check_rhv_repos(self, version):
        '''
        Check repositories for RHV

        Parameters:
            version: RHEV version to check, example of values (str):
                4.0
                4.1

        Returns: True or False
        '''
        enabled = set(self.repos)

        if version == '4.0':
            required = set(self.RHV_40_REPOS)
        elif version == '4.1':
            required = set(self.RHV_41_REPOS)
        else:
            raise RuntimeError('Version parameters not supported!')

        unknown = enabled.difference(required)
        missing = required.difference(enabled)
        if missing:
            print("The following repositories are required for {ver}".format(
                    ver=version))
            for repo in missing:
                print((" - {repo}".format(repo=repo)))

        if unknown:
            print("The following repositories are enabled and not supported "
                  "for RHV {ver}".format(ver=version))

        if missing or unknown:
            return False

        return True

    def enable_repo(self, repo):
        '''
        Enable repository using subscription-manager
        Parameters:
            repo - repository name (str or list)
        Returns: command output
        '''
        rhsm_cmd = list(self.SUBSCRIPTION_MANAGER_ENABLE_REPO)
        rhsm_cmd.extend(repo)

        return execute_cmd(rhsm_cmd)

    def disable_repo(self, repo):
        '''
        Disable repository using subscription-manager
        Parameters:
            repo - repository name (str or list)
        Returns: command output
        '''
        rhsm_cmd = list(self.SUBSCRIPTION_MANAGER_DISABLE_REPO)
        rhsm_cmd.extend(repo)

        return execute_cmd(rhsm_cmd)


class UpgradeHelper(object):

    UPGRADE_CHECK = [
        'env', 'LC_ALL=C', 'engine-upgrade-check'
    ]

    YUM_UPDATE_CMD = [
        'env', 'LC_ALL=C', 'yum', 'update'
    ]

    LIST_RPM_PKGS = [
        'rpm', '-qa', '--queryformat=%{NAME}\n'
    ]

    ENGINE_SETUP = [
        'env', 'LC_ALL=C', 'engine-setup'
    ]

    def __init__(self):
        super(UpgradeHelper, self).__init__()

    def is_upgrade_available(self):
        '''
        Execute engine-upgrade-check
        Returns: command output
        '''
        return execute_cmd(self.UPGRADE_CHECK)

    def upgrade_engine_setup(self):
        '''
        Look for packages with ovirt-engine-setup* name
        and execute yum update
        Returns: Empty list or yum update output
        '''

        print("Consulting ovirt-engine-setup packages in the "
              "system for update...")

        pkgs_for_update = []
        for pkg in execute_cmd(self.LIST_RPM_PKGS).split():
            if 'ovirt-engine-setup' in pkg:
                pkgs_for_update.append(pkg)

        if pkgs_for_update:
            yum_update_cmd = list(self.YUM_UPDATE_CMD)
            yum_update_cmd.extend(pkgs_for_update)

            return execute_cmd(yum_update_cmd)

        return pkgs_for_update

    def run_engine_setup(self):
        '''
        Execute engine-setup
        Returns: command output
        '''
        return execute_cmd(self.ENGINE_SETUP)

    def update_system(self):
        '''
        Execute yum update
        Returns: command output
        '''
        return execute_cmd(self.YUM_UPDATE_CMD)


def main():
    '''
    A tool to help users upgrade RHV environments
    '''

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description='Tool to upgrade RHV environments',
        epilog='Example of use:\n%(prog)s '
                    '--check-upgrade-rhv-4-0'
    )

    parser.add_argument(
        '--check-upgrade-rhv-4-0',
        action='store_true',
        help='Check if RHV 4.0 channels have upgrade available. '
             'Also enable 4.1 channels',
    )

    parser.add_argument(
        '--check-upgrade-rhv-4-1',
        action='store_true',
        help='Check if RHV 4.1 channels have zstream upgrade available. '
             'Also enable 4.2 channels',
    )

    parser.add_argument(
        '--list-enabled-repos',
        action='store_true',
        help='List all enabled repositories',
    )

    args = parser.parse_args()
    c = Subscriptions()

    if args.list_enabled_repos:
        print((c.get_enabled_repos()))
        return 0

    elif args.check_upgrade_rhv_4_0 and c.check_rhv_repos('4.0'):
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
              "https://access.redhat.com/documentation/en/red-hat-virtual"
              "ization/4.1/single/upgrade-guide#chap-Post-Upgrade_Tasks")

    elif args.check_upgrade_rhv_4_1 and c.check_rhv_repos('4.1'):
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
              "https://access.redhat.com/documentation/en/red-hat-virtuali"
              "zation/4.2/single/upgrade-guide#chap-Post-Upgrade_Tasks")
    else:
        print('Error: You must specify a valid operation. See usage:')
        parser.print_usage()

    return 0


if __name__ == '__main__':
    sys.exit(main())
