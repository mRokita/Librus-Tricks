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


def test_grades():
    ensure_session()
    grades = session.grades()
    teachers = [x.teacher for x in grades]
    subjects = [x.subject for x in grades]
    cats = [x.category for x in grades]
    return teachers, subjects, cats


def test_attendances():
    ensure_session()
    att = session.attendances()
    types = [x.type for x in att]
    return att, types


def test_timetable():
    ensure_session()
    timetable = session.today_timetable.lessons
    subjects = []
    for lesson in timetable:
        subjects.append(lesson.subject)
