from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.views.decorators.cache import cache_page

from emailer.apps import EmailerConfig
from emailer.views import ClientCreateView, main_page, ClientListView, ClientDetailView, ClientUpdateView, \
    ClientDeleteView, MailingSettingsCreateView, MailingSettingsListView, MailingSettingsDetailView, \
    MailingSettingsUpdateView, \
    MailingSettingsDeleteView, MessageCreateView, MessageListView, MessageDetailView, MessageUpdateView, \
    MessageDeleteView, send_mails, BlogListView, BlogDetailView, BlogCreateView, BlogUpdateView, BlogDeleteView, \
    toggle_activity

app_name = EmailerConfig.name


urlpatterns = [
    path('', cache_page(5)(main_page), name='main'),

    path('client_create/', ClientCreateView.as_view(), name='client_create'),
    path('client_list/', cache_page(60)(ClientListView.as_view()), name='client_list'),
    path('client_detail/<int:pk>/', ClientDetailView.as_view(), name='client_detail'),
    path('client_update/<int:pk>/', ClientUpdateView.as_view(), name='client_update'),
    path('client_delete/<int:pk>/', ClientDeleteView.as_view(), name='client_delete'),

    path('subscription_create/', MailingSettingsCreateView.as_view(), name='subscription_create'),
    path('subscription_list/', cache_page(60)(MailingSettingsListView.as_view()), name='subscription_list'),
    path('subscription_detail/<int:pk>/', MailingSettingsDetailView.as_view(), name='subscription_detail'),
    path('subscription_update/<int:pk>/', MailingSettingsUpdateView.as_view(), name='subscription_update'),
    path('subscription_delete/<int:pk>/', MailingSettingsDeleteView.as_view(), name='subscription_delete'),

    path('message_create/', MessageCreateView.as_view(), name='message_create'),
    path('message_list/', MessageListView.as_view(), name='message_list'),
    path('message_detail/<int:pk>/', MessageDetailView.as_view(), name='message_detail'),
    path('message_update/<int:pk>/', MessageUpdateView.as_view(), name='message_update'),
    path('message_delete/<int:pk>/', MessageDeleteView.as_view(), name='message_delete'),

    path('blog/', cache_page(60)(BlogListView.as_view()), name='blog_list'),
    path('blog/<int:pk>/veiw/', cache_page(60)(BlogDetailView.as_view()), name='blog_view'),
    path('blog/create/', BlogCreateView.as_view(), name='blog_create'),
    path('blog/edit/<int:pk>/', BlogUpdateView.as_view(), name='blog_edit'),
    path('blog/delete/<int:pk>/', BlogDeleteView.as_view(), name='blog_delete'),
    path('blog/activity/<int:pk>/', toggle_activity, name='blog_toggle_activity'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
