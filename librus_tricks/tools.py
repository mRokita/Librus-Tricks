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


def weighted_average(*grades_and_weights):
    values = 0
    count = 0
    for grade_weight in grades_and_weights:
        count += grade_weight[1]
        for _ in range(grade_weight[1]):
            values += grade_weight[0]

    return values / count


def extracted_percentages(grades):
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


def percentage_average(grades, count_generics=5):
    def compare_lists(list_a, list_b):
        result = []
        for item in list_a:
            if item not in list_b:
                result.append(item)
        return result

    percentages = extracted_percentages(grades)
    generics = compare_lists(grades, [grade_weight_tuple[0] for grade_weight_tuple in tuple(percentages.values())[0]])
    averages = {}
    for subject_name in percentages:
        averages[subject_name] = weighted_average(
            *[(grade_percent[1], grade_percent[0].category.weight) for grade_percent in percentages[subject_name]],
            *[((generic.real_value / count_generics) * 100, generic.category.weight) for generic in generics if
              count_generics is not None or not False if generic.real_value is not None if
              generic.subject.name == subject_name]
        )
    return averages


def subjects_averages(subject_keyed_grades):
    averages = {}
    for subject in subject_keyed_grades:
        averages[subject] = weighted_average(
            *[(grade.real_value, grade.category.weight) for grade in subject_keyed_grades[subject] if
              grade.real_value is not None]
        )

    return averages


def count_attendances(attendances):
    """

    :param iterable[librus_tricks.classes.SynergiaAttendance] attendances:
    :return:
    """
    categories = set()
    for attendance in attendances:
        categories.add(attendance.type.name)

    results = {}
    for cat in categories:
        results[cat] = 0

    for attendance in attendances:
        results[attendance.type.name] += 1

    return results


def present_percentage(attendances):
    """

    :param list[librus_tricks.classes.SynergiaAttendance] attendances:
    :return:
    """
    present = 0
    absent = 0
    for attendance in attendances:
        if attendance.type.is_presence_kind:
            present += 1
        else:
            absent += 1

    return present / attendances.__len__() * 100


def percentages_of_attendances(attendances):
    """

    :param list[librus_tricks.classes.SynergiaAttendance] attendances:
    :return:
    """
    results = count_attendances(attendances)
    for category in results:
        results[category] = results[category] / attendances.__len__() * 100

    return results
