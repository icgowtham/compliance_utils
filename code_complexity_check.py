"""Utility to check Code Complexity."""

import sys

from radon.complexity import cc_visit, cc_rank, sorted_results

from compliance_check import Compliance
from helper_utils import filter_files
from config import (ERROR_MSG, OKAY_MSG)


class CodeComplexity(Compliance):
    """Class to check code complexity."""

    def parse_args(self, description=None):
        """
        Parse the command line arguments.

        :param description: OPTIONAL string @n
            Description of the program.
        :return: object
        """
        return super(CodeComplexity, self).parse_args(description)

    def get_files_list(self, description=None):
        """
        Get the list of files to check.

        :param description: OPTIONAL string @n
            Description of the program.
        :return: list
        """
        return super(CodeComplexity, self).get_files_list(description)

    def check(self, files_list):
        """
        Check code complexity compliance using 'radon'.

        :param files_list: @MANDATORY list @n
            List of files to check for code complexity compliance.
        :return: None
        """
        if files_list:
            files_list = filter_files(files_list)

            for filename in files_list:
                print("Checking file: {file}".format(file=filename))
                with open(filename) as fobj:
                    source = fobj.read()
                blocks = cc_visit(source)
                for result in sorted_results(blocks):
                    try:
                        component_result = str(result)
                        cc_rk = cc_rank(int(component_result.split()[-1]))
                        '''
                        21 - 30	D (more than moderate risk - more complex block)
                        31 - 40	E (high risk - complex block, alarming)
                        41+     F (very high risk - error-prone, unstable block)
                        '''
                        if cc_rk in ['D', 'E', 'F']:
                            error_msg = "Code complexity appears to be high, please re-factor:\n" + ERROR_MSG
                            print(error_msg + " " + component_result[:-1] + cc_rk)
                            sys.exit(1)
                    except ValueError:
                        pass
                print("No issues found with code complexity check for: {file} ".format(file=filename) + OKAY_MSG)


def main():
    """Main function."""
    compliance = CodeComplexity()
    files_list = compliance.get_files_list("Check code complexity compliance using 'radon'.")

    if files_list:
        print("Checking code complexity compliance on:\n {files}".format(files='\n '.join(files_list)))
        compliance.check(files_list=files_list)


if __name__ == '__main__':
    main()
