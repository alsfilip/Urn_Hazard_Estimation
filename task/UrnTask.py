from psychopy import visual, event, core
import numpy as np
from math import log
import os, time, random
import pylink as pl

'''
Alexandre Filipowicz & Derek Nuamah, July 1st, 2019

Urn Hazard prediction task

The goal of this task is to track people's uncertainty while either infering a state or a hazard rate.

The task is a coin estimation task in which people see "blocks" of trials (ranging from 1-5 trials). On each trial, subjects see the result of a coin flip (i.e. heads or tails) and are asked to make one of two estimations:
    1) Which coin is being flipped?: In this condition, the coin could be one of two biased coins (one biased 80% towards heads, 20% towards tails or vice versa). After every observation, the subject's job is to report which coin they think is being flipped
    2) Which person is choosing coins?: In this condition, two people are choosing coins - a) slow switcher, who picks tails or heads and keeps showing this first pick on subsequebnt trials, rarely switching to the other, and b) fast switcher, a person who frequently switches between heads and tails, rarely repeating the same coin twice.

People are meant to respond with a slider to report their confidence (ranging from 100% confident heads/slow switcher ------ not sure -------- 100% cofident tails/fast switcher). At the end of each trial block, the person is given feedback as to which was the right coin, and given points based on their confidence judgement.

The idea is that certainty dynamics (how certainty changes with each observation) show depend on whether or not a person is making a hazard rate judgement. Confidence should increase after the first observation if you're making a coin judgement, but you need at least two pieces of evidence before being confident in the hazard judgement condition.
'''

##################
## SUBJECT INFO ##
##################
test = True
if test == True:
    fs = False
    instr = False
    subID = 'Alex_TEST'
    cond = 1
    age = 'TEST'
    sex = 'TEST'
else:
    fs = True
    
# TO DO: Make gui to get subject info and add condition
subID = 'Alex_TEST'
cond = 1
age = 'TEST'
sex = 'TEST'

#####################
## GENERATE TRIALS ##
#####################

# Generate the trial blocks
niter = 2 #number of times each trial block length is repeated - make sure this is an even number
trialBlocks = [1,2,3,4,5]*niter
random.shuffle(trialBlocks)

# Randomly generate the sequence of tails/heads and low/high hazard 
#0 = heads/low, 1 = tails/high
trialIDs = [0,1]*int(len(trialBlocks)/2)
random.shuffle(trialIDs)

print(len(trialBlocks))
print(len(trialIDs))

######################
## TASK ENVIRONMENT ##
######################

# TO DO: Make full screen

#Get path 
path = os.getcwd()      # Get directory path

# Create task window
#disp = pl.getDisplayInformation()
#sx = disp.width
#sy = disp.height
sx = 1000
sy = 800
win = visual.Window(size=(sx,sy),units="pix",fullscr=fs)

#Get mouse
mouse = event.Mouse()
mouse.setVisible(False)

# Create Visual Stimuli
# fixation cross
cross = visual.TextStim(win,text = "+",height = 40)

#Multipliers for stim
mult = .06 #multiplier to set coin/person size according to the screen
posMult = .3 #multiploer to set position of left/right stimuli


# Positions for the options
addObject = sx*.05
leftPos = (-sx*posMult-addObject,0)
rightPos = (sx*posMult+addObject,0)

#Beads
blueBead = visual.Circle(win, radius = sy*mult, pos = (0,0),fillColor ="cyan",lineWidth = 5)
orangeBead = visual.Circle(win, radius = sy*mult, pos = (0,0),fillColor ="orange",lineWidth = 5)
beads = [orangeBead, blueBead]

# Urns
#Biased Urns
orangeUrn = visual.ImageStim(win,path+'/OrangeUrn.png', pos = leftPos, size = (sy*.1,sy*.12))
blueUrn = visual.ImageStim(win,path+'/BlueUrn.png', pos = rightPos, size = (sy*.1,sy*.12))

#Full Urns
orangeFullUrn = visual.ImageStim(win,path+'/OrangeFullUrn.png', pos = leftPos, size = (sy*.1,sy*.12))
blueFullUrn = visual.ImageStim(win,path+'/BlueFullUrn.png', pos = rightPos, size = (sy*.1,sy*.12))

# People
low = visual.ImageStim(win,path+'/LowPerson.png', pos = leftPos, size = (sy*.11,sy*.12))
high = visual.ImageStim(win,path+'/HighPerson.png', pos = rightPos, size = (sy*.11,sy*.12))

#Text for URN or HAZARD phase
urnPredText = visual.TextStim(win, text="From which container are these beads being drawn?", height = 40, wrapWidth = sx*.8,pos = (0,sy*.25))
hazardPredText = visual.TextStim(win, text="Which person is drawing the beads?", height = 40, wrapWidth = sx*.8,pos = (0,sy*.25))


#Slider
#cfY = -sy*.25 
cfY = 0
lWidth = .005
confLine = visual.Rect(win,height = sy*lWidth, width = sx*(posMult*2),pos = (0,cfY),fillColor='white')
confLine_left = visual.Rect(win,height = sy*.03,width = sy*lWidth,pos = (-sx*posMult,cfY),fillColor='white')
confLine_mid = visual.Rect(win,height = sy*.03,width = sy*lWidth,pos = (0,cfY),fillColor='white')
confLine_right = visual.Rect(win,height = sy*.03,width = sy*lWidth,pos = (sx*posMult,cfY),fillColor='white')
confLines = [confLine,confLine_left,confLine_mid,confLine_right]

confLine_leftText = visual.TextStim(win,text = "100% confident\nOrange", alignHoriz = 'center',height = 20,pos=(-sx*posMult-addObject,cfY+-(sy*.1)))
confLine_midText = visual.TextStim(win,text = "Not Sure", height = 20,pos=(0,cfY+-(sy*.1)))
confLine_rightText = visual.TextStim(win,text = "100% confident\nBlue", height = 20,pos=(sx*posMult+addObject,cfY+-(sy*.1)))
confText = [confLine_leftText,confLine_midText,confLine_rightText]

#Subject confidence line
subLine = visual.Rect(win,height = sy*.05,width = sx*lWidth,pos = (0,cfY),fillColor='red')

#lineBounds
lbounds = [-sx*(posMult*2),sx*(posMult*2)]

# Bead reminders
beadRem = {}
beadNames = ['bead1','bead2','bead3','bead4','bead5']
tWidth = sx*.2
incr = tWidth/4
posY = (sy*.13)
posSet = []
for i in np.arange(len(beadNames)):
    poses = []
    if i == 0:
        poses.append((0,posY))
    else:
        posX = -(incr*.5)*(i)
        print(incr)
        print(posX)
        for j in np.arange(i+1):
            poses.append((posX,posY))
            posX += incr
    posSet.append(poses)
    beadRem[beadNames[i]] = visual.Circle(win, radius = sy*(mult/3), fillColor='white',pos = (0,0))


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
# ItemLeft: option that was on the left for that trial
# ItemRight: option that was on the right for that trial
# SideChosen: Side the subject chose (0 for left, 1 for right)
# Prediction: Subject's prediction on that trial
# Confidence: confidence raiting
# Reward: if the subject got reward on that trial, how much did they get
# RT: response time
dataHeader = ["SubjectID","Age","Sex","Condition","BlockType","TrialBlock","TrialNumber","CurrGen","Bead","ItemLeft","ItemRight","SideChoisen","Prediction","Confidence","Correct","Reward","RT"]
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

#Function before Trial Block to indicate whether this is a Coin Bias or Person Switching Scenario
def trialBlockType(typeText,win):
    win.flip()
    core.wait(1)
    tbt_text = visual.TextStim(win,text=typeText,height=40,wrapWidth = sx*.8)
    tbt_text.draw()
    win.flip()
    keys = event.waitKeys(keyList = ['space','q','escape'])
    if keys[0] in ['q','escape']:
        core.quit()

#Function to draw beads seen up to this points
def drawSeenBeads(trialNum,beadRem,beadDraws,beadPoses):
    keyNames = ['bead1','bead2','bead3','bead4','bead5']
    poses = beadPoses[trialNum-1]
    for i in np.arange(trialNum):
        b = beadRem[keyNames[i]]
        col = beadDraws[i]
        if beadDraws[i] == 'blue':
            col = 'cyan'
        b.setFillColor(col)
        b.setPos(poses[i])
        b.draw()

#Function to draw confidence line
def drawConfLines(clines,ctext_stim,ctext,items,cross,positions,prevBeads,trialNum,beadPoses,predText = False,subSlider = False):
    # Draw options to select
    if predText != False:
        predText.draw()
    for i in np.arange(len(items)):
        items[i].setPos(positions[i])
        items[i].draw()
        p = positions[i]
        
    #Draw and buffer confidence lines
    for cl in clines:
        cl.draw()
    for i in np.arange(len(ctext)):
        ctext_stim[i].setText(ctext[i])
        ctext_stim[i].draw()
    if subSlider != False:
        subSlider.draw()
    drawSeenBeads(trialNum,beadRem,prevBeads,beadPoses)
    cline_image = visual.BufferImageStim(win)
    return(cline_image)

#Function to launch the prediction screen
def predict(win,predText,cross,items,itemNames,positions,respPos,subSlider,prevBeads,trial,beadPoses,mouse,bounds):
    #Half a second blank screen
    win.flip()
    core.wait(.5)

    #Draw stimuli and text to indicate whether they are responding to coins or people
    cTexts = ["Very confident\n%s"%itemNames[0],"Not Sure","Very confident\n%s"%itemNames[1]]
    if trial == 1:
        getResp_screen = drawConfLines(confLines,confText,cTexts,items,cross,positions,prevBeads,trial,beadPoses,predText = predText)
    else:
        subSlider.setColor('blue')
        getResp_screen = drawConfLines(confLines,confText,cTexts,items,cross,positions,prevBeads,trial,beadPoses,predText = predText,subSlider = subSlider)
        subSlider.setColor('red')
    getResp_screen.draw()
    win.flip()
    
    #Get confidence judgement
    mouse.setVisible(True)
    subSlider.setPos((0,cfY))
    conf = None
    while True:
        keys = event.getKeys(keyList = ['q','escape'])
        if len(keys):
            datafile.close()
            core.quit()
        x,y = mouse.getPos()
        pressed = mouse.getPressed()
        if pressed[0] == 1:
            if (x > -20) and (x < 20):
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
        elif (x >= bounds[0]) and (x <= bounds[1]) and (y < 50):
            subSlider.setPos((x/2,cfY))
        elif x < bounds[0]:
            subSlider.setPos((bounds[0]/2,cfY))
        elif x > bounds[1]:
            subSlider.setPos((bounds[1]/2,cfY))
        getResp_screen.draw()
        subSlider.draw()
        win.flip()
        time.sleep(1/60)
    
    
    getResp_screen = drawConfLines(confLines,confText,cTexts,items,cross,positions,prevBeads,trial,beadPoses,subSlider = subSlider)
    if side != None:
        resp = respPos[side]
    mouse.setVisible(False)
    return([resp,round(conf,2),side,getResp_screen])


#Function to display coin
def urnDraw(bead,cross,win,blkType):
    # Test to tell the person that coin is being flipped
    if blkType == 'urn':
        txt = 'Drawing bead...'
    else: 
        txt = 'Person drawing bead...'

    #Half a second blank screen
    win.flip()
    core.wait(.5)
    
    # Show text for half a second
    cFlipText = visual.TextStim(win,text = txt,height = 40)
    cFlipText.draw()
    win.flip()
    core.wait(.75)
    win.flip()
    core.wait(.25)
    
#    #Coin on for a second
#    if bead == 'orange':
#        beadItem = orangeBead
#    elif bead == 'blue':
#        beadItem = blueBead
#    beadItem.draw()
#    win.flip()
#    core.wait(1)

def genTrials(blkType, freqUrn,rareUrn, ntrials,person = False):
    print(freqUrn)
    print(rareUrn)
    if blkType == 'urn':
        trials = np.random.uniform(0,1,ntrials)<.8
        urns = [freqUrn]*ntrials
        beadDraws = []
        for i in np.arange(ntrials):
            if trials[i] == True:
                beadDraws.append(freqUrn)
            else:
                beadDraws.append(rareUrn)

    elif blkType == 'hazard':
        if person == 'low':
            h = .2
        elif person == 'high':
            h = .8
        currUrn = random.choice([freqUrn,rareUrn])
        urns = []
        beadDraws = []
        for i in np.arange(ntrials):
            urns.append(currUrn)
            beadDraws.append(currUrn)
            if np.random.uniform(0,1,1) < h:
                if currUrn == freqUrn:
                    currUrn = rareUrn
                elif currUrn == rareUrn:
                    currUrn = freqUrn
    return urns, beadDraws

#Convert confidence value into adjusted points value
def adjustConf(conf):
    intercept = -log(.05)+1
    normFact = intercept+log(.95)
    if conf <= .05:
        payoff = conf/low
    elif conf < .95:
        payoff = intercept + log(conf)
    elif conf >= .95:
        payoff = intercept + log(.95)+(conf-.95)/.95
    return(payoff/normFact)

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
        points = 10*adjustConf(conf)
        pcol = 'green'
        imBuffer.draw()
        fb = visual.Rect(win,height=sy*.12,width=sy*.12,fillColor=(0,1,0),lineWidth=0,opacity = .5)
        fb.setPos(fbPos)
        fb.draw()
    elif response != correct:
        points = -10*adjustConf(conf)
        pcol = 'red'
        fb = visual.TextStim(win,text = 'X', height = 100,color = 'red')
        imBuffer.draw()
        fb.setPos(fbPos)
        fb.draw()
    pointsText = visual.TextStim(win,text = '%d points'%points,height = 30,color=pcol,pos=(0,sy*.25))
    pointsText.draw()

    win.flip()
    core.wait(1)
    return response == correct,points

#Function to run blocks of trials
def trialBlockRun(ntrials,subInfo,blkType,tblock,items,itemNames,positions,respPos,predText,beads,trialID,totScore,dfile=datafile):

    #Show person that new trial block is starting
    if blkType == 'urn':
        trialBlockType('Current Score: %d\n\n\nPress space to start draws from new container'%totScore,win)
        person = False
        if trialID == 1:
            rareID = 0
        else:
            rareID = 1
        freqUrn = itemNames[trialID]
        rareUrn = itemNames[rareID]
    else:
        trialBlockType('Current Score: %d\n\n\nPress space to start draws from new person'%totScore,win)
        person = itemNames[trialID]
        freqUrn = 'orange'
        rareUrn = 'blue'

    urns,trials = genTrials(blkType,freqUrn,rareUrn,ntrials,person=person)
    print('Generating Urn')
    print(itemNames[trialID])
    for i in np.arange(len(trials)):
        urnDraw(trials[i],cross,win,blkType)
        start = time.time()
        response,confidence,side,respScreen = predict(win,predText,cross,items,itemNames,positions,respPos,subLine,trials,i+1,posSet,mouse,lbounds)
        print('Response:'+str(response))
        recDat(dfile,[subInfo[0],subInfo[1],subInfo[2],subInfo[3],blkType,tblock,i+1,itemNames[trialID],trials[i],itemNames[0],itemNames[1],side,response,confidence,'NA','NA',str(time.time()-start)])
    correct,tScore = feedback(response,itemNames[trialID],side,confidence,respScreen,totScore)
    recDat(dfile,[subInfo[0],subInfo[1],subInfo[2],subInfo[3],blkType,tblock,i+1,itemNames[trialID],'NA'itemNames[0],itemNames[1],side,response,confidence,int(correct),tScore,'NA'])
    return(tScore)


##################
## INSTRUCTIONS ##
##################

def urnInstructions(blueUrn,orangeUrn,beads,leftPos,rightPos):
    # Display instruction text for urn condition
    txt1 = 'In this task, you will be asked to make predictions about which container beads are being drawn.'
    txt2 = 'One of the containers has 80% orange beads and 20% blue beads and the other container has 80% blue beads and 20% orange beads'
    txt3 = 'You are going to see a few trial blocks and each trial block will see between 1 and 5 bead draws.\n\n After each draw we will ask you to rate how confident you are that the beads are being drawn from the mostly orange or mostly blue container.'
    txt4 = 'At the end of each trial block you will get points for your predictions.\n\nIf you guess correctly, you will get between 0 and 10 points, depedning on how confident you were in your answer.\n\nIf you guess incorrectly, you will lose between 0 and 10 points based on your confidence.\n\nAnswering "not sure" will not result in gaining or losing any points.'
    txtList = [txt1,txt2,txt3,txt4]
    for i in np.arange(len(txtList)):
        t = txtList[i]+'\n\nPress any key to continue'
        txtStim = visual.TextStim(win,t,height = 30,wrapWidth = sx*.8)
        txtStim.draw()
        win.flip()
        keys = event.waitKeys()
        if keys[0] in ['q','escape']:
            datafile.close()
            core.quit()
    orangeUrn.setPos(leftPos)
    blueUrn.setPos(rightPos)
    
    #Examples of beads drawn from orange container
    orangeTxt = visual.TextStim(win,text = 'Press any key to see examples of beads drawn from the orange container',height = 30,wrapWidth = sx*.8,pos=(0,sy*.25))
    orangeTxt.draw()
    win.flip()
    keys = event.waitKeys()
    if keys[0] in ['q','escape']:
        datafile.close()
        core.quit()
    # Examples of draws from the orange urn
    trials = [beads[0]]*3+[beads[1]]+[beads[0]]*2+[beads[1]]+[beads[0]]*2
    for t in trials:
        orangeUrn.draw()
        win.flip()
        core.wait(.5)
        
        orangeUrn.draw()
        t.draw()
        win.flip()
        core.wait(1)
    
    #Examples of beads drawn from blue container
    blueTxt = visual.TextStim(win,text = 'Press any key to see examples of beads drawn from the blue container',height = 30,wrapWidth = sx*.8,pos=(0,sy*.25))
    blueTxt.draw()
    blueUrn.draw()
    win.flip()
    keys = event.waitKeys()
    if keys[0] in ['q','escape']:
        datafile.close()
        core.quit()
    #Examples of draws from the blue urnPredText
    trials = [beads[1]]+[beads[0]]+[beads[1]]*4+[beads[0]]+[beads[1]]*3
    for t in trials:
        blueUrn.draw()
        win.flip()
        core.wait(.5)
        
        blueUrn.draw()
        t.draw()
        win.flip()
        core.wait(1)

#Instructions for hazard rate block
def hazardInstructions(blueFullUrn,orangeFullUrn,loPerson,hiPerson,beads,leftPos,rightPos):
    # Display instruction text for hazard condition
    txt1 = 'In this task, one of two people will be drawing beads from containers containing only orange or only blue beads.'
    txt2 = 'Each person switches from which container they draw their beads. One of the people (low switcher) switches infrequently between the two containers (switches 20% of the time) whereas the other person switches very frequently (high switcher) between containers (80% of the time).'
    txt3 = 'You are going to see a few trial blocks and each trial block will have between 1 and 5 bead draws.\n\nAfter every bead you will be asked to rate how confident you are that the beads are being drawn by the low switcher or the high switcher.'
    txt4 = 'At the end of each trial block you will get points for your predictions.\n\nIf you guess correctly, you will get between 0 and 10 points, depending on how confident you were in your answer.\n\nIf you guess incorrectly, you will lose between 0 and 10 points based on your confidence.\n\nAnswering "not sure" will not result in gaining or losing any points.'
    txtList = [txt1,txt2,txt3,txt4]
    for i in np.arange(len(txtList)):
        t = txtList[i]+'\n\nPress any key to continue'
        txtStim = visual.TextStim(win,t,height = 30,wrapWidth = sx*.8)
        txtStim.draw()
        win.flip()
        keys = event.waitKeys()
        if keys[0] in ['q','escape']:
            datafile.close()
            core.quit()
    orangeFullUrn.setPos(leftPos)
    blueFullUrn.setPos(rightPos)
    
    loPerson.setPos((0,sy*.25))
    hiPerson.setPos((0,sy*.25))
    
    #Examples of beads drawn from low switcher
    lowTxt = visual.TextStim(win,text = 'Press any key to see examples of beads drawn from the person who switches infrequently',height = 30,wrapWidth = sx*.8,pos=(0,sy*.25))
    lowTxt.draw()
    win.flip()
    keys = event.waitKeys()
    if keys[0] in ['q','escape']:
        datafile.close()
        core.quit()
    # Examples of draws from the low switcher
    trials = [beads[0]]*6+[beads[1]]*4
    urns = [orangeFullUrn]*6+[blueFullUrn]*4
    for i in np.arange(len(trials)):
        loPerson.draw()
        urns[i].draw()
        win.flip()
        core.wait(.5)
        
        loPerson.draw()
        urns[i].draw()
        trials[i].draw()
        win.flip()
        core.wait(1)
    
    #Examples of beads drawn from high switcher
    hiTxt = visual.TextStim(win,text = 'Press any key to see examples of beads drawn from the person who switches frequently',height = 30,wrapWidth = sx*.8,pos=(0,sy*.25))
    hiTxt.draw()
    win.flip()
    keys = event.waitKeys()
    if keys[0] in ['q','escape']:
        datafile.close()
        core.quit()
    # Examples of draws from the high switcher
    trials = [beads[0],beads[1],beads[0],beads[1],beads[0],beads[0],beads[1],beads[0],beads[1],beads[1]]
    urns = [orangeFullUrn,blueFullUrn,orangeFullUrn,blueFullUrn,orangeFullUrn,orangeFullUrn,blueFullUrn,orangeFullUrn,blueFullUrn,blueFullUrn]
    for i in np.arange(len(trials)):
        hiPerson.draw()
        urns[i].draw()
        win.flip()
        core.wait(.5)
        
        hiPerson.draw()
        urns[i].draw()
        trials[i].draw()
        win.flip()
        core.wait(1)
        
##################
## TRIAL HANDLER ##
##################
subInfo = [subID,age,sex,cond]
# Based on the conditon set which type of trils goes first
if cond == 1:
    blkTypes = ['urn','hazard']
    blkText = ['Start Container Trials','Start Person Trials']
else:
    blkTypes = ['hazard','urn']
    blkText = ['Start Person Trials','Start Container Trials']

#Iterate through different block types


cnt = 0
totalScore = 0
for blkType in blkTypes:
    tScore = 100
    if blkType == 'urn':
        urnInstructions(blueUrn,orangeUrn,beads,leftPos,rightPos)
    else:
        hazardInstructions(blueFullUrn,orangeFullUrn,low,high,beads,leftPos,rightPos)
    
    text = visual.TextStim(win,blkText[cnt],height = 30)
    text.draw()
    win.flip()
    core.wait(2)
    cnt += 1
    #Run through Trials
    for i in np.arange(len(trialBlocks)):
        if blkType == 'urn':
            itemNames = ['orange','blue']
            items = [orangeUrn,blueUrn]
            predText = urnPredText
        elif blkType == 'hazard':
            itemNames = ['low','high']
            items = [low,high]
            predText = hazardPredText
        positions = [leftPos,rightPos]
        if np.random.uniform(0,1,1) < .5:
            positions = [rightPos,leftPos]
            itemNames = [itemNames[1],itemNames[0]]
            print('reverse')
        respPos = itemNames
        tscore = trialBlockRun(trialBlocks[i],subInfo,blkType,i+1,items,itemNames,positions,respPos,predText,beads,trialIDs[i],tScore)
        tScore += round(tscore)
        totalScore += tScore


win.flip()
core.wait(.5)

endScreen = visual.TextStim(win,text = 'Experiment done! Thank you for your participation!\n\nYour final score is: %s'%totalScore,height = 40)
event.waitKeys()
core.quit()

