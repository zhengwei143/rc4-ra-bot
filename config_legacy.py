import csv

#Configuration file for RA Helper bot

ra_token = '609175111:AAHtto1acCS7T1kBMw_-aONeKrntnRgSW7k'
dev_token = '418919776:AAFtP-yRuriRMPZp7jZp-MIkmfjv668nFGI'

ra_list = {'Abdullah': (88985965, 'Ursa'), 'Anh': (215588173, 'Aquila'), 'Claudia': (297090900, 'Ursa'),
           'David': (11549679, 'Leo'), 'Hafiz': (174955135, 'Noctua'), 'Jingjing': (228914289, 'Noctua'),
           'Joshua': (128731381, 'Draco'), 'Kai Lin': (145540392, 'Draco'), 'Nabil': (97332271, 'Aquila'),
           'Sabrina': (36007644, 'Ursa'), 'Sugiarto': (135474172, 'Aquila'), 'Wei Song': (130446496, 'Leo'),
           'Yi Quan': (104986701, 'Draco'), 'Ying Tze': (114835155, 'Noctua'), 'Zicen': (139286512, 'Leo'),
           'Brian': (209469386, 'Draco'),'Reuben': (111493999, 'Leo')
           }
ra_listbyid = {'88985965': ('Abdullah', 'Ursa'), '215588173': ('Anh', 'Aquila'), '209469386': ('Brian', 'Draco'),
               '11549679': ('David', 'Leo'), '174955135': ('Hafiz', 'Noctua'), '228914289': ('Jingjing', 'Noctua'),
               '128731381': ('Joshua', 'Draco'), '145540392': ('Kai Lin', 'Draco'), '97332271': ('Nabil', 'Aquila'),
               '36007644': ('Sabrina', 'Ursa'), '135474172': ('Sugiarto', 'Aquila'), '130446496': ('Wei Song', 'Leo'),
               '104986701': ('Yi Quan', 'Draco'), '114835155': ('Ying Tze', 'Noctua'), '139286512': ('Zicen', 'Leo'),
               '297090900': ('Claudia', 'Ursa'), '111493999': ('Reuben', 'Leo')
               }

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

        
