# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from django.conf import settings
from django.utils.translation import trans_real

from microsite.models import PontoonLocale


def google_tag(request):
    return {"GOOGLE_TAG_ID": settings.GOOGLE_TAG_ID}


def default_locale(request):
    """Get default locale from Accept-language request header."""

    header = request.META.get("HTTP_ACCEPT_LANGUAGE", "")
    accept = trans_real.parse_accept_lang_header(header)
    locales = PontoonLocale.objects.values_list("code", flat=True)

    for a in accept:
        for locale in locales:
            if a[0].casefold() == locale.casefold():
                return {"default_locale": locale}

    return {"default_locale": "en-GB"}
