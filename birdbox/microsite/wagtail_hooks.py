from django.contrib import messages
from django.core.management import call_command
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.views.decorators.http import require_GET

from wagtail import hooks
from wagtail.admin import messages
from wagtail.admin.menu import MenuItem

from wagtailstreamforms.utils.requests import get_form_instance_from_request

from urllib.parse import urlencode

from microsite.models import PontoonLocale


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

                try:
                    locale = PontoonLocale.objects.get(code=form.cleaned_data.get("language", "en-GB")).code
                except PontoonLocale.DoesNotExist:
                    locale = "en-GB"

                query_params = {
                    "search": form.cleaned_data.get("search"),
                    "locale": locale,
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


# Admin view that triggers management command
@require_GET
def sync_data_view(request):
    call_command("sync_pontoon_data")
    messages.success(request, "Pontoon data synced successfully.")
    return redirect('/admin/snippets/')

@hooks.register("register_admin_urls")
def register_sync_data_url():
    return [path("pontoon-data/sync/", sync_data_view, name="pontoon_data_sync")]

@hooks.register("register_admin_menu_item")
def register_sync_menu_item():
    return MenuItem(
        "Sync Data",
        reverse("pontoon_data_sync"),
        icon_name="repeat",
        order=1000,
    )
