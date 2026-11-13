from datetime import timedelta

from django import forms
from django.utils import timezone


class RenewBookForm(forms.Form):
    renewal_date = forms.DateField(
        label="Новая дата возврата",
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
    )

    def clean_renewal_date(self):
        new_date = self.cleaned_data["renewal_date"]
        today = timezone.localdate()

        if new_date < today:
            raise forms.ValidationError("Дата возврата не может быть в прошлом.")

        if new_date > today + timedelta(weeks=4):
            raise forms.ValidationError("Выбери дату в пределах четырёх недель от сегодня.")

        return new_date