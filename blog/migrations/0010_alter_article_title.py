# Generated by Django 4.1.2 on 2023-06-18 20:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0009_subscription_delete_relation"),
    ]

    operations = [
        migrations.AlterField(
            model_name="article",
            name="title",
            field=models.CharField(max_length=55),
        ),
    ]