import os
from dotenv import load_dotenv

from django.test import TestCase, override_settings

from todo.tasks import send_code_on_email


class TasksTestCase(TestCase):

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True, CELERY_TASK_EAGER_PROPOGATES=True)
    def test_send_code_on_email(self):

        load_dotenv()
        
        code = 12345
        email = os.getenv('EMAIL')
        result = send_code_on_email.delay(code, email)

        self.assertTrue(result.successful())
        self.assertIsNone(result.get())
