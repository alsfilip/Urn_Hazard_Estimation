from psychopy import visual, event, core, gui
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
test = False #Set test to true to skip instructions and not make the task full screen
if test == True:
    scr = 0
    fs = False
    instr = False
    subID = 'TEST'
    cond = 1
    age = 'TEST'
    sex = 'TEST'
else:
    # Set full screen to true and use second monitor
    fs = True
    scr = 0
    
    # Creates a dialogue box to get subject info before experiment starts
    infoBox = gui.Dlg(title = "Participant Information")
    infoBox.addField("Subject ID: ")
    infoBox.addField("Condition (1 or 2): ")
    infoBox.addField("Age: ")
    infoBox.addField("Sex (M,F,O): ")
    infoBox.show()
    if gui.OK:
        pData = infoBox.data
        subID = str(pData[0])
        cond = int(pData[1])
        age = str(pData[2])
        sex = str(pData[3])
    elif gui.CANCEL:
        core.quit()

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

######################
## TASK ENVIRONMENT ##
######################

# TO DO: Make full screen

#Get path 
path = os.getcwd()      # Get directory path

# Create task window
disp = pl.getDisplayInformation()
sx = disp.width
sy = disp.height
#sx = 1200
#sy = 900
win = visual.Window(size=(sx,sy),units="pix",fullscr=fs,screen = scr)

#Get mouse
mouse = event.Mouse()
mouse.setVisible(False)

# Create Visual Stimuli
# fixation cross
cross = visual.TextStim(win,text = "+",height = 40)

#Multipliers for stim
mult = .02 #multiplier to set coin/person size according to the screen
posMult = .3 #multiploer to set position of left/right stimuli


# Positions for the options
addObject = sx*.05
leftPos = (-sx*posMult-addObject,0)
rightPos = (sx*posMult+addObject,0)

#Beads
blueBead = visual.Circle(win, radius = sy*mult,fillColor ="cyan",lineWidth = 2,pos=(0,(sy*.13)))
orangeBead = visual.Circle(win, radius = sy*mult,fillColor ="orange",lineWidth = 2,pos=(0,(sy*.13)))
beads = [orangeBead, blueBead]

# Urns
#Biased Urns
orangeUrn = visual.ImageStim(win,path+'//img//OrangeUrn.png', pos = leftPos, size = (sy*.1,sy*.12))
blueUrn = visual.ImageStim(win,path+'//img//BlueUrn.png', pos = rightPos, size = (sy*.1,sy*.12))

#Full Urns
orangeFullUrn = visual.ImageStim(win,path+'//img//OrangeFullUrn.png', pos = leftPos, size = (sy*.1,sy*.12))
blueFullUrn = visual.ImageStim(win,path+'//img//BlueFullUrn.png', pos = rightPos, size = (sy*.1,sy*.12))

# People
low = visual.ImageStim(win,path+'//img/LowPerson.png', pos = leftPos, size = (sy*.11,sy*.12))
high = visual.ImageStim(win,path+'//img/HighPerson.png', pos = rightPos, size = (sy*.11,sy*.12))

#Text for URN or HAZARD phase
urnPredText = visual.TextStim(win, text="From which container are the beads being drawn?", height = 40, wrapWidth = sx*.8,pos = (0,sy*.25))
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

confLine_leftText = visual.TextStim(win,text = "100% confident\nOrange", alignHoriz = 'center',height = 30,pos=(-sx*posMult-addObject,cfY+-(sy*.1)))
confLine_midText = visual.TextStim(win,text = "Not Sure", height = 30,pos=(0,cfY+-(sy*.1)))
confLine_rightText = visual.TextStim(win,text = "100% confident\nBlue", height = 30,pos=(sx*posMult+addObject,cfY+-(sy*.1)))
confText = [confLine_leftText,confLine_midText,confLine_rightText]

#Subject confidence line
subLine = visual.Rect(win,height = sy*.05,width = sx*lWidth,pos = (0,cfY),fillColor='red')

#lineBounds
lbounds = [-sx*(posMult),sx*(posMult)]

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
        for j in np.arange(i+1):
            poses.append((posX,posY))
            posX += incr
    posSet.append(poses)
    beadRem[beadNames[i]] = visual.Circle(win, radius = sy*(mult), fillColor='white',pos = (0,0))


#####################
## DATA COLLECTION ##
#####################

# Info to use for data file names
date_time=time.asctime()        #Date and Time
dt=date_time.replace(' ','_')    # Replace spaces with underscores where needed
dt=dt.replace('/','_')      #Replace slashes with underscores where needed
dt=dt.replace(':','')      #Replace slashes with underscores where needed

# Initialize data file
datafile = open(path+"//data//%s_CoinTask_%s.csv"%(subID,dt), 'w')

#  Data to be collected:
# SubjectID,Age,Sex: Subject information
# Condition: condition number (1 - coin trials first, 2 - hazard trials first)
# BlockType: which block is currently being observed (Coin or Hazard)
# TrialBlock: Which trial block is being seen (1 to however many trial blocks are observed)
# TrialNumber: Trial number within the current trial block (length 1-5)
# CurrGen: which urn or hazard rate is generating observations
# Bead: Which bead was observed
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

def getKeypress(df=datafile):
    keys = event.waitKeys()
    if keys[0] in ['q','escape']:
        df.close()
        core.quit()

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
    #Short blank screen
    win.flip()
    core.wait(.25)

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
            subSlider.setPos((x,cfY))
        elif x < bounds[0]:
            subSlider.setPos((bounds[0],cfY))
        elif x > bounds[1]:
            subSlider.setPos((bounds[1],cfY))
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

    #Short blank screen
    win.flip()
    core.wait(.25)
    
    # Show text for half a second
    cFlipText = visual.TextStim(win,text = txt,height = 40)
    cFlipText.draw()
    win.flip()
    core.wait(.75)
    
#    #Coin on for a second
#    if bead == 'orange':
#        beadItem = orangeBead
#    elif bead == 'blue':
#        beadItem = blueBead
#    beadItem.draw()
#    win.flip()
#    core.wait(1)

def genTrials(blkType, freqUrn,rareUrn, ntrials,person = False):
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
#def adjustConf(conf):
#    intercept = -log(.05)+1
#    normFact = intercept+log(.95)
#    if conf <= .05:
#        payoff = conf/.05
#    elif conf < .95:
#        payoff = intercept + log(conf)
#    elif conf >= .95:
#        payoff = intercept + log(.95)+(conf-.95)/.95
#    return(payoff/normFact)

def adjustConf(conf,slp,loBound=-.5,hiBound=.5):
    lowestVal = 1/(1+np.exp(-loBound/slp))
    highestVal = 1/(1+np.exp(-hiBound/slp))
    normFact = highestVal-lowestVal 
    if conf <= loBound:
        rew = 0
    elif conf >= hiBound:
        rew = 1
    else:
        rew = ((1/(1+np.exp(-conf/slp)))-lowestVal)/normFact
    pay = (rew*2)-1 #adjust to put on a -1,1 scale
    return(pay)

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
        points = 10*adjustConf(conf/2,.08) #adjusted reward - logit with slope = to .08
        pcol = 'green'
        imBuffer.draw()
        fb = visual.Rect(win,height=sy*.12,width=sy*.12,fillColor=(0,1,0),lineWidth=0,opacity = .5)
        fb.setPos(fbPos)
        fb.draw()
    elif response != correct:
        points = -10*conf #linear punishment
        pcol = 'red'
        fb = visual.TextStim(win,text = 'X', height = 100,color = 'red')
        imBuffer.draw()
        fb.setPos(fbPos)
        fb.draw()
    points = round(points)
    pointsText = visual.TextStim(win,text = '%d points'%points,height = 30,color=pcol,pos=(0,sy*.25))
    pointsText.draw()

    win.flip()
    core.wait(1)
    return response == correct,points

#Function to run blocks of trials
def trialBlockRun(ntrials,subInfo,blkType,tblock,items,itemNames,positions,respPos,predText,beads,trialID,totScore,dfile=datafile,instruct = False):

    #Show person that new trial block is starting
    if blkType == 'urn':
        trialBlockType('Current Score: %d\n\n\nPress space to start draws from a new container'%totScore,win)
        person = False
        if trialID == 1:
            rareID = 0
        else:
            rareID = 1
        freqUrn = itemNames[trialID]
        rareUrn = itemNames[rareID]
    else:
        trialBlockType('Current Score: %d\n\n\nPress space to start draws from a new person'%totScore,win)
        person = itemNames[trialID]
        freqUrn = 'orange'
        rareUrn = 'blue'

    urns,trials = genTrials(blkType,freqUrn,rareUrn,ntrials,person=person)
    print('Generating Urn:'+itemNames[trialID])
    mouse.setPos((0,0))
    for i in np.arange(len(trials)):
        urnDraw(trials[i],cross,win,blkType)
        start = time.time()
        response,confidence,side,respScreen = predict(win,predText,cross,items,itemNames,positions,respPos,subLine,trials,i+1,posSet,mouse,lbounds)
        print('Response:'+str(response))
        print('Confidence:'+str(confidence))
        if instruct == False:
            recDat(dfile,[subInfo[0],subInfo[1],subInfo[2],subInfo[3],blkType,tblock,i+1,itemNames[trialID],trials[i],itemNames[0],itemNames[1],side,response,confidence,'NA','NA',str(time.time()-start)])
    correct,tScore = feedback(response,itemNames[trialID],side,confidence,respScreen,totScore)
    print([totScore,tScore])
    if instruct == False:
        recDat(dfile,[subInfo[0],subInfo[1],subInfo[2],subInfo[3],blkType,tblock,i+1,itemNames[trialID],'NA',itemNames[0],itemNames[1],side,response,confidence,int(correct),tScore,'NA'])
    return(tScore)


##################
## INSTRUCTIONS ##
##################

def urnInstructions(blueUrn,orangeUrn,beads,leftPos,rightPos):
    # Display instruction text for urn condition
    txt1 = 'In this part of the task, you will see blue and orange beads and be asked to guess from which container the beads are being drawn.'
    txt2 = 'One of the containers has 80% orange beads and 20% blue beads.\n\nThe other container has 80% blue beads and 20% orange beads'
    txt3 = 'In this part of the task you will see between 1 and 5 beads drawn from one of the two containers.\n\nAfter every bead is drawn you will be asked to rate how confident you are that the beads are being drawn from the orange or blue container.'
    txt4 = 'When the beads are done being drawn from the container, you will get points for your predictions.\n\nIf you guess correctly, you will get between 0 and 10 points, depending on how confident you were in your answer.\n\nIf you guess incorrectly, you will lose between 0 and 10 points.\n\nAnswering "not sure" will not result in gaining or losing any points.'
    txt5 = 'To get the most points by the end of the task, the best strategy is to report your confidence as accurately as possible.'
    txt6 = 'You will start with 100 points and receive a payment bonus for scores above 100.\n\nThe more points you get above 100, the higher your payment bonus.'
    txtList = [txt1,txt2,txt3,txt4,txt5,txt6]
    for i in np.arange(len(txtList)):
        t = txtList[i]+'\n\nPress any key to continue'
        txtStim = visual.TextStim(win,t,height = 40,wrapWidth = sx*.8)
        txtStim.draw()
        win.flip()
        getKeypress()
    orangeUrn.setPos((0,0))
    blueUrn.setPos((0,0))
    
    #Examples of beads drawn from orange container
    orangeTxt = visual.TextStim(win,text = 'Press any key to see examples of beads drawn from the orange container',height = 40,wrapWidth = sx*.8)
    orangeTxt.draw()
    win.flip()
    getKeypress()
    # Examples of draws from the orange urn
    trials = [beads[0]]*3+[beads[1]]+[beads[0]]*2+[beads[1]]+[beads[0]]*2
    for t in trials:
        orangeUrn.draw()
        win.flip()
        core.wait(.25)
        
        orangeUrn.draw()
        t.draw()
        win.flip()
        core.wait(.75)
    
    #Examples of beads drawn from blue container
    blueTxt = visual.TextStim(win,text = 'Press any key to see examples of beads drawn from the blue container',height = 40,wrapWidth = sx*.8)
    blueTxt.draw()
    win.flip()
    getKeypress()
    #Examples of draws from the blue urnPredText
    trials = [beads[1]]+[beads[0]]+[beads[1]]*4+[beads[0]]+[beads[1]]*3
    for t in trials:
        blueUrn.draw()
        win.flip()
        core.wait(.25)
        
        blueUrn.draw()
        t.draw()
        win.flip()
        core.wait(.75)
    exTrialText = visual.TextStim(win,text = 'Press any key to run through example trials',height = 40,wrapWidth = sx*.8)
    exTrialText.draw()
    win.flip()
    getKeypress()

#Instructions for hazard rate block
def hazardInstructions(blueFullUrn,orangeFullUrn,loPerson,hiPerson,beads,leftPos,rightPos):
    # Display instruction text for hazard condition
    txt1 = 'In this part of the task, two people will be drawing beads from containers containing only orange or only blue beads.'
    txt2 = 'Each person switches between the containers at different rates.\n\nOne person (low switcher) switches between containers 20% of the time.\n\nThe other person (high switcher) switches between containers 80% of the time.'
    txt3 = 'In this part of the task you will see between 1 and 5 beads drawn from one of the two people.\n\nAfter every bead is drawn you will be asked to rate how confident you are that the beads are being drawn by the low switcher or the high switcher.'
    txt4 = 'After the person is done drawing beads, you will get points for your predictions.\n\nIf you guess correctly, you will get between 0 and 10 points, depending on how confident you were in your answer.\n\nIf you guess incorrectly, you will lose between 0 and 10 points.\n\nAnswering "not sure" will not result in gaining or losing any points.'
    txt5 = 'To get the most points by the end of the task, the best strategy is to report your confidence as accurately as possible.'
    txt6 = 'You will start with 100 points and receive a payment bonus for scores above 100.\n\nThe more points you get above 100, the higher your payment bonus.'
    txtList = [txt1,txt2,txt3,txt4,txt5,txt6]
    for i in np.arange(len(txtList)):
        t = txtList[i]+'\n\n\nPress any key to continue'
        txtStim = visual.TextStim(win,t,height = 40,wrapWidth = sx*.8)
        txtStim.draw()
        win.flip()
        getKeypress()
    orangeFullUrn.setPos(leftPos)
    blueFullUrn.setPos(rightPos)
    
    loPerson.setPos((0,sy*.25))
    hiPerson.setPos((0,sy*.25))
    
    #Examples of beads drawn from low switcher
    lowTxt = visual.TextStim(win,text = 'Press any key to see examples of beads drawn from the person who switches infrequently',height = 40,wrapWidth = sx*.8)
    lowTxt.draw()
    win.flip()
    getKeypress()
    # Examples of draws from the low switcher
    trials = [beads[0]]*6+[beads[1]]*4
    urns = [orangeFullUrn]*6+[blueFullUrn]*4
    for i in np.arange(len(trials)):
        loPerson.draw()
        urns[i].draw()
        win.flip()
        core.wait(.25)
        
        loPerson.draw()
        urns[i].draw()
        trials[i].draw()
        win.flip()
        core.wait(.75)
    
    #Examples of beads drawn from high switcher
    hiTxt = visual.TextStim(win,text = 'Press any key to see examples of beads drawn from the person who switches frequently',height = 40,wrapWidth = sx*.8)
    hiTxt.draw()
    win.flip()
    getKeypress()
    # Examples of draws from the high switcher
    trials = [beads[0],beads[1],beads[0],beads[1],beads[0],beads[0],beads[1],beads[0],beads[1],beads[1]]
    urns = [orangeFullUrn,blueFullUrn,orangeFullUrn,blueFullUrn,orangeFullUrn,orangeFullUrn,blueFullUrn,orangeFullUrn,blueFullUrn,blueFullUrn]
    for i in np.arange(len(trials)):
        hiPerson.draw()
        urns[i].draw()
        win.flip()
        core.wait(.25)
        
        hiPerson.draw()
        urns[i].draw()
        trials[i].draw()
        win.flip()
        core.wait(.75)
    exTrialText = visual.TextStim(win,text = 'Press any key to run through example trials',height = 40,wrapWidth = sx*.8)
    exTrialText.draw()
    win.flip()
    getKeypress()

##################
## TRIAL HANDLER ##
##################
subInfo = [subID,age,sex,cond]
# Based on the conditon set which type of trils goes first
if cond == 1:
    blkTypes = ['urn','hazard']
    scoreInd = [0,1]
else:
    blkTypes = ['hazard','urn']
    scoreInd = [1,0]

#Iterate through different block types


totalScore = [0,0]
startText = visual.TextStim(win,text='Press any key to start the first part of the experiment.',height = 40,wrapWidth = sx*.8)
startText.draw()
win.flip()
getKeypress()
for cnt in np.arange(len(blkTypes)):
    if blkTypes[cnt] == 'urn':
        itemNames = ['orange','blue']
        items = [orangeUrn,blueUrn]
        predText = urnPredText
    elif blkTypes[cnt] == 'hazard':
        itemNames = ['low','high']
        items = [low,high]
        predText = hazardPredText
    positions = [leftPos,rightPos]
    tScore = 100
    instrBlocks = [4]
    intrIDs = [1]
    if blkTypes[cnt] == 'urn' and test == False:
        urnInstructions(blueUrn,orangeUrn,beads,leftPos,rightPos)
        for i in np.arange(len(instrBlocks)):
            positions = [leftPos,rightPos]
            respPos = itemNames
            extscore = trialBlockRun(instrBlocks[i],subInfo,blkTypes[cnt],i+1,items,itemNames,positions,respPos,predText,beads,intrIDs[i],tScore,instruct =True)
    elif blkTypes[cnt] == 'hazard' and test == False:
        hazardInstructions(blueFullUrn,orangeFullUrn,low,high,beads,leftPos,rightPos)
        for i in np.arange(len(instrBlocks)):
            positions = [leftPos,rightPos]
            respPos = itemNames
            extscore = trialBlockRun(instrBlocks[i],subInfo,blkTypes[cnt],i+1,items,itemNames,positions,respPos,predText,beads,intrIDs[i],tScore,instruct =True)
    win.flip()
    core.wait(.75)
    text = visual.TextStim(win,'\n\nEnd of instructions.\n\nPress any key to start the real trials.',height = 40,wrapWidth = sx*.8)
    text.draw()
    win.flip()
    getKeypress()
    #Run through Trials
    for i in np.arange(len(trialBlocks)):
        if blkTypes[cnt] == 'urn':
            itemNames = ['orange','blue']
            items = [orangeUrn,blueUrn]
            predText = urnPredText
        elif blkTypes[cnt] == 'hazard':
            itemNames = ['low','high']
            items = [low,high]
            predText = hazardPredText
        positions = [leftPos,rightPos]
        if np.random.uniform(0,1,1) < .5:
            positions = [rightPos,leftPos]
            itemNames = [itemNames[1],itemNames[0]]
        respPos = itemNames
        tscore = trialBlockRun(trialBlocks[i],subInfo,blkTypes[cnt],i+1,items,itemNames,positions,respPos,predText,beads,trialIDs[i],tScore)
        tScore += round(tscore)
        totalScore[scoreInd[cnt]] = tScore
    if cnt == 0:
        endText = visual.TextStim(win,text='End of first part.\n\nPress any key to start the instructions for the second part of the experiment.',height = 40,wrapWidth = sx*.8)
        endText.draw()
        win.flip()
        getKeypress()

win.flip()
core.wait(.5)

ub = 900
cashBonus = (sum(totalScore)/ub)*10
endScreen = visual.TextStim(win,text = 'Experiment done! Thank you for your participation!\n\nFinal container score: %s\n\nFinal person score: %s\n\nTotal Score: %s\n\nCash Bonus: $%s'%(str(int(round(totalScore[0]))),str(int(round(totalScore[1]))),str(int(round(sum(totalScore)))),str(int(round(cashBonus)))),height = 40,wrapWidth = sx*.8)
endScreen.draw()
win.flip()
getKeypress()

