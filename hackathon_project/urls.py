from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from hackathon_app.views import getNeuronNames, clothoView

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'hackathon_project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^clotho/', 'hackathon_app.views.clothoView', name='clotho'),
)+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
