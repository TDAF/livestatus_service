'''
The MIT License (MIT)

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

import unittest

from livestatus_service.external_commands import get_command_group_and_arg


class ExternalCommandsTests(unittest.TestCase):

    def test_get_command_group_and_arg_for_global_command(self):
        group, arg = get_command_group_and_arg("CHANGE_GLOBAL_HOST_EVENT_HANDLER")
        self.assertEqual(group, "GLOBAL_CMDS")

    def test_get_command_group_and_arg_for_disabled_commands(self):
        group, arg = get_command_group_and_arg("DEL_DOWNTIME_BY_START_TIME_COMMENT")
        self.assertEqual(group, "DISABLED_CMDS")

    def test_get_command_group_and_arg_for_hostname_commands_with_host(self):
        hostname = "HOST"
        group, arg = get_command_group_and_arg("ACKNOWLEDGE_HOST_PROBLEM;%s" % hostname)
        self.assertEqual(group, "HOSTNAME_CMDS")
        self.assertEqual(arg, hostname)

    def test_get_command_group_and_arg_for_servicegroup_commands_without_host(self):
        group, arg = get_command_group_and_arg("DISABLE_SERVICEGROUP_HOST_CHECKS")
        self.assertEqual(group, "SERVICEGROUPNAME_CMDS")
        self.assertEqual(arg, None)

    def test_get_command_group_and_arg_for_servicegroup_commands_with_semicolon(self):
        group, arg = get_command_group_and_arg("DISABLE_SERVICEGROUP_HOST_CHECKS;")
        self.assertEqual(group, "SERVICEGROUPNAME_CMDS")
        self.assertEqual(arg, '')
