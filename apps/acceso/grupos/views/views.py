from django.views.generic import TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import Group

from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper



class GruposListView(PermissionRequiredMixin, TemplateView):
    permission_required = ("auth.view_user")
    template_name = "grupos-list.html"

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        context.update(
            {
                "grupos": Group.objects.all().order_by('id'),
            }
        )

        TemplateHelper.map_context(context)
        return context