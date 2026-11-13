from django.test import TestCase

# Создайте ваши тесты здесь

import datetime
from django.utils import timezone

from django import forms
from catalog.forms import RenewBookForm

class RenewBookFormTest(TestCase):

    def test_renew_form_has_date_field(self):
        form = RenewBookForm()
        self.assertIsInstance(form.fields["renewal_date"], forms.DateField)

    def test_renewal_date_is_required(self):
        form = RenewBookForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("renewal_date", form.errors)

    def test_renew_form_date_in_past(self):
        date = timezone.localdate() - datetime.timedelta(days=1)
        form_data = {'renewal_date': date}
        form = RenewBookForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_renew_form_date_too_far_in_future(self):
        date = timezone.localdate() + datetime.timedelta(weeks=4) + datetime.timedelta(days=1)
        form_data = {'renewal_date': date}
        form = RenewBookForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_renew_form_date_today(self):
        date = timezone.localdate()
        form_data = {'renewal_date': date}
        form = RenewBookForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_renew_form_date_max(self):
        date = timezone.localdate() + datetime.timedelta(weeks=4)
        form_data = {'renewal_date': date}
        form = RenewBookForm(data=form_data)
        self.assertTrue(form.is_valid())
