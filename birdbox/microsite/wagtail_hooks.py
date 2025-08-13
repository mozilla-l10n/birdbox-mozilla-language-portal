from django.contrib import messages
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from wagtail import hooks

from wagtailstreamforms.conf import get_setting
from wagtailstreamforms.utils.requests import get_form_instance_from_request

from urllib.parse import urlencode

LOCALE_MAP = {
    "Slovenian": "sl",
    "English (US)": "en-US",
    "English (UK)": "en-GB",
    "Italian": "it",
    "French": "fr",
}

@hooks.register('before_serve_page')
def process_form(page, request, *args, **kwargs):

    if request.method == 'POST':
        form_def = get_form_instance_from_request(request)

        if form_def:
            form = form_def.get_form(request.POST, request.FILES, page=page, user=request.user)
            context = page.get_context(request, *args, **kwargs)

            if form.is_valid():
                form_def.process_form_submission(form)

                if form_def.success_message:
                    messages.success(request, form_def.success_message, fail_silently=True)

                redirect_page = form_def.post_redirect_page or page
                query_params = {
                    "search": form.cleaned_data.get("search"),
                    "locale": LOCALE_MAP.get(form.cleaned_data.get("language"), "en-GB"),
                }
                redirect_url = f"{redirect_page.get_url(request)}?{urlencode(query_params)}"
                return redirect(redirect_url)

            else:
                context.update({
                    'invalid_stream_form_reference': form.data.get('form_reference'),
                    'invalid_stream_form': form
                })
                if form_def.error_message:
                    messages.error(request, form_def.error_message, fail_silently=True)
                return TemplateResponse(
                    request,
                    page.get_template(request, *args, **kwargs),
                    context
                )
