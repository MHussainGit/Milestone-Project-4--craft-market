# conftest.py — pytest-django configuration
# pytest.ini sets DJANGO_SETTINGS_MODULE.
#
# Python 3.14 + Django 4.2 compatibility fix:
# django.template.context.BaseContext.__copy__ uses `copy(super())` which
# fails in Python 3.14 because super() objects no longer support __dict__
# attribute assignment.  We patch it here before any tests run.


def _patch_django_template_context():
    from django.template.context import BaseContext

    def _fixed_copy(self):
        new_obj = self.__class__.__new__(self.__class__)
        new_obj.__dict__.update(self.__dict__)
        new_obj.dicts = self.dicts[:]
        return new_obj

    BaseContext.__copy__ = _fixed_copy


_patch_django_template_context()
