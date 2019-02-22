import requests

from . import errors as li_err
from .advanced_types import SynergiaGrade, SynergiaTimetableEntry, SynergiaAttendance


class SynergiaSession:
    def __init__(self, user, api_url='https://api.librus.pl/2.0/'):
        """

        :type user: SynergiaSessionUser
        """
        self.user = user
        self.auth_headers = {'Authorization': f'Bearer {user.token}'}
        self.session = requests.session()
        self.__api_url = api_url

    def __repr__(self):
        return f'<Synergia session for {self.user}>'

    def get(self, *path, params=dict()):
        path_str = f'{self.__api_url}'
        for p in path:
            path_str += f'{p}/'
        response = self.session.get(
            path_str,
            headers=self.auth_headers,
            params=params
        )

        if response.status_code == 401:
            raise li_err.TokenExpired(response.text)
            # print(self.auth_headers)
            # print('Token wygasł, pozyskiwanie nowego')
            # print(
            #     f'https://portal.librus.pl/api/SynergiaAccounts/fresh/{self.user.login}')  # TODO: wejście na https://portal.librus.pl/api/SynergiaAccounts/fresh/6379114u roziwązuje problem
            # fr = self.session.get(f'https://portal.librus.pl/api/SynergiaAccounts/fresh/{self.user.login}',
            #                       headers=self.auth_headers)
            # print(fr.text)
            # return self.get(*path, params=params)
        elif response.status_code == 404:
            raise li_err.ObjectNotFound(response.text)
        return response

    def walk(self, path=''):
        """
        Development function, zostanie w najbliższym czasie usunięta
        """
        import json
        print(json.dumps(requests.get(
            f'{self.__api_url}{path}',
            headers=self.auth_headers
        ).json(), indent=2))

    def get_timetable(self, week_start_str=None, type='obj', print_on_collect=False, collect_extra=True):
        """
        Zwraca plan lekcji w postaci tablic z obiektami

        :param week_start_str: Data w formacie rrrr-mm-dd
        :type week_start_str: str
        :param type: Określa typ obiektu, który otrzymujesz na wyjściu (raw, as_dict, obj)
        :type type: str
        :param raw: Określa czy chcesz dostać czystego json'a w formie tekstowej
        :type raw: bool
        :return: json in str, dict lub dict z obiektami
        """
        if type == 'raw':
            if week_start_str:
                return self.get('Timetables', params={'weekStart': week_start_str}).text
            else:
                return self.get('Timetables').text
        elif type == 'as_dict':
            if week_start_str:
                return self.get('Timetables', params={'weekStart': week_start_str}).json()
            else:
                return self.get('Timetables').json()
        elif type == 'obj':
            if week_start_str:
                tt = self.get('Timetables', params={'weekStart': week_start_str}).json()['Timetable']
            else:
                tt = self.get('Timetables').json()['Timetable']
        else:
            raise li_err.WrongOption('Podana opcja jest nie poprawna, wybierz pomiędzy "obj", "as_dict" i "raw"')

        fancy_tt = {}
        for date in tt.keys():
            fancy_tt[date] = []
            if print_on_collect:
                print(date)
            for l_dict in tt[date]:
                if l_dict.__len__() != 0:
                    ste = SynergiaTimetableEntry(l_dict[0], self, collect_extra=collect_extra)
                    fancy_tt[date].append(ste)
                    if print_on_collect:
                        print(ste)
        return fancy_tt

    def get_grades(self, type='obj', print_on_collect=False, collect_extra=False):
        if type == 'raw':
            return self.get('Grades').text
        elif type == 'as_dict':
            return self.get('Grades').json()
        elif type == 'obj':
            grades_list = self.get('Grades')
            grades_list = grades_list.json()['Grades']
        else:
            raise li_err.WrongOption('Podana opcja jest nie poprawna, wybierz pomiędzy "obj", "as_dict" i "raw"')

        obj_grades = {}
        for grade_source in grades_list:
            sg = SynergiaGrade(grade_source, self, get_extra_info=collect_extra)
            if not (sg.subject.oid in obj_grades.keys()):
                obj_grades[sg.subject.oid] = list()
            obj_grades[sg.subject.oid].append(sg)
            if print_on_collect:
                print(grade_source)
                print(sg)
        return obj_grades

    def get_attendances(self, type='obj', print_on_collect=False, collect_extra=False):
        if type == 'raw':
            return self.get('Attendances').text
        elif type == 'as_dict':
            return self.get('Attendances').json()
        elif type == 'obj':
            attendances_list = self.get('Attendances')
            attendances_list = attendances_list.json()['Attendances']
        else:
            raise li_err.WrongOption('Podana opcja jest nie poprawna, wybierz pomiędzy "obj", "as_dict" i "raw"')

        attendances_dict = {}
        for att in attendances_list:
            sa = SynergiaAttendance(att, self, get_extra_info=collect_extra)
            if not (sa.attendance_date in attendances_dict.keys()):
                attendances_dict[sa.attendance_date] = list()
            attendances_dict[sa.attendance_date].append(sa)
            if print_on_collect:
                print(att)
                print(sa)
        return attendances_dict

    def get_lucky_num(self):
        return self.get(
            'LuckyNumbers'
        ).json()['LuckyNumber']


class SynergiaSessionUser:
    def __init__(self, data_dict):
        self.uid = data_dict['id']
        self.login = data_dict['login']
        self.token = data_dict['accessToken']
        self.name, self.surname = data_dict['studentName'].split(' ')

    def __repr__(self):
        return f'<Synergia user called {self.name} {self.surname}>'
