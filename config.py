import csv

#Configuration file for RA Helper bot

ra_token = '609175111:AAHtto1acCS7T1kBMw_-aONeKrntnRgSW7k'
# ra_token = '901297398:AAH64M9uzAmr5dzkv9MNcd8UsdRe3wOhZ_g'
dev_token = '418919776:AAFtP-yRuriRMPZp7jZp-MIkmfjv668nFGI'

'''
ra_list = {'Abdullah': (88985965, 'Ursa'), 'Anh': (215588173, 'Aquila'), 'Claudia': (297090900, 'Ursa'),
           'David': (11549679, 'Leo'), 'Hafiz': (174955135, 'Noctua'), 'Jingjing': (228914289, 'Noctua'),
           'Joshua': (128731381, 'Draco'), 'Kai Lin': (145540392, 'Draco'), 'Nabil': (97332271, 'Aquila'),
           'Sabrina': (36007644, 'Ursa'), 'Sugiarto': (135474172, 'Aquila'), 'Wei Song': (130446496, 'Leo'),
           'Yi Quan': (104986701, 'Draco'), 'Ying Tze': (114835155, 'Noctua'), 'Zicen': (139286512, 'Leo'),
           'Brian': (209469386, 'Draco'),'Reuben': (111493999, 'Leo')
           }
'''

ra_masterlist = {'88985965': ('Abdullah', 88985965, 'Ursa', 'unanswered'), '215588173': ('Anh', 215588173, 'Aquila','unanswered'),
               '209469386': ('Brian', 209469386, 'Draco', 'unanswered'), '174955135': ('Hafiz', 174955135, 'Noctua','unanswered'),
               '228914289': ('Jingjing', 228914289, 'Noctua','unanswered'), '128731381': ('Joshua',128731381, 'Draco','unanswered'),
               '145540392': ('Kai Lin', 145540392, 'Draco','unanswered'), '97332271': ('Nabil',97332271, 'Aquila','unanswered'),
               '36007644': ('Sabrina', 36007644, 'Ursa','unanswered'), '135474172': ('Sugiarto', 135474172, 'Aquila','unanswered'),
               '130446496': ('Wei Song', 130446496, 'Leo','unanswered'),
               '114835155': ('Ying Tze', 114835155, 'Noctua','unanswered'), '139286512': ('Zicen', 139286512, 'Leo','unanswered'),
               '297090900': ('Claudia', 297090900, 'Ursa', 'unanswered'), '111493999': ('Reuben', 111493999, 'Leo','unanswered')
               }

# str id : (name, tele_id, house, state) where state can be any of the 4: ['leave','present', 'unanswered', 'absent']




duty_filename = 'RA Duty and Leave Schedule_201819S1.xlsx'

admin_ra = ['Claduia','Anh','Ying Tze']

def read_csv(csvfilename):
    rows = ()
    with open(csvfilename) as csvfile:
        file_reader = csv.reader(csvfile)
        for row in file_reader:
            rows += (tuple(row), )
    return rows

def import_ra_list():
    ra_csv = read_csv('RA_list_rc4.csv')[1:] #reads csv file containing values of RA
    ra_id_dict = {}
    ra_dict ={}
    for row in ra_csv:
        name, tele_id, house = row
        ra_dict[name] = (int(tele_id), house)
        ra_id_dict[tele_id] = (name, house)
    return ra_id_dict


#### Roll call class
class Attendance():
    #General poll object
    def __init__(self, chat_id, title, date, shift):
        self.chat_id = chat_id
        self.title = title
        self.msg_id = None #identifier to edit rollcall message
        self.date = date
        self.ralist = ra_masterlist.copy()
        self.shift = shift

    def get_msg_id(self):
        return self.msg_id

    def get_date(self):
        return self.date

    def get_title(self):
        return self.title

    def edit_status(self, user_tup, answer):
        userid = user_tup[1]
        user_attribute = self.ralist[str(userid)]
        new_user_attribute = user_attribute[0:3]+(answer,)
        self.ralist[str(userid)] = new_user_attribute
        return None

    def get_result(self):
        result = self.get_title() + '\n\n'

        present = []
        absent = []
        leave = []
        unanswered = []
        #Classify base on status

        for userkey in self.ralist:
            ra_attribute = self.ralist[userkey]
            ra_name, ra_teleid, ra_house, ra_status = ra_attribute

            if ra_status == 'present':
                present.append((ra_name, ra_house))

            elif ra_status == 'absent':
                absent.append((ra_name, ra_house))

            elif ra_status == 'leave':
                leave.append((ra_name, ra_house))

            elif ra_status == 'unanswered':
                unanswered.append(ra_name)

        #Generate Message String
        present_msg = ''

        house_list = ['Aquila', 'Noctua', 'Ursa', 'Leo', 'Draco']

        def get_fil_list(house, stat_list):
            return list(filter(lambda x: x[1] == house, stat_list))

        for rc_house in house_list:
            house_present = get_fil_list(rc_house, present)
            present_msg += (rc_house + ': ')
            if house_present:
                for user_present in house_present:
                    present_msg += (user_present[0] + ', ')
            else:
                present_msg += 'None'

            present_msg += '\n'

        #Generate not staying
        absent_msg = '\nRA(s) Not Staying:\n'

        for rc_house in house_list:
            if absent == False:
                absent_msg += 'None'
                break
            house_absent = get_fil_list(rc_house, absent)
            absent_msg += (rc_house + ': ')
            if house_absent:
                for user_absent in house_absent:
                    absent_msg += (user_absent[0]+', ')
            else:
                absent_msg += 'None'

            absent_msg += '\n'

        #Generate on leave
        leave_msg = '\nRA(s) on Leave:\n'

        for rc_house in house_list:
            if leave == False:
                leave_msg += 'None'
                break
            house_leave = get_fil_list(rc_house, leave)
            leave_msg += (rc_house + ': ')
            if house_leave:
                for user_leave in house_leave:
                    leave_msg += (user_leave[0]+', ')
            else:
                leave_msg += 'None'

            leave_msg += '\n'

        #Generate unanswered list
        unanswered_msg = '\nHave not responded:\n'

        for users in unanswered:
            unanswered_msg += users
            unanswered_msg += ', '

        combine = (result+ present_msg+ absent_msg+ leave_msg+ unanswered_msg)
        msg_tuple = (result, present_msg, absent_msg, leave_msg, unanswered_msg, combine)

        return msg_tuple

    def publish(self, pub_type):
        #Send a format for easy copy pasting
        quote = 'I am the duty RA for ' + self.get_date() + self.shift + '\n\
I have changed the duty cards in Level 1 and Basement. I will be staying in the building until the duty time is over.\n'
        msg_tuple = self.get_result()
        result, present_msg, absent_msg, leave_msg, unanswered, combined = msg_tuple

        if pub_type == 'stay':
            return quote +'\n'+ result+ present_msg + leave_msg
        else:
            return quote +'\n'+ absent_msg + leave_msg
