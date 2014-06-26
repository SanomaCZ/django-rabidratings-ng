from django.conf.urls import patterns, include

urlpatterns = patterns('',
    ('^', include('rabidratings.urls', namespace='rabidratings')),
)
