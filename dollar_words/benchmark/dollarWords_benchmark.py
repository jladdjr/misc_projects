#!/usr/bin/python

import time

startTime = int(round(time.time() * 1000))

#Create dictionary with letter values
letterValue = \
        {'a':1,
         'b':2,
         'c':3,
         'd':4,
         'e':5,
         'f':6,
         'g':7,
         'h':8,
         'i':9,
         'j':10,
         'k':11,
         'l':12,
         'm':13,
         'n':14,
         'o':15,
         'p':16,
         'q':17,
         'r':18,
         's':19,
         't':20,
         'u':21,
         'v':22,
         'w':23,
         'x':24,
         'y':25,
         'z':26}

#Open file
#f = open("words.txt")
f = open("words-200k.txt")

#While next word exists
for line in f:
    word = line.strip().rstrip()
    wordValue = 0

    #Skip word if fewer than four characters
    if len(word) < 4:
        continue

    #For each letter in word
    for char in word:
        #Prep character
        char = char.lower()
        if char not in letterValue.keys():
            continue

        wordValue += letterValue[char]

        #Stop if sum greater than 100
        if wordValue > 100:
            break

    #Print if value is 100
    #if wordValue == 100:
    #    print word

#Close text file
f.close()

stopTime = int(round(time.time() * 1000))

benchmark = stopTime - startTime

print "Time Elapsed (milliseconds): %s" % benchmark
