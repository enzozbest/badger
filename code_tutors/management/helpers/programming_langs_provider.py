from faker.providers import BaseProvider

class ProgrammingLangsProvider(BaseProvider):
    def programming_langs(self):
        langs = ['C++', 'Scala','Python', 'Java', 'Django', 'Robotics', 'Databases', 'JavaScript','Internet Systems']
        return self.random_element(langs)