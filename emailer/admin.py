from django.contrib import admin

from emailer.models import Client, MailingSettings, Message, MailingLog, Blog


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):

    list_display = ('email', 'first_name', 'last_name', 'comment')
    list_filter = ('email',)
    search_fields = ('email',)


@admin.register(MailingSettings)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('pk', 'period', 'status',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'mail',)
    search_fields = ('subject',)


@admin.register(MailingLog)
class MailingLogAdmin(admin.ModelAdmin):
    list_display = ('client', 'subscription', 'status', 'last_try_date',)
    search_fields = ('client', 'status',)


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'content', 'is_published')
    list_filter = ('title', 'is_published',)
