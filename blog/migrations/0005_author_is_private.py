# Generated by Django 4.1.2 on 2023-06-22 09:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0004_rename_author_subscription_target_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="author",
            name="is_private",
            field=models.BooleanField(default=False),
        ),
    ]
