# Generated by Django 5.2 on 2025-04-13 20:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("reddit", "0008_rankedredditpost_created_at_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="rankedredditpost",
            name="reddit_post",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="reddit.redditpost",
                unique=True,
            ),
        ),
    ]
