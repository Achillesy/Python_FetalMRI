# Generated by Django 2.2.5 on 2021-03-19 20:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manage_app', '0002_auto_20210319_1823'),
    ]

    operations = [
        migrations.CreateModel(
            name='series',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('PseudoAcc', models.CharField(max_length=6)),
                ('SeriesID', models.TextField()),
                ('SeriesNumber', models.IntegerField()),
                ('SeriesBrief', models.TextField()),
                ('SeriesDescription', models.TextField()),
                ('AcquisitionMatrix', models.TextField()),
                ('Rows', models.IntegerField()),
                ('Columns', models.IntegerField()),
                ('PixelSpacing', models.TextField()),
                ('Height', models.IntegerField()),
                ('Width', models.IntegerField()),
                ('State', models.IntegerField()),
            ],
        ),
    ]
