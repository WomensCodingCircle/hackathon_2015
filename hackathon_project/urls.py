from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from hackathon_app.views import simple_view

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'hackathon_project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^user_interface/', 'hackathon_app.views.simple_view',name='simple_view'),
)+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
