import datetime
import random
from time import strftime, gmtime

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse, Http404, HttpResponseNotAllowed
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView

from emailer.forms import ClientCreateForm, SubscriptionForm, MessageCreateForm, ManagerSubsForm
from emailer.models import Client, Message, MailingSettings, MailingLog, Blog
from emailer.services import send_email, get_cached_details_for_client


class QuerysetForListMixin:
    """
    Выводим для пользователя его список объектов, кроме суперюзера

    """
    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
            get_cached_details_for_client()
            return queryset
        else:
            get_cached_details_for_client()
            return queryset


class FormValidForCreateMixin:
    """
    Вписываем кто создал объект
    """
    def form_valid(self, form):
        self.object = form.save()
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)


class GetObjectInGroupMixin:
    """
    Ограничивает доступ к UpdateView группам manager и content_manager
    """
    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        manager = self.request.user.groups.filter(name='manager').exists()
        content = self.request.user.groups.filter(name='content_manager').exists()
        if manager or content:
            raise Http404
        else:
            return self.object


class GetContextDataForCreateMixin:
    """
    Ограничиваем создание объектов для групп manager и content_manager
    """
    def get_context_data(self, **kwargs):
        manager = self.request.user.groups.filter(name='manager').exists()
        content = self.request.user.groups.filter(name='content_manager').exists()
        if manager or content:
            raise Http404
        else:
            return super().get_context_data(**kwargs)


class ClientCreateView(LoginRequiredMixin, GetContextDataForCreateMixin, FormValidForCreateMixin, CreateView):
    model = Client
    form_class = ClientCreateForm
    success_url = reverse_lazy('emailer:client_list')


class ClientUpdateView(LoginRequiredMixin, GetObjectInGroupMixin, UpdateView):
    model = Client
    form_class = ClientCreateForm

    def get_success_url(self):
        return reverse('emailer:client_detail', args=[self.kwargs.get('pk')])


class ClientListView(LoginRequiredMixin, QuerysetForListMixin, ListView):
    model = Client


class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client


class ClientDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Client
    permission_required = 'emailer.delete_client'
    success_url = reverse_lazy('emailer:client_list')


def main_page(request):
    client_qty = Client.objects.count()
    active_subscriptions = MailingSettings.objects.filter(status='started').count()
    qty_subscriptions = MailingSettings.objects.count()
    blog_list = list(Blog.objects.filter(is_published=True))
    random_blog = random.sample(blog_list, 3)

    context = {
        'client_qty': client_qty,
        'active_subscriptions': active_subscriptions,
        'qty_subscriptions': qty_subscriptions,
        'blog_list': random_blog
    }

    return render(request, 'emailer/index.html', context)


class MailingSettingsCreateView(LoginRequiredMixin, GetContextDataForCreateMixin, FormValidForCreateMixin, CreateView):
    model = MailingSettings
    form_class = SubscriptionForm
    success_url = reverse_lazy('emailer:subscription_list')


class MailingSettingsUpdateView(LoginRequiredMixin, GetObjectInGroupMixin, UserPassesTestMixin, UpdateView):
    model = MailingSettings
    form_class = SubscriptionForm

    def get_success_url(self):
        return reverse('emailer:subscription_detail', args=[self.kwargs.get('pk')])

    def test_func(self):
        first_option = self.request.user.groups.filter(name='manager').exists()
        second_options = self.request.user

        if first_option:
            self.form_class = ManagerSubsForm
            return first_option
        if second_options:
            self.form_class = SubscriptionForm
            return second_options


class MailingSettingsListView(LoginRequiredMixin, QuerysetForListMixin, ListView):
    model = MailingSettings


class MailingSettingsDetailView(LoginRequiredMixin, DetailView):
    model = MailingSettings


class MailingSettingsDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = MailingSettings
    success_url = reverse_lazy('emailer:subscriptions_list')
    permission_required = 'emailer.delete_mailingsettings'


class MessageCreateView(LoginRequiredMixin, GetContextDataForCreateMixin, CreateView):
    model = Message
    form_class = MessageCreateForm
    success_url = reverse_lazy('emailer:message_list')


class MessageUpdateView(LoginRequiredMixin, GetObjectInGroupMixin, UpdateView):
    model = Message
    form_class = MessageCreateForm

    def get_success_url(self):
        return reverse('emailer:message_update', args=[self.kwargs.get('pk')])

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        manager = self.request.user.groups.filter(name='manager').exists()
        content = self.request.user.groups.filter(name='content_manager').exists()
        if not manager or not content:
            raise Http404
        else:
            return self.object


class MessageListView(LoginRequiredMixin, ListView):
    model = Message


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    success_url = reverse_lazy('emailer:message_list')


def send_mails(request):

    now = datetime.datetime.now()
    time_now = strftime('%H:%M:%S', gmtime())

    for ms in MailingSettings.objects.filter(status=MailingSettings.STATUS_STARTED):

        for mc in ms.clients.all():

            ml = MailingLog.objects.filter(client=mc)

            header = {
                'email': mc.email,
                'mess': list(ms.message.values('subject', 'mail')),
                'client': mc,
                'subscription': ms
            }
            if ml.exists():
                last_try_date = str(ml.order_by('-last_try_date').first())
                last_try_date = last_try_date.split('+00:00')[0]
                last_try = datetime.datetime.strptime(last_try_date, '%Y-%m-%d %H:%M:%S.%f')

                if ms.period == MailingSettings.PERIOD_DAILY and ms.time == time_now:

                    if (now - last_try).days >= 1:
                        send_email(header)
                        return HttpResponse()

                elif ms.period == MailingSettings.PERIOD_WEEKLY and ms.time == time_now:
                    if (now - last_try).days >= 7:
                        send_email(header)
                        return HttpResponse()

                elif ms.period == MailingSettings.PERIOD_MONTHLY and ms.time == time_now:
                    if (now - last_try).days >= 30:
                        send_email(ms, mc)
                        return HttpResponse()
            else:

                send_email(header)
                return HttpResponse()

    return HttpResponse()


class BlogCreateView(LoginRequiredMixin, CreateView):
    model = Blog
    fields = ('title', 'content', 'preview_image', 'is_published',)
    success_url = reverse_lazy('emailer:main')


class BlogUpdateView(LoginRequiredMixin, UpdateView):
    model = Blog
    fields = ('title', 'content', 'preview_image',)
    success_url = reverse_lazy('emailer:blog_list')
    permission_required = 'emailer.change_blog'

    def get_success_url(self):
        return reverse('emailer:blog_view', args=[self.kwargs.get('pk')])


class BlogListView(ListView):
    model = Blog

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        queryset = queryset.filter(is_published=True)
        return queryset


class BlogDetailView(DetailView):
    model = Blog

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        self.object.view_count += 1
        self.object.save()
        return self.object


class BlogDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Blog
    success_url = reverse_lazy('emailer:main')
    permission_required = 'emailer.delete_blog'


def toggle_activity(request, pk):
    blog_activity = get_object_or_404(Blog, pk=pk)
    if blog_activity.is_published:
        blog_activity.is_published = False
    else:
        blog_activity.is_published = True

    blog_activity.save()

    return redirect(reverse('emailer:main'))
