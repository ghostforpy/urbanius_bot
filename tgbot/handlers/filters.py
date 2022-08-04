from telegram.ext import Filters
FilterPrivateNoCommand = Filters.chat_type.private & (~Filters.command)