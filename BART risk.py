import random
import csv
import socket
import pygame
import math

import Util

WIDTH = 1280
HEIGHT = 720


class States():
    '''
    Abstract class that all state classes inherit from
    '''

    def __init__(self):
        # All state objects must have these attributes
        self.quit = False
        self.done = False
        self.next = None
        self.previous = None
    
    # Every state class must have these methods (prevents errors)
    def enter(self, args):
        '''
        Method called upon entering a new state
        Arguments: args (list containing any values that need to be passed into the new state)
        Returns: None
        '''
        pass

    def exit(self):
        '''
        Method called upon exiting the current state
        Arguments: None
        Returns: args (list containing any values that need to be passed into the next state)
        '''
        return None

    def getEvent(self, event):
        '''
        Handles user input events for current state
        Arguments: event (pygame event object)
        Returns: None
        '''
        pass

    def update(self, screen):
        '''
        Any functionality that needs to be executed every frame
        Arguments: screen (pygame surface object for the screen)
        Returns: None
        '''
        pass

    def draw(self, screen):
        '''
        Handles graphics (called in update method)
        Arguments: screen (pygame surface object for the screen)
        Returns: None
        '''
        pass
    
    def cleanup(self):
        '''
        Resets attributes ready for next iteration of current state
        Arguments: None
        Returns: None
        '''
        pass

class Start(States):
    '''
    Initial state entered upon starting the game
    '''

    def __init__(self):
        super().__init__()
        self.next = "setup"
    
    def enter(self, args):
        #These values must pass through every state
        self.user_ID, self.num_rounds, self.active_response = args
    
    def exit(self):
        #Passes these values into next state
        return [self.user_ID, self.num_rounds, self.active_response]

    def cleanup(self):
        #Deletes these variables (saves memory)
        del self.user_ID
        del self.num_rounds
        del self.active_response
    
    def getEvent(self, event):
        if event.type == pygame.KEYDOWN:
            # Quits game if <q> pressed
            if event.key == pygame.K_q:
                self.quit = True
            #Enters game if <enter> pressed
            elif event.key == pygame.K_RETURN:
                self.done = True
    
    def update(self, screen):
        self.draw(screen)
    
    def draw(self, screen):
        #Displays welcome messages
        Util.displayText(screen, "Welcome to the Balloon Analogue Risk Task (BART)!", 32, screen.get_width() // 2, screen.get_height()  // 2 - 50, "black")
        Util.displayText(screen, "Press enter to start or <q> to quit", 32, screen.get_width() // 2, screen.get_height()  // 2, "black")

class Setup(States):
    '''
    State before starting game
    Sets up csv, socket and initialises other values that persist between rounds
    '''

    def __init__(self):
        super().__init__()
        self.next = "play"
    
    def enter(self, args):
        self.user_ID, self.num_rounds, self.active_response = args

        # Initialises network socket
        # Used to send triggers to EEG-Enobio
        self.socket = Util.setupSocket()

        # Sets up CSV objects
        # Allows program to write data to CSV file
        self.csv_file, self.csv_writer = Util.setupCSV(self.user_ID, True)

        # Gets probability distribution from multi-risk file
        self.probs = Util.extractProb(True)

        self.overall_total = 0
        self.round_risks = Util.populateRisks(self.num_rounds)
    
    def exit(self):
        # Passes all values into play state
        return [self.user_ID, self.socket, self.csv_file, self.csv_writer, self.probs, self.num_rounds, self.overall_total, self.round_risks, self.active_response]
    
    def update(self, screen):
        # Once all variables have been set-up, nothing else needs to be done in this state
        self.done = True

    def cleanup(self):
        # Deletes attributes to save space
        del self.user_ID
        del self.socket
        del self.csv_file
        del self.csv_writer
        del self.probs
        del self.num_rounds
        del self.overall_total
        del self.round_risks
        del self.active_response

class Play(States):
    '''
    State where each round is run
    '''

    def __init__(self):
        super().__init__()
        self.next = None # Determined during round
        
        # Initialises state-local attributes
        self.round_total = 0
        self.popped = False
        self.cashed = False
        self.balloon_size = 0
    
    def enter(self, args):
        # Passes in 'global' attributes
        self.user_ID, self.socket, self.csv_file, self.csv_writer, self.probs, self.num_rounds_left, self.overall_total, self.round_risks, self.active_response = args
        # Resets round-only attributes
        self.round_total = 0
        self.popped = False
        self.cashed = False
        self.balloon_size = 0
        self.risk = self.round_risks[len(self.round_risks) - self.num_rounds_left]
        self.next = "popped"
    
    def exit(self):
        # Once the round is over, writes relevant data to CSV file
        self.csv_writer.writerow({'num_keypresses' : self.balloon_size, 'round_money_won' : self.round_total * (not self.popped), 'total_money_won' : self.overall_total, 'popped' : self.popped, 'risk' : self.risk})
        # Passes global values into next state (whilst decreasing number of rounds remaining)
        return [self.user_ID, self.socket, self.csv_file, self.csv_writer, self.probs, self.num_rounds_left - 1, self.overall_total, self.round_total, self.balloon_size, self.round_risks, self.risk, self.active_response]

    def getEvent(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                # Variable <popped> acts as a random variable with an experimenter-decided probability distribution
                
                self.popped = random.randint(10 - self.probs[self.risk][self.balloon_size] + 1, 10) == 10
                
                if not self.popped:
                    #If not popped, increases size of balloon and money to win this round
                    self.round_total += 1
                    self.balloon_size += 1
                else:
                    self.next = "popped" # Sets next state
                    self.done = True #Ends round
                
            elif event.key == pygame.K_LEFT:
                self.overall_total += self.round_total #Adds total won this round to the overall total
                self.cashed = True #Sets cashed to true
                self.next = "cashed" #Sets next state
                self.done = True #Ends round
    
    def update(self, screen):
        self.draw(screen)
    
    def draw(self, screen):
        # Different balloon image drawn depending on the size of the balloon
        # Allows for more realistic inflating compared to just scaling one image
        Util.drawImage(screen, f"images/balloon{self.balloon_size + 1}{self.risk}.png", screen.get_width() // 2, screen.get_height()  // 2, (400, 540))

        # Displays total money won across the test so far and how would be won in this round (if the user cashed now)
        Util.displayText(screen, f"Money won this round: £{self.round_total}", 24, screen.get_width() // 4, 30, "black")
        Util.displayText(screen, f"Total money won: £{self.overall_total}", 24, screen.get_width() // 4 * 3, 30, "black")
    
    def cleanup(self):
        # Deletes all attributes to reset them for next iteration
        # Also to save memory
        del self.user_ID
        del self.socket
        del self.csv_file
        del self.csv_writer
        del self.probs
        del self.num_rounds_left
        del self.overall_total
        del self.round_risks
        del self.active_response

        del self.round_total
        del self.popped
        del self.cashed
        del self.balloon_size
        del self.risk

class EndRound(States):
    '''
    Class that Popped and Cashed classes inherit from.
    Handles common features that happen both when the balloon pops and the player cashes in.
    '''
    def __init__(self):
        super().__init__()
        self.next = "play"
    
    def enter(self, args):
        # Both states receive passed data
        self.user_ID, self.socket, self.csv_file, self.csv_writer, self.probs, self.num_rounds_left, self.overall_total, self.round_total, self.balloon_size, self.round_risks, self.risk, self.active_response = args

        # In both cases, if there aren't any rounds left,
        # should transition to exit state once current processes are complete
        if self.num_rounds_left == 0:
            self.next = "exit"

    def exit(self):
        # Both states passs same data onwards
        return [self.user_ID, self.socket, self.csv_file, self.csv_writer, self.probs, self.num_rounds_left, self.overall_total, self.round_risks, self.active_response]
    
    def getEvent(self, event):
        if event.type == pygame.KEYDOWN:
            # In both cases, pressing <enter> transitions to next state
            if event.key == pygame.K_RETURN:
                self.done = True
    
    def update(self, screen):
        self.draw(screen)
    
    def draw(self, screen):
        # Both states display the info on money won in total and this round
        Util.displayText(screen, f"Money won this round: £{self.round_total}", 24, screen.get_width() // 4, 30, "black")
        Util.displayText(screen, f"Total money won: £{self.overall_total}", 24, screen.get_width() // 4 * 3, 30, "black")
        # Both display same prompt to continue
        Util.displayText(screen, "Press enter to continue", 32, screen.get_width() // 2, screen.get_height() - 40, "black")
        # Both draw the balloon at final size
        Util.drawImage(screen, f"images/balloon{self.balloon_size + 1}{self.risk}.png", screen.get_width() // 2, screen.get_height() // 2, (400, 540))

    def cleanup(self):
        # Both must delete all these attributes in order to reset them for next iteration
        del self.user_ID, self.socket, self.csv_file, self.csv_writer, self.probs, self.num_rounds_left, self.overall_total, self.round_total, self.balloon_size, self.round_risks, self.risk, self.active_response

class Popped(EndRound):
    '''
    State entered when the balloon pops
    '''

    def enter(self, args):
        super().enter(args)
        # Sends trigger to EEG-Enobio
        # Sends value 9 to indicate that the balloon was popped
        self.socket.sendall(b"<TRIGGER>9</TRIGGER>")
    
    def draw(self, screen):
        super().draw(screen) # Draws common text and images
        # Draws a 'bang' of size proportional to size of balloon
        Util.drawImage(screen, "images/bang.png", screen.get_width() // 2, screen.get_height() // 2 - self.balloon_size * 10, pygame.Vector2(112, 105) * math.sqrt(self.balloon_size + 1))
        
        if self.active_response:
            # Displays loss message
            Util.displayText(screen, "Boom!! You lost this round!", 32, screen.get_width() // 2, screen.get_height() - 80, "red")

class Cashed(EndRound):
    '''
    State entered when the player cashes in
    '''

    def enter(self, args):
        super().enter(args)
        # Sends trigger to EEG-Enobio
        # Sends value 7 to indicate that the player cashed in
        self.socket.sendall(b"<TRIGGER>7</TRIGGER>")
    
    def draw(self, screen):
        super().draw(screen) #Draws common text and images

        if self.active_response:
            #Displays how much money has been gained next to overall total
            Util.displayText(screen, f"+£{self.round_total}", 24, screen.get_width() // 4 * 3 + 145 + 15 * (len(str(self.overall_total)) - 1), 30, "green")
            #Displays win message
            Util.displayText(screen, f"You won £{self.round_total} this round!", 32, screen.get_width() // 2, screen.get_height() - 80, "green")

class Exit(States):
    '''
    State entered when the test is complete
    '''

    def enter(self, args):
        # Since end round passes same variables into both play and exit,
        # only some values are required
        self.socket, self.csv_file, self.csv_writer = args[1:4] 
        # Closes socket and file instances
        self.socket.close()
        self.csv_file.close()
    
    def getEvent(self, event):
        if event.type == pygame.KEYDOWN:
            # When <enter> pressed, game program quits
            if event.key == pygame.K_RETURN:
                self.quit = True
    
    def update(self, screen):
        self.draw(screen)
    
    def draw(self, screen):
        # Displays end game messages and input prompt
        Util.displayText(screen, "The test is now complete", 32, screen.get_width() // 2, screen.get_height() // 2, "black")
        Util.displayText(screen, "Press <enter> to exit the app", 32, screen.get_width() // 2, screen.get_height() // 2 + 40, "black")
    

class Control():
    '''
    Acts as statemachine; controls the flow of control between states.
    '''

    def __init__(self, **settings):
        # Adds attributes relating to fps and screen size
        self.__dict__.update(settings)
        self.done = False
        pygame.init() # Initialises pygame
        # Initialises window
        # Allows for window to be resized
        self.screen = pygame.display.set_mode(self.size, pygame.RESIZABLE)

        if self.bg_image_name:
            # Sets background image
            self.bg_image = pygame.image.load(f"images/{self.bg_image_name}.jpg").convert()

        # Sets icon in top-right corner to a balloon
        pygame.display.set_icon(pygame.image.load("images/balloon-icon.png"))
        # Sets window caption
        pygame.display.set_caption("Balloon Analogue Risk Task (multi-risk)")
        # Intialises clock object
        self.clock = pygame.time.Clock()

    def setupStates(self, state_dict, start_state, args = []):
        '''
        Sets up state dictionary and enters the intial state
        Arguments: state_dict (dictionary storing state objects)
                   start_state (initial state)
                   args (any arguments that need to be passed into the initial state)
        Returns: None
        '''
        # Sets up state dictionary
        self.state_dict = state_dict
        # Sets up initial state
        self.state_name = start_state
        self.state = self.state_dict[self.state_name]
        # Enters initial state, passing in any args
        self.state.enter(args)
    
    def changeState(self):
        # Resets state.done to prevent immediate transition
        self.state.done = False
        # Assigns current_state's name to previous temp variable
        # Sets the current_state's name to the next state's name
        previous, self.state_name = self.state_name, self.state.next
        # Exits current state, storing any return values in args
        args = self.state.exit()
        # Cleans up current state
        self.state.cleanup()
        # Transition to next state
        self.state = self.state_dict[self.state_name]
        # Enters next state, passing in args
        self.state.enter(args)
        # Keeps reference to previous state
        self.state.previous = previous
    
    def update(self):
        if self.state.quit:
            # Ends game loop
            self.done = True
        elif self.state.done:
            self.changeState()
        
        self.screen.fill("white") # Prevents images bleeding between frames

        # Scales and draws background image if it exists
        if self.bg_image_name:
            bg = pygame.transform.scale(self.bg_image, (self.screen.get_width(), self.screen.get_height()))
            self.screen.blit(bg, (0,0))

        self.state.update(self.screen) # Draws next frame
    
    def eventLoop(self):
        for event in pygame.event.get():
            # In all states, if X buttion clicked, then program should quit
            if event.type == pygame.QUIT:
                self.done = True
            # Redraws screen to new size
            elif event.type == pygame.VIDEORESIZE:
                old_screen = self.screen
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self.screen.blit(old_screen, (0, 0))
                del old_screen
            # Handles state-specific events
            self.state.getEvent(event)
    
    def mainGameLoop(self):
        while not self.done:
            self.clock.tick(self.fps) #Increments clock
            self.eventLoop() # Handles user input
            self.update() # Draws frame
            pygame.display.update() # Updates display

def main():
    '''
    Executes program
    '''

    # Experimenter can input user ID, the number of rounds, the background image and whether to turn on active responses before the test begins
    user_ID = Util.getUserID()
    num_rounds = Util.getNumRounds()
    bg_image_name = Util.getBgImage()
    active_response = Util.getActiveResponses()

    settings = {'size' : (1280, 720), 'fps' : 60, 'bg_image_name' : bg_image_name} # Sets fps and window size
    app = Control(**settings) # Creates Control object
    # Sets up state dictionary
    state_dict = {
        'start' : Start(),
        'setup' : Setup(),
        'play' : Play(),
        'popped' : Popped(),
        'cashed' : Cashed(),
        'exit' : Exit()
    }
    # Sets up states and enters initial state
    app.setupStates(state_dict, 'start', [user_ID, num_rounds, active_response])
    # Starts game loop
    app.mainGameLoop()
    # Once game loop has been exited, the game has been quit
    pygame.quit()

# When the python file is run as a program (instead of imported), runs main()
if __name__ == "__main__":
    main()