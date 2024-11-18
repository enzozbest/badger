from faker.providers import BaseProvider

class TermProvider(BaseProvider):
    def term(self):
        terms = ['September', 'January', 'May']
        return self.random_element(terms)