import telegram as t
import telegram.ext as tex
import json
import random

TOKEN = '1611542237:AAGPMlkeNxp3geL0urxsSsBncnOBROjctsg' # só pra testar


users_file = open('users.json')
game_users = json.load(users_file)
users_file.close()


def random_start(a, b):
    if(random.randint(0,1) == 0):
        return a, b 
    return b, a

def set_adversary(user_id, adversary_id):
    for user in game_users:
        if user["user_id"] == user_id:
            user["adversary"] = adversary_id
            return


def set_listening(user_id, condition):
    for user in game_users:
        if user["user_id"] == user_id:
            user["listening"] = condition
            return


def nick_exists(nickname):
    for user in game_users:
        if(nickname == user["nickname"]):
            return True
    return False


def invalid_nick(update, context):
    update.message.reply_text(
        "Nickname inválido! Ele NÃO pode começar com '/'. Digite outro:")
    return "SET_NICK"


def search_user_in_list_by_name(username):
    for user in game_users:
        if(username == user["username"]):
            return user
    return None


def search_user_in_list_by_nick(nickname):
    for user in game_users:
        if(nickname == user["nickname"]):
            return user
    return None


def search_user_by_id(users, user_id):
    for user in users:
        if(user_id == user["user_id"]):
            return user
    return None


def remove_user_from_queue(user_id):
    for user in game_users:
        if(user_id == user["user_id"]):
            game_users.remove(user)


def deactivate_user(user_id):
    for user in game_users:
        if(user_id == user["user_id"]):
            #game_users.remove(user)
            #update_list_json_file()
            user["active"] = False



def activate_user(user_id):
    for user in game_users:
        if(user_id == user["user_id"]):
            #game_users.remove(user)
            #update_list_json_file()
            user["active"] = True


def get_user_from_list_start(skip_user_id):
  
    for user in game_users:
        if (user["user_id"] != skip_user_id and user["active"] == True and user["adversary"] == None):
            game_users.remove(user)
            game_users.append(user)
            deactivate_user(user["user_id"])
            return user    
    return None

def start(update, context):
    if search_user_by_id(game_users, update.effective_user.id) != None:
        update.message.reply_text("Você já está presente no jogo! Digite /play para ir para o menu!")
        return tex.ConversationHandler.END
    update.message.reply_text("Bem-vindo(a/e)! Escolha um nickname:")
    return "SET_NICK"


def set_nick(update, context):
    my_nick = update.message.text
    my_username = update.effective_user.name
    my_user_id = update.effective_user.id

    if nick_exists(my_nick):
        update.message.reply_text("Esse nick já existe, por favor digite outro")
        return "SET_NICK"


    for user in game_users:
        if my_user_id == user["user_id"]:
            user["nickname"] = my_nick
            #update_list_json_file()
            update.message.reply_text('Nickname modificado com sucesso!')
            return tex.ConversationHandler.END

    user_object = {
        "user_id": my_user_id,
        "username": my_username,
        "nickname": my_nick,
        "active": False,
        "adversary": None,
        "listening": False
    }

    game_users.append(user_object)
    #update_list_json_file()

    text = f'Muito bem, {my_nick}. Digite /play para ir para o menu do jogo ou aguarde ser chamado para uma partida'
    update.message.reply_text(text)
    return tex.ConversationHandler.END


def change_nick(update, context):
    if search_user_by_id(game_users, update.effective_user.id) == None:
        update.message.reply_text("Impossível mudar seu apelido! Dê o comando /start para iniciar.")
        return tex.ConversationHandler.END
    update.message.reply_text("Digite o novo nickname.")
    return "SET_NICK"

def users(update, context):
    users = []

   # update.message.reply_text('Atualmente, esses são os outros usuários presentes na fila:')

    for user in game_users:
        if(user["active"] == True and user["adversary"] == None and update.effective_user.id != user["user_id"]): 
            users.append(user['nickname'])

    if len(users) > 0:
        text = "\n".join(users)
    else:
        text = 'Parece que não há ninguém por aqui'

    context.bot.sendMessage(
        chat_id=update.effective_chat.id, text=text)


def play_command(update, context):
    options = []
    user = search_user_by_id(game_users, update.effective_user.id)
    if user == None:
        update.message.reply_text('Você não está cadastrado! Digite /start para continuar')
        return tex.ConversationHandler.END
    elif user["active"] == False:
        options.append(['Entrar na fila'])
        options.append(['Jogar (usuário aleatório)'])
        options.append(['Jogar (usuário específico)'])
    else:
        options.append(['Sair da fila'])
    keyboard = t.ReplyKeyboardMarkup(options, one_time_keyboard=True)
    text = 'Selecione uma opção:'
    update.message.reply_text(text, reply_markup=keyboard)
    return 'CHECK_OPTION' 

def random_user(update, context):
    player1_id = update.effective_user.id
    player1 = search_user_by_id(game_users, player1_id)
    player2 = get_user_from_list_start(update.effective_user.id)
    text = ''
    if player2 == None:
        text = 'Parece que você está sozinho por aqui. Não há usuários disponíveis. '
        text += 'Compartilhe o bot com os amigos para poder jogar.'
        update.message.reply_text(text)
        return tex.ConversationHandler.END
    else:
        player1, player2 = random_start(player1, player2)
        text1 = f'{player1["username"]}, você vai jogar com {player2["username"]}, você começa jogando.'
        text2 = f'{player2["username"]}, você vai jogar com {player1["username"]}, você começa esperando.'
        context.bot.sendMessage(chat_id=player1["user_id"], text=text1)
        context.bot.sendMessage(chat_id=player2["user_id"], text=text2)
        
        set_listening(player1["user_id"], False)
        activate_user(player1["user_id"])
        set_adversary(player1["user_id"], player2["user_id"])
        
        set_listening(player2["user_id"], True)
        activate_user(player2["user_id"])
        set_adversary(player2["user_id"], player1["user_id"])

        
    return "CONVERSATION"



def specific_user(update, context):
    player1_id = update.effective_user.id
    
    player1 = search_user_by_id(game_users, player1_id)
    player2 = search_user_in_list_by_nick(update.message.text)
    
    if player2 == None:
        text = 'Não foi encontrado nenhum usuário com esse nome na fila'
        context.bot.sendMessage(chat_id=update.effective_user.id, text=text)
        return tex.ConversationHandler.END
    
    elif player2["user_id"] == player1_id:
        text = 'Você não pode jogar consigo mesmo!'
        context.bot.sendMessage(chat_id=update.effective_user.id, text=text)
        return tex.ConversationHandler.END
    
    player1, player2 = random_start(player1, player2)
    text1 = f'{player1["username"]}, você vai jogar com {player2["username"]}, você começa jogando.'
    text2 = f'{player2["username"]}, você vai jogar com {player1["username"]}, você começa esperando.'
    context.bot.sendMessage(chat_id=player1["user_id"], text=text1)
    context.bot.sendMessage(chat_id=player2["user_id"], text=text2)
    
    set_listening(player1["user_id"], False)
    activate_user(player1["user_id"])
    set_adversary(player1["user_id"], player2["user_id"])
    
    set_listening(player2["user_id"], True)
    activate_user(player2["user_id"])
    set_adversary(player2["user_id"], player1["user_id"])
    return "CONVERSATION"


def check_option(update, context):
    user_input = update.message.text 
    user_id = update.effective_user.id

    existing_user = search_user_by_id(game_users, user_id)

    if existing_user == None:
        text = 'Você ainda não está cadastrado! Dê /start para começar'
        return tex.ConversationHandler.END

    if (existing_user["active"] == False and user_input == 'Entrar na fila'):
        text = 'Entrando na fila...'
        context.bot.sendMessage(chat_id=user_id, text=text)
        activate_user(update.effective_user.id)
        set_listening(existing_user["user_id"], True)
        return "CONVERSATION"
    else:
        if user_input == 'Sair da fila':
            text = 'Saindo da fila...'
            context.bot.sendMessage(chat_id=user_id, text=text)
            return remove_user(update, context)
        elif user_input == 'Jogar (usuário aleatório)':
            text = 'Você vai jogar com um usuário aleatório'
            context.bot.sendMessage(chat_id=user_id, text=text)
            return random_user(update, context)
        elif user_input == 'Jogar (usuário específico)':
            text = 'Você vai jogar com um usuário específico'
            context.bot.sendMessage(chat_id=user_id, text=text)
            text = 'Digite o nickname de seu adversário'
            context.bot.sendMessage(chat_id=user_id, text=text)
            return 'SPECIFIC_USER'
        else:
            text = 'Opção inválida!'
            context.bot.sendMessage(chat_id=user_id, text=text)
            return 'CHECK_OPTION'
    return tex.ConversationHandler.END


def remove_user(update, context):
    existingPlayer = search_user_by_id(game_users, update.effective_user.id)

    if existingPlayer == None:
        text = 'Você não estava cadastrado. Digite /start para continuar'
        context.bot.sendMessage(chat_id=update.effective_user.id, text=text)
        return tex.ConversationHandler.END
    else:
        deactivate_user(existingPlayer["user_id"])
        text = 'Você saiu do jogo!'
        context.bot.sendMessage(chat_id=update.effective_user.id, text=text)
    return tex.ConversationHandler.END


def CONVERSATION(update, context):
    id = update.effective_user.id
    user = search_user_by_id(game_users, id)
    adversary = search_user_by_id(game_users, user["adversary"])
    text = update.message.text

    if(text == "sair"):
        if(user["adversary"] == None):
            return remove_user(update, context)
        else:
            update.message.reply_text("Você está no meio de uma partida...")
            return "CONVERSATION"


    if(user["listening"] == True):
        update.message.reply_text("Você deve esperar pelo adversário")
        return "CONVERSATION"

    if(text == "FIM"):
        set_listening(adversary["user_id"], False)
        set_adversary(adversary["user_id"], None)
        deactivate_user(adversary["user_id"])
        
        set_listening(user["user_id"], False)
        set_adversary(user["user_id"], None)
        deactivate_user(user["user_id"])

        update.message.reply_text("Você deu FIM a partida, para jogar novamente, digite /play.")
        context.bot.sendMessage(chat_id=adversary["user_id"], text="Seu adversário deu fim a partida, digite \"sair\" para sair também!")
        return tex.ConversationHandler.END

    
    context.bot.sendMessage(chat_id=adversary["user_id"], text=text)
    update.message.reply_text("Mensagem enviada, espere por uma resposta")

    set_listening(user["user_id"], True)
    set_listening(adversary["user_id"], False)


    return "CONVERSATION"
    



#updater = tex.Updater('1297400305:AAGjXuYCv00jzjaiCpDQSsl8G6TDLXkx_Cs')
updater = tex.Updater(token=TOKEN, use_context=True)

dispatcher = updater.dispatcher

start_handler = tex.ConversationHandler(
    entry_points=[tex.CommandHandler('start', start)],
    states={
        "SET_NICK": [tex.MessageHandler(tex.Filters.text & ~tex.Filters.command, set_nick)]
    },
    fallbacks=[tex.MessageHandler(tex.Filters.all, invalid_nick)]
)

play_handler = tex.ConversationHandler(
    entry_points=[tex.CommandHandler("play", play_command)],
    states={
        'CHECK_OPTION': [tex.MessageHandler(tex.Filters.text, check_option)],
        'SPECIFIC_USER': [tex.MessageHandler(tex.Filters.text, specific_user)],
        'CONVERSATION': [tex.MessageHandler(tex.Filters.text, CONVERSATION)]
    },
    fallbacks=[tex.CommandHandler("play", play_command)]
)

change_nick_handler = tex.ConversationHandler(
    entry_points = [tex.CommandHandler("change", change_nick)],
    states={
        "SET_NICK": [tex.MessageHandler(tex.Filters.text & ~tex.Filters.command, set_nick)]
    },
    fallbacks=[tex.MessageHandler(tex.Filters.all, invalid_nick)]
)

users_handler = tex.CommandHandler('users', users)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(play_handler)
dispatcher.add_handler(users_handler)
dispatcher.add_handler(change_nick_handler)

updater.start_polling()

print("The bot is now running!")
updater.idle()
print("The bot is now shutting down...")