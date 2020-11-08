import csv


def updateChecker(clientNo):

    clientNo = str(clientNo)  # To make sure that client_no is a string

    print(f'recieved param of type {type(clientNo)}')
    csv_file = open('./database/updates.csv', 'r')
    reader = csv.reader(csv_file, delimiter=',')

    for row in reader:
        if(row[0] == clientNo):
            return row[1]

    return 0


# for testing this module
# clientNo = input('enter client no: ')

# update = updateChecker(clientNo)

# if update == 0:
#     print('no update for this client')
# else:
#     print(update)
