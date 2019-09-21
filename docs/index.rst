.. Librus-Tricks documentation master file, created by
   sphinx-quickstart on Sat Sep 21 09:23:54 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Dokumentacja Librus Tricks
===========================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   auth
   core
   classes

Instalacja
===========

.. code-block:: bash

   pip install librus_tricks

Quick start
============

Stwórzmy sobie sesję

.. code-block:: python

   from librus_tricks import create_session
   session = create_session('kocham@librus.pl', 'SynergiaJestSuper')

To wszystko!

Może teraz byśmy sobie wyświetli oceny...

>>> session.grades_categorized
{'Fizyka': [<SynergiaGrade 5 from SynergiaSubject with id 37660 added 2019-09-17 10:05:41>, <SynergiaGrade 5 from SynergiaSubject with id 37660 added 2019-09-19 11:42:34>], 'Informatyka': [<SynergiaGrade 2+ from SynergiaSubject with id 37664 added 2019-09-11 11:38:11>], 'Matematyka': [<SynergiaGrade + from SynergiaSubject with id 37670 added 2019-09-04 08:47:47>], 'Wychowanie fizyczne': [<SynergiaGrade 5 from SynergiaSubject with id 37678 added 2019-09-20 11:33:49>]}

Sprawdźmy teraz kiedy nie było ciebie w szkole

>>> session.all_absences
(<SynergiaAttendance at 2019-09-05 08:14:51 (1615317)>, <SynergiaAttendance at 2019-09-05 09:58:28 (1795174)>, <SynergiaAttendance at 2019-09-05 10:21:47 (1838202)>, <SynergiaAttendance at 2019-09-05 11:23:10 (1953054)>, <SynergiaAttendance at 2019-09-05 11:54:54 (2015674)>, <SynergiaAttendance at 2019-09-05 13:00:22 (2130346)>, <SynergiaAttendance at 2019-09-09 08:21:46 (3591701)>, <SynergiaAttendance at 2019-09-20 13:37:29 (14515355)>, <SynergiaAttendance at 2019-09-20 13:38:06 (14516604)>)


Indeksy
========

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
