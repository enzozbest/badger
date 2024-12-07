from django.test import TestCase

from code_tutors.aws.resources import yaml_loader


class TestYamlLoader(TestCase):
    def setUp(self):
        self.file = yaml_loader.load_yaml('code_tutors/tests_code_tutors/resources/test.yaml')

    def tearDown(self):
        yaml_loader._yaml_file = None
        yaml_loader._yaml_path = None

    def test_yaml_loader_cache(self):
        file = yaml_loader.load_yaml('code_tutors/tests_code_tutors/resources/test.yaml')
        self.assertIsNotNone(file)
        self.assertEqual(file, self.file)

    def test_get_bucket_name(self):
        bucket_name = yaml_loader.get_bucket_name('invoicer')
        self.assertEqual('test-badger-2024-bucket', bucket_name)

    def test_get_access_role(self):
        access_role_name = yaml_loader.get_role_name('invoicer-s3')
        self.assertEqual('test-badger-2024-access-role', access_role_name)

    def test_get_logo_name(self):
        logo_name = yaml_loader.get_logo_name()
        self.assertEqual('test-logo.jpeg', logo_name)
