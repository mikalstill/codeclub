import random
import sys

# Pick a random number
number = random.randint(0, 10)

# Now ask for guesses until the correct guess is made
done = False
attempts = 0

while not done:
    guess = int(raw_input('What is your guess? '))
    print 'You guessed: %d' % guess
    
    attempts += 1
    if guess < number:
        print 'Higher!'
    elif guess > number:
        print 'Lower!'
    else:
        print 'Right!'
        done = True

    if attempts > 5:
        print 'Too many attempts!'
        sys.exit(1)
