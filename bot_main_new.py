import time as ostime
import telepot
import random
from telepot.loop import *
from telepot.namedtuple import *
from datetime import *
import pandas as pd
import duty_reminder
import threading as thr
from config import *
import builtins

def print_ucs2(*args, print=builtins.print, **kwds):
    args2 = []
    for a in args:
        a = str(a)
        if max(a) > '\uffff':

            b = a.encode('utf-16le', 'surrogatepass')
            chars = [b[i:i+2].decode('utf-16le', 'surrogatepass')
                for i in range(0, len(b), 2)]
            a = ''.join(chars)
        args2.append(a)
    print(*args2, **kwds)

builtins._print = builtins.print
builtins.print = print_ucs2

bot = telepot.Bot(ra_token)
print(bot.getMe())

initiate = duty_reminder.Duty_cal()
initiate.start()

#User polls stored in a dictionary. chat_id : [poll name]
bot_mem = {}


rollkey = InlineKeyboardMarkup(inline_keyboard=[
                   [InlineKeyboardButton(text='I\'m In', callback_data='present'),
                    InlineKeyboardButton(text='I\'m Out', callback_data='absent'),
                    InlineKeyboardButton(text='On Leave', callback_data='leave')],
                   [InlineKeyboardButton(text='Publish (Present)', callback_data='present_pub'),
                    InlineKeyboardButton(text='Publish (Absent)', callback_data='absent_pub')],
               ])
## Bot commands

def bot_help(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    help_text = 'Residential Assistant Bot has been made by Wei Song \n\
For any bugs or issues, pm @twsx94\n\nUtown Campus Security 6601 2004\nRC4 maintenance 6516 1515'

    bot.sendMessage(chat_id, help_text)

def roll(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    bot.sendMessage(chat_id, 'Random roll: ' + str(random.randint(1,100)))

def compliment(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    username = get_command_arg(msg)
    if not username:
        username, user_id = get_user(msg)
    compliments = ['is GOD DAMN SEXY', 'makes other people look bad', 'is PERFECTION!', 'is so Humourous!', 'is my inspiration', 'has the Figure that KILLS!']
    bot.sendMessage(chat_id, username + ' ' + random.choice(compliments))

def greetings(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    text_len = len(msg['text'])
    comm_len = get_command_length(msg)
    if text_len > get_command_length(msg):
        user = msg['text'][comm_len+1:]
    else:
        user, user_id = get_user(msg)
    bot.sendMessage(chat_id, 'GREETINGS! ' + user)

def rollcall(msg, shift):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(shift + ' check')

    arg = get_command_arg(msg)
    if arg == 'tmr':
        check_date = date.today() + timedelta(days=1)
    elif arg == 'dayafter':
        check_date = date.today() + timedelta(days=2)
    else:
        check_date = date.today()
    title = 'RA Staying in for ' + check_date.strftime('%d %b %Y') + shift
    ra_poll = Attendance(chat_id, title, check_date.strftime('%d %b %Y'), shift)

    sent = bot.sendMessage(chat_id, ra_poll.get_title(), reply_markup=rollkey)
    ra_poll.msg_id = telepot.message_identifier(sent)
    bot_mem[ra_poll.get_msg_id()] = ra_poll #stores poll in memory

def whosduty(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    todate = datetime.today().strftime('%A %d %b %Y')
    tomonth = datetime.today().strftime('%b')
    dutycal = initiate.get_cal()
    duty = dutycal[tomonth][todate]
    for shift in duty:
        name = duty[shift]
        if name:
            bot.sendMessage(chat_id, 'Hola mi amigo! {},\nYou have {} duty today ({})'.format(name, shift, todate))
        else:
            bot.sendMessage(chat_id, 'No one has been scheduled to be on duty today ({})'.format(todate))

def applyleave(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    file_path = leave_file_path
    document= open(file_path,'rb')
    note ='Hello people, below are some administrative matters regarding leave applications.\n'\
              'To apply for leave,\n'\
              '1) Print the leave application form and get your RF to sign it for their approval.\n'\
              '2) Text Prof Nav (DSL) to inform him about it (YOUR LEAVE WILL ONLY BE APPROVED AFTER HIS APPROVAL)\n'\
              '3) Pass the form to the admin team (i.e. Claudia till the next team is formed) for them to record it on SharePoint and they will then pass it to prof nav for him to sign\n\n'\
              'Note: As stated in the contract, all leave applications must be approved 2 weeks before the commencement of your leave. For emergency cases, please contact Prof nav for more assistance.\n'\
              '- Claudia'

    bot.sendDocument(chat_id, document)
    bot.sendMessage(chat_id, note)


#Dictionary of bot functions
bot_func = {'/help': bot_help,
            '/roll': roll,
            '/compliment': compliment,
            '/greet': greetings,
            '/rollcallpm': lambda msg: rollcall(msg, ' PM'),
            '/rollcallam': lambda msg: rollcall(msg, ' AM'),
            '/whosduty': whosduty,
	    '/applyleave': applyleave,
            }

## Message handling
def get_command_arg(msg):
    #checks if command is followed by an argument, returns argument in string. Default returns username
    text_len = len(msg['text'])
    comm_len = get_command_length(msg)
    if text_len > get_command_length(msg):
        arg = msg['text'][comm_len+1:]
    else:
        arg = False
    return arg

def text_type(msg):
    #returns type of entities contained in message, in string

    if 'entities' in msg:
        msg_type = msg['entities'][0]['type']
    else:
        msg_type = list(msg)[4]

    return msg_type

def get_command_length(msg):
    return msg['entities'][0]['length']

def get_user(msg):
    return (msg['from']['first_name'], msg['from']['id'])


def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    #print(msg, '\n')
    user_id = get_user(msg)

    #check message type and pass to appropriate handles.
    msg_type = text_type(msg)
    if msg_type == 'bot_command':
        #print('command received')
        command_length = get_command_length(msg)
        command = msg['text']
        if '@RA_Helperbot' in command: #removes bot handle from command if it exist
            command = command.replace('@RA_Helperbot', '')
        bot_func[command[:command_length]](msg)

    elif msg_type == 'text':
        print('text received')
    if msg_type == 'photo':
        print('photo received')

def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    msg_identifier = telepot.origin_identifier(msg) #retrieves message identifier from callback query [chat id, msg id]
    user_tup = get_user(msg) #gets username and id

    state = ('leave','absent','present')
    if msg_identifier in bot_mem: # Check for poll existence
        poll = bot_mem[msg_identifier] # Gets referenced poll


        if query_data == 'present_pub':
            bot.sendMessage(from_id, poll.publish('stay'))
            bot.answerCallbackQuery(query_id, 'Published!')

        elif query_data == 'absent_pub':
            bot.sendMessage(from_id, poll.publish('absent'))
            bot.answerCallbackQuery(query_id, 'Published!')

        elif query_data in state:

            poll.edit_status(user_tup, query_data)
            result_tup = poll.get_result()
            bot.editMessageText(msg_identifier, result_tup[5], reply_markup=rollkey) #modify poll with answer
            bot.answerCallbackQuery(query_id, 'Answer Submitted')


    else:
        print('poll not found')
        bot.answerCallbackQuery(query_id, 'Poll Error, Try starting new Roll call')


'''
def backup():
    #sets excel file path
    filename = 'poll_backup.xlsx' #datetime.today().strftime('%d%b%Y %H%M_%S')
    writer = pd.ExcelWriter(filename)
    poll_store = [] #store poll data in list

    for chat_id in bot_mem: #iterate through every poll
        polls = bot_mem[chat_id]
        msg_tuple = polls.get_result()
        data = [polls.get_date(), polls.get_title(), polls.shift, staying, absent, chat_id]
        poll_store.append(data)

    #Generate dataframe
    poll_df = pd.DataFrame(poll_store,
                           columns=['Date', 'Title', 'Shift', 'Present', 'Absent', 'Chat_id'])
    print(poll_df)
    poll_df.to_excel(writer,'Polls') #Convert dataframe to excel, sheet name = Polls
    writer.save() #save excel
    writer.close() #close writer

    print('Poll saved \nLast backup ' + filename)

def restore():
    filename = 'poll_backup.xlsx'
    dfs = pd.read_excel(filename, sheet_name='Polls')
    for poll in dfs.values:
        date, title, shift, present, absent, chat_id = list(poll)
        bot_mem[eval(chat_id)] = Poll(eval(chat_id), title, date, shift)
        bot_mem[eval(chat_id)].response = [eval(present),eval(absent)]


    return True
'''

duty_cal = duty_reminder.Duty_cal() #Create calendar instance

#restore() #restores poll from backup

## Starts listening for messages
MessageLoop(bot, {'chat': on_chat_message,
                  'callback_query': on_callback_query,}
            ).run_as_thread(relax=2)

print('Listening ...')

while True:
    ostime.sleep(10)

'''
def test():
    counter = 1
    while counter < 10:
        counter += 1
        print(counter)
        ostime.sleep(10)

if __name__ == '__main__': # If this module is being imported, code below will not run
    p = thr.Thread(target=test) #sets target function as a Thread
    print('parallel process running')
    p.start()
'''
