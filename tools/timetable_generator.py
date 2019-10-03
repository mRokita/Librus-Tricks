import os
from librus_tricks import minified_login, SynergiaTimetable

session = minified_login(os.environ['librus_email'], os.environ['librus_password'])

timetable = session.timetable()

def convert_timetable_matrix(timetable: SynergiaTimetable):
    days = timetable.days
    weekdays = []

    for weekday in days.keys():
        if days[weekday].lessons.__len__() > 0:
            weekdays.append(weekday.strftime("%A"))

    matrix = [[] for _ in weekdays]

    matrix_pointer = 0
    for day in days.values():
        for lesson in day.lessons:
            matrix[matrix_pointer].append(lesson)
        matrix_pointer += 1

    return matrix


def matrix_completion(matrix):
    """

    :param list[list[librus_tricks.classes.SynergiaTimetableEvent]] matrix:
    :return:
    """
    first_lesson_no = 1
    last_lesson_no = 1
    for col in matrix:
        for lesson in col:
            if lesson.lesson_no > last_lesson_no:
                last_lesson_no = lesson.lesson_no
            if lesson.lesson_no < first_lesson_no:
                first_lesson_no = lesson.lesson_no

    class EmptyWindow:
        subject = ''

    for col in matrix:
        first_lesson =  col[0].lesson_no
        last_lesson = col[-1].lesson_no

        lessons_to_add_on_beginning = first_lesson - first_lesson_no
        lessons_to_add_on_end = last_lesson_no + last_lesson

        col = [EmptyWindow() for _ in range(lessons_to_add_on_beginning)] + col + [EmptyWindow() for _ in range(lessons_to_add_on_end)]
        




if __name__ == '__main__':
    matrix = convert_timetable_matrix(timetable)
    matrix_completion(matrix)
