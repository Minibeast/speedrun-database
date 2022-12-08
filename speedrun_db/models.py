from django.contrib.auth.models import User
from django.db import models

class Game(models.Model):
    order_by = models.IntegerField()
    name = models.TextField()
    abbreviation = models.TextField()
    use_game_time = models.BooleanField()
    show_on_home = models.BooleanField()

    def __str__(self) -> str:
        return self.name

class Category(models.Model):
    order_by = models.IntegerField()
    held_game = models.ForeignKey(Game, on_delete=models.CASCADE)
    name = models.TextField()
    abbreviation = models.TextField()
    show_on_home = models.BooleanField()
    subcategory_filter = models.BooleanField()
    is_multiplayer = models.BooleanField()

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self) -> str:
        return self.name

class Run(models.Model):
    url_id = models.TextField()
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    time = models.TimeField()
    date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    players = models.TextField(blank=True)
    video = models.TextField(blank=True)
    subcategory = models.TextField(blank=True)
    platform = models.TextField()
    demos = models.TextField(blank=True)
    splits = models.TextField(blank=True)
    offset = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.url_id
