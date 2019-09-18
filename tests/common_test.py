import os
import sys

sys.path.extend(['./'])

from librus_tricks import create_session, cache


def ensure_session():
    if 'session' not in globals():
        global EMAIL
        global PASSWORD
        global session
        EMAIL = os.environ['librus_email']
        PASSWORD = os.environ['librus_password']
        session = create_session(EMAIL, PASSWORD, cache=cache.AlchemyCache(engine_uri='sqlite:///:memory:'))


def test_auth():
    ensure_session()
    return session.user.is_valid


def test_attendance():
    ensure_session()
    return session.attendances()


def test_exams():
    ensure_session()
    return session.exams()


def test_grades():
    ensure_session()
    return session.grades()


def test_timetable():
    ensure_session()
    return session.tomorrow_timetable, session.today_timetable, session.timetable()


def test_newsfeed():
    ensure_session()
    return session.news_feed()


def test_messages():
    ensure_session()
    return session.message_reader.read_messages()


def test_colors():
    ensure_session()
    return session.colors()


def test_subjects():
    ensure_session()
    return session.subjects()


def test_school():
    ensure_session()
    return session.school


def test_lucky():
    ensure_session()
    return session.lucky_number
