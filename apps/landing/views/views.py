from django.views.generic import TemplateView
from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper


class LandingView(TemplateView):
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        context.update(
            {
                "layout": "front",
                "layout_path": TemplateHelper.set_layout("layout_front.html", context),
                "active_url": self.request.path, 
            }
        )

        TemplateHelper.map_context(context)

        return context

    def post(self):
        pass
