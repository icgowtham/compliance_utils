"""Utility to check documentation compliance."""

import subprocess
import sys

from compliance_check import Compliance
from helper_utils import execute_shell_command
from config import (ERROR_MSG, OKAY_MSG)


class DocCompliance(Compliance):
    """Class to handle doc compliance."""

    def parse_args(self, description=None):
        """
        Parse the command line arguments.

        :param description: str
            Description of the program.
        :return: object
        """
        return super(DocCompliance, self).parse_args(description)

    def get_files_list(self, description=None):
        """
        Get the list of files to check.

        :param description: str
            Description of the program.
        :return: list
        """
        return super(DocCompliance, self).get_files_list(description)

    def check(self, files_list):
        """
        Check documentation compliance using 'pep257'.

        :param files_list: list
            List of files to check for documentation compliance.
        :return: None
        """
        if files_list:
            commands = ['pep257']
            commands.extend(files_list)
            try:
                execute_shell_command(command=commands)
            except subprocess.CalledProcessError:
                error_msg = "Found documentation compliance violations! " + ERROR_MSG
                print(error_msg)
                sys.exit(1)
            else:
                print("All files have passed documentation compliance check. " + OKAY_MSG)


def main():
    """Main function."""
    compliance = DocCompliance()
    files_list = compliance.get_files_list("Check documentation compliance using 'pep257'")

    if files_list:
        print("Checking documentation compliance on:\n {files}".format(files='\n '.join(files_list)))
        compliance.check(files_list=files_list)


if __name__ == '__main__':
    main()
