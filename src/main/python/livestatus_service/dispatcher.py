'''
The MIT License (MIT)

Copyright (c) 2013 ImmobilienScout24

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

from __future__ import absolute_import
from livestatus_service.configuration import get_current_configuration
from livestatus_service.icinga import perform_command as perform_icinga_command
from livestatus_service.livestatus import perform_query as perform_livestatus_query
from livestatus_service.livestatus import perform_command as perform_livestatus_command
from livestatus_service.external_commands import get_command_group_and_arg
import logging

'''
    Decides how queries and commands are performed based on the 'handler'.
    Then performs the query or command after determining run-time configuration.
'''

LOGGER = logging.getLogger('livestatus.livestatus')


def perform_query(query, key=None, auth=None, handler=None):
    configuration = get_current_configuration()

    # Admins could query everything
    if auth in configuration.admins:
        auth = None

    if _is_livestatus_handler(handler):
        socket_path = configuration.livestatus_socket
        return perform_livestatus_query(query, socket_path, key, auth=auth)

    raise ValueError('No handler {0}.'.format(handler))


def check_contact_permissions(command, auth):
    cmd_group, param = get_command_group_and_arg(command)
    LOGGER.debug("cmd_group: %s, param: %s", cmd_group, param)

    LOGGER.debug("Checking if contact {0} has permissions to execute {1}".format(auth, command))

    check_function_name = "check_auth_%s" % cmd_group.lower()
    if not eval(check_function_name)(auth, param):
        raise ValueError('{0} is not allowed to run {1} or target is empty'.format(auth, command))
    else:
        LOGGER.debug("Access allowed")


def check_auth_contactgroup_cmds(auth, param):
    # For this table auth is ignored. We check if our contact is in the target contactgroup
    contactgroups = eval(perform_query("GET contactgroups\nColumns: name\nFilter: name = %s\nFilter: members >= %s" % (param, auth), auth=auth))
    LOGGER.debug("check_auth_hostgroupname_cmds, query result: %s", contactgroups)
    return len(contactgroups) > 0


def check_auth_contactname_cmds(auth, param):
    # For this table auth is ignored. We check if our contact is the target
    contact = eval(perform_query("GET contacts\nColumns: name\nFilter: name = %s" % auth, auth=auth))
    LOGGER.debug("check_auth_hostgroupname_cmds, query result: %s", contact)
    return len(contact) > 0


def check_auth_hostgroupname_cmds(auth, param):
    hostgroups = eval(perform_query("GET hostgroups\nColumns: name\nFilter: name = %s" % param, auth=auth))
    LOGGER.debug("check_auth_hostgroupname_cmds, query result: %s", hostgroups)
    return len(hostgroups) > 0


def check_auth_servicegroupname_cmds(auth, param):
    servicegroups = eval(perform_query("GET servicegroups\nColumns: name\nFilter: name = %s" % param, auth=auth))
    LOGGER.debug("check_auth_servicegroupname_cmds, query result: %s", servicegroups)
    return len(servicegroups) > 0


def check_auth_hostname_cmds(auth, param):
    hosts = eval(perform_query("GET hosts\nColumns: host_name\nFilter: host_name = %s" % param, auth=auth))
    LOGGER.debug("check_auth_hostname_cmds, query result: %s", hosts)
    return len(hosts) > 0


def check_auth_commentid_cmds(auth, param):
    """Hard to check if user has permission to modify a comment by it's id and not very useful"""
    return False


def check_auth_downtimeid_cmds(auth, param):
    """Hard to check if user has permission to modify a downtime by it's id and not very useful"""
    return False


def check_auth_disabled_cmds(auth, param):
    """Commands hard to check if user has permission to modify"""
    return False


def check_auth_global_cmds(auth, param):
    """Commands that affect all system. Only admins"""
    return False


def perform_command(command, key=None, auth=None, handler=None):
    configuration = get_current_configuration()

    LOGGER.debug("admins: %s", configuration.admins)
    # Admins users could run all commands
    if auth not in configuration.admins:
        check_contact_permissions(command, auth)

    if _is_livestatus_handler(handler):
        socket_path = configuration.livestatus_socket
        return perform_livestatus_command(command, socket_path, key, auth=auth)
    elif handler == 'icinga':
        command_file_path = configuration.icinga_command_file
        return perform_icinga_command(command, command_file_path, key, auth=auth)

    raise ValueError('No handler {0}.'.format(handler))


def _is_livestatus_handler(handler):
    return handler is None or handler == 'livestatus'
