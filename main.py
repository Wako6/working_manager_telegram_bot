# import threading
import time
import asyncio
from telegram.ext import (ApplicationBuilder, CommandHandler, MessageHandler,
                          filters)
from datetime import timedelta

# initialize API token - Telegram
TOKEN = '6489762665:AAGAx5xytbcmQFM_oDkRbpsKoAF19sTz7NA'

STOP_SIGNAL = False
THREAD = None
START_TIME = None
WORKING_TIME = 60 * 45  # 45min
BREAK_TIME = 60 * 5  # 5min


# creating functionalities
async def william_host_service(update, context):
    if len(context.args) == 1 and context.args[0] == "help":
        await help(update, context)
    elif len(context.args) == 1 and context.args[0] == "go":
        await go(update, context)
    elif len(context.args) == 1 and context.args[0] == "stop":
        await stop(update, context)
    elif len(context.args) == 2 and " ".join(context.args[0:2]) == "get time":
        await gettime(update, context)
    elif len(context.args) == 4 and " ".join(context.args[0:2]) == "set time":
        await settime(update, context, context.args[2:])
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Désolé, je n'ai pas compris votre requête")


async def help(update, context):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Voici tout ce que je sais faire:\n\n" +
        "𝗵𝗲𝗹𝗽: Indique tout ce que je sais faire\n" +
        "𝗴𝗼: Lance le mode travail\n" + "𝘀𝘁𝗼𝗽: Arrête le mode travail\n" +
        "𝗴𝗲𝘁 𝘁𝗶𝗺𝗲: Depuis combien vous êtes en mode travail\n" +
        "𝘀𝗲𝘁 𝘁𝗶𝗺𝗲 <𝘄𝗼𝗿𝗸_𝗱𝘂𝗿𝗮𝘁𝗶𝗼𝗻> <𝗯𝗿𝗲𝗮𝗸_𝗱𝘂𝗿𝗮𝘁𝗶𝗼𝗻>: Paramétrer votre mode de travail\n"
    )


async def go(update, context):
    global THREAD

    if THREAD and not THREAD.cancelled():
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Vous êtes déjà en mode travail")
        return

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="C'est partie !")
    THREAD = asyncio.create_task(timer_action(update, context))


async def timer_action(update, context):
    global STOP_SIGNAL, START_TIME, WORKING_TIME, BREAK_TIME

    START_TIME = time.perf_counter()

    try:
        while not STOP_SIGNAL:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=
                f"Dans {int(WORKING_TIME / 60)} min vous pourrez pendre une pause"
            )

            await asyncio.sleep(WORKING_TIME)  # 45min

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Vous avez {int(BREAK_TIME / 60)} min de pause")

            await asyncio.sleep(BREAK_TIME)  # 45min

            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text="C'est repartie !")
    except asyncio.CancelledError:
        pass

    STOP_SIGNAL = False  # Réinitialise le signal d'arrêt


async def stop(update, context):

    global THREAD, STOP_SIGNAL, START_TIME

    if not THREAD or THREAD.cancelled():
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Vous n'êtes actuellement pas en mode travail")

        return

    STOP_SIGNAL = True  # Pour arrêter le timer
    THREAD.cancel()  # Arrête le thread
    THREAD = None

    # Calcule du temps de travail
    end_time = time.perf_counter()
    total_time = end_time - START_TIME

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Vous avez travaillé pendant {format_timedelta(total_time)}")


def format_timedelta(seconds):
    td = timedelta(seconds=seconds)
    hours, remainder = divmod(td.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)

    formated_timedelta = f"{int(hours)}h" if hours > 0 else ""
    formated_timedelta += f" {int(minutes)}min" if minutes > 0 else ""
    formated_timedelta += f" {int(seconds)}s"

    return formated_timedelta


async def gettime(update, context):
    global START_TIME, WORKING_TIME, BREAK_TIME

    # Calcule du temps de travail
    end_time = time.perf_counter()
    total_time = end_time - START_TIME

    # Calcule du temps qu'il reste
    left_time = total_time % (WORKING_TIME + BREAK_TIME)
    if left_time < WORKING_TIME:
        message = f"Il reste {format_timedelta(WORKING_TIME - left_time)} avant la prochaine pause."
    else:
        message = f"Il reste {format_timedelta((WORKING_TIME + BREAK_TIME) - left_time)} de pause."

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=
        f"Ca fait exactement {format_timedelta(total_time)} que vous avez commencé à travailler. {message}"
    )


async def settime(update, context, args: list[str]):
    global THREAD, WORKING_TIME, BREAK_TIME

    if THREAD and not THREAD.cancelled():
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=
            "Vous êtes actuellement en mode travail. Veuillez vous arreter pour modifier le paramétrage"
        )
        return

    working_duration, break_duration = args

    if not working_duration.isnumeric() or not break_duration.isnumeric:
        return

    WORKING_TIME, BREAK_TIME = int(working_duration) * 60, int(
        break_duration) * 60

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Très bien, c'est noté ! ✅")


if __name__ == "__main__":
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler('william', william_host_service))

    application.run_polling()
