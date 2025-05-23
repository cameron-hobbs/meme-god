# Generated by Django 5.2 on 2025-04-19 18:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="RedditPost",
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
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=255)),
                ("over_18", models.BooleanField()),
                ("post_id", models.CharField(max_length=255, unique=True)),
                ("send_replies", models.BooleanField()),
                ("is_video", models.BooleanField()),
                ("post_created_at", models.DateTimeField()),
                ("score", models.IntegerField()),
                ("ups", models.IntegerField()),
                ("downs", models.IntegerField()),
                ("pwls", models.IntegerField(null=True)),
                ("upvote_ratio", models.DecimalField(decimal_places=2, max_digits=3)),
                ("total_awards_received", models.IntegerField()),
                ("is_created_from_ads_ui", models.BooleanField()),
                ("edited", models.BooleanField(null=True)),
                ("post_hint", models.CharField(max_length=255)),
                ("pinned", models.BooleanField()),
                ("url", models.URLField(max_length=255)),
                ("num_comments", models.IntegerField()),
                ("is_self", models.BooleanField()),
                ("num_reports", models.IntegerField(null=True)),
                ("thumbnail_height", models.IntegerField(null=True)),
                ("thumbnail_width", models.IntegerField(null=True)),
                ("quarantine", models.BooleanField()),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="RedditSub",
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
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("tag", models.CharField(max_length=255, unique=True)),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("memes", "Memes"),
                            ("london", "London"),
                            ("food", "Food"),
                            ("animals", "Animals"),
                            ("china", "China"),
                        ],
                        max_length=255,
                    ),
                ),
                ("should_scrape", models.BooleanField(default=True)),
                ("subscribers", models.IntegerField(null=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="RedditUser",
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
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255, unique=True)),
                ("full_name", models.CharField(max_length=255, null=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="RankedRedditPost",
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
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("ranking", models.FloatField(default=0)),
                (
                    "reddit_post",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="reddit.redditpost",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="RedditPostChangeLog",
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
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "field_changed",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("old_value", models.TextField(blank=True, null=True)),
                ("new_value", models.TextField(blank=True, null=True)),
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="change_log",
                        to="reddit.redditpost",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="redditpost",
            name="subreddit",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="posts",
                to="reddit.redditsub",
            ),
        ),
        migrations.AddField(
            model_name="redditpost",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="content_posted",
                to="reddit.reddituser",
            ),
        ),
    ]
