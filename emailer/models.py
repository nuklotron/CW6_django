from django.db import models


# Create your models here.
NULLABLE = {'blank': True, 'null': True}


class Client(models.Model):
    email = models.EmailField(verbose_name='email', unique=True)
    first_name = models.CharField(max_length=100, verbose_name='имя', **NULLABLE)
    last_name = models.CharField(max_length=100, verbose_name='фамилия', **NULLABLE)
    comment = models.TextField(verbose_name='комментарий', **NULLABLE)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='создал', **NULLABLE)

    def __str__(self):
        return f'{self.email}'

    class Meta:
        verbose_name = 'клиент'
        verbose_name_plural = 'клиенты'


class MailingSettings(models.Model):
    PERIOD_DAILY = 'daily'
    PERIOD_WEEKLY = 'weekly'
    PERIOD_MONTHLY = 'monthly'

    PERIODS = (
        (PERIOD_DAILY, 'Ежедневная'),
        (PERIOD_WEEKLY, 'Раз в неделю'),
        (PERIOD_MONTHLY, 'Раз в месяц'),
    )

    STATUS_CREATED = 'created'
    STATUS_STARTED = 'started'
    STATUS_DONE = 'done'

    STATUSES = (
        (STATUS_STARTED, 'Запущена'),
        (STATUS_CREATED, 'Создана'),
        (STATUS_DONE, 'Завершена'),
    )

    time = models.TimeField(editable=True, auto_now=False, auto_now_add=False, verbose_name='время рассылки')
    period = models.CharField(max_length=20, choices=PERIODS, verbose_name='периодичность рассылки')
    status = models.CharField(max_length=20, choices=STATUSES, verbose_name='статус рассылки')
    message = models.ManyToManyField('Message', verbose_name='рассылка')
    clients = models.ManyToManyField('Client', verbose_name='клиенты')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='создал', **NULLABLE)

    def __str__(self):
        subject = ", ".join(str(sub) for sub in self.message.all())
        return f'{subject}'

    class Meta:
        verbose_name = 'рассылка'
        verbose_name_plural = 'рассылки'


class Message(models.Model):
    subject = models.CharField(max_length=100, verbose_name='тема')
    mail = models.TextField(verbose_name='сообщение')

    def __str__(self):
        return f'{self.subject}'

    class Meta:
        verbose_name = 'сообщение'
        verbose_name_plural = 'сообщения'


class MailingLog(models.Model):

    STATUS_OK = 'ok'
    STATUS_FAILED = 'failed'
    STATUSES = (
        (STATUS_OK, 'Успешно'),
        (STATUS_FAILED, 'Ошибка'),
    )

    last_try_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUSES, verbose_name='статус')
    client = models.ForeignKey('Client', on_delete=models.CASCADE, verbose_name='адрес клиента')
    subscription = models.ForeignKey('MailingSettings', on_delete=models.CASCADE, verbose_name='подписка клиента')

    def __str__(self):
        return f'{self.last_try_date}'

    class Meta:
        verbose_name = 'лог'
        verbose_name_plural = 'логи'


class Blog(models.Model):
    title = models.CharField(max_length=100, verbose_name='заголовок')
    content = models.TextField(verbose_name='содержимое', **NULLABLE)
    preview_image = models.ImageField(upload_to='content_image/', default='content_image/default.jpg', verbose_name='изображение (превью)', **NULLABLE)
    creation_date = models.DateField(verbose_name='дата создания', auto_now=True)
    is_published = models.BooleanField(default=True, verbose_name='опубликовано')
    view_count = models.IntegerField(default=0, verbose_name='просмотры')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'публикации'
