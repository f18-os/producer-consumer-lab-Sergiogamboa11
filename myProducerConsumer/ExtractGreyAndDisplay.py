#!/usr/bin/env python3

from threading import Thread
import sys
import cv2
import numpy as np
import base64
import queue
import time
import os
import threading

outputDir = 'frames'
if not os.path.exists(outputDir):
    print("Output directory {} didn't exist, creating".format(outputDir))
    os.makedirs(outputDir)
outputDir = 'greyFrames'
if not os.path.exists(outputDir):
    print("Output directory {} didn't exist, creating".format(outputDir))
    os.makedirs(outputDir)

def extract():
    sem.acquire()
    print("Extracting:")
    # globals
    outputDir = 'frames'
    clipFileName = 'clip.mp4'
    # initialize frame count
    count = 0
    # open the video clip
    vidcap = cv2.VideoCapture(clipFileName)
    # read one frame
    success, image = vidcap.read()
    sem.release()

    print("Reading frame {} {} ".format(count, success))
    while success:
        # write the current frame out as a jpeg image
        sem.acquire()
        cv2.imwrite("{}/frame_{:04d}.jpg".format(outputDir, count), image)
        sem.release()
        success, image = vidcap.read()
        print('Reading frame {}'.format(count))
        count += 1
    sem.release()


def convert():
    # await semaphore.acquire()
    print("Converting:")
    # globals
    outputDir = 'frames'
    outputDir2 = 'greyFrames'

    # initialize frame count
    count = 0

    # get the next frame file name
    inFileName = "{}/frame_{:04d}.jpg".format(outputDir, count)

    # load the next file
    sem.acquire()
    inputFrame = cv2.imread(inFileName, cv2.IMREAD_COLOR)
    sem.release()

    while True:

        if inputFrame is not None:
            print("Converting frame {}".format(count))

            # convert the image to grayscale
            grayscaleFrame = cv2.cvtColor(inputFrame, cv2.COLOR_BGR2GRAY)

            # generate output file name
            outFileName = "{}/grayscale_{:04d}.jpg".format(outputDir2, count)

            # write output file
            semOut.acquire()
            cv2.imwrite(outFileName, grayscaleFrame)
            semOut.release()

            count += 1

            # generate input file name for the next frame
            inFileName = "{}/frame_{:04d}.jpg".format(outputDir, count)

            # load the next frame
            sem.acquire()
            inputFrame = cv2.imread(inFileName, cv2.IMREAD_COLOR)
            sem.release()
        sem.release()
        semOut.release()



def display():
    print("Displaying:")
    # globals
    outputDir    = 'greyFrames'
    frameDelay   = 42       # the answer to everything

    # initialize frame count
    count = 0

    startTime = time.time()

    # Generate the filename for the first frame
    frameFileName = "{}/grayscale_{:04d}.jpg".format(outputDir, count)

    # load the frame
    semOut.acquire()
    frame = cv2.imread(frameFileName)
    semOut.release()

    while True:
        if frame is not None:

            print("Displaying frame {}".format(count))
            # Display the frame in a window called "Video"
            cv2.imshow("Video", frame)

            # compute the amount of time that has elapsed
            # while the frame was processed
            elapsedTime = int((time.time() - startTime) * 1000)
            print("Time to process frame {} ms".format(elapsedTime))

            # determine the amount of time to wait, also
            # make sure we don't go into negative time
            timeToWait = max(1, frameDelay - elapsedTime)

            # Wait for 42 ms and check if the user wants to quit
            if cv2.waitKey(timeToWait) and 0xFF == ord("q"):
                break

            # get the start time for processing the next frame
            startTime = time.time()

            # get the next frame filename
            count += 1
            frameFileName = "{}/grayscale_{:04d}.jpg".format(outputDir, count)

            # Read the next frame file
            semOut.acquire()
            frame = cv2.imread(frameFileName)
            semOut.release()
    cv2.destroyAllWindows()

class ExtractThread(Thread):
    def __init__(self):
        Thread.__init__(self, daemon=False)
        self.start()

    def run(self):
        extract()

class PlayThread(Thread):
    def __init__(self):
        Thread.__init__(self, daemon=False)
        self.start()

    def run(self):
        display()

class ConvertThread(Thread):
    def __init__(self):
        Thread.__init__(self, daemon=False)
        self.start()

    def run(self):
        convert()

# filename of clip to load
filename = 'clip.mp4'

#Semaphore for Extraction and input to Conversion
sem = threading.Semaphore()

#Semaphore for conversion output and Playback
semOut = threading.Semaphore()

ExtractThread()
time.sleep(0.1)
ConvertThread()
time.sleep(0.1)
PlayThread()
