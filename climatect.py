import discord
from discord import app_commands
import requests

TOKEN = "token"
ID_SERVIDOR = id servidor

bot = discord.Client(intents=discord.Intents.default())
comandos = app_commands.CommandTree(bot)


@comandos.command(name="clima", description="Consulta o clima de uma cidade")
async def clima(interaction: discord.Interaction, cidade: str):
    await interaction.response.defer()

    try:
        r = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": cidade, "count": 1, "language": "pt"},
            timeout=10
        )
        r.raise_for_status()
        locais = r.json().get("results", [])

        if not locais:
            await interaction.followup.send("Cidade não encontrada!")
            return

        local = locais[0]

        r = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": local["latitude"],
                "longitude": local["longitude"],
                "current": "temperature_2m,weather_code",
                "timezone": "auto"
            },
            timeout=10
        )
        r.raise_for_status()
        dados = r.json()["current"]

        condicoes = {
            0: "Céu limpo ☀️",
            1: "Predominantemente limpo 🌤️",
            2: "Parcialmente nublado ⛅",
            3: "Nublado ☁️",
            45: "Neblina 🌫️",
            48: "Neblina 🌫️",
            51: "Garoa 🌦️",
            53: "Garoa moderada 🌦️",
            55: "Garoa intensa 🌧️",
            61: "Chuva fraca 🌧️",
            63: "Chuva moderada 🌧️",
            65: "Chuva forte 🌧️",
            80: "Pancadas de chuva 🌦️",
            81: "Pancadas de chuva 🌧️",
            82: "Pancadas fortes ⛈️",
            95: "Trovoada ⛈️",
            96: "Trovoada com granizo ⛈️",
            99: "Trovoada forte com granizo ⛈️"
        }

        tempo = condicoes.get(dados["weather_code"], "Condição variável 🌥️")

        if dados["weather_code"] == [95, 96, 99]:
            dica = "⚠️ Tempestade detectada! Procure abrigo em um local fechado e seguro."

        elif dados["weather_code"] == [65, 82]:
            dica = "⚠️ Chuva muito forte! Evite sair de casa e procure um local seguro."

        elif dados["weather_code"] == [45, 48]:
            dica = "⚠️ Neblina! Reduza a velocidade se estiver dirigindo."

        else:
            dica = "✅ Nenhuma condição perigosa identificada."

        await interaction.followup.send(
            f"🌦️ **Climatect — {local['name']}**\n\n"
            f"🌡️ Temperatura: {dados['temperature_2m']} °C\n"
            f"🌤️ Condição: {tempo}\n\n"
            f"🛡️ **Recomendação:** {dica}"
        )

    except requests.RequestException:
        await interaction.followup.send("Erro ao consultar o clima!")


@bot.event
async def on_ready():
    servidor = discord.Object(id=ID_SERVIDOR)
    comandos.copy_global_to(guild=servidor)
    registrados = await comandos.sync(guild=servidor)
    print(f"Climatect online! Comandos registrados: {len(registrados)}")


bot.run(TOKEN)
