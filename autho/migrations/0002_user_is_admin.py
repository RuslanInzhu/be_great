# Generated by Django 3.2.12 on 2022-04-10 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('autho', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_admin',
            field=models.BooleanField(default=False),
        ),
    ]
