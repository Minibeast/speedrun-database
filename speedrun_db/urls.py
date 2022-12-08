from django.urls import path

from . import views

app_name='speedrun_db'
urlpatterns = [
    path('', views.index, name='index'),
    path('games/', views.get_games, name='games'),
    path('run/<str:run_id>/', views.get_run, name='run'),
    path('run/<str:run_id>/splits/', views.get_splits, name='splits'),
    path('compare/<str:run_id>/', views.make_comparison, name='comparison_make'),
    path('compare/<str:run1_id>/<str:run2_id>/', views.comparison, name='comparison'),
    path('<str:game_abv>/', views.get_game, name='game'),
    path('<str:game_abv>/<str:category_abv>/', views.get_category, name='category'),
    path('<str:game_abv>/<str:category_abv>/barriers', views.category_minute_barriers, name='barriers'),
    path('<str:game_abv>/<str:category_abv>/pb', views.get_pb, name='get_pb')
]
