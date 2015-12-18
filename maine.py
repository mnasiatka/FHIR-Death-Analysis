import csv,string
from operator import itemgetter

class Stay:
    def __init__(self,subject_id,hadm_id,sequence,code):
        self.subject_id = subject_id
        self.hadm_id = hadm_id
        self.sequence = sequence
        self.code = code

numOverOne = 0
maxValue = 0
maxStays = -1
s = ""
occurancesDict = {}
subj_ICDs = {}
maxConditions = []
todayString = 'Nov 15 2015'

with open('ICD9.csv','rb') as ICD9file:
    ICD9reader = csv.reader(ICD9file)
    headerRow = True
    while True:
        try:
            row = ICD9reader.next()
            subject_id = row[0]
            hadm_id = row[1]
            sequence = row[2]
            code = row[3]
            try: # If subject has been seen before
                subj_ICDs[subject_id] # If subject has been seen before
                try:
                    subj_ICDs[subject_id][hadm_id] # If we're on the same hospital stay as the previous line
                    subj_ICDs[subject_id][hadm_id].append((sequence,code)) # Add stay info onto currently appending hospital stay
                except:
                    subj_ICDs[subject_id][hadm_id] = [todayString, (sequence,code)] # Else first hospital admit Id for this already seen subject
            except:
                subj_ICDs[subject_id] = {} # New subject, initialize dict at that key
                subj_ICDs[subject_id][hadm_id] = [todayString, (sequence,code)] # Then initialize hospital stay data for the new subject
        except:
            break

print 'Total subjects: ' + str(len(subj_ICDs))
for subject_stays in subj_ICDs:
    maxStays = max(len(subject_stays),maxStays)
print 'Most hospital stays: ' + str(maxStays)

with open('hospID-DATE.csv','rb') as hospfile:
    hosp_reader = csv.reader(hospfile)
    while True:
        try:
            row = hosp_reader.next()
            hadm_id = row[0]
            date = row[1]
            dateSplit = string.split(date, '/')
            month = int(dateSplit[0])
            if month in [1,3,5,7,8,10,12]:
                month = month * 31
            elif month in [4,6,9,11]:
                month = month * 30
            else:
                month = month * 28
            day = int(dateSplit[1])
            year = int(dateSplit[2]) * 365
            date = year + month + day
            for subj_id in subj_ICDs:
                if hadm_id in subj_ICDs[subj_id]:
                    subj_ICDs[subj_id][hadm_id][0] = date
        except:
            break

# For every subject that we have visiting the hospital
for subject_stays in subj_ICDs:
    if len(subj_ICDs[subject_stays]) > 1: # If they have more than 1 stay we can use their data
        numOverOne += 1 # Find how many we're visiting
        prevConditions = [] # Reset previous conditions since is a new patient
        patientStaysUnsorted = []
        patientStaysSorted = []
        # Sort the stays of this patient
        for hosp_stay in subj_ICDs[subject_stays]: # for each hospital stay
            curStay = subj_ICDs[subject_stays][hosp_stay] # Get the date and diagnoses
            patientStaysUnsorted.append(curStay)
        patientStaysSorted = patientStaysUnsorted
        for i in range(len(patientStaysSorted) - 1):
            for j in range(i+1,len(patientStaysSorted)):
                if patientStaysSorted[i] > patientStaysSorted[j]:
                    temp = patientStaysSorted[i]
                    patientStaysSorted[i] = patientStaysSorted[j]
                    patientStaysSorted[j] = temp
        for hosp_stay in subj_ICDs[subject_stays]: # For each hospital stay this patient has had
            curStay = subj_ICDs[subject_stays][hosp_stay] # Get the date and diagnoses
            newConditions = [] # Get ready to find what new/ongoing conditions they were diagonsed with this time
            iterableConditions = curStay[1:] # We just want data here
            for rank, condition in iterableConditions: # Diagnosis is in form (rank,condition)
                newConditions.append(condition) # Add the current condition to his list of new conditions
                # TODO Constrain comparisons to n-highest ranked conditions
                # TODO Compare to next n visits
                for prevCondition in prevConditions: # Pair this new condition with every other previous condition
                    if not prevCondition == condition: # As long as it's not the same condition
                        conditionKey = prevCondition + "->" + condition # Key is in form A->B, where A and B are the previous and new conditions, respectively
                        if conditionKey in occurancesDict: # If this progression has been seen before, increment its count
                            occurancesDict[conditionKey] += 1
                        else: # Otherwise add it to the dictionary with initial count of 1
                            occurancesDict[conditionKey] = 1
            prevConditions = newConditions # For the next visit, these new conditions will be the previous ones

print str(numOverOne) + " people have more than 1 stay"
print str(len(occurancesDict)) + ' items in dictionary'

#TODO get n-most frequent progressions
#TODO learn to sort excel by column
with open('output.csv','wb') as outputCSV:
    outputWriter = csv.writer(outputCSV)
    for key in occurancesDict:
        value = occurancesDict[key]
        initial, final = string.split(key,'->')
        outputWriter.writerow([initial, final, value])