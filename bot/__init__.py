from .bot import Bot
import os
import yfinance as yf
import requests
from datetime import datetime
import logging
import discord
from logger import logger, streamer
from threading import Thread
from zipfile import ZipFile
bot = Bot('$',streamer)

@bot.event
async def on_ready():
  print(f"Booting up: {bot.user}")

@bot.command(name="printLog")
async def print_log(ctx):
  for log in bot.log_stream.logs:
    print(log)
  await ctx.send(f"Log printed in console {datetime.now()}")

@bot.command(name="hello")
async def greeting(ctx):
  await ctx.send(f'Hello {ctx.author.display_name}')

@bot.command(name="enableLog")
async def enable_log(ctx):
  logging.disable(logging.NOTSET)
  await ctx.send(f"Logging enabled {datetime.now()}")

@bot.command(name="disableLog")
async def disable_log(ctx):
  bot.log_stream.refresh()
  logging.disable(logging.CRITICAL)
  await ctx.send(f"Logging disabled {datetime.now()}")
  
@bot.command(name="file")
async def log_files(ctx):
  with ZipFile("formatted_logs.zip", "w") as zip:
            folder_path = "formatted_logs"
            for _, _, files in os.walk(folder_path):
                for filename in files:
                    zip.write("formatted_logs/"+filename)
            zip.close()
  await ctx.send(file=discord.File("formatted_logs.zip"))


def get_weather():
    """
    Currently only does weather for waterloo
    ---------------------------------------------
    Return: 
        msg - a string indicating the weather or if there was an error
    """
    key = os.environ.get("weather_key")
    response = requests.get('http://api.openweathermap.org/data/2.5/weather?q=Waterloo&units=metric&appid=' + key)

    weather_report = {"complete":True} # dictionary of weather info incase furthur processing is wanted
    msg = "An error has occured" 

    if response.status_code == 200:
        # getting data in the json format
        data = response.json()
        # getting the main dict block
        main = data['main']
        # getting temperature
        weather_report["ctemp"] = main['temp']
        # getting high and low temps
        weather_report['max_temp'] = main['temp_max']
        weather_report['min_temp'] = main['temp_min']
        # getting the humidity
        weather_report["humidity"] = main['humidity']
        # weather description
        weather_report["description"] = data['weather'][0]['description']
        #format the msg that needs to be sent (could be updated to pythons new string formatting)
        msg = "Current temp: {}°C\nHigh: {}°C\nLow: {}°C\nHumidity: {}%\nDescription: {}\n".\
                format(weather_report["ctemp"],weather_report["max_temp"],weather_report["min_temp"],weather_report["humidity"],\
                    weather_report["description"])
    else:
        # showing the error message
        weather_report["complete"] = False
    return msg

@bot.command(name='weather')
async def on_message(ctx):
    await ctx.send(get_weather())

@bot.command(name="stock")
async def stocks(ctx,stock_ticker):
  stock_ticker = stock_ticker.upper()
  try:
    ticker = yf.Ticker(stock_ticker)
    data = ticker.history()
    last_quote = (data.tail(1)['Close'].iloc[0])
    await ctx.send(f"{stock_ticker}: {last_quote} {ticker.info['currency']}")
  except Exception as err:
    logger.error(str(err))
    await ctx.send(f"Ticker {stock_ticker} unavailable or functionality not working")