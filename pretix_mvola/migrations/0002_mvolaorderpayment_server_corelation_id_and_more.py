# Generated by Django 4.2.16 on 2024-11-19 22:09

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pretix_mvola', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mvolaorderpayment',
            name='server_corelation_id',
            field=models.CharField(db_index=True, default=django.utils.timezone.now, max_length=190, unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='mvolaorderpayment',
            name='reference',
            field=models.CharField(db_index=True, max_length=20, unique=True),
        ),
    ]
