# This script is used to create the threshold data


class TMCCount:
    def __init__(self, word):
        self.word = word
        self.bin_word = format(int(word, 16), '08b')

        self.edge_count = self.bin_word[3:]

        if (self.bin_word[2] == '1'):
            self.edge_valid = True
        else:
            self.edge_valid = False

        self.bit_7 = self.bin_word[0]

    def dump(self):
        output = ' TMCCount:'
        output += ' edge_count=' + str(self.edge_count)
        output += ' edge_valid=' + str(self.edge_valid)
        output += ' bit_7=' + str(self.bit_7)
        print(output)


class DAQStatus:
    def __init__(self, word):
        self.word = word
        self.bin_word = format(int(word, 16), '04b')

        self.bit_0 = self.bin_word[3]
        self.bit_1 = self.bin_word[2]
        self.bit_2 = self.bin_word[1]
        self.bit_3 = self.bin_word[0]

        if ((int(self.bit_0) + int(self.bit_1) + int(self.bit_2) + int(self.bit_3)) > 0):
            self.is_ok = False
        else:
            self.is_ok = True


class DAQLine:
    def __init__(self, words):
        self.words = words

        self.re_1 = TMCCount(words[1])
        self.fe_1 = TMCCount(words[2])

        self.re_2 = TMCCount(words[3])
        self.fe_2 = TMCCount(words[4])

        self.re_3 = TMCCount(words[5])
        self.fe_3 = TMCCount(words[6])

        self.re_4 = TMCCount(words[7])
        self.fe_4 = TMCCount(words[8])

        self.clock_count = words[0]
        self.pps = words[9]
        self.utc_time = words[10]
        self.utc_date = words[11]

        if words[12] == 'A':
            self.gps_valid = True
        elif words[12] == 'V':
            self.gps_valid = False

        self.n_gps = int(words[13])
        self.daq_status = DAQStatus(words[14])
        self.time_delay = words[15]

    def dump(self):
        output = 'DAQLine:'
        output += ' clock_count=' + str(self.clock_count)
        output += ' pps=' + str(self.pps)
        output += ' utc_time=' + str(self.utc_time)
        output += ' utc_date=' + str(self.utc_date)
        output += ' gps_valid=' + str(self.gps_valid)
        output += ' time_delay=' + str(self.time_delay)
        print(output)

        print(' rising edge 0:')
        self.re_0.dump()
        print(' falling edge 0:')
        self.fe_0.dump()

# Example of event
# 687C4047 80 00 2B 00 00 00 00 00 67037CB8 000322.027 180516 A 03 0 +0053
# 687C4047 00 00 00 00 3A 00 00 00 67037CB8 000322.027 180516 A 03 0 +0053
# 687C4048 00 00 00 28 00 00 00 00 67037CB8 000322.027 180516 A 03 0 +0053
# 687C4048 00 00 00 00 00 36 00 00 67037CB8 000322.027 180516 A 03 0 +0053


def EventFinder(data):
    # iterates through a list and identifies events. Collects them and returns list of events, each of which is a list
    # of data lines within event

    single_event = []
    AllEvents = []

    index = 0

    while index != len(data):
        single_event = []
        single_event.append(data[index])

        while ((int(format(int((data[index][9:11]), 16), '08b'))/10000000)) != 1:

            single_event.append(data[index])
            index += 1
            print index
        AllEvents.append(single_event)
    print AllEvents[0]
    return AllEvents

    # # Loop through the enre data creating a list AllEvents which contain Lists of the linces of each event
    # while data != []:
    #     # Loop through the lines until you have the first event tag over 1
    #     single_event = []
    #     flag = False
    #     for line in data:
    #         check = line[9:11]
    #         check_bin = format(int(check, 16), '08b')
    #         print check_bin
    #         if check_bin[0] == '1' and flag == False:
    #             single_event.append(line)
    #             flag = True
    #         elif check_bin[0] == '0' and flag == True:
    #             single_event.append(line)
    #         elif check_bin[0] == '1' and flag == True:
    #             for item in single_event:
    #                 data.remove(item)
    #             AllEvents.append(single_event)
    #             break

    # return 0


def MainThreshold(file):
    # Main Function
    data = open(file, 'r')
    data_lines = data.readlines()
    AllEvents = EventFinder(data_lines)

    # Returns a path to the created file
    return AllEvents


MainThreshold('6148.2016.0518.0')
