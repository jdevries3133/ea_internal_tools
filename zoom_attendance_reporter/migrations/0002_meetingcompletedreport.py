# Generated by Django 3.1.3 on 2020-11-14 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zoom_attendance_reporter', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MeetingCompletedReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topic', models.CharField(max_length=100)),
                ('datetime', models.DateField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]