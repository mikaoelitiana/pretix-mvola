# Generated by Django 4.2.16 on 2024-11-19 22:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pretix_mvola', '0003_rename_server_corelation_id_mvolaorderpayment_server_correlation_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='mvolaorderpayment',
            name='user_account_identifier',
            field=models.CharField(default='123', max_length=20),
            preserve_default=False,
        ),
    ]
