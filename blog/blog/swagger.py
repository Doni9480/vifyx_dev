import re
from django.urls import path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator


class CustomSchema(OpenAPISchemaGenerator):
    def should_include_endpoint(self, path, method, view, public):
        pattern = r"api\/v1\/([a-zA-Z0-9_]+)\/"
        slugify_path = re.search(pattern, path)
        if slugify_path and slugify_path.group(1) not in [
            # "comments",
            # "tests",
            "posts",
            # "quests",
            # "surveys",
            # "blogs",
            # "notifications",
        ]:
            return True
        return False


schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version="v1",
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    generator_class=CustomSchema,
)

urlpatterns = [
    path(
        "swagger<format>/",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
]
