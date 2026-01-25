from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path


class BookrAdminSite(admin.AdminSite):
    title_header = 'Bookr Admin'
    site_header = 'Bookr administration'
    index_title = 'Bookr site admin'

    def profile_view(self, request):
        request.current_app = self.name
        context = self.each_context(request)
        
        return TemplateResponse(request, "admin/admin_profile.html", context)

    def get_urls(self):
        urls = super().get_urls()
        url_patterns = [
            path("admin_profile", self.admin_view(self.profile_view)),
        ]
        return url_patterns + urls


