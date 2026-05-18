@echo off
echo Abriendo puerto 8000 en el Firewall de Windows...
netsh advfirewall firewall add rule name="Flota App Puerto 8000" dir=in action=allow protocol=TCP localport=8000
echo.
echo Listo. Ahora el celular puede conectarse a la app.
pause
