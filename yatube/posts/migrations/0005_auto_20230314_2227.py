# Generated by Django 2.2.9 on 2023-03-14 19:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_auto_20230314_1417'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-pub_date'], 'verbose_name': 'post', 'verbose_name_plural': 'posts'},
        ),
    ]