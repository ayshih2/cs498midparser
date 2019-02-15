import csv
import os
import collections

# directory is the path to a folder of peer evaluation txt files
directory = '/Users/annabelleshih/Desktop/CS498PeerEvaluations/peerevaluationstxtfiles'
# key - netid, value - object w/ team #, num teammates, own score, averaged score from others
students = {}
# number of actual people per team - 8 teams total for SP19 CS 498 MID class
teams = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0}


class grades:
    def __init__(self, team, own, other, num_teammates, teammates):
        self.team = team
        self.own = own
        self.other = other
        self.num_teammates = num_teammates
        self.teammates = teammates


# populate students dict with netid as key and new grades object (default: team #, 0, 0, {})
with open("/Users/annabelleshih/Desktop/CS498PeerEvaluations/CS498_team_assignments.csv") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
        if row:
            email = row[2]
            if email != "Email" and email != "":
                students[email[:email.find("@")]] = grades(row[3], 0, 0, 0, {})
                # keep track of num students in a team
                teams[row[3]] += 1


# since students enter score as [number]%, must strip % symbol
def get_score(score_str):
    return int(score_str[:score_str.find("%")])


for filename in os.listdir(directory):
    if filename.endswith(".txt"):
        # read contents of each file
        with open(directory + "/" + filename, encoding="utf-8-sig") as f:
            foundOwner = False
            findScore = False
            curr_student = ""
            owner = ""

            for line in f:
                # for some reason, downloading files from Compass gives me 2 versions. only want peer evaluation
                if "Name:" not in line:
                    # must parse file
                    curr_line = line.strip().lower()

                    # if on prev iteration, have found a netid, now have to find associated score
                    if findScore and curr_student == owner:
                        students[curr_student].own = get_score(curr_line)
                        findScore = False
                    elif findScore and curr_student != owner:
                        students[curr_student].num_teammates += 1
                        students[curr_student].other += get_score(curr_line)
                        # to keep track of what other students gave each other
                        students[curr_student].teammates[owner] = get_score(curr_line)
                        findScore = False

                    # finding a netid
                    if foundOwner is False and curr_line in students:
                        foundOwner = True
                        owner = curr_line
                        curr_student = curr_line
                    elif foundOwner is True and curr_line in students:
                        # have found owner, on next iteration must get scores
                        curr_student = curr_line
                        findScore = True
                else:
                    # file isn't the wanted peer evaluation file
                    break
        continue
    else:
        # file isn't a txt file, whatever
        continue


def formattingForCompass(ownScore, teamAvg, teamnum):
    formattedStr = "Team members' perception of your contribution for Assignment 1: {:0.1f}% (averaged) \n".format(teamAvg) \
                   + "Your perception of your own contribution for Assignment 1: {}%".format(ownScore)

    if ownScore < teamAvg:
        formattedStr += "\nYou might be under-valuing the contribution that you are making to the team."
    elif teamAvg < ownScore:
        formattedStr += "\nYou might need to make additional contributions to the team in future assignments or " \
                        "you might need to better demonstrate or communicate the contributions that you are making " \
                        "to the assignments."

    if ownScore < (100 / int(teams[teamnum])) and teamAvg < (100 / int(teams[teamnum])):
        formattedStr += "\nYou probably need to make additional contributions to the team assignments in the future."

    return formattedStr


def main():
    students_w_no_submission = []
    no_teammates = []

    # sort students dictionary by netid
    sortedStudents = collections.OrderedDict(sorted(students.items()))

    for key in sortedStudents:
        curr_student = students[key]
        if curr_student.num_teammates != 0:
            if (curr_student.own == 0):
                students_w_no_submission.append(key)
            print("{} || Team #: {}, Number of teammates: {}".format(key.upper(), curr_student.team, curr_student.num_teammates))
            for member, grade in curr_student.teammates.items():
                print(member + ": " + str(grade) + " ", end=" ")
            print("\nOwn Score: {}, Team Avg: {}\n".format(curr_student.own, curr_student.other / curr_student.num_teammates))
        else:
            no_teammates.append(key)

    # print students w/ submission issues
    print("\nFollowing are the students who didn't give themselves a score or did not submit:")
    for student in students_w_no_submission:
        print(student)

    # no teammates / probably an error due to the parser
    print("\nFollowing students have no teammates:")
    for student in no_teammates:
        print(student)

    # write to a txt file w/ everything formatted and ready to copy and paste to compass
    f = open('cs498compassformat.txt', 'w')
    for key in sortedStudents:
        student = students[key]
        f.write(key + "\n")
        if student.num_teammates != 0:
            f.write(formattingForCompass(student.own, student.other / student.num_teammates, student.team) + "\n\n")
    f.close()


if __name__ == "__main__":
    main()
