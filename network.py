import telegram
import telegram.ext as tex
import json

users_file = open('users.json')
users_queue = json.load(users_file)


def start(update, context):
    user_id = update.effective_user.id
    for user in users_queue:
        if(user_id == user["user_id"]):
            update.message.reply_text("Você já possui um nickname.Se deseja trocá-lo, digite /change. Se deseja excluí-lo, digite /delete")
            return tex.ConversationHandler.END

    update.message.reply_text("Bem-vindo(a/e)! Escolha um nickname:")
    return "SET_NICK"


def set_nick(update, context):
    my_nick = update.message.text
    my_username = update.effective_user.name
    my_user_id = update.effective_user.id
    for user in users_queue:
        if(my_nick == user["nickname"]):
            update.message.reply_text("Esse nick já existe, por favor digite outro")
            return "SET_NICK"

    user_object = {
        "user_id": my_user_id,
        "username": my_username,
        "nickname": my_nick
    }

    users_queue.append(user_object)
    update.message.reply_text("Nickname inserido com sucesso!")
    return tex.ConversationHandler.END

def change(update, context):
    update.message.reply_text("Digite o novo nickname.")
    return "SET_NICK"

def set_new_nick(update, context):
    new_nick = update.message.text
    user_id = update.effective_user.id
    
    for user in users_queue:
        if(new_nick == user["nickname"]):
            update.message.reply_text("Esse nick já existe, por favor digite outro")
            return "SET_NICK"
    
    for user in users_queue:
        if(user_id == user["user_id"]):
            user["nickname"] = new_nick
            update.message.reply_text("Nickname modificado com sucesso!")
            return tex.ConversationHandler.END

    update.message.reply_text("Voce ainda não possui um nick, para adicionar um, digite /start")
    return tex.ConversationHandler.END


def invalid_nick(update, context):
    update.message.reply_text(
        "Nickname inválido! Ele NÃO pode começar com '/'. Digite outro:")
    return "SET_NICK"


def users(update, context):
    user_id = update.effective_user.id
    users = []

    for user in users_queue:
        if(user_id != user["user_id"]): users.append(user['nickname'])

    text_user_list = "\n".join(users)

    context.bot.sendMessage(
        chat_id=update.effective_chat.id, text=text_user_list)

def delete(update, context):
    user_id = update.effective_user.id
    for user in users_queue:
        if (user_id == user["user_id"]):
            users_queue.remove(user)
            update.message.reply_text("Seu nick foi removido com sucesso!")
            return

    update.message.reply_text("Você ainda não possui um nickname, para adicionar um, digite /start")


#1649441076:AAEs_jpV6L7nmsAEPVMGVYbfjbB6RteKLho

#bot do vitao
#1297400305:AAGjXuYCv00jzjaiCpDQSsl8G6TDLXkx_Cs

updater = tex.Updater('1649441076:AAEs_jpV6L7nmsAEPVMGVYbfjbB6RteKLho')
dispatcher = updater.dispatcher

start_handler = tex.ConversationHandler(
    entry_points=[tex.CommandHandler('start', start)],
    states={
        "SET_NICK": [tex.MessageHandler(tex.Filters.text & ~tex.Filters.command, set_nick)]
    },
    fallbacks=[tex.MessageHandler(tex.Filters.all, invalid_nick)]
)

change_nick_handler = tex.ConversationHandler(
    entry_points = [tex.CommandHandler("change", change)],
    states={
        "SET_NICK": [tex.MessageHandler(tex.Filters.text & ~tex.Filters.command, set_new_nick)]
    },
    fallbacks=[tex.MessageHandler(tex.Filters.all, invalid_nick)]
)

users_handler = tex.CommandHandler('users', users)
delete_handler = tex.CommandHandler('delete', delete)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(users_handler)
dispatcher.add_handler(change_nick_handler)
dispatcher.add_handler(delete_handler)

updater.start_polling()

print("The bot is now running!")
updater.idle()
print("The bot is now shutting down...")
