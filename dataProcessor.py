#########################
## for ploting
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt



from struct import *

preIntOffSet = 2 # other addtional information before INT header
intOffSet = 5    # INT header, granularity: 4 bytes 


sinceLocated = -100
switchCnt = 0
switchLoopCnt = 0
#print 'switchLoopCnt', switchLoopCnt
insCnt = 0 # number of INT instructions

#####################################################
# counters for recording
a1Cnt = 0
a2Cnt = 0
b1Cnt = 0
b2Cnt = 0
othersCnt = 0
flagCnt = 0
#####################################################
# Flags for detecting specific switch
sB2Detected = False


###################
# Lists for ploting

# for switch A1
a1HopLantency = []
a1QueueOcuupancy = []

# tmp
globalTimeStamp = 0
globalTimeStampList = []

####################################################
## Helper Functions
####################################################

## mean calculation

def meanCalulationForList(inputList):
    sum = 0
    for data in inputList:
        sum += data
    return sum / len(inputList)


def readFirstLineOfINTMetaData(line):

    global switchLoopCnt
    global a1Cnt 
    global a2Cnt
    global b1Cnt
    global b2Cnt
    global sB2Detected
    global flagCnt

    #if int(insCnt) != 0 and (sinceLocated - preIntOffSet - intOffSet) % int(insCnt) == 1:
 
         
    switchLoopCnt += 1

    print 'switchloopCnt = ', switchLoopCnt
    #print line.split('-')[3]          
    #print 'switchCnt = ', int(switchCnt) 

    if switchLoopCnt <= int(switchCnt):
	line = line.strip()
	dataList = line.split('-')
	# print dataList
	if len(dataList) == 4:
		    
	    # reset switch-detected flags
	   # sB2Detected = False
		   
	    # distinguish INT data with switch ID
		    
		      
	    if dataList[3] == 'A1':
		a1Cnt += 1
		sB2Detected = False
	    elif dataList[3] == 'A2':
		a2Cnt += 1
	        sB2Detected = False

	    elif dataList[3] == 'B1':
		b1Cnt += 1
	        sB2Detected = False

	    elif dataList[3] == 'B2':
		b2Cnt += 1
		sB2Detected = True
			

	    else:
		othersCnt += 1
		sB2Detected = False

    #if sB2Detected == True:
    #    flagCnt += 1


####################################

def readSecondLineOfINTMetaData(line): 

    global switchLoopCnt
    

    # mask B000           
    # second INT data: Hop latenciy
    #if int(insCnt) != 0 and (sinceLocated - preIntOffSet - intOffSet) % int(insCnt) == 2:

    # if sB2Detected == True:
    #     flagCnt += 1



    print 'switchLoopCnt = ', switchLoopCnt    
    print 'HopLantency = ', line 
    dataList = line.split('-')
    print dataList
    if len(dataList) == 4:
	print 'Hop Latency = ', dataList[2], dataList[3]
	print 'Hop Latency = ', int(str(dataList[2]), 16), int(str(dataList[3]), 16)
	latency = int(str(dataList[2]), 16) * 16 * 16 + int(str(dataList[3]), 16)
	a1HopLantency.append(latency) 

	globalTimeStampList.append(globalTimeStamp) 

 
#####################################################
# Start Reading...

f = open('int-data-mask-FF00', 'r')

for line in f.readlines():
    line = line.strip()

    if line == 'NewPacket':
        # reset counts
        switchCnt = 0
        mdBytes = 0
        switchLoopCnt = 0
        insCnt = 0 # number of INT instructions

        # reset Flags        
    #    sB2Detected = False

        # mark
        sinceLocated = 0
        print('----------')
        print('located!')
       
    
    else:
        # start analyzing data for each packet
        
        sinceLocated += 1
        
        if sinceLocated == 1:
            timeStamp = float(line)
            print 'Analyzed TimeStamp: ', int(timeStamp)
            globalTimeStamp = int(timeStamp)

        if sinceLocated == 2:
            mdBytes = line
            print 'mdBytes = ', int(mdBytes)
            print mdBytes
        
        if sinceLocated == 3:
           # print line
            dataList = line.split('-')
 
            if len(dataList) == 4:
                if dataList[3] == '04':
                    print dataList[0], dataList[1], dataList[2], dataList[3]
        
        # the fifth line of INT header
        if sinceLocated == 7:        
            dataList = line.split('-')
            if len(dataList) == 4:
                insCnt = dataList[1]
                print 'insCnt = ', int(insCnt)

                # Determine the number of switch
                if int(mdBytes) != 0 and int(insCnt) != 0:
                #print int(mdBytes)
                    switchCnt = int(mdBytes) / 4 / int(insCnt)        
                print 'switchCnt = ', switchCnt
 
        # Accessing INT meta data
        IntMetaDataUpperBound = preIntOffSet + intOffSet + 1
        IntMetaDataLowerBound = preIntOffSet + intOffSet + 1 + int(switchCnt) * int(insCnt)
      
        

        # first line of INT Varible Option Data
       # if sinceLocated == preIntOffSet + intOffSet + 1:
       #     print 'start INT data'

       

        if sinceLocated >= IntMetaDataUpperBound:
            print 'Inside INT Meda Data'
            print 'current INT line: ', sinceLocated - preIntOffSet - intOffSet
            print 'insCnt = ', int(insCnt)  




            if int(insCnt) != 0:

                # reset Flags        
	        sB2Detected = False




                intMetaDataLineNum = (sinceLocated - preIntOffSet - intOffSet) % int(insCnt)
            
                # first INT data: Switch ID
                if intMetaDataLineNum == 1:

                    readFirstLineOfINTMetaData(line)

                if sB2Detected == True:
                    flagCnt += 1

                if intMetaDataLineNum == 3:

                    readSecondLineOfINTMetaData(line)



f.close

print a1Cnt, a2Cnt, b1Cnt, b2Cnt, othersCnt
print 'flagCnt = ', flagCnt



############################################################
## Start Ploting...
############################################################
print 'Size of a1HopLantencyList = ', len(a1HopLantency) 
print 'Size of alTimeStampList = ', len(globalTimeStampList)

# strip data lists
xList = globalTimeStampList[500:len(globalTimeStampList)-500]
yList = a1HopLantency[500:len(a1HopLantency)-500]

print len(xList), len(yList)

print meanCalulationForList(yList)

aList = ['0xA000', '0xFF00']
bList = [1978, 2665]

'''
plt.plot(xList, yList)
plt.ylabel('Latency')
#plt.axis([0, 40000, 0, 16000])
plt.grid(True)
pp = PdfPages('latency-A1-Switch-Mask-F000.pdf')
pp.savefig()
pp.close()

''' 
