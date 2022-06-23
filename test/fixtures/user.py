import uuid
import pytest
import json
from faker import Faker
from flask import current_app

from src.models.users import User

@pytest.fixture(scope="class")
def dummy_user(request):

    fake = Faker()

    request.cls.dummy_user = User(
        username=fake.user_name(),
        first_name=fake.first_name_male(),
        last_name=fake.last_name(),
        email=fake.email(),
        password=fake.password()
    )

    return request.cls.dummy_user
