@echo off
echo Construyendo el ejecutable Gym Manager...

flet pack gym_manager\main.py ^
--name "Gym Manager" ^
--icon gym_manager\assets\app.ico ^
--add-data "gym_manager\assets;assets" ^
--hidden-import gym_manager.imports_for_pyinstaller ^
--hidden-import gym_manager.views.member_view ^
--hidden-import gym_manager.views.backup_view ^
--hidden-import gym_manager.views.statistics_view ^
--hidden-import gym_manager.views.login_view ^
--hidden-import gym_manager.views.home_view ^
--hidden-import gym_manager.views.payment_view ^
--hidden-import gym_manager.views.routine_view ^
--hidden-import gym_manager.views.user_view ^
--hidden-import gym_manager.views.payment_method_view ^
--hidden-import gym_manager.views.payment_receipt_view ^
--hidden-import gym_manager.controllers.statistics_controller ^
--hidden-import gym_manager.controllers.auth_controller ^
--hidden-import gym_manager.controllers.member_controller ^
--hidden-import gym_manager.controllers.payment_controller ^
--hidden-import gym_manager.services.backup_service ^
--hidden-import gym_manager.services.restore_service ^
--hidden-import gym_manager.services.auth ^
--hidden-import gym_manager.services.database ^
--hidden-import gym_manager.utils.database ^
--hidden-import gym_manager.utils.navigation ^
--hidden-import gym_manager.config ^
--hidden-import plotly ^
--hidden-import plotly.graph_objs ^
--hidden-import flet.plotly_chart ^
--hidden-import kaleido ^
--hidden-import pymysql ^
--hidden-import pymysql.cursors ^
--hidden-import pymysql.connections ^
--hidden-import reportlab ^
--hidden-import reportlab.lib ^
--hidden-import reportlab.platypus ^
--hidden-import openpyxl

echo Construccion completada!
pause
