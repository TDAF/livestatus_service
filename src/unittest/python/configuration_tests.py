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

from mock import patch, call
import tempfile
import unittest

from livestatus_service.configuration import Configuration, get_current_configuration


class ConfigurationTests(unittest.TestCase):

    def test_constructor_should_raise_exception_when_config_file_does_not_exist(self):
        def callback():
            Configuration(("/foo/bar/does_not_exist.cfg"))

        self.assertRaises(ValueError, callback)

    def test_constructor_should_raise_exception_when_config_file_has_invalid_content(self):
        with tempfile.NamedTemporaryFile() as configuration_file:
            configuration_file.write(b'foobar')
            configuration_file.flush()

            def callback():
                Configuration(configuration_file.name)
            self.assertRaises(ValueError, callback)

    def test_constructor_should_raise_exception_when_config_does_not_contain_expected_section(self):
        with tempfile.NamedTemporaryFile() as configuration_file:
            configuration_file.write(b"[spam]\nspam=eggs")
            configuration_file.flush()

            def callback():
                Configuration(configuration_file.name)
            self.assertRaises(ValueError, callback)

    def test_constructor_should_raise_exception_when_config_contains_error(self):
        with tempfile.NamedTemporaryFile() as configuration_file:
            configuration_file.write(b"[spam]\nspam=%{foobar}")  # illegal variable interpolation
            configuration_file.flush()

            def callback():
                Configuration(configuration_file.name)
            self.assertRaises(ValueError, callback)

    def test_should_return_default_log_file_when_no_log_file_option_is_given(self):
        with tempfile.NamedTemporaryFile() as configuration_file:
            configuration_file.write(b"[livestatus-service]\n")
            configuration_file.flush()
            config = Configuration(configuration_file.name)
            self.assertEqual(config.log_file, Configuration.DEFAULT_LOG_FILE)

    def test_should_return_given_log_file_when_log_file_option_is_given(self):
        with tempfile.NamedTemporaryFile() as configuration_file:
            configuration_file.write(b"[livestatus-service]\nlog_file=spam.log")
            configuration_file.flush()
            config = Configuration(configuration_file.name)
            self.assertEqual(config.log_file, "spam.log")

    def test_should_return_default_livestatus_socket(self):
        with tempfile.NamedTemporaryFile() as configuration_file:
            configuration_file.write(b"[livestatus-service]\n")
            configuration_file.flush()
            config = Configuration(configuration_file.name)
            self.assertEqual(config.livestatus_socket, Configuration.DEFAULT_LIVESTATUS_SOCKET)

    def test_should_return_configured_livestatus_socket(self):
        with tempfile.NamedTemporaryFile() as configuration_file:
            configuration_file.write(b"[livestatus-service]\nlivestatus_socket=foo/bar")
            configuration_file.flush()
            config = Configuration(configuration_file.name)
            self.assertEqual(config.livestatus_socket, "foo/bar")

    def test_should_return_default_icinga_command_file(self):
        with tempfile.NamedTemporaryFile() as configuration_file:
            configuration_file.write(b"[livestatus-service]\n")
            configuration_file.flush()
            config = Configuration(configuration_file.name)
            self.assertEqual(config.icinga_command_file, Configuration.DEFAULT_ICINGA_COMMAND_FILE)

    def test_should_return_configured_icinga_command_file(self):
        with tempfile.NamedTemporaryFile() as configuration_file:
            configuration_file.write(b"[livestatus-service]\nicinga_command_file=foo/bar.cmd")
            configuration_file.flush()
            config = Configuration(configuration_file.name)
            self.assertEqual(config.icinga_command_file, "foo/bar.cmd")


class ConfigurationLoadingTests(unittest.TestCase):

    @patch('livestatus_service.configuration.Configuration')
    def test_get_current_configuration_should_open_default_configuration_file(self, mock_configuration):
        get_current_configuration()

        self.assertEqual(mock_configuration.call_args, call(mock_configuration.DEFAULT_CONFIGURATION_FILE))
