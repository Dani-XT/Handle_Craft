from django.views.generic import TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth import get_user_model

from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper

User = get_user_model()

class UsersListView(PermissionRequiredMixin, TemplateView):
    permission_required = ("auth.view_user")
    template_name = "usuarios-list.html"

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        context.update(
            {
                "usuarios": User.objects.all().order_by('id'),
            }
        )

        TemplateHelper.map_context(context)
        return context