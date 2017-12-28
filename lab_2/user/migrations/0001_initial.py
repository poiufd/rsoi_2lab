# Generated by Django 2.0 on 2017-12-26 08:28

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('login', models.CharField(max_length=25, unique=True)),
                ('password', models.CharField(max_length=30)),
                ('name', models.CharField(max_length=35)),
            ],
        ),
    ]
