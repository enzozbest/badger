from django.test import TestCase, override_settings

from code_tutors.aws import s3


@override_settings(USE_AWS_S3=True)
class TestS3(TestCase):
    def setUp(self):
        self.test_file_path = 'code_tutors/tests_code_tutors/resources/test.pdf'
        self.file_key = 'pdfs/test.pdf'

    def tearDown(self):
        s3.__delete(self.file_key)

    def test_upload_file(self):
        with open(self.test_file_path, 'rb') as f:
            try:
                s3.upload(obj=f, key=self.file_key)
            except Exception as e:
                self.fail("Test raised an exception!")

    def test_get_access_url(self):
        with open(self.test_file_path, 'rb') as f:
            try:
                s3.upload(obj=f, key=self.file_key)
            except Exception as e:
                self.fail("Test raised an exception!")
        url = s3.generate_access_url(key=self.file_key)
        self.assertIsNotNone(url)
        self.assertTrue(isinstance(url, str))
