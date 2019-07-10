from psychopy import visual, event, core
import numpy as np
import os, time, random
import pylink as pl

##################
## SUBJECT INFO ##
##################


subID = 'TEST'
cond = 1
age = 'TEST'
sex = 'TEST'

########
## Task Environment ##
########

#Get path 
path = os.getcwd()      # Get directory path

# Create task window
sx = 1000
sy = 800
win = visual.Window(size=(sx,sy),units="pix",fullscr=False)

#Get mouse
mouse = event.Mouse()
mouse.setVisible(False)

# Create Visual Stimuli
# fixation cross
cross = visual.TextStim(win,text = "+",height = 40)

#Coin Stimuli
mult = .05  #multiplier to set coin/person size according to the screen
posMult = .3 #multiplier to set position of left/right stimuli
#heads coins
leftPos = (-sx*posMult,0)
blueBeads = visual.Circle(win, radius = sy*mult, pos = leftPos,fillColor ="cyan",lineWidth = 5)

#tails coins
rightPos = (sx*posMult,0)
orangeBeads = visual.Circle(win, radius = sy*mult, pos = rightPos,fillColor ="orange",lineWidth = 5)

#Text for COIN prediction phase
beadPredText = visual.TextStim(win, text="Which container are these beads being selected from?", height = 40, wrapWidth = sx*.8,pos = (0,sy*.25))

#Hazard Stimuli
# low hazard rate 
low = visual.ImageStim(win,path+'/Person.png', pos = leftPos, size = (sy*.1,sy*.1))
lo = visual.TextStim(win,text='low switch',pos = (-sx*posMult,-sy*.09),height=30,color = 'white')

# high hazard rate
high = visual.ImageStim(win,path+'/Person.png', pos = rightPos, size = (sy*.1,sy*.1),color = 'black')
hi = visual.TextStim(win,text='high switch',pos = (sx*posMult,-sy*.09),height=30,color = 'black')

#Text for SWITCH prediction phase
hazardPredText = visual.TextStim(win, text="Which person is choosing the beads?", height = 40, wrapWidth = sx*.8,pos = (0,sy*.25))

#Slider
cfY = -sy*.25
lWidth = .005
confLine = visual.Rect(win,height = sy*lWidth, width = sx*(posMult*2), pos = (0,cfY), fillColor = 'white')
confLine_left = visual.Rect(win,height = sy*.03, width = sy*lWidth, pos = (-sx*posMult,cfY), fillColor = 'white')
confLine_mid = visual.Rect(win,height = sy*.03,width = sy*lWidth, pos = (0,cfY), fillColor = 'white')
confLine_right = visual.Rect(win,height = sy*.03, width = sy*lWidth, pos = (sx*posMult,cfY), fillColor = 'white')
confLines = [confLine,confLine_left,confLine_mid,confLine_right]

confLine_leftText = visual.TextStim(win,text = "100% confident\nBlue", height = 20,
pos=(-sx*posMult,cfY+-(sy*.05)))
confLine_midText = visual.TextStim(win,text = "Not Sure", height = 20,
pos=(0,cfY+-(sy*.05)))
confLine_rightText = visual.TextStim(win,text = "100% confident\nOrange", height = 20,
pos=(sx*posMult,cfY+-(sy*.05)))
confText = [confLine_leftText,confLine_midText,confLine_rightText]

#Subject confidence line
subLine = visual.Rect(win,height = sy*.05,width = sx*lWidth, pos = (0,cfY),fillColor='red')

# linebounds
lbounds = [-sx*(posMult*2),sx*(posMult*2)]

#####################
## DATA COLLECTION ##
#####################

# Info to use for data file names
date_time = time.asctime()         #Date and Time
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
"TrialNumber","CurrGen","ItemLeft","ItemRight","SideChosen","Prediction","Confidence","Reward","RT"]
datafile.write(",".join(dataHeader)+'\n')
datafile.flush()

#Function to record data
def recDat(dfile,dat_vec):
    dat = map(str,dat_vec)
    dfile.write(",".join(dat)+'\n')
    dfile.flush()


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
        
#Function to draw confidence line
def drawConfLines(clines,ctext_stim,ctext,items,cross,positions,predText = False,subSlider = False):
    #Draw options to select
    cross.draw()
    if predText != False:
        predText.draw()
    for i in np.arange(len(items)):
        items[i].setPos(positions[i])
        items[i].draw()
        p = positions[i]
        
    # Draw and buffer confidence lines
    for cl in clines:
        cl.draw()
    print (positions)
    for i in np.arange(len(ctext)):
# ctext_stim[i].setPos(positions[i])
        ctext_stim[i].setText(ctext[i])
        ctext_stim[i].draw()
    if subSlider != False:
        subSlider.draw()
    cline_image = visual.BufferImageStim(win)
    return(cline_image)

#Function to launch the prediction screen
def predict(win,predText,cross,items,itemNames,positions,subSlider,trial,mouse,bounds):
    #Half a seconf blank screen
    win.flip()
    core.wait(.5)
    
    #Draw stimuli and text to indicate whether they are responding to coins or people
    cTexts = ["Very confident\n%s"%itemNames[0],"Not Sure","Very confident\n%s"%itemNames[1]]
    if trial == 1:
        getResp_screen = drawConfLines(confLines,confText,cTexts,items,cross, positions,predText = predText)
    else:
        subSlider.setColor('blue')
        getResp_screen = drawConfLines(confLines,confText,cTexts,items,cross,positions,predText = predText,subSlider = subSlider)
        subSlider.setColor('red')
    getResp_screen.draw()
    win.flip()
    # Get confidence judgement
    mouse.setVisible(True)
    mouse.setPos((0,0))
    conf = None
    while True:
        keys = event.getKeys(keyList = ['q','escape'])
        if len(keys):
            datafile.close()
            core.quit()
        x,y = mouse.getPos()
        pressed = mouse.getPressed()
        if pressed[0] == 1:
            if (x > -10) and (x < 10):
                side = None
                resp = None
                conf = 0
            else: 
                side = np.sign(x)
                if side == -1:
                    side = 0
                elif side == 1:
                    side = 1
                conf = abs(x)/abs(bounds[0])
            if conf > 1:
                conf = 1
            break
        elif (x >= bounds[0]) and (x <= bounds[1]) and (y < 0):
            subSlider.setPos((x/2,cfY))
        elif x < bounds[0]:
            subSlider.setPos((bounds[0]/2,cfY))
        elif x > bounds[1]:
            subSlider.setPos((bounds[1]/2,cfY))
        getResp_screen.draw()
        subSlider.draw()
        win.flip()
        time.sleep(1/60)
    
    getResp_screen = drawConfLines(confLines,confText,cTexts,items,cross,positions,subSlider = subSlider)
    if side != None:
        resp = itemNames[side]
    return([resp,round(conf,2),side,getResp_screen])

#Function to display coin
def coinFlip(coin,orgPos,cross,win,blkType):
    if blkType == 'coin':
        txt = 'Selecting bead...'
    else: 
        txt = 'Person selecting bead...'
    #Half a second blank screen
    win.flip()
    core.wait(.5)
    
    # Show text for half a second
    cFlipText = visual.TextStim(win,text = txt, height = 40)
    cFlipText.draw()
    win.flip()
    core.wait(.75)
    win.flip()
    core.wait(.25)
    
    #Coin on for a second
    coin.setPos((0,0))
    coin.draw()
    win.flip()
    core.wait(1.5)
    
    #Put coin back in original position
    coin.setPos(orgPos)
    
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
        
# Feedback screen
def feedback(response,correct,rside,conf,imBuffer,totPoints,fbPositions = [leftPos,rightPos]):
    win.flip()
    core.wait(.5)
#Figure out how many points the person can get/lose
    if rside != None:
        fbPos = fbPositions[rside]
    points = 0 #If resp/rside = None
    pcol = 'white'
    if response == None:
        points = 0
        imBuffer.draw()
    elif response == correct:
        points = 10*conf
        pcol = 'green'
        imBuffer.draw()
        fb = visual.Rect(win,height=sy*.12,width=sy*.12,fillColor=(0,1,0),lineWidth=0,opacity = .5)
        #fbText = visual.TextStim(win,text = 'Correct',height = 40,pos=(0,sy*.25))
        fb.setPos(fbPos)
        fb.draw()
        #fbText.draw()
    elif response != correct:
        points = -10*conf
        pcol = 'red'
        fb = visual.TextStim(win,text = 'X', height = 100,color = 'red')
        #fbText = visual.TextStim(win,text = 'Incorrect',height = 40,pos=(0,sy*.25))
        imBuffer.draw()
        fb.setPos(fbPos)
        fb.draw()
        #fbText.draw()
    pointsText = visual.TextStim(win,text = '%d points'%points,height = 30,color=pcol,pos=(0,sy*.25))
    pointsText.draw()

    win.flip()
    core.wait(1)
    return response == correct,points
    
#Function to run blocks of trials
def trialBlockRun(ntrials,subInfo,blkType,tblock,items,itemNames,positions,
predText,coins,trialID,totScore,dfile=datafile):
    side = ['left','right']
    #Show person that new trial block is starting
    if blkType == 'coin':
        trialBlockType('Current Score: %f\n\nNew container being selected...\n\nPress space to start trials'%totScore,win)
    else:
        trialBlockType('Current Score: %f\n\nNew person being selected...\n\nPress space to start trials'%totScore,win)
        
    trials = genTrials(blkType,ntrials,side[trialID])
    print(trials)
        
    for i in np.arange(len(trials)):
        coinFlip(coins[trials[i]],positions[trials[i]],cross,win,blkType)
        start = time.time()
        response,confidence,side,respScreen = predict(win,predText,cross,items,itemNames,positions,subLine,i+1,mouse,lbounds)
        recDat(dfile,[subInfo[0],subInfo[1],subInfo[2],subInfo[3],blkType,tblock,i+1,itemNames[trialID],itemNames[0],itemNames[1],side,response,confidence,'NA',str(time.time()-start)])
    correct,tScore = feedback(response,itemNames[trialID],side,confidence,respScreen,totScore)
    recDat(dfile,[subInfo[0],subInfo[1],subInfo[2],subInfo[3],blkType,tblock,i+1,itemNames[trialID],itemNames[0],itemNames[1],side,response,confidence,int(correct),'NA'])
    return(tScore)

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
tScore = 100
for blkType in blkTypes:
    if blkType == 'coin':
        itemNames = ['heads','tails']
        items = [heads,tails]
        predText = coinPredText
    elif blkType == 'hazard':
        itemNames = ['low','high']
        items = [low,high]
        predText = hazardPredText
    positions = [leftPos,rightPos]
    
    #Run through Trials
    for i in np.arange(len(trialBlocks)):
        print(trialIDs[i])
#def trialBlockRun(ntrials,subInfo,blkType,tblock,items,itemNames,positions,predText,coins,trialID,totScore,dfile=datafile):
        tscore = trialBlockRun(trialBlocks[i],subInfo,blkType,i+1,items,itemNames,
positions,predText,[heads,tails],trialIDs[i],tScore)
        tScore += tscore


win.flip()
core.wait(.5)
core.quit()

