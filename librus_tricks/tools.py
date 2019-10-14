from datetime import datetime, timedelta
import re


def get_next_monday(now=datetime.now()):
    for _ in range(8):
        if now.weekday() == 0:
            return now.date()
        now = now + timedelta(days=1)
    return


def get_actual_monday(now=datetime.now()):
    for _ in range(8):
        if now.weekday() == 0:
            return now.date()
        now = now - timedelta(days=1)
    return


def extract_percentage(grade):
    """

    :param librus_tricks.classes.SynergiaGrade grade:
    :return:
    """
    for comment in grade.comments:
        matches = re.findall(r'(\d+)%', comment.text)
        if matches.__len__() > 0:
            return float(matches[0])
    return


def return_extract_percentages(grades):
    grades = [grade for grade in grades if extract_percentage(grade) is not None]
    subjects = set([grade.subject.name for grade in grades])
    categorized = {}
    for subject in subjects:
        categorized[subject] = []
    for grade in grades:
        categorized[grade.subject.name].append((grade, extract_percentage(grade)))
    return categorized


def no_cache(func):
    def wrapper(*args, **kwargs):
        return func(*args, **{**kwargs, 'expire': 0})

    return wrapper
