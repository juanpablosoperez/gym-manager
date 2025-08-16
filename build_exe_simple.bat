@echo off
echo Construyendo el ejecutable Gym Manager (version simple)...

flet pack gym_manager\main.py ^
--name "Gym Manager" ^
--icon gym_manager\assets\app.ico ^
--add-data "gym_manager\assets;assets" ^
--hidden-import gym_manager.views.member_view ^
--hidden-import gym_manager.views.backup_view ^
--hidden-import gym_manager.views.statistics_view ^
--hidden-import gym_manager.controllers.statistics_controller ^
--hidden-import gym_manager.views.payment_view ^
--hidden-import gym_manager.views.routine_view ^
--hidden-import gym_manager.views.user_view ^
--hidden-import gym_manager.views.payment_method_view ^
--hidden-import gym_manager.services.backup_service ^
--hidden-import gym_manager.services.restore_service ^
--hidden-import gym_manager.config ^
--hidden-import pymysql ^
--hidden-import plotly ^
--hidden-import flet.plotly_chart ^
--hidden-import kaleido

echo Construccion completada!
pause
