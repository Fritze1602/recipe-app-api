"""
Test custom Django management commands
"""
from unittest.mock import patch

from psycopg2 import OperationalError as Psycopg2Error

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase


@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    """Test commands"""

    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for database if database ready"""
        patched_check.return_value = True

        call_command('wait_for_db')
        # Checkes if check method is been called
        # (mocekd method (Command.check) is called)
        patched_check.assert_called_once_with(databases=['default'])

    @patch('time.sleep')
    # Das erzeugt ein Magic Mock Objekt.
    # Reihenfolge der Argumente von innen nach außen. Etwas uninituitiv.
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """
        Test waiting for database when getting operational error
        Side effect is for raise exceptions
        Die ersten beiden Male, soll Error (Psycopg2Error von der DB) werfen,
        dann 3 Operational Errors (von Django) und dann True
        """
        patched_check.side_effect = [Psycopg2Error] * 2 + \
            [OperationalError] * 3 + [True]

        call_command('wait_for_db')

        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=['default'])
