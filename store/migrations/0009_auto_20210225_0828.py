# Generated by Django 3.1.6 on 2021-02-25 08:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_customer_customer_image'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customer',
            old_name='customer_image',
            new_name='profile_pic',
        ),
    ]
