# Generated by Django 2.2.5 on 2021-03-18 21:36

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='track',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('PseudoAcc', models.TextField()),
                ('PseudoID', models.TextField()),
                ('PseudoName', models.TextField()),
                ('OrigAcc', models.TextField()),
                ('OrigMR', models.TextField()),
                ('OrigName', models.TextField()),
                ('OrigGA', models.TextField()),
                ('State', models.IntegerField()),
            ],
        ),
    ]
