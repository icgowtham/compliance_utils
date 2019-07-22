"""Design compliance utility."""

import inspect
import sys

from compliance_check import Compliance
from config import (
    OKAY_MSG,
    ERROR_MSG)
from helper_utils import (
    get_plugins,
    load_plugin,
    get_function_calls_from_file,
    get_imported_modules_from_file)


class RegisterDict(dict):
    """For registering the methods by name."""

    def __call__(self, name):
        """Making it simpler to use."""

        def func_wrapper(func):
            """Function wrapper."""
            self[name] = func
            return func

        return func_wrapper


class DesignCompliance(Compliance):
    """Class to handle Design Compliance."""

    register = RegisterDict()
    check_types = None
    inspectMap = {
        'class': inspect.isclass,
        'module': inspect.ismodule,
        'function': inspect.isfunction
    }
    _default_checks = ['DebugEnabledCheck', 'OtherComplianceCheck']

    def __init__(self,
                 default_checks=None, ):
        """
        Initialization method.

        :param default_checks: OPTIONAL list @n
            List of checks to perform by default.
        """
        super(DesignCompliance, self).__init__()
        if default_checks:
            self._defaultTcChecks = default_checks[:]

    def parse_args(self, description=None):
        """
        Parse command line arguments.

        Extends from class Compliance.

        :param description: OPTIONAL string @n
            Description of the program.
        :return: object
        """
        parser = super(DesignCompliance, self).parse_args(description)
        parser.add_argument(
                '--check_type',
                default=['module', 'function', 'class'],
                help='The type of checks (module, function, class)')
        args = parser.parse_args()
        self.check_types = args.check_type
        return parser

    def get_files_list(self, description=None):
        """
        Get the list of files to check.

        :param description: OPTIONAL string @n
            Description of the program.
        :return: list
        """
        return super(DesignCompliance, self).get_files_list(description)

    def check(self, files_list):
        """
        Check for design compliance.

        :param files_list: MANDATORY list @n
            List to files to check.
        :return: None
        """
        if files_list:
            self.check_files(files_list=files_list)
            print("No design compliance issues found in the files. " + OKAY_MSG)

    def check_files(self, files_list):
        """
        Check files belonging to Eureka infrastructure for various compliance.

        :param files_list: MANDATORY list @n
            List of files to check.
        :return: None
        """
        for file_name in files_list:
            imported_modules = get_imported_modules_from_file(file_name=file_name)
            function_calls = get_function_calls_from_file(file_name=file_name)
            kwargs = {'file_name': file_name,
                      'imported_modules': imported_modules,
                      'function_calls': function_calls}
            for name in self.register:
                if name in self._defaultInfraChecks:
                    self.call_registered(name, **kwargs)

    @register('OtherComplianceCheck')
    def check_for_other_compliance(self, **kwargs):
        """
        Method to check various other design compliance.

        :param kwargs: MANDATORY dict @n
            Dictionary containing the required values.
        :return: None
        """
        files_list = kwargs['files_list']
        for plugin in get_plugins():
            compliance_check_plugin = load_plugin(plugin=plugin)
            compliance_check_plugin.run(filesList=files_list)

    @register('DebugEnabledCheck')
    def check_if_debug_enabled(self, **kwargs):
        """
        Check whether a file contains calls to the debugger and/or print statements.

        :param kwargs: MANDATORY dict @n
            Dictionary containing the required values.
        :return: None
        """
        file_name = kwargs['file_name']
        imported_modules = kwargs['imported_modules']
        function_calls = kwargs['function_calls']
        files_with_debugging_enabled = set()

        if 'ipdb' in imported_modules or 'pdb' in imported_modules or \
                'ipdb.set_trace' in function_calls or 'pdb.set_trace' in function_calls:
            files_with_debugging_enabled.add(file_name)
            error_msg = ERROR_MSG + " {file} has debugging enabled!".format(file=file_name)
            print(error_msg)
        if 'print' in function_calls:
            files_with_debugging_enabled.add(file_name)
            error_msg = ERROR_MSG + " {file} contains print statements!".format(file=file_name)
            print(error_msg)

        if files_with_debugging_enabled:
            error_msg = ERROR_MSG + " Debug statements and/or print statements found: "
            print(error_msg + "\n".join(files_with_debugging_enabled))
            sys.exit(1)

    def call_registered(self, name=None, *args, **kwargs):
        """Call the function via name lookup."""
        func = self.register.get(name, None)
        if func is None:
            raise Exception("No function registered against - " + str(name))
        return func(self, *args, **kwargs)


def main():
    """Main function to check if unsupported packages are imported in test files."""
    sys.path.insert(0, "../../")
    sys.path.insert(0, ".")

    compliance = DesignCompliance()
    files_list = compliance.get_files_list("Check for any non supported packages used in swtc")

    if files_list:
        compliance.check(files_list=files_list)


if __name__ == '__main__':
    main()
