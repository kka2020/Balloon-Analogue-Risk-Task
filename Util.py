import pygame
import csv
import socket
import random

def displayText(screen, text, size, x, y, color):
    '''
    Draws text to screen
    Arguments: screen (window surface object to draw text on),
               text (text to be displayed),
               size (font size),
               x, y (coordinates of center)
               color (font color)
    Returns: None
    '''
    font = pygame.font.Font("freesansbold.ttf", size) # Creates font object to be rendered
    text = font.render(text, True, color) # Renders text
    text_rect = text.get_rect() # Creates rect object (easy to centre)
    text_rect.center = (x, y) # Sets rect centre
    screen.blit(text, text_rect) # Draws to screen

def drawImage(screen, source, x, y, size):
    '''
    Draws image to screen
    Arguments: screen (window surface object)
               source (file name)
               x, y (coordinates of centre)
               size (scale factor 2D vector)
    Returns: None
    '''
    image = pygame.image.load(source) # Creates image surace
    image = pygame.transform.scale(image, size) # Scales to desired size
    rect = image.get_rect()
    rect.center = (x, y) # Centres rect to desired location
    screen.blit(image, rect) # Draws to screen


def getUserID():
    '''
    Gets validated user input for user ID
    Arguments: None
    Returns: user_ID
    '''
    
    user_ID = ""
    valid = False
    while not valid:
        user_ID = str(input("Please enter the user ID (4 digits):> "))
        if user_ID.isdigit() and len(user_ID) == 4:
            valid = True
        else:
            print("Inputted user ID is invalid. Please try again.")
    
    return user_ID

def setupSocket():
    '''
    Initialises network socket
    Arguments: None
    Returns: s (socket object)
    '''
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Initialises client socket
    s.connect(("127.0.0.1", 1234)) #Connects to port 1234 on localhost (sends TCP packets to NIC)

    return s

def setupCSV(user_ID, multi = False):
    '''
    Initialises CSV file and CSV writer objects
    Arguments: user_ID
    Returns: csv_file (CSV file object which needs to be closed)
             writer (CSV writer object that writes data to file)
    '''
    # Opens different files depending on the script type
    if multi:
        csv_file = open(f"BART_multirisk_data_{user_ID}.csv", "w")
        writer = csv.DictWriter(csv_file, fieldnames=["num_keypresses", "round_money_won", "total_money_won", "popped", "risk"])
    else:
        csv_file = open(f"BART_basic_data_{user_ID}.csv", "w")
        writer = csv.DictWriter(csv_file, fieldnames=["num_keypresses", "round_money_won", "total_money_won", "popped"])

    writer.writeheader()

    return csv_file, writer

def extractProb(multi = False):
    '''
    Converts probabilities.txt into array of probabilities
    Probability = 1 in X where X = current entry
    Arguments: multi (bool indicating which file to extract from)
    Returns: array of probabilities
    '''
    # Reads from different files depending on script type
    if multi:
        with open("probabilities_risk.txt", "r") as file:
            risks = ["high", "medium", "low"]
            probs = {"high" : [], "medium" : [], "low" : []}

            for risk in risks:
                probs[risk] = file.readline() #Reads first line from file
                probs[risk] = probs[risk].split(",") #Splits string into array (separating by comma)
                probs[risk] = list(map(int, probs[risk])) #Converts each entry in array to integer
                probs[risk].append(1) #Ensures balloon will pop at the end
    else:
        with open(f"probabilities_basic.txt", "r") as file:
            probs = file.readline() #Reads first line from file
            probs = probs.split(",") #Splits string into array (separating by comma)
            probs = list(map(int, probs)) #Converts each entry in array to integer
            probs.append(1) #Ensures 10th pump results in popping

    return probs

def getNumRounds():
    '''
    Gets validated user input for the number of rounds to be played
    Arguments: None
    Returns: num_rounds (no. rounds)
    '''
    num_rounds = 0 #Declares variable num_rounds (stores number of rounds)

    # Keeps asking for number of rounds until valid number entered
    valid = False
    while not valid:
        num_rounds = int(input("Please enter the number of rounds (1 to 240):> "))
        if 1 <= num_rounds <= 240:
            valid = True
    
    return num_rounds

def populateRisks(num_rounds):
    '''
    Equally distributes risk levels across the rounds
    Arguments: num_rounds (number of rounds to be played)
    Returns: round_risk (array holding risk level associated with each round)
    '''
    risks = ["high", "medium", "low"] #Allows enumeration through risk levels
    output = [None] * num_rounds #Initialises empty array of length = num_rounds

    # Repeats process for each risk level
    for i in range(0, 3):
        # Determines number of the current risk level to seed
        # If num_rounds / 3 isn't whole, then ensure medium have more occurences than high or low
        upper_bound = i == 1 and num_rounds // 3 + num_rounds % 3 or num_rounds // 3

        for j in range(0, upper_bound):
            # Ensures empty slot has been found
            valid = False
            index = None

            while not valid:
                index = random.randint(0, num_rounds - 1)
                valid = output[index] == None
            
            output[index] = risks[i] #Assigns risk level to empty slot

    return output

def getBgImage():
    '''
    Gets validated user input choosing which background image to use
    Arguments: None
    Returns: image (string of image name) or None
    '''
    
    # Set to false initially to start loop
    valid = False

    while not valid:
        image = str(input("Please choose which background image to use: police, trees, gambling, or none (type which option):> "))

        valid = image in ["police", "trees", "gambling", "none"]

        if not valid:
            input("Invalid string entered. Press enter to try again.")
        else:
            if image == "none":
                return None
            else:
                return image

def getActiveResponses():
    '''
    Gets validated user input choosing whether to include active responses or not
    '''
    # Set to false initially to start loop
    valid = False

    while not valid:
        response = str(input("Turn on active responses? (y/n):> "))

        valid = response in ["y", "n"]

        if not valid:
            input("Invalid string entered. Press enter to try again.")
        else:
            return response == "y"