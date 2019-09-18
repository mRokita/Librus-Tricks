import os
import sys

sys.path.extend(['./'])

EMAIL = os.environ['librus_email']
PASSWORD = os.environ['librus_password']

from librus_tricks import create_session, cache

session = create_session(EMAIL, PASSWORD, cache=cache.AlchemyCache(engine_uri='sqlite:///:memory:'))


def test_auth():
    return session.user.is_revalidation_required(use_query=True)


def test_attendance():
    return session.attendances()


def test_exams():
    return session.exams()


def test_grades():
    return session.grades()


def test_timetable():
    return session.tomorrow_timetable, session.today_timetable, session.timetable()


def test_newsfeed():
    return session.news_feed()


def test_messages():
    return session.message_reader.read_messages()


def test_colors():
    return session.colors()


def test_subjects():
    return session.subjects()
