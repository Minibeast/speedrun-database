# Generated by Django 4.1.3 on 2022-11-17 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('speedrun_db', '0002_alter_run_demos_alter_run_players_alter_run_splits_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name_plural': 'categories'},
        ),
        migrations.AlterField(
            model_name='run',
            name='date',
            field=models.DateField(auto_now_add=True),
        ),
    ]
