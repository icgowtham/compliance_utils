"""Utility to check code compliance using 'flake8'."""

import importlib
import sys

from compliance_check import Compliance, ComplianceViolationException
from config import (ERROR_MSG,
                    OKAY_MSG,
                    CODE_COMPLIANCE_IGNORE_LIST,
                    CODE_VALIDATOR_TO_MODULE_MAP)


class CodeCompliance(Compliance):
    """Class to check code compliance."""

    __code_validators = None
    validator_to_function_map = dict()

    @property
    def code_validators(self):
        """Property 'getter' method."""
        return self.__code_validators

    @code_validators.setter
    def code_validators(self, value):
        """Property 'setter' method."""
        self.__code_validators = value

    def __init__(self):
        """Initialization method."""
        super(CodeCompliance, self).__init__()
        self.validator_to_function_map = {
            "flake8": CodeCompliance._run_flake8_validator,
            "pylint": CodeCompliance._run_pylint_validator
        }

    def parse_args(self, description=None):
        """
        Parse the command line arguments.

        :param description: str
            Description of the program.
        :return: object
        """
        parser = super(CodeCompliance, self).parse_args(description)
        parser.add_argument('--code_validators', nargs='*', default=['flake8'], help='The code validator to use.')
        args = parser.parse_args()
        self.code_validators = args.code_validators

        return parser

    def get_files_list(self, description=None):
        """
        Get the list of files to check.

        :param description: str
            Description of the program.
        :return: list
        """
        return super(CodeCompliance, self).get_files_list(description)

    def check(self, files_list):
        """
        Check code compliance using 'flake8'.

        :param files_list: list
            List of files to check for code compliance.
        :return: None
        """
        if not all(validators in CODE_VALIDATOR_TO_MODULE_MAP for validators in self.code_validators):
            raise ComplianceViolationException('\'{mod}\' not supported currently.'.format(mod=self.code_validators))

        # We need this branching since the way the validation is done is different for
        # for different validation utilities.
        for validator in self.code_validators:
            validator_module = CODE_VALIDATOR_TO_MODULE_MAP.get(validator, None)
            if validator_module is not None:
                self.validator_to_function_map[validator](validator_module, files_list)
            else:
                raise ComplianceViolationException('The corresponding module for \'{val}\' is \'None\'.'.format(
                        val=validator))

    @staticmethod
    def _run_flake8_validator(validator_module, files_list):
        """
        Check code compliance using 'flake8'.

        :param validator_module: str
            Fully qualified name of the Python module of the validator.
        :param files_list: list
            List of files to check for code compliance.
        :return: None
        """
        flake8 = importlib.import_module(validator_module)
        style_guide = flake8.get_style_guide(ignore=CODE_COMPLIANCE_IGNORE_LIST)
        style_guide.options.max_line_length = 120
        report = style_guide.check_files(files_list)
        if report.total_errors > 0:
            error_msg = ERROR_MSG + " Found code compliance violations!"
            print(error_msg)
            sys.exit(1)
        else:
            print("All files have passed code compliance check. " + OKAY_MSG)

    @staticmethod
    def _run_pylint_validator(validator_module, files_list):
        """
        Check code compliance using 'pylint'.

        :param validator_module: str
            Fully qualified name of the Python module of the validator.
        :param files_list: list
            List of files to check for code compliance.
        :return: None
        """
        lint = importlib.import_module(validator_module)
        error_report = set()

        for fileName in files_list:
            (pylint_out, pylint_err) = lint.py_run(fileName, return_std=True)
            errors = [output for output in pylint_out.readlines() if ': error ' in output]
            if pylint_err or errors:
                error_report.add('\n'.join(errors))

        if error_report:
            error_msg = ERROR_MSG + " Found code compliance violations!"
            print("\n" + error_msg + "\n".join(error_report))
            sys.exit(1)
        else:
            print("All files have passed code compliance check. " + OKAY_MSG)


def main():
    """Main function."""
    compliance = CodeCompliance()
    files_list = compliance.get_files_list("Check code compliance.")

    if files_list:
        print("Checking code compliance using '{val}' on:\n {files}".format(
                val=', '.join(compliance.code_validators),
                files='\n '.join(files_list)))
        compliance.check(files_list=files_list)


if __name__ == '__main__':
    main()
