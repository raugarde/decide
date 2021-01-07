# Generated by Django 2.0 on 2021-01-07 02:02

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('option_types', models.PositiveIntegerField(choices=[(1, 'Unique option'), (2, 'Multiple option'), (3, 'Rank order scale')], default='1')),
                ('desc', models.TextField(unique=True)),
                ('type', models.PositiveIntegerField(choices=[(0, 'IDENTITY'), (1, 'BORDA'), (2, 'HONDT'), (3, 'EQUALITY'), (4, 'SAINTE_LAGUE'), (5, 'DROOP'), (6, 'IMPERIALI'), (7, 'HARE')], default='0')),
            ],
        ),
        migrations.CreateModel(
            name='QuestionOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveIntegerField(blank=True, null=True)),
                ('option', models.CharField(max_length=200)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='voting.Question')),
            ],
        ),
        migrations.CreateModel(
            name='TypeVoting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Voting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('desc', models.TextField(blank=True, null=True)),
                ('points', models.PositiveIntegerField(default='1')),
                ('start_date', models.DateTimeField(blank=True, null=True)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('started_by', models.CharField(blank=True, max_length=200, null=True)),
                ('tally', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('tallyM', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('tallyF', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('postproc', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('auths', models.ManyToManyField(related_name='votings', to='base.Auth')),
                ('pub_key', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='voting', to='base.Key')),
                ('question', models.ManyToManyField(related_name='voting', to='voting.Question')),
            ],
        ),
    ]
