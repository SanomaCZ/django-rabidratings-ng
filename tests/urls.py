from django.conf.urls.defaults import patterns, include

urlpatterns = patterns('',
    ('^', include('rabidratings.urls', namespace='rabidratings')),
)
