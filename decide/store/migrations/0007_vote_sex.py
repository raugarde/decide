# Generated by Django 2.0 on 2021-01-01 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_merge_20210101_1335'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote',
            name='sex',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
