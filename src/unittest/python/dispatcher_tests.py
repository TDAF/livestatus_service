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

from mock import patch, Mock
import unittest

from livestatus_service.dispatcher import perform_command, perform_query, check_contact_permissions, check_auth_contactgroup_cmds


class DispatcherTests(unittest.TestCase):

    @patch('livestatus_service.dispatcher.get_current_configuration')
    @patch('livestatus_service.dispatcher.perform_livestatus_command')
    def test_perform_command_should_dispatch_to_livestatus_if_handler_is_livestatus(self, cmd, current_config):
        mock_config = Mock()
        mock_config.livestatus_socket = '/path/to/socket'
        mock_config.admins = ["admin"]
        current_config.return_value = mock_config

        perform_command('FOO;bar', None, handler='livestatus', auth="admin")

        cmd.assert_called_with('FOO;bar', '/path/to/socket', None, auth='admin')

    @patch('livestatus_service.dispatcher.get_current_configuration')
    @patch('livestatus_service.dispatcher.perform_icinga_command')
    def test_perform_command_should_dispatch_to_icinga_if_handler_is_icinga(self, cmd, current_config):
        mock_config = Mock()
        mock_config.icinga_command_file = '/path/to/commandfile.cmd'
        mock_config.admins = ["admin"]
        current_config.return_value = mock_config

        perform_command('FOO;bar', key=None, handler='icinga', auth="admin")

        cmd.assert_called_with('FOO;bar', '/path/to/commandfile.cmd', None, auth='admin')

    @patch('livestatus_service.dispatcher.get_current_configuration')
    def test_perform_command_should_raise_exception_when_handler_does_not_exist(self, current_config):
        mock_config = Mock()
        current_config.return_value = mock_config
        self.assertRaises(BaseException, perform_command, 'FOO;bar', None, 'mylittlepony')

    @patch('livestatus_service.dispatcher.get_current_configuration')
    def test_perform_query_should_raise_exception_when_handler_does_not_exist(self, current_config):
        mock_config = Mock()
        current_config.return_value = mock_config
        self.assertRaises(BaseException, perform_query, 'GET HOSTS', None, 'mylittlepony')

    @patch('livestatus_service.dispatcher.get_current_configuration')
    @patch('livestatus_service.dispatcher.perform_livestatus_query')
    def test_perform_query_should_dispatch_to_livestatus_if_handler_is_livestatus(self, query, current_config):
        mock_config = Mock()
        mock_config.livestatus_socket = '/path/to/socket'
        mock_config.admins = []
        current_config.return_value = mock_config

        perform_query('FOO;bar', key=None, handler='livestatus', auth='user')

        query.assert_called_with('FOO;bar', '/path/to/socket', None, auth='user')

    @patch('livestatus_service.dispatcher.get_current_configuration')
    @patch('livestatus_service.dispatcher.perform_livestatus_query')
    def test_perform_query_should_dispatch_to_livestatus_if_handler_is_livestatus_admin_default_is_none(self, query, current_config):
        mock_config = Mock()
        mock_config.livestatus_socket = '/path/to/socket'
        mock_config.admins = []
        current_config.return_value = mock_config

        perform_query('FOO;bar', key=None, handler='livestatus')

        query.assert_called_with('FOO;bar', '/path/to/socket', None, auth=None)

    @patch('livestatus_service.dispatcher.get_current_configuration')
    @patch('livestatus_service.dispatcher.perform_livestatus_query')
    def test_perform_query_should_dispatch_to_livestatus_with_auth_none_if_admin_user(self, query, current_config):
        mock_config = Mock()
        mock_config.livestatus_socket = '/path/to/socket'
        mock_config.admins = ["admin"]
        current_config.return_value = mock_config

        perform_query('FOO;bar', key=None, handler='livestatus', auth="admin")

        query.assert_called_with('FOO;bar', '/path/to/socket', None, auth=None)


    @patch('livestatus_service.dispatcher.check_auth_contactgroup_cmds')
    def test_check_contact_permissions_should_call_cmd_group_check_function(self, check_func):
        check_contact_permissions("DISABLE_CONTACTGROUP_HOST_NOTIFICATIONS;contactgroup", "admin")
        check_func.assert_called_with("admin", "contactgroup")

    @patch('livestatus_service.dispatcher.check_auth_contactgroup_cmds')
    def test_check_contact_permissions_should_call_cmd_group_check_function(self, check_func):
        self.assertRaises(NameError, check_contact_permissions, "NO_EXISTANT_COMMAND;contactgroup", "admin")

    @patch('livestatus_service.dispatcher.perform_query')
    def test_check_auth_func_return_false_if_empty_response(self, query):
        query.return_value = "[]"

        self.assertFalse(check_auth_contactgroup_cmds("admin","param"))

    @patch('livestatus_service.dispatcher.perform_query')
    def test_check_auth_func_return_true_if_non_empty_response(self, query):
        query.return_value = '["something"]'

        self.assertTrue(check_auth_contactgroup_cmds("admin","param"))

    @patch('livestatus_service.dispatcher.check_contact_permissions')
    @patch('livestatus_service.dispatcher.get_current_configuration')
    @patch('livestatus_service.dispatcher.perform_livestatus_command')
    def test_perform_command_should_call_check_contact_permissions_if_not_admin(self, cmd, current_config, perm):
        mock_config = Mock()
        mock_config.livestatus_socket = '/path/to/socket'
        mock_config.admins = ["admin"]
        current_config.return_value = mock_config

        perform_command('FOO;bar', None, handler='livestatus', auth="ftp")

        perm.assert_called_with('FOO;bar', 'ftp')

    @patch('livestatus_service.dispatcher.check_contact_permissions')
    @patch('livestatus_service.dispatcher.get_current_configuration')
    @patch('livestatus_service.dispatcher.perform_livestatus_command')
    def test_perform_command_should_call_check_contact_permissions_if_not_admin(self, cmd, current_config, perm):
        mock_config = Mock()
        mock_config.livestatus_socket = '/path/to/socket'
        mock_config.admins = ["admin"]
        current_config.return_value = mock_config

        perform_command('FOO;bar', None, handler='livestatus', auth="admin")

        self.assertFalse(perm.called)
