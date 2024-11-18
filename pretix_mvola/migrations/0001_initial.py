# Generated by Django 4.2.16 on 2024-11-18 20:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('pretixbase', '0274_alter_customer_locale_alter_event_currency_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='MVolaOrderPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('reference', models.CharField(db_index=True, max_length=190, unique=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pretixbase.order')),
                ('payment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='pretixbase.orderpayment')),
            ],
        ),
    ]