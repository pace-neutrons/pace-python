# Find BASH
# This module looks for BASH and sets the following:
# BASH_COMMAND - Command suitable for running .sh scripts

find_program(BASH_EXECUTABLE
	NAMES bash
	DOC "BASH command"
)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(
	BASH
	REQUIRED_VARS
    BASH_EXECUTABLE
)

mark_as_advanced (BASH_EXECUTABLE)
