#!/usr/bin/python3
__author__ = 'Eric Light'
__copyright__ = "Copyleft 2014, Eric Light"
__license__ = "GPLv3"
__version__ = "2014-12-02 (v0.1)"
__maintainer__ = "Eric Light"
__email__ = "eric@ericlight.com"
__status__ = "Production"

from argparse import ArgumentParser
import logging as log
from subprocess import check_output, CalledProcessError
from os import path, mkdir

global VERBOSE


def startup():
    """
    Basic startup, mostly argument checking
    :return: returns the list of passed-in command-line arguments
    """

    parser = ArgumentParser(description="Exports all Virtual Machine definitions from virsh.  Exports definition "
                                        "files to [output_folder]/<domain_name>.xml.")
    parser.add_argument('-v', '--verbose', action='count', help="print more detailed progress messages")
    parser.add_argument('--version', action='version', version='DumpXML version %s' % __version__)
    parser.add_argument('output_folder', nargs='?', help="Path where the XML definitions should be exported (default"
                                                         " is the current working directory)", default='./')

    parsed_arguments = parser.parse_args()

    return parsed_arguments


def check_output_folder(folder_to_check):
    """
    Check that the target output folder exists, and create it if it isn't.

    :param folder_to_check: the target output folder provided by the user at runtime.
    """

    log.debug("Checking the folder at %s" % folder_to_check)
    if not path.exists(folder_to_check):
        log.warning("The folder at %s doesn't exist; creating it..." % folder_to_check)
        try:
            mkdir(folder_to_check)
        except PermissionError:
            exit("You don't have permissions to create that folder; you may need to run with sudo.")
        except Exception as error_details:
            exit("Wow, unexpected problem when trying to access the folder: %s" % error_details)

    log.debug("Output folder at %s looks fine" % folder_to_check)


def trailing_slash(output_folder_name):
    """
    Add a trailing slash to the provided target folder, if needed.
    """

    log.debug("Making sure we were passed a folder name, not a pointer to a file")
    if not output_folder_name[-1:] == '/':
        return output_folder_name + '/'
    return output_folder_name


def find_VM_names():
    """
    Ask virsh to list all the domains; return the results

    :return: Returns a utf-8 encoded string, holding the names of all defined VM's
    """

    try:
        log.debug("Asking virsh for VM names")
        vm_names = check_output(['virsh', 'list', '--name', '--all'])
    except OSError:
        exit("Error listing the VM domain names from virsh.  Do you have virsh installed?")
    except Exception as error_details:
        exit("Wow, unexpected problem when trying to get the domain list from virsh: %s" % error_details)

    return vm_names


def output_XML_definitions(vm_names,output_folder):
    """
    For each defined VM, call virsh dumpxml, and save the results to the target output folder.

    :param vm_names: utf-8 encoded string containing virsh's response to virsh list --name --all
    :param output_folder: the target output folder provided by the user at runtime

    """
    log.debug("Looping through exported VM names & dumping XML")

    for vm_name in vm_names.decode("utf-8").split():
        log.debug("Dumping XML for domain %s to %s%s.xml" % (vm_name, output_folder, vm_name) )

        try:
            with open(output_folder+vm_name+'.xml','w') as xml_output:
                xml_output.write(check_output(['virsh', 'dumpxml', '%s' % vm_name]).decode("utf-8"))
        except IOError:
            exit("Error!  Unable to write to %s" % output_folder+vm_name+'.xml')
        except Exception as error_details:
            exit("Unexpected error when trying to dump the XML into the target files: " % error_details)


if __name__ == "__main__":

    cli_args = startup()

    if cli_args.verbose:
        VERBOSE = True
        log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
        log.debug("Basic startup complete.  Giving verbose output.")
    else:
        VERBOSE = False
        log.basicConfig(format="%(levelname)s: %(message)s")

    output_folder = cli_args.output_folder
    output_folder = trailing_slash(output_folder)
    log.debug("Will save XML definitions to %s" % output_folder)
    check_output_folder(output_folder)

    defined_VMs = find_VM_names()
    log.debug("Got a list of VM names which is %s bytes long." % len(defined_VMs))
    output_XML_definitions(defined_VMs, output_folder)
    log.debug("Looks like everything went fine!")