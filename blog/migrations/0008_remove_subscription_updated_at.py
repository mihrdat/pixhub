# Generated by Django 4.1.2 on 2023-06-24 20:51

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0007_article_updated_at_author_updated_at_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="subscription",
            name="updated_at",
        ),
    ]
