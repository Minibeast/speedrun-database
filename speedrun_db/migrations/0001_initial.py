# Generated by Django 4.1.3 on 2022-11-17 17:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_by', models.IntegerField()),
                ('name', models.TextField()),
                ('abbreviation', models.TextField()),
                ('show_on_home', models.BooleanField()),
                ('subcategory_filter', models.BooleanField()),
                ('is_multiplayer', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_by', models.IntegerField()),
                ('name', models.TextField()),
                ('abbreviation', models.TextField()),
                ('use_game_time', models.BooleanField()),
                ('show_on_home', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Run',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url_id', models.TextField()),
                ('time', models.TimeField()),
                ('date', models.DateField()),
                ('players', models.TextField()),
                ('video', models.TextField()),
                ('subcategory', models.TextField()),
                ('platform', models.TextField()),
                ('demos', models.TextField()),
                ('splits', models.TextField()),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='speedrun_db.category')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='speedrun_db.game')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='category',
            name='held_game',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='speedrun_db.game'),
        ),
    ]
