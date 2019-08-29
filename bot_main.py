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

# Modified print function to handle UCS-2 characters
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

#Start of Bot
bot = telepot.Bot(ra_token)
print(bot.getMe()) #check bot details

ra_id = []

#User polls stored in a dictionary. chat_id : [poll name]
bot_mem = {}
rollkey = InlineKeyboardMarkup(inline_keyboard=[
                   [InlineKeyboardButton(text='I\'m In', callback_data='stay'),
                    InlineKeyboardButton(text='Not Staying', callback_data='notstay')],
                   [InlineKeyboardButton(text='Publish (Present)', callback_data='present_pub')],
                   [InlineKeyboardButton(text='Publish (Absent)', callback_data='absent_pub')],
               ])

initiate = duty_reminder.Duty_cal() #Create calendar instance

class Poll():
    #General poll object
    def __init__(self, chat_id, title, date, shift):
        self.chat_id = chat_id
        self.title = title
        self.msg_id = None #identifier for response edit
        self.keyboard = []
        self.date = date
        self.response = [[],[]]
        self.shift = shift

    def get_msg_id(self):
        return self.msg_id

    def addButton(self, buttontext):
        #adds keyboard button
        self.keyboard.append([InlineKeyboardButton(text=buttontext, callback_data = buttontext)])
        return True

    def get_date(self):
        return self.date

    def get_title(self):
        return self.title

    def add_response(self, user_tup, answer):
        staying, absent = self.response
        if answer == 'stay' and (user_tup not in staying):
            if user_tup in absent:
                absent.remove(user_tup)
            staying.append(user_tup)
            return True

        elif answer == 'notstay' and (user_tup not in absent):
            if user_tup in staying:
                staying.remove(user_tup)
            absent.append(user_tup)
            return True
        return False

    def get_result(self):
        result = self.get_title() + '\n\n'
        staying, absent = self.response

        # Dictionary of RA staying and absent [[stay],[absent]]
        house_dict = {'Aquila': ['',''], 'Noctua': ['',''], 'Ursa': ['',''], 'Leo': ['',''], 'Draco': ['','']}

        for userinfo in staying:
            username, userid = userinfo
            name, house = ra_listbyid[str(userid)]
            house_dict[house][0] += (name+', ') #add name to staying

        for userinfo in absent:
            username, userid = userinfo
            name, house = ra_listbyid[str(userid)]
            house_dict[house][1] += (name+', ') #add name to absent

        notstay = 'RA(s) Not Staying:\n'
        for house in house_dict:
            if house_dict[house][0]: #If there is RA staying
                result += (house + ': ' + house_dict[house][0] + '\n')
            else:
                result += (house + ': none\n')
            if house_dict[house][1]: #If there is RA not staying
                notstay += (house + ': ' + house_dict[house][1] + '\n')
            else:
                notstay += (house + ': none\n')
        return (result, notstay)

    def publish(self, pub_type):
        #Send a format for easy copy pasting
        quote = 'I am the duty RA for ' + self.get_date() + self.shift + '\n\
I have changed the duty cards in Level 1 and Basement. I will be staying in the building until the duty time is over.'
        stay, notstay = self.get_result()

        if pub_type == 'stay':
            return quote +'\n\n'+ stay
        else:
            return quote +'\n\n'+ notstay



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
    ra_poll = Poll(chat_id, title, check_date.strftime('%d %b %Y'), shift)

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
        bot.sendMessage(chat_id, 'Hola mi amigo! {},\nYou have {} duty today ({})'.format(name, shift,todate))
def applyleave(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    document= open('RAs\' Leave Application Form.pdf','rb')
    note ='Hello people, below are some administrative matters regarding leave applications.\n'\
              'To apply for leave,\n'\
              '1) Print the leave application form and get your RF to sign it for their approval.\n'\
              '2) Text Prof Nav (DSL) to inform him about it (YOUR LEAVE WILL ONLY BE APPROVED AFTER HIS APPROVAL)\n'\
              '3) Pass the form to the admin team (i.e. Claudia till the next team is formed) for them to record it on SharePoint and they will then pass it to prof nav for him to sign\n\n'\
              'Note: As stated in the contract, all leave applications must be approved 2 weeks before the commencement of your leave. For emergency cases, please contact Prof nav for more assistance.\n'\
              '- Claudia'

    bot.sendDocument(chat_id, file_name)
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

    print(msg, '\n')

    user_id = get_user(msg)
    if user_id not in ra_id:
        ra_id.append(user_id)
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

    if msg_identifier in bot_mem: # Check for poll existence
        poll = bot_mem[msg_identifier] # Gets referenced poll
        if query_data == 'stay': # Check button
            if poll.add_response(user_tup, query_data):
                result_tup = poll.get_result()[0] +'\n'+ poll.get_result()[1]
                bot.editMessageText(msg_identifier, result_tup, reply_markup=rollkey) #modify poll with answer
                bot.answerCallbackQuery(query_id, 'Answer Submitted')
            else:
                bot.answerCallbackQuery(query_id, 'Same Answer')

        elif query_data == 'notstay':
            if poll.add_response(user_tup, query_data):
                result_tup = poll.get_result()[0] +'\n'+ poll.get_result()[1]
                bot.editMessageText(msg_identifier, result_tup, reply_markup=rollkey) #modify poll with answer
                bot.answerCallbackQuery(query_id, 'Answer Submitted')
            else:
                bot.answerCallbackQuery(query_id, 'Same Answer')

        elif query_data == 'present_pub':
            bot.sendMessage(from_id, poll.publish('stay'))
            bot.answerCallbackQuery(query_id, 'Published!')

        elif query_data == 'absent_pub':
            bot.sendMessage(from_id, poll.publish('absent'))
            bot.answerCallbackQuery(query_id, 'Published!')
    else:
        print('poll not found')
        bot.answerCallbackQuery(query_id, 'Poll Error')



def backup():
    #sets excel file path
    filename = 'poll_backup.xlsx' #datetime.today().strftime('%d%b%Y %H%M_%S')
    writer = pd.ExcelWriter(filename)
    poll_store = [] #store poll data in list

    for chat_id in bot_mem: #iterate through every poll
        polls = bot_mem[chat_id]
        staying, absent = polls.response
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


initiate.start()
# restore() #restores poll from backup

## Starts listening for messages
MessageLoop(bot, {'chat': on_chat_message,
                  'callback_query': on_callback_query,}
            ).run_as_thread(relax=2)

print('Listening ...')



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
