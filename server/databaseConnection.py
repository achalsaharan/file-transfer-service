import csv


class Database:

    def findFileHash(self, filename):
        csv_file = open('./database/updates.csv', 'r')
        reader = csv.reader(csv_file, delimiter=',')

        for row in reader:
            if(row[1] == filename):
                return row[2]

        return 0

    def checkUpdate(self, clientNo):

        clientNo = str(clientNo)  # To make sure that client_no is a string

        csv_file = open('./database/updates.csv', 'r')
        reader = csv.reader(csv_file, delimiter=',')

        for row in reader:
            if(row[0] == clientNo):
                return row[1]

        return 0
     
    def erase_entry(self, clientNo):
        clientNo = str(clientNo)
                
        lines = list()

        with open('./database/updates.csv', 'r') as readFile:
            reader = csv.reader(readFile)
            for row in reader:
                if row[0] == clientNo:
                    continue
                lines.append(row)

                
        with open('./database/updates.csv', 'w', newline='') as writeFile:
            writer = csv.writer(writeFile)
            for row in lines:
                writer.writerow(row)

    # for testing this module
    # clientNo = input('enter client no: ')

# update = updateChecker(clientNo)

# if update == 0:
#     print('no update for this client')
# else:
#     print(update)
