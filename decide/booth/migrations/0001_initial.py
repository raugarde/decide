# Generated by Django 2.0 on 2021-01-14 15:09



from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SuggestingForm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('title', models.CharField(max_length=200)),
                ('suggesting_date', models.DateField()),
                ('content', models.TextField()),
                ('send_date', models.DateField()),
                ('is_approved', models.NullBooleanField()),
            ],
        ),
    ]
