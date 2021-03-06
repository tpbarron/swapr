from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
admin.autodiscover()


breaks_urls = patterns('swapr.classifieds.views',
    url(r'^$', 'breaks'),
    url(r'^(?P<break_id>\d+)/$', 'break_detail'),
    url(r'^add/$', 'break_add'),
    url(r'^search/$','break_search'),
)

sales_urls = patterns('swapr.classifieds.views',
    url(r'^$', 'products'),
    url(r'^(?P<prod_id>\d+)/$', 'product_detail'),
    url(r'^add/$', 'product_add'),
    url(r'^search/$','product_search'),
)

books_urls = patterns('swapr.classifieds.views',
    url(r'^$', 'books'),
    url(r'^(?P<book_id>\d+)/$', 'book_detail'),
    url(r'^add/$', 'book_add'),
    url(r'^category/(?P<cat>[^/]+)/$', 'book_category'),
    url(r'^search/$','book_search'),
)

discussions_urls = patterns('swapr.classifieds.views',
    url(r'^$', 'discussions'),
    url(r'^(?P<disc_id>\d+)/$', 'discussion_detail'),
    url(r'^add/$', 'discussion_add'),
    url(r'^search/$','discussion_search'),
    url(r'^vote/(?P<v>\d+)/(?P<disc_id>\d+)/$', 'vote'),
)

events_urls = patterns('swapr.classifieds.views',
    url(r'^$', 'events'),
    url(r'^(?P<event_id>\d+)/$', 'event_detail'),
    url(r'^add/$', 'event_add'),
    url(r'^calendar/$', 'events_calendar'),
    url(r'^data/$', 'events_json'),
    url(r'^search/$','event_search'),
    url(r'^(?P<event_id>\d+)/qrcode/$', 'event_qrcode'),
    url(r'^ajax/reversegeocode/$', 'event_map_reverse_geocode'),
)

transportation_urls = patterns('swapr.classifieds.views',
    url(r'^$', 'transportation'),
    url(r'^(?P<trans_id>\d+)/$', 'transportation_detail'),
    url(r'^add/$', 'transportation_add'),
    url(r'^search/$','transportation_search'),
)

settings_urls = patterns('swapr.classifieds.views',
    url(r'^$', 'user_settings'),
    url(r'^edit$', 'edit_user_settings'),
)


urlpatterns = patterns('swapr.classifieds.views',
    url(r'^$', 'home', name='home'),
    url(r'^about', 'about'),
    
    url(r'^login/$', 'login'),
    url(r'^login-error/$', 'login_error'),
    url(r'^logout/$', 'logout'),
    url(r'^newuser/$', 'new_user'),
    url(r'^passwordreset_email/$', 'password_reset_email'),
    url(r'^passwordreset_password/(?P<key>[^/]+)/$', 'password_reset_password'),
    
    url(r'^thanks/$', 'thanks'),
    url(r'^feedback/$', 'feedback'),
    url(r'^confirmation/(?P<key>[^/]+)/$', 'confirm_account'),
    url(r'^contact/(?P<uname>[^/]+)/$', 'contact_user'),
    url(r'^completed/(?P<item_type>[^/]+)/(?P<item_id>\d+)/$', 'item_completed'),
    url(r'^delete_comment/(?P<item_type>[^/]+)/(?P<item_id>\d+)/(?P<comment_id>\d+)/$', 'delete_comment'),
    
    url(r'^breaks/', include(breaks_urls)),
    url(r'^sales/', include(sales_urls)),
    url(r'^books/', include(books_urls)),
    url(r'^suggestions/', include(discussions_urls)),
    url(r'^rides/', include(transportation_urls)),
    url(r'^events/', include(events_urls)),
    url(r'^settings/', include(settings_urls)),
    
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

