import os
import math
import csv

def load_files(directory):
    files = os.listdir(directory)
    file_list = []
    for f in files:
        file_list.append(directory+f)
    return file_list

def prior(dataset, label_list, num_games):
    smooth = 1 # smoothing factor
    logprob = {}
    for label in label_list:
        # Calculate prior probabilities
        p_label = (len(dataset[label])+smooth)/(num_games[label]+(smooth*len(label_list)))
        log_p_label = math.log(p_label)
        logprob[label] = log_p_label
    return logprob

def p_win_given_opponent(dataset, label_list, num_games, opponent, priors):
    smooth = 1 # smoothing factor
    win_count = 0
    p_win = {}

    for l in label_list:
        win_count = 0
        won_games = dataset[l]
        for g in won_games:
            g_label = get_range_label(g)
            if(g_label == opponent):
                win_count += 1
        log_win = math.log((win_count+smooth)/(num_games[opponent]+smooth))
        p_win[l] = log_win
    return p_win

def find_num_games_played(dataset, label):
    num_games = 0
    for d in dataset:
        for g in dataset[d]:
            if d == label:
                num_games += 1
            else:
                g_label = get_range_label(g)
                if g_label == label:
                    num_games += 1
    return num_games

def get_data(dataset, file_list):
    for f in file_list:
        with open(f, mode='r',encoding='utf-8-sig') as win_data:
            reader = csv.reader(win_data, delimiter=',')
            row_count = 0
            label_list = {}
            for row in reader:
                for i in range(len(row)):
                    if row_count == 0:
                        if (row[i] != ''):
                            percentage = calc_percentage(row[i])
                            label = get_range_label(percentage)
                            label_list[i] = label
                    else:
                        if(row[i] != ''):
                            percentage = calc_percentage(row[i])
                            add_to_dataset(dataset, label_list[i], percentage)
                row_count += 1
    return dataset

def add_to_dataset(dataset, label, data):
    if label in dataset:
        dataset[label].append(data)
    else:
        dataset[label] = [data]

def get_range_label(percentage):
    if(percentage >= .95):
        return '100-95'
    elif(percentage >= .90):
        return '95-90'
    elif(percentage >= .85):
        return '90-85'
    elif(percentage >= .80):
        return '85-80'
    elif(percentage >= .75):
        return '80-75'
    elif(percentage >= .70):
        return '75-70'
    elif(percentage >= .65):
        return '70-65'
    elif(percentage >= .60):
        return '65-60'
    elif(percentage >= .55):
        return '60-55'
    elif(percentage >= .50):
        return '55-50'
    elif(percentage >= .45):
        return '50-45'
    elif(percentage >= .40):
        return '45-40'
    elif(percentage >= .35):
        return '40-35'
    elif(percentage >= .30):
        return '35-30'
    else:
        return '25-0'

def calc_percentage(win_str):
    w, l = map(int,win_str.split('/'))
    percentage = w/(w+l)
    return percentage

def classify_win(training_probs, team1_record, team2_record):
    p1 = calc_percentage(team1_record)
    p2 = calc_percentage(team2_record)
    p1_label = get_range_label(p1)
    p2_label = get_range_label(p2)
    print("Team 1 prob: ", math.exp(training_probs[p1_label]))
    print("Team 2 prob: ", math.exp(training_probs[p2_label]))
    if(training_probs[p1_label] > training_probs[p2_label]):
        return "Team 1"
    elif(training_probs[p1_label] < training_probs[p2_label]):
        return "Team 2"
    else:
        return "Equally likely"

def print_training_loss(file, training_probs):
    with open(file, mode='r',encoding='utf-8-sig') as test_data:
        reader = csv.reader(test_data, delimiter=',')
        row_count = 0
        label_list = {}
        loss = 0
        games = 0
        for row in reader:
            for i in range(len(row)):
                games += 1
                if row_count == 0:
                    if (row[i] != ''):
                        percentage = calc_percentage(row[i])
                        label = get_range_label(percentage)
                        label_list[i] = label
                else:
                    if(row[i] != ''):
                        percentage = calc_percentage(row[i])
                        team2 = get_range_label(percentage)
                        if(training_probs[label_list[i]] < training_probs[team2]):
                            loss += 1
            row_count += 1
    print("TOTAL LOSS: {}".format((loss/games)*100))


def test_matchup(training_probs):
    # Get input
    done = False
    while not done:
        print("Type 'n' for next matchup, or type 'q' to quit")
        input_str = input()
        if input_str == 'q':
            done = True
        elif input_str == 'n':
            # Get num wins and losses
            team1_wins = input("Enter team 1's win record: ")
            team1_losses = input("Enter team 1's loss record: ")
            team2_wins = input("Enter team 2's win record: ")
            team2_losses = input("Enter team 2's loss record: ")
            # Format as record
            team1_record = "{}/{}".format(team1_wins, team1_losses)
            team2_record = "{}/{}".format(team2_wins, team2_losses)
            # Calculate probability
            print(classify_win(training_probs, team1_record, team2_record))
        else:
            print("That was not an option, try again.")

def test_file(training_probs):
    input_str = input("Enter file name:")
    print_training_loss(input_str, training_probs)

if __name__ == '__main__':
    # Get data
    file_list = load_files("./training/")
    if './training/.DS_Store' in file_list: file_list.remove('./training/.DS_Store')
    labels = ['100-95', '95-90', '90-85', '85-80', '80-75', '75-70', '70-65', '65-60', '60-55', '55-50', '50-45', '45-40', '40-35', '35-30', '30-25', '25-0']
    dataset = {k:[] for k in labels}
    dataset = get_data(dataset, file_list)
    total_num_games = {k:[] for k in labels}
    for d in dataset:
        total_num_games[d] = find_num_games_played(dataset, d)
    log_priors = prior(dataset, labels, total_num_games)
    training_probs = p_win_given_opponent(dataset, labels, total_num_games, '85-80', log_priors)

    # Get input
    os.system('clear')
    input_str = input("Type 'm' to test a matchup, or 'f' to test a file: ")
    if(input_str == 'm'):
        test_matchup(training_probs)
    if(input_str == 'f'):
        test_file(training_probs)
    