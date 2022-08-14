from telegram.ext import Filters
FilterPrivateNoCommand = Filters.chat_type.private & (~Filters.command)
FilterGroupNoCommand = Filters.chat_type.groups & (~Filters.command)