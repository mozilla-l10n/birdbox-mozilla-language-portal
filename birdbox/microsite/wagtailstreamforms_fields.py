# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django import forms

from wagtailstreamforms.fields import BaseField, register

from microsite.models import PontoonLocale


class PontoonLocaleChoiceField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):

        locales = PontoonLocale.objects.all().order_by("name")
        choices = [(l.code, f"{l.name} · {l.code}") for l in locales]
        kwargs.setdefault("choices", choices)
        kwargs.setdefault("required", False)
        super().__init__(*args, **kwargs)


@register("pontoon_locale_dropdown")
class PontoonLocaleDropdown(BaseField):
    """
    Streamforms field: shows a dropdown of Pontoon locales.
    Appears in the form builder as a new field type.
    """

    field_class = PontoonLocaleChoiceField
    icon = "globe"
    label = "Pontoon Locale (synced)"
