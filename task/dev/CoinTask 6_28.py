from psychopy import visual, event, core
import numpy as np
import os, time, random

########
## Task Environment ##
########

#Get path 
path = os.getcwd()      # Get directory path

# Create task window
sx = 1000
sy = 800
win = visual.Window(size=(sx,sy),units="pix")

# Create Visual Stimuli
# fixation cross
cross = visual.TextStim(win,text = "+",height = 40)

#Coin Stimuli
#heads coins
leftPos = (-sx*.25,0)
heads = visual.Circle(win, radius = sy*.05, pos = leftPos,fillColor ="cyan",lineWidth = 5)
h = visual.TextStim(win,text='H',height = 40,pos = leftPos)

#tails coins
rightPos = (sx*.25,0)
tails = visual.Circle(win, radius = sy*.05, pos = rightPos,fillColor ="orange",lineWidth = 5)
t = visual.TextStim(win,text='T',height = 40,pos = rightPos)

#Text for COIN prediction phase
coinPredText = visual.TextStim(win, text="Which biased coin is being flipped?", height = 40, wrapWidth = sx*.8,pos = (0,sy*.25))

#Hazard Stimuli
# low hazard rate 
low = visual.ImageStim(win,path+'/Person.png', pos = leftPos, size = (sy*.1,sy*.1))
lo = visual.TextStim(win,text='low switch',pos = (-sx*.25,-sy*.09),height=30,color = 'white')

# high hazard rate
high = visual.ImageStim(win,path+'/Person.png', pos = rightPos, size = (sy*.1,sy*.1),color = 'black')
hi = visual.TextStim(win,text='high switch',pos = (sx*.25,-sy*.09),height=30,color = 'black')

#Text for SWITCH prediction phase
hazardPredText = visual.TextStim(win, text="Which person is choosing coins?", height = 40, wrapWidth = sx*.8,pos = (0,sy*.25))

##################
## SUBJECT INFO ##
##################

subID = 'TEST'
cond = 2
age = 'TEST'
sex = 'TEST'

#####################
## DATA COLLECTION ##
#####################

# Info to use for data file names
date_time=time.asctime()        #Date and Time
dt=date_time.replace('','_')    # Replace spaces with underscores where needed
dt=dt.replace('/','_')      #Replace slashes with underscores where needed

# Initialize data file
datafile = open(path+"//data//%s_CoinTask_%s.csv"%(subID,dt), 'w')

#  Data to be collected:
# SubjectID,Age,Sex: Subject information
# Condition: condition number (1 - coin trials first, 2 - hazard trials first)
# BlockType: which block is currently being observed (Coin or Hazard)
# TrialBlock: Which trial block is being seen (1 to however many trial blocks are observed)
# TrialNumber: Trial number within the current trial block (length 1-5)
# CurrGen: which coin or hazard rate is generating observations
# Prediction: Subject's prediction on that trial
# Confidence: confidence raiting
# Reward: if the subject got reward on that trial, how much did they get
# RT: response time
dataHeader = ["SubjectID","Age","Sex","Condition","BlockType","TrialBlock",
"TrialNumber","CurrGen","Prediction","Confidence","Reward","RT"]
datafile.write(",".join(dataHeader)+'\n')
datafile.flush()

#Function to record data
def recDat(dfile,dat_vec):
    dat = map(str,dat_vec)
    dfile.write(",".join(dat)+'\n')
    dfile.flush()

#####################
## GENERATE TRIALS ##
#####################

# Generate the trial blocks
niter = 2 #number of times each trial block length is repeated
trialBlocks = [1,2,3,4,5]*niter
random.shuffle(trialBlocks)

# Randomly generate the sequence of tails/heads and low/high hazard 
#0 = heads/low, 1 = tails/high
trialIDs = [0,1]*int(len(trialBlocks)/2)
random.shuffle(trialIDs)

print(trialBlocks)
print(trialIDs)


#####################
## TRIAL FUNCTIONS ##
#####################

#Function before Trial Block to indicate whether this is a Coin Bias or Switching Scenario
def trialBlockType(typeText,win):
    win.flip()
    core.wait(1)
    tbt_text = visual.TextStim(win,text=typeText,height=40,wrapWidth = sx*.8)
    tbt_text.draw()
    win.flip()
    keys = event.waitKeys(keyList = ['space','q','escape'])
    if keys[0] in ['q','escape']:
        core.quit()
        
# Feedback screen
def feedback(response,correct,left,right,lett_l,lett_r,win):
    #Display participant's response and adjust feedback position accordingly
    if response == 'left':
            resp = left
            lett = lett_l
            fbPos = (-sx*.25,0)
    else:
        resp = right
        lett = lett_r
        fbPos = (sx*.25,0)
    # Set feedback and display for 1.5 seconds
    if response == correct:
        fb = visual.Rect(win,height=sy*.12,width=sy*.12,fillColor=(0,1,0),lineWidth=0)
        fbText = visual.TextStim(win,text = 'Correct!',height = 40,pos=(0,sy*.25))
        fb.setPos(fbPos)
        fb.draw()
        fbText.draw()
        resp.draw()
        lett.draw()
    else:
        fb = visual.TextStim(win,text = 'X', height = 70,color = 'red')
        fbText = visual.TextStim(win,text = 'Incorrect',height = 40,pos=(0,sy*.25))
        fb.setPos(fbPos)
        resp.draw()
        fbText.draw()
        lett.draw()
        fb.draw()
    win.flip()
    core.wait(1.5)
    return(response == correct)
    
#Function to launch the prediction screen
def predict(win,predText,cross,left,right,lett_l,lett_r):
    
    #Half a seconf blank screen
    win.flip()
    core.wait(.5)
    
    #Draw stimuli
    predText.draw()
    cross.draw()
    left.draw()
    right.draw()
    lett_l.draw()
    lett_r.draw()
    win.flip()
    
    #Get and return prediction
    keys = event.waitKeys(keyList = ['left','right','q','escape'])
    if keys[0] in ['q','escape']:
        core.quit()
    else:
        if keys[0] == 'left':
            left.draw()
            lett_l.draw()
        elif keys[0] == 'right':
            right.draw()
            lett_r.draw()
        predText.draw()
        cross.draw()
        win.flip()
        core.wait(1)
    return(keys[0])


#Function to display coin
def coinFlip(coin,lett_coin,orgPos,cross,win,blkType):
    if blkType == 'coin':
        txt = 'Flipping coin...'
    else: 
        txt = 'Person choosing coin...'
    #Half a second blank screen
    win.flip()
    core.wait(.5)
    
    # Flipping coin test
    cFlipText = visual.TextStim(win,text = txt,height = 40)
    cFlipText.draw()
    win.flip()
    core.wait(.75)
    
    #Coin on for a second
    coin.setPos((0,0))
    coin.draw()
    lett_coin.setPos((0,0))
    lett_coin.draw()
    win.flip()
    core.wait(1.5)
    
    #Put coin back in original position
    coin.setPos(orgPos)
    lett_coin.setPos(orgPos)
    
def genTrials(blkType, ntrials,side):
    if blkType == 'coin':
        if side == 'left':
            trials = np.random.uniform(0,1,ntrials)>.8
        elif side == 'right':
            trials = np.random.uniform(0,1,ntrials)<.8
    elif blkType == 'hazard':
        if side == 'left':
            h = .2
        elif side == 'right':
            h = .8
        currCoin = random.choice([0,1])
        trials = np.empty(ntrials)
        for i in np.arange(ntrials):
            trials[i] = currCoin
            if np.random.uniform(0,1,1) < h:
                if currCoin == 0:
                    currCoin = 1
                elif currCoin == 1:
                    currcoin = 0
        trials = trials.astype(bool)
    return(trials)
        

#Function to run blocks of trials
def trialBlockRun(ntrials,subInfo,blkType,tblock,items,itemNames,letters,positions,
predText,coins,coinLett,trialID,dfile=datafile):
    side = ['left','right']
    #Show person that new trial block is starting
    if blkType == 'coin':
        trialBlockType('New coin being selected...\n\nPress space to start trials',win)
    else:
        trialBlockType('New person being selected...\n\nPress space to start trials',win)
        
    trials = genTrials(blkType,ntrials,side[trialID])
    print(trials)
        
    for i in np.arange(len(trials)):
        coinFlip(coins[trials[i]],coinLett[trials[i]],positions[trials[i]],cross,win,blkType)
        start = time.time()
        keypress = predict(win,predText,cross,items[0],items[1],letters[0],letters[1])
        recDat(dfile,[subInfo[0],subInfo[1],subInfo[2],subInfo[3],blkType,tblock,i+1,itemNames[trialID],keypress,'NA','NA',str(time.time()-start)])
    correct = feedback(keypress,side[trialID],items[0],items[1],letters[0],letters[1],win)
    recDat(dfile,[subInfo[0],subInfo[1],subInfo[2],subInfo[3],blkType,tblock,'NA','NA',int(correct),'NA'])

##################
## TRIAL HANDLER ##
##################
subInfo = [subID,age,sex,cond]
# Based on the conditon set which type of trils goes first
if cond == 1:
    blkTypes = ['coin','hazard']
else:
    blkTypes = ['hazard','coin']

#Iterate through different block tyoes
for blkType in blkTypes:
    if blkType == 'coin':
        gen = ['heads','tails']
        items = [heads,tails]
        letters = [h,t]
        predText = coinPredText
    elif blkType == 'hazard':
        gen = ['low','high']
        items = [low,high]
        letters = [lo,hi]
        predText = hazardPredText
    positions = [leftPos,rightPos]
    
    #Run through Trials
    for i in np.arange(len(trialBlocks)):
        print(trialIDs[i])
        trialBlockRun(trialBlocks[i],subInfo,blkType,i+1,items,gen,letters,
        positions,predText,[heads,tails],[h,t],trialIDs[i])


win.flip()
core.wait(.5)
core.quit()

