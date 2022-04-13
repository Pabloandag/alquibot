# AlquiBOT

Basado en [este post](https://dev.to/fernandezpablo/scrappeando-propiedades-con-python-4cp8) para scrappear propiedades, cambiadas algunas configuraciones del scrapper para manejarse con la actualización de las páginas.


## Variables a setear

- **URLS**: Tienen que mostrar un listado filtrado de las propiedades que te interesan ordenadas para que te muestren las propiedades más nuevas.
- **BOT_ID**: Crear un bot con BotFather, este bot te devuelve el token de tu nuevo bot. [INFO](https://core.telegram.org/bots).
- **ROOM_ID**: ID de la sala de chat que va a utilizar el bot.Cuando agregues al bot a un grupo y mandes un mensaje, o simplemente le mandes un mensaje a su conversación privada, haciendo un request a  https://api.telegram.org/bot{YourBOTToken}/getUpdates podes conseguir el chat id. [INFO](https://stackoverflow.com/questions/32423837/telegram-bot-how-to-get-a-group-chat-id). Si el bot no actualiza verificá que tenga acceso a los mensajes con BotFather.