import requests

from librus_tricks import cache as cache_lib
from librus_tricks import exceptions, tools
from librus_tricks.classes import *
from librus_tricks.messages import MessageReader
from datetime import timedelta


class SynergiaClient:
    """Sesja z API Synergii"""

    def __init__(self, user, api_url='https://api.librus.pl/2.0', user_agent='LibrusMobileApp',
                 cache=cache_lib.AlchemyCache(), synergia_user_passwd=None):
        """
        Tworzy sesję z API Synergii.

        :param librus_tricks.auth.SynergiaUser user: Użytkownik sesji
        :param str api_url: Bazowy url api, zmieniaj jeżeli chcesz używać proxy typu beeceptor
        :param str user_agent: User-agent klienta http, domyślnie się podszywa pod aplikację
        :param librus_tricks.cache.CacheBase cache: Obiekt, który zarządza cache
        :param str synergia_user_passwd: Hasło do dziennika Synergia
        """
        self.user = user
        self.session = requests.session()

        if cache_lib.CacheBase in cache.__class__.__bases__:
            self.cache = cache
            self.li_session = self
        else:
            raise exceptions.InvalidCacheManager(f'{cache} can not be a cache object!')

        if synergia_user_passwd:
            self.message_reader = MessageReader(self.user.login, synergia_user_passwd)
        else:
            self.message_reader = None

        self.__auth_headers = {'Authorization': f'Bearer {user.token}', 'User-Agent': user_agent}
        self.__api_url = api_url

    def __repr__(self):
        return f'<Synergia session for {self.user}>'

    @staticmethod
    def assembly_path(*elements, prefix='', suffix='', sep='/'):
        """
        Składa str w jednego str, przydatne przy tworzeniu url.

        :param str elements: Elementy do stworzenia str
        :param str prefix: Początek str
        :param str suffix: Koniec str
        :param str sep: str wstawiany pomiędzy elementy
        :return: Złożony str
        :rtype: str
        """
        for el in elements:
            prefix += sep + str(el)
        return prefix + suffix

    # HTTP part

    @staticmethod
    def dispatch_http_code(response: requests.Response):
        """
        Sprawdza czy serwer zgłasza błąd poprzez podanie kodu http, w przypadku błędu, rzuca wyjątkiem.

        :param requests.Response response:
        :raises librus_tricks.exceptions.SynergiaNotFound: 404
        :raises librus_tricks.exceptions.SynergiaForbidden: 403
        :raises librus_tricks.exceptions.SynergiaAccessDenied: 401
        :raises librus_tricks.exceptions.SynergiaInvalidRequest: 401
        """
        if response.status_code >= 400:
            raise {
                500: Exception('Server error'),
                404: exceptions.SynergiaNotFound(response.url),
                403: exceptions.SynergiaForbidden(response.json()),
                401: exceptions.SynergiaAccessDenied(response.json()),
                400: exceptions.SynergiaInvalidRequest(response.json()),
            }[response.status_code]

    def get(self, *path, request_params=None):
        """
        Zwraca json'a przekonwertowany na dict'a po podaniu prawidłowego url.

        przykład: ``session.get('Grades', '42690')``

        :param path: Ścieżka zawierająca węzeł API
        :type path: str
        :param request_params: dict zawierający kwargs dla zapytania http
        :type request_params: dict
        :return: json przekonwertowany na dict'a
        :rtype: dict
        """
        if request_params is None:
            request_params = dict()
        path_str = self.assembly_path(*path, prefix=self.__api_url)
        response = self.session.get(
            path_str, headers=self.__auth_headers, params=request_params
        )

        self.dispatch_http_code(response)

        return response.json()

    def post(self, *path, request_params=None):
        """
        Pozwala na dokonanie zapytania http POST.

        :param path: Ścieżka zawierająca węzeł API
        :type path: str
        :param request_params: dict zawierający kwargs dla zapytania http
        :type request_params: dict
        :return: json przekonwertowany na dict'a
        :rtype: dict
        """
        if request_params is None:
            request_params = dict()
        path_str = self.assembly_path(*path, prefix=self.__api_url)
        response = self.session.post(
            path_str, headers=self.__auth_headers, params=request_params
        )

        self.dispatch_http_code(response)

        return response.json()

    # Cache

    def get_cached_response(self, *path, http_params=None, max_lifetime=timedelta(hours=1)):
        """
        Wykonuje zapytanie http GET z poprzednim sprawdzeniem cache.

        :param path: Niezłożona ścieżka do węzła API
        :param request_params: dict zawierający kwargs dla zapytania http
        :type request_params: dict
        :param timedelta max_lifetime: Maksymalny czas ważności cache dla tego zapytania http
        :return: dict zawierający odpowiedź zapytania
        :rtype: dict
        """
        uri = self.assembly_path(*path, prefix=self.__api_url)
        response_cached = self.cache.get_query(uri, self.user.uid)

        if response_cached is None:
            http_response = self.get(*path, request_params=http_params)
            self.cache.add_query(uri, http_response, self.user.uid)
            return http_response

        age = datetime.now() - response_cached.last_load

        if age > max_lifetime:
            http_response = self.get(*path, request_params=http_params)
            self.cache.del_query(uri, self.user.uid)
            self.cache.add_query(uri, http_response, self.user.uid)
            return http_response
        return response_cached.response

    def get_cached_object(self, uid, cls, max_lifetime=timedelta(hours=1)):
        """
        Pobiera dany obiekt z poprzednim sprawdzeniem cache. Nie używane domyślnie w bibliotece.

        :param str uid: Id żądanego obiektu
        :param cls: Klasa żądanego obiektu
        :param timedelta max_lifetime: Maksymalny czas ważności cache dla tego obiektu
        :return: Żądany obiekt
        """
        requested_object = self.cache.get_object(uid, cls)

        if requested_object is None:
            requested_object = cls.create(uid=uid, session=self)
            self.cache.add_object(uid, cls, requested_object._json_resource)
            return requested_object

        age = datetime.now() - requested_object.last_load

        if age > max_lifetime:
            requested_object = cls.create(uid=uid, session=self)
            self.cache.del_object(uid)
            self.cache.add_object(uid, cls, requested_object._json_resource)

        return requested_object

    # API query part

    def return_objects(self, *path, cls, extraction_key=None, lifetime=timedelta(seconds=10), bypass_cache=False):
        """
        Zwraca listę obiektów lub obiekt, wygenerowaną z danych danej ścieżki API.

        :param str path: Niezłożona ścieżka do węzła API
        :param cls: Klasa żądanych obiektów
        :param str extraction_key: Klucz do wyjęcia danych, pozostawienie tego parametru na None powoduje
            automatyczną próbę zczytania danych
        :param timedelta lifetime: Maksymalny czas ważności cache dla tego zapytania http
        :param bool bypass_cache: Ustawienie tego parametru na True powoduje ignorowanie mechanizmu cache
        :return:
        :rtype: list of SynergiaGenericClass
        """
        if bypass_cache:
            raw = self.get(*path)
        else:
            raw = self.get_cached_response(*path, max_lifetime=lifetime)

        if extraction_key is None:
            extraction_key = SynergiaGenericClass.auto_extract(raw)

        raw = raw[extraction_key]

        if isinstance(raw, list):
            stack = []
            for stored_payload in raw:
                stack.append(cls.assembly(stored_payload, self))
            return tuple(stack)
        if isinstance(raw, dict):
            return cls.assembly(raw, self)

        return None

    def grades(self, *grades):
        """
        Zwraca daną listę ocen.

        :param int grades: Id ocen
        :rtype: tuple of librus_tricks.classes.SynergiaGrade
        """
        if grades.__len__() == 0:
            return self.return_objects('Grades', cls=SynergiaGrade, extraction_key='Grades')
        else:
            ids_computed = self.assembly_path(*grades, sep=',', suffix=grades[-1])[1:]
            return self.return_objects('Grades', ids_computed, cls=SynergiaGrade, extraction_key='Grades')

    def attendances(self, *attendances):
        """
        Zwraca daną listę obiektów frekwencji.

        :param int attendances: Id obecności
        :rtype: tuple of librus_tricks.classes.SynergiaAttendance
        """
        if attendances.__len__() == 0:
            return self.return_objects('Attendances', cls=SynergiaAttendance, extraction_key='Attendances')
        else:
            ids_computed = self.assembly_path(*attendances, sep=',', suffix=attendances[-1])[1:]
            return self.return_objects('Attendances', ids_computed, cls=SynergiaGrade, extraction_key='Attendances')

    @property
    def illegal_absences(self):
        """
        Zwraca wszystkie nieusprawiedliwione nieobecności.

        :rtype: tuple of librus_tricks.classes.SynergiaAttendance
        """
        def is_absence(k):
            if k.type.uid == '1':
                return True
            else:
                return False

        return tuple(filter(is_absence, self.attendances()))

    @property
    def all_absences(self):
        """
        Zwraca wszystkie nieobecności.

        :rtype: tuple of librus_tricks.classes.SynergiaAttendance
        """
        return tuple(filter(lambda k: k.type.is_presence_kind == False, self.attendances()))

    def exams(self, *exams):
        """
        Zwraca dane sprawdziany, kartkówki etc.

        :param int exams: Id egzaminów
        :rtype: tuple of librus_tricks.classes.SynergiaExam
        """
        if exams.__len__() == 0:
            return self.return_objects('HomeWorks', cls=SynergiaExam, extraction_key='HomeWorks')
        else:
            ids_computed = self.assembly_path(*exams, sep=',', suffix=exams[-1])[1:]
            return self.return_objects('HomeWorks', ids_computed, cls=SynergiaExam, extraction_key='HomeWorks')

    def colors(self, *colors):
        """
        Zwraca dane kolory z dziennika.

        :param int colors: Id kolorów
        :rtype: tuple of librus_tricks.classes.SynergiaColors
        """
        if colors.__len__() == 0:
            return self.return_objects('Colors', cls=SynergiaColor, extraction_key='Colors')
        else:
            ids_computed = self.assembly_path(*colors, sep=',', suffix=colors[-1])
            return self.return_objects('Colors', ids_computed, cls=SynergiaColor, extraction_key='Colors')

    def timetable(self, for_date=datetime.now()):
        """
        Zwraca dict'a którego kluczami są obiekty date.

        :param datetime.datetime for_date: Data dnia, który ma być w planie lekcji
        :rtype: dict[datetime.date, librus_tricks.classes.SynergiaTimetableDay]
        """
        monday = tools.get_actual_monday(for_date).isoformat()
        r = self.get('Timetables', request_params={'weekStart': monday})
        return SynergiaTimetable.assembly(r['Timetable'], self)

    def timetable_day(self, for_date: datetime):
        return self.timetable(for_date)[for_date.date()]

    @property
    def today_timetable(self):
        """
        Zwraca dzisiejszy plan lekcji.

        :rtype: list of librus_tricks.classes.SynergiaTimetableDay
        """
        return self.timetable().days[datetime.now().date()]

    @property
    def tomorrow_timetable(self):
        """
        Zwraca jutrzejszy plan lekcji.

        :rtype: list of librus_tricks.classes.SynergiaTimetableDay
        """
        return self.timetable(datetime.now() + timedelta(days=1)).days[(datetime.now() + timedelta(days=1)).date()]

    def messages(self, *messages):
        """
        Zwraca natywne wiadomości, wymaga mobilnych dodatków.

        :param messages:
        :rtype: tuple of librus_tricks.classes.SynergiaMessages
        """
        if messages.__len__() == 0:
            return self.return_objects('Messages', cls=SynergiaNativeMessage, extraction_key='Messages')
        else:
            ids_computed = self.assembly_path(*messages, sep=',', suffix=messages[-1])[1:]
            return self.return_objects('Messages', ids_computed, cls=SynergiaNativeMessage, extraction_key='Messages')

    def news_feed(self):
        return self.return_objects('SchoolNotices', cls=SynergiaNews, extraction_key='SchoolNotices')

    def subjects(self, *subject):
        """
        Zwraca dane przedmioty.

        :param int subject:
        :rtype: tuple of librus_tricks.classes.SynergiaSubject
        """
        if subject.__len__() == 0:
            return self.return_objects('Subjects', cls=SynergiaSubject, extraction_key='Subjects')
        else:
            ids_computed = self.assembly_path(*subject, sep=',', suffix=subject[-1])[1:]
            return self.return_objects('Subjects', ids_computed, cls=SynergiaSubject, extraction_key='Subjects')

    @property
    def school(self):
        """
        Zwraca informacje o twojej szkole.

        :rtype: librus_tricks.classes.SynergiaSchool
        """
        return self.return_objects('Schools', cls=SynergiaSchool, extraction_key='School')

    @property
    def lucky_number(self):
        """
        Zwraca szczęśliwy numerek.

        :rtype: int
        """
        return self.get('LuckyNumbers')['LuckyNumber']['LuckyNumber']
