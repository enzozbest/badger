import json

from user_system.models import Day, KnowledgeArea, User


def create_test_users() -> None:
    """Function to parse the test_users.json fixture and create corresponding User model objects which are available
    in the database.

    This code has deliberately not been refactored, to keep the loading of users simple: You should never change this
    code. Any relevant changes should only be made to the JSON file, and this function will parse it properly.
    """
    with open('user_system/fixtures/test_users.json', 'r') as file:
        users = json.load(file)

        for user_data in users:
            availability_days = user_data.pop('availability', [])
            knowledge_areas = user_data.pop('knowledge_areas', [])
            user, _ = User.objects.get_or_create(**user_data)

            if availability_days:
                update_availability(user, availability_days)

            if user.is_tutor and knowledge_areas:
                add_knowledge_areas(user, knowledge_areas)


def update_availability(user: User, days: list[str]):
    """Function to update the availability of a user.
    Given a list of day strings (names) and a user, get the corresponding Day model objects and update the availability
    of the user.

    :param user: the user whose availability is to be updated
    :param days: list of day names in which the user is available
    """
    for day_name in days:
        day, _ = Day.objects.get_or_create(day=day_name)
        user.availability.add(day)
        user.save()


def add_knowledge_areas(user: User, areas: list[str]):
    """Function to add knowledge areas to the user's profile.

    Given a user and a list of knowledge area names, add them to the user's profile.
    :param user: the user whose knowledge areas are to be updated
    :param areas: list of knowledge area names in which the user is an expert
    """
    for subject in areas:
        KnowledgeArea.objects.get_or_create(subject=subject, user=user)
