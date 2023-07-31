# Generated by Django 4.1.2 on 2023-07-27 07:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("chat", "0002_rename_receiver_message_recipient_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ChatPage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=55, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name="message",
            name="chat_page",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="messages",
                to="chat.chatpage",
            ),
        ),
    ]