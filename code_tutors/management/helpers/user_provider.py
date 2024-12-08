from faker.providers import BaseProvider
from user_system.models.user_model import User


class UserProvider(BaseProvider):
    def student(self):
        students = User.objects.filter(user_type='Student')
        return self.random_element(students) if students else None

    def tutor(self):
        tutors = User.objects.filter(user_type='Tutor')
        return self.random_element(tutors) if tutors else None

    def admin(self):
        admins = User.objects.filter(user_type='Admin')
        return self.random_element(admins) if admins else None
