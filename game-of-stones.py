import telebot


users = {}
games_hosting = {}
game_standard = {'heaps': '2', 'stones_start': [10, 10], 'modes': [1, 2], 'modes_params': {1: '5', 2: '2'},
                 's': '63', 'first': 'wins', 'ready': False, 'players': [], 'now_goes': 0}
user_standard = {'mode': 'start', 'game': 0}
possibilities = ['', 'увеличить на {}', 'увеличить в {} раз(а)', 'суммировать камни во всех кучах']

bot = telebot.TeleBot('1363217139:AAFuY3UrGbfa2HIODvfUsRcr3AYJy3xT8bs')
welcome_message = '''
Приветствую в увелкательнейшей игре 21-го столетия\n
Есть n-ное количество куч, в каждой из которых есть x-ное количество камней
(все эти параметры вы выбираете самостоятельно) игроки по очереди увеличивают количество камней одним из трех
способов (в зависимости от режима игры):\n
1) Увеличить количество камней в 1 куче на r (r - параметр)\n
2) Увеличить количество камней в 1 куче в b раз (b - параметр)\n
3) Взять сумму камней во всех кучах и заменить количество камней в одной из куч на значение этой суммы (на выбор)\n
Побеждает или проигрывает (в зависимости от режима игры) тот игрок, который первым наберет сумму во всех кучах S.

/create_game - создать сервер игры с возможностью редактирования правил
/join_game - присоедениться к одному из существующих серверов (если имеются оные)
'''


@bot.message_handler(commands=['start'])
def starter(message):
    usr = message.from_user.id
    if usr not in users:
        users[usr] = {'mode': 'start', 'game': 0}
        bot.send_message(usr, welcome_message)
    else:
        if (usr in games_hosting and games_hosting[usr]['ready']) or users[usr]['mode'] == 'playing' or\
                users[usr]['mode'] == 'heap':
            bts = [telebot.types.InlineKeyboardButton(text='Да'), telebot.types.InlineKeyboardButton(text='Нет')]
            kb = telebot.types.ReplyKeyboardMarkup()
            kb.add(bts[0], bts[1])
            bot.send_message(usr, 'Вы собираетесь покинуть игру, хотите выйти?', reply_markup=kb)
            users[usr]['mode'] = 'leaving?'
        else:
            bot.send_message(usr, 'you are already in')


def create_inf_possible(user):
    modes = games_hosting[user]['modes']
    text = ''
    if 1 in modes:
        text += possibilities[1].format(games_hosting[user]['modes_params'][1]) + '; '
    if 2 in modes:
        text += possibilities[2].format(games_hosting[user]['modes_params'][2]) + '; '
    if 3 in modes:
        text += possibilities[3]
    return text


def create_inf_s(user):
    text = ''
    if games_hosting[user]['first'] == 'wins':
        text += 'Побеждает'
    else:
        text += 'Проигрывает'
    text += f' тот, кто первым набирает в сумме {games_hosting[user]["s"]} камней(я)(ень)'
    return text


def game_info(user):
    a = f'''
Режим игры:
Количество куч - {games_hosting[user]['heaps']}
Количество камней в кучах (по индексу) - {games_hosting[user]['stones_start']}
В игре можно {create_inf_possible(user)}
{create_inf_s(user)}
    '''
    buttons = ['start', 'изменить кол-во куч', 'изменить кол-во камней в каждой куче',
               'редактировать режимы изменения кол-ва камней', 'изменить пороговое значение суммы камней']
    keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    for btn in buttons:
        button = telebot.types.InlineKeyboardButton(text=btn)
        keyboard.add(button)
    bot.send_message(user, a, reply_markup=keyboard)


@bot.message_handler(commands=['create_game'])
def create_game(message):
    usr = message.from_user.id
    if usr not in users:
        users[usr] = {'mode': 'start', 'game': 0}
    if (usr in games_hosting and games_hosting[usr]['ready']) or users[usr]['mode'] == 'playing' or \
            users[usr]['mode'] == 'heap':
        bts = [telebot.types.InlineKeyboardButton(text='Да'), telebot.types.InlineKeyboardButton(text='Нет')]
        kb = telebot.types.ReplyKeyboardMarkup()
        kb.add(bts[0], bts[1])
        bot.send_message(usr, 'Вы собираетесь покинуть игру, хотите выйти?', reply_markup=kb)
        users[usr]['mode'] = 'leaving?'
    else:
        games_hosting[usr] = {'heaps': '2', 'stones_start': [10, 10], 'modes': [1, 2], 'modes_params': {1: '5', 2: '2'},
                              's': '63', 'first': 'wins', 'ready': False, 'players': [], 'now_goes': 0, 'closed': False,
                              'message_heaps': {}, 'message_goes': {}, 'log': [], 'last_player': 0}
        users[usr]['mode'] = 'game_creating'
        game_info(usr)


def new_member(user, new_user):
    btn = telebot.types.InlineKeyboardButton(text=f'Начать игру с количеством игроков: '
                                                  f'{len(games_hosting[user]["players"])}')
    kb = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1)
    btn1 = telebot.types.InlineKeyboardButton(text='Покинуть')
    kb.add(btn, btn1)
    bot.send_message(user, f'Новый игрок: {bot.get_chat_member(new_user, new_user).user.first_name}', reply_markup=kb)


@bot.message_handler(commands=['join_game'])
def join_game(message):
    user = message.from_user.id
    if user not in users:
        users[user] = {'mode': 'start', 'game': 0}
    if (user in games_hosting and games_hosting[user]['ready']) or users[user]['mode'] == 'playing' or \
            users[user]['mode'] == 'heap':
        bts = [telebot.types.InlineKeyboardButton(text='Да'), telebot.types.InlineKeyboardButton(text='Нет')]
        kb = telebot.types.ReplyKeyboardMarkup()
        kb.add(bts[0], bts[1])
        bot.send_message(user, 'Вы собираетесь покинуть игру, хотите выйти?', reply_markup=kb)
        users[user]['mode'] = 'leaving?'
    else:
        buttons = []
        for game in games_hosting:
            if games_hosting[game]['ready']:
                server_name = bot.get_chat_member(game, game).user.first_name
                buttons.append(telebot.types.InlineKeyboardButton(text=str(game) + ' ' + server_name))
        if len(buttons) == 0:
            bot.send_message(user, 'Нет доступных серверов, обновить список - команда /join_game')
        else:
            kb = telebot.types.ReplyKeyboardMarkup()
            for b in buttons:
                kb.add(b)
            bot.send_message(user, 'Выберите сервер, обновить список - команда /join_game', reply_markup=kb)
            users[user]['mode'] = 'connecting'


def query_check(query):
    if query.from_user.id not in users:
        return False
    if query.data not in ['1', '2', '3']:
        return False
    if users[query.from_user.id]['mode'] != 'playing':
        return False
    return True


@bot.callback_query_handler(lambda q: query_check(q))
def play(query):
    user = query.from_user.id
    game = users[user]['game']
    if games_hosting[game]['players'][games_hosting[game]['now_goes']] != user:
        bot.send_message(user, 'Не твой ход!')
    else:
        users[user]['mode'] = 'choose_heap'
        message_heaps = games_hosting[game]['message_heaps'][user]
        kb = telebot.types.InlineKeyboardMarkup(row_width=10)
        for u in range(len(games_hosting[game]['stones_start'])):
            kb.add(telebot.types.InlineKeyboardButton(text=str(u + 1), callback_data=query.data + ' ' + str(u)))
        bot.edit_message_text(str(games_hosting[game]['stones_start']) + '\n' + 'Выберите кучу:', user,
                              message_heaps.message_id, reply_markup=kb,
                              inline_message_id=query.id)
        users[user]['mode'] = 'heap'


@bot.callback_query_handler(lambda q: q.from_user.id in users and users[q.from_user.id]['mode'] == 'heap')
def change_heap(query):
    user = query.from_user.id
    game = users[user]['game']
    data = query.data.split()
    heaps = games_hosting[game]['stones_start']
    if data[0] == '1':
        evaluate = games_hosting[game]['modes_params'][1]
        heaps[int(data[1])] += int(evaluate)
    elif data[0] == '2':
        evaluate = int(games_hosting[game]['modes_params'][2])
        heaps[int(data[1])] *= evaluate
    elif data[0] == '3':
        evaluate = sum(heaps)
        heaps[int(data[1])] = evaluate
    games_hosting[game]['stones_start'] = heaps[:]
    users[user]['mode'] = 'playing'
    buttons = [telebot.types.InlineKeyboardButton(text=str(x), callback_data=x) for x in
               games_hosting[game]['modes']]
    kb = telebot.types.InlineKeyboardMarkup(row_width=3)
    games_hosting[game]['log'].append(heaps)
    for b in buttons:
        kb.add(b)
    for player in games_hosting[game]['players']:
        bot.edit_message_text(text=str(games_hosting[game]['stones_start']), chat_id=player,
                              message_id=games_hosting[game]['message_heaps'][player].message_id,
                              inline_message_id=query.id, reply_markup=kb)
    if sum(games_hosting[game]['stones_start']) >= int(games_hosting[game]['s']):
        set_winner(user)
    else:
        games_hosting[game]['now_goes'] += 1
        games_hosting[game]['now_goes'] = games_hosting[game]['now_goes'] % len(games_hosting[game]['players'])
        now_goes = games_hosting[game]['players'][games_hosting[game]['now_goes']]
        for player in range(len(games_hosting[game]['players'])):
            if player != games_hosting[game]['now_goes']:
                bot.edit_message_text('Сейчас ходит ' + bot.get_chat_member(now_goes, now_goes).user.first_name,
                                      games_hosting[game]['players'][player],
                                      games_hosting[game]['message_goes'][games_hosting[game]['players'][player]].
                                      message_id)
            else:
                try:
                    bot.edit_message_text('Ваш ход',
                                          games_hosting[game]['players'][player],
                                          games_hosting[game]['message_goes'][games_hosting[game]['players'][player]].
                                          message_id)
                except:
                    pass


def set_winner(winner):
    game = users[winner]['game']
    for player in games_hosting[users[winner]['game']]['players']:
        users[player]['mode'] = 'start'
        users[player]['game'] = 0
        if player == winner:
            bot.send_message(player, 'Ты победил, игра окончена')
        else:
            bot.send_message(player, 'Победитель - ' + bot.get_chat_member(winner, winner).user.first_name +
                             '. Игра окончена')
    games_hosting.pop(game)


@bot.message_handler(content_types=['text'])
def handle(message):
    user = message.from_user.id
    msg = message.text
    if user not in users:
        users[user] = {'mode': 'start', 'game': 0}
    mode = users[user]['mode']
    if mode == 'game_creating':
        if msg == 'изменить кол-во куч':
            users[user]['mode'] = 'change_heaps'
            bot.send_message(user, 'Отправьте количество куч (только число)')
        elif msg == 'изменить кол-во камней в каждой куче':
            users[user]['mode'] = 'change_stones'
            bot.send_message(user, 'Отправьте количество камней в каждой куче в формате: 5, 5, ..., 5')
        elif msg == 'редактировать режимы изменения кол-ва камней':
            users[user]['mode'] = 'change_modes'
            bot.send_message(user, 'Введите режим (1, 2 или 3) и его параметр'
                                   ' (0 в случае режима 3) в формате: 1 - 3, 2 - 4, 3 - 0 (можно использовать'
                                   ' не все параметры, в этом случае его не нужно писать)')
        elif msg == 'изменить пороговое значение суммы камней':
            users[user]['mode'] = 'change_threshold'
            bot.send_message(user, 'Отправьте новое значение пороговой суммы')
        elif msg == 'start':
            if len(games_hosting[user]['stones_start']) != int(games_hosting[user]['heaps']):
                bot.send_message(user, 'Количество куч и длина массива с количеством камней в каждой куче не совпадают')
            else:
                games_hosting[user]['ready'] = True
                games_hosting[user]['players'].append(user)
                users[user]['game'] = user
                users[user]['mode'] = 'in-game'
                btn = telebot.types.InlineKeyboardButton(text=f'Начать игру с количеством игроков: '
                                                              f'{len(games_hosting[user]["players"])}')
                btn2 = telebot.types.InlineKeyboardButton(text='Покинуть')
                kb = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1)
                kb.add(btn, btn2)
                bot.send_message(user, f'Ожидаем игроков. Код игры: {user}', reply_markup=kb)

    elif mode == 'change_heaps':
        try:
            games_hosting[user]['heaps'] = str(int(msg))
            game_info(user)
            users[user]['mode'] = 'game_creating'
        except:
            bot.send_message(user, 'wrong format')
    elif mode == 'change_stones':
        stones = msg.split(', ')
        try:
            stones = [int(x) for x in stones]
            games_hosting[user]['stones_start'] = stones
            game_info(user)
            users[user]['mode'] = 'game_creating'
        except:
            bot.send_message(user, 'wrong format')
    elif mode == 'change_modes':
        try:
            designed = msg.split(', ')
            modes = [None, None, None, None]
            for one in designed:
                n = one.split(' - ')
                modes[int(n[0])] = n[1]
            fin_modes = []
            mode_params = {}
            for m in range(4):
                if modes[m] is not None:
                    fin_modes.append(m)
                    mode_params[m] = str(int(modes[m]))
            games_hosting[user]['modes'] = fin_modes
            games_hosting[user]['modes_params'] = mode_params
            game_info(user)
            users[user]['mode'] = 'game_creating'
        except Exception:
            bot.send_message(user, 'wrong format')
    elif mode == 'change_threshold':
        try:
            msg = str(int(msg))
            games_hosting[user]['s'] = msg
            game_info(user)
            users[user]['mode'] = 'game_creating'
        except:
            bot.send_message(user, 'wrong format')
    elif mode == 'leaving?' or mode == 'leaving_game? heap' or mode == 'leaving_game? playing':
        if msg == 'Да':
            if user in games_hosting:
                for usr in games_hosting[user]['players']:
                    if usr != user:
                        users[usr]['game'] = 0
                        users[usr]['mode'] = 'start'
                        bot.send_message(usr, 'Владелец сервера игры покинул её же саму, игра окончена')
                games_hosting.pop(user)
            else:
                name = bot.get_chat_member(user, user).user.first_name
                for usr in games_hosting[users[user]['game']]['players']:
                    if usr != user:
                        bot.send_message(usr, f'Игрок {name} вышел из игры')
                games_hosting[users[user]['game']]['players'].remove(user)
                if mode == 'leaving?':
                    length = len(games_hosting[users[user]["game"]]["players"])
                    btn = telebot.types.InlineKeyboardButton(text=f'Начать игру с количеством игроков: '
                                                                  f'{length}')
                    btn1 = telebot.types.InlineKeyboardButton(text='Покинуть')
                    kb = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
                    kb.add(btn, btn1)
                    bot.send_message(users[user]["game"], 'Потеря бойца', reply_markup=kb)
                elif mode == 'leaving_game? playing' or mode == 'leaving_game? heap':
                    game = users[user]['game']
                    if games_hosting[game]['players'][games_hosting[game]['now_goes']] == user:
                        games_hosting[game]['now_goes'] += 1
                        games_hosting[game]['now_goes'] = games_hosting[game]['now_goes'] % len(
                            games_hosting[game]['players'])
                        now_goes = games_hosting[game]['players'][games_hosting[game]['now_goes']]
                        for player in games_hosting[game]['players']:
                            if player != user:
                                try:
                                    bot.edit_message_text(
                                        'Сейчас ходит ' + bot.get_chat_member(now_goes, now_goes).user.first_name,
                                        games_hosting[game]['players'][player],
                                        games_hosting[game]['message_goes'][
                                            games_hosting[game]['players'][player]].
                                        message_id)
                                except:
                                    pass
            users[user]['game'] = 0
            users[user]['mode'] = 'start'
            bot.send_message(user, 'Вы покинули игру')
        elif msg == 'Нет':
            if user in games_hosting:
                if mode == 'leaving?':
                    btn = telebot.types.InlineKeyboardButton(text=f'Начать игру с количеством игроков: '
                                                                  f'{len(games_hosting[user]["players"])}')
                    kb = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1)
                    btn1 = telebot.types.InlineKeyboardButton(text='Покинуть')
                    kb.add(btn, btn1)
                else:
                    btn = 'Выйти'
                    kb = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1)
                    kb.add(btn)
                bot.send_message(user, 'Игра продолжается', reply_markup=kb)

            else:
                bot.send_message(user, 'Игра продолжается')
            if mode == 'leaving_game? heap':
                users[user]['mode'] = 'heap'
            elif mode == 'leaving?':
                users[user]['mode'] = 'in-game'
            else:
                users[user]['mode'] = 'playing'

    elif mode == 'connecting':
        query = message.text.split()
        query = [query[0], user]
        try:
            query[0] = int(query[0])
            if query[0] in games_hosting:
                users[user]['game'] = query[0]
                btn = telebot.types.InlineKeyboardButton(text='Покинуть')
                kb = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
                kb.add(btn)
                bot.send_message(query[1], 'Игра скоро начнётся', reply_markup=kb)
                games_hosting[query[0]]['players'].append(user)
                new_member(query[0], user)
                users[user]['mode'] = 'in-game'
            else:
                bot.send_message(query[1], 'Кажется, этот сервер ныне недоступен')
        except:
            bot.send_message(user, 'error')
    elif mode == 'in-game':
        if msg == 'Покинуть':
            bts = [telebot.types.InlineKeyboardButton(text='Да'), telebot.types.InlineKeyboardButton(text='Нет')]
            kb = telebot.types.ReplyKeyboardMarkup()
            kb.add(bts[0], bts[1])
            bot.send_message(user, 'Вы собираетесь покинуть игру, хотите выйти?', reply_markup=kb)
            users[user]['mode'] = 'leaving?'
        if user in games_hosting:
            sp = msg.split()
            if sp[:5] == ['Начать', 'игру', 'с', 'количеством', 'игроков:']:
                games_hosting[user]['last_player'] = user
                games_hosting[user]['log'].append(games_hosting[user]['stones_start'])
                first = games_hosting[user]['players'][0]
                if sum(games_hosting[user]['stones_start']) >= int(games_hosting[user]['s']):
                    set_winner(games_hosting[user]['last_player'])
                else:
                    for usr in games_hosting[user]['players']:
                        bot.send_message(usr, f'Первый, кто наберет сумму больше либо равную '
                                              f'{games_hosting[user]["s"]}, победил')
                        bot.send_message(usr, 'Положение куч(и) камней: ')
                        buttons = [telebot.types.InlineKeyboardButton(text=str(x), callback_data=x) for x in
                                   games_hosting[user]['modes']]
                        text = ''
                        for one in games_hosting[user]['modes_params']:
                            text += str(one) + '. ' + possibilities[one].\
                                format(games_hosting[user]['modes_params'][one]) + '\n'
                        kb = telebot.types.InlineKeyboardMarkup(row_width=3)
                        for b in buttons:
                            kb.add(b)
                        games_hosting[user]['message_heaps'][usr] = \
                            bot.send_message(usr, str(games_hosting[user]['stones_start']), reply_markup=kb)

                        bot.send_message(usr, text)
                        btn = telebot.types.InlineKeyboardButton(text='Выйти')
                        kb = telebot.types.ReplyKeyboardMarkup()
                        kb.add(btn)
                        if usr != first:
                            games_hosting[user]['message_goes'][usr] = \
                                bot.send_message(usr, 'Первый ход делает ' + str(bot.get_chat_member(first, first).
                                                                                 user.first_name))
                            bot.send_message(usr, 'Игра началась', reply_markup=kb)
                        else:
                            games_hosting[user]['message_goes'][usr] = bot.send_message(usr, 'Первый ход делаете вы')
                            bot.send_message(usr, 'Игра началась', reply_markup=kb)
                        users[usr]['mode'] = 'playing'
    elif mode == 'playing' or mode == 'heap':
        if msg == 'Выйти':
            bts = [telebot.types.InlineKeyboardButton(text='Да'), telebot.types.InlineKeyboardButton(text='Нет')]
            kb = telebot.types.ReplyKeyboardMarkup()
            kb.add(bts[0], bts[1])
            bot.send_message(user, 'Вы собираетесь покинуть игру, хотите выйти?', reply_markup=kb)
            users[user]['mode'] = 'leaving_game? ' + mode

# изменить начальное количество камней
# При редактировании условий игры должно редактироваться сообщение с условиями и удаляться сообщения пользователя
# возможность установить название сервера
# возможность создания частного сервера
# сделать try для каждого edit_message


try:
    bot.polling()
except:
    pass
 