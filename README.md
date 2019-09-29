<div align="center">
    <h1>Librus Tricks</h1>

[![Tests](https://img.shields.io/travis/Backdoorek/Librus-Tricks.svg?logo=travis&style=for-the-badge)](https://travis-ci.org/Backdoorek/Librus-Tricks)[![Codacy grade](https://img.shields.io/codacy/grade/afcbb085b8a746db8795c3a5a13054e6.svg?logo=codacy&style=for-the-badge)](https://app.codacy.com/project/Backdoorek/Librus-Tricks/dashboard)

[![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/Backdoorek/Librus-Tricks.svg?color=gray&logo=github&style=for-the-badge)![GitHub commit activity](https://img.shields.io/github/commit-activity/m/Backdoorek/Librus-Tricks.svg?style=for-the-badge)](https://github.com/Backdoorek/Librus-Tricks)

[![PyPI - Downloads](https://img.shields.io/pypi/dm/librus-tricks.svg?style=for-the-badge)![PyPI - Version](https://img.shields.io/pypi/v/librus-tricks.svg?style=for-the-badge)![PyPI - Python Version](https://img.shields.io/pypi/pyversions/librus-tricks.svg?style=for-the-badge)](https://pypi.org/project/librus-tricks/)

Fast and powerful Synergia Librus API wrapper
</div>

## What is inside the box?
 - Flexible cache system (Based on SQLAlchemy ORM)
 - Easy to use authentication process
 - Lazy object loading
 - Use features from `Mobilne Dodatki` or their spare solutions
 - `__repr__` and `__str__` are pretty human readable

## [Docs are here](http://librustricks.kpostek.pl/)

## Install
```text
# Windows
# Latest stable
pip install librus-tricks
# Dev channel
pip install git+https://github.com/Backdoorek/Librus-Tricks.git@prototype

# Linux
# Latest stable
sudo -H pip3 install librus-tricks
# Dev channel
sudo -H pip3 install git+https://github.com/Backdoorek/Librus-Tricks.git@prototype
```

## Examples
```python
# Create session (with support for messages, require the same password for Portal Librus and Synergia)
from librus_tricks import create_session
session = create_session('my@email.com', 'admin1')

# If passwords are different
from librus_tricks import SynergiaClient, authorizer
session = SynergiaClient(authorizer('my@email.com', 'admin1')[0], synergia_user_passwd='admin2')

# Get selected grades
grades = session.grades()
print(*grades)
# + 2+ np - 5 +

# Get future exams
exams = session.exams()
print(*exams)
# <SynergiaExam 2019-09-20 for subject Matematyka> <SynergiaExam 2019-09-24 for subject Język polski>

# Get timetable
timetable = session.today_timetable
print(*timetable.lessons)
# {} {} {} Język angielski Język angielski Matematyka Matematyka Informatyka Informatyka {} {}

# Get messages
messages = session.messages() # Requires mobilne dodatki
print(*messages)
# <SynergiaNativeMessage 417629 at 0x1f644ddd548> <SynergiaNativeMessage 390558 at 0x1f643148488> <SynergiaNativeMessage 286746 at 0x1f643da28c8>
messages = session.message_reader.read_messages() # Uses html scrapper to read messages, doesn't require mobilne dodatki 
print(*messages)
# <Message from ... Artur (... Artur) into /wiadomosci/1/5/417629/f0> <Message from ... Marzenna (... Marzenna) into /wiadomosci/1/5/390558/f0> <Message from SuperAdministrator into /wiadomosci/1/5/286746/f0>
```



> Written with ❤ from a scratch by Krystian _`Backdoorek`_ Postek
>
> Wanna chat? You can find me on [discord](https://discord.gg/WHY87GR) and [telegram](https://t.me/Backdoorek)
