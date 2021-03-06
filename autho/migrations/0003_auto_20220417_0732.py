# Generated by Django 3.2.12 on 2022-04-17 07:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('autho', '0002_user_is_admin'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='email',
            field=models.CharField(max_length=50, null=True, unique=True, verbose_name='Рабочая почта'),
        ),
        migrations.AlterUniqueTogether(
            name='user',
            unique_together={('phone', 'email')},
        ),
    ]
