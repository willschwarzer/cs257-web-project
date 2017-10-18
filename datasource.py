import psycopg2
import numpy as np
import seaborn as sns; sns.set()
import matplotlib.pyplot as plt
import pandas as pd

class DataSource:

    def __init__(self):
        #self.getQueryFromWebsite(websiteQuery)
        self.connection = psycopg2.connect("dbname=mannesn user=mannesn")
        self.initializeCursor()
    
     # Future pandas objects
    theDataFrame = None
    theSeries = None
    
    # Future data array
    dataArray = []

    
    #TODO: error check this super hard
    def getQueryFromWebsite(self, websiteQuery):
        self.primary = websiteQuery[0]
        self.secondary = websiteQuery[1]
        self.control1 = ""
        self.control2 = ""
    
    #TODO, make dataframe work with control variable(s)
    #this is basically the only thing that will get called
    def dataFrame(self):
        self.dictQuery = self.getDictionary()
        #if self.control2 != "":
         #   return self.getDictionary()
        #elif self.control1 != "":
        #    return self.getDictionary()
        if self.secondary != "":
            return self.dictionaryToArrayTwoVariables()
        else:
            return self.dictionaryToArrayOneVariable()
    
    def initializeCursor(self):
        self.cursor = self.connection.cursor()
          
    def query(self):
        self.setCursor()
        self.cursor.fetchone()
        return self.cursor.fetchall()
        
    def getNPArray(self):
        self.dataArray = np.asArray(self.query())
    
    def getDictionary(self):
        responses = self.query()
        dict = {}
        for response in responses:
            dict.setdefault(response, "dummy value")
            if dict[response] == "dummy value":
                dict[response] = 1
            else:
                dict[response] = dict[response] + 1
        self.dictQuery = dict
        return dict
                   
    def getOrderedVariables(self, varName):
        varNP = np.load("orders.npy")
        varDict = varNP.item()
        varList = varDict[varName]
        vars = []
        if self.isCategorical(varName):
            for x in varList:
                temp = x[1]
                temp = temp.replace('"', '')
                vars.append(temp)
            return self.removeExtraVariables(vars, varDict)[::-1]
        else:
            return self.getVarKeys(varName)
            
    def getVarKeys(self, varName):  
        vars = []
        keys = sorted(self.dictQuery.keys())
        if varName == self.primary:
            for k in keys:
                vars.append(k[0])
        elif varName == self.secondary:
            for k in keys:
                vars.append(k[1])
        elif varName == self.control1:
             for k in keys:
                vars.append(k[2])
        else:
            for k in keys:
                vars.append(k[3])
        return vars
        
    def isCategorical(self, varName):
        vars = []
        keys = sorted(self.dictQuery.keys())
        if varName == self.primary:
            for k in keys:
                vars.append(k[0])
        elif varName == self.secondary:
            for k in keys:
                vars.append(k[1])
        elif varName == self.control1:
             for k in keys:
                vars.append(k[2])
        else:
            for k in keys:
                vars.append(k[3])

        for key in vars:
            if not key[0].isdigit():
                return True
        return False
    
    def fetchCountOneVariable(self, dict, row):
        listOfKeys = dict.keys()
        x = 0
        for key in listOfKeys:
            if row in key:
                x += dict[key]
        return x
    
    def fetchCountTwoVariables(self, dict, row, column):
        listOfKeys = dict.keys()
        x = 0
        for key in listOfKeys:
            if row in key and column in key:
                x += dict[key]
        return x
        
    
    def isInKeys(self, dict, s):
        keys = dict.keys()
        for key in keys:
            if s in key:
                return False
        return True
    
    #some variable queries have variables we don't want to crosstab
    def removeExtraVariables(self, l, dict):
        newList = []
        badNames = ["IAP", "UNCODEABLE & IAP", "UNCODEABLE"]
        for x in l:
            if self.isInKeys(dict, x) and x not in badNames:
                newList.append(x)
        return newList
                
    def dictionaryToArrayOneVariable(self):
        orderedRow = self.getOrderedVariables(self.primary)
        values = []
        for response in orderedRow:
            values.append(self.dictQuery[response])
        returnArray = []
        returnArray.append(orderedRow)
        returnArray.append(values)
        self.dataArray = array
        return returnArray 
                   
    def dictionaryToArrayTwoVariables(self):
        orderedRow = self.getOrderedVariables(self.primary)
        orderedColumn = self.getOrderedVariables(self.secondary)
        array = []
        array.append([""] + orderedColumn)
        for rowvar in orderedRow:
            nextRow = []
            nextRow.append(rowvar)
            for column in orderedColumn:
               nextRow.append(self.fetchCountTwoVariables(self.dictQuery, rowvar, column))
            array.append(nextRow)
        self.dataArray = array
        return array
        
    def dictionaryToArrayOneControl(self):
        return self.query()
        
    def dictionaryToArrayTwoControls(self):
        return self.query()
       
    def setCursor(self):
        if self.control2 != "":
            self.queryTwoVariablesTwoControls()
        elif self.control1 != "":
            self.queryTwoVariablesOneControl()
        elif self.secondary != "":
            self.queryTwoVariables()
        else:
            self.queryOneVariable()
                
                               
    def queryOneVariable(self):
        query = "SELECT %s FROM gssdata WHERE %s IS NOT NULL;" % (self.primary, self.primary)
        self.cursor.execute(query)
      
    def queryTwoVariables(self):
        query = "SELECT %s, %s FROM gssdata WHERE %s IS NOT NULL AND %s IS NOT NULL"
        query = query % (self.primary, self.secondary, self.primary, self.secondary)
        self.cursor.execute(query)
             
    def queryTwoVariablesOneControl(self):
        query = "SELECT %s, %s, %s FROM gssdata WHERE %s"
        query +=" IS NOT NULL AND %s IS NOT NULL AND %s IS NOT NULL;"
        query = query % (self.primary, self.secondary, self.control1,
        self.primary, self.secondary, self.control1)
        self.cursor.execute(query)
        
    def queryTwoVariablesTwoControls(self):
        query = "SELECT %s, %s, %s, %s FROM gssdata WHERE %s"
        query +=" IS NOT NULL AND %s IS NOT NULL AND %s IS NOT NULL AND %s IS NOT NULL;"
        query = query % (self.primary, self.secondary, self.control1, self.control2,
        self.primary, self.secondary, self.control1, self.control2)
        self.cursor.execute(query)

    def getGraph(self):
        dataType = self.getDataType(self.dataArray)
        if dataType == "single-categorical":
            self.getBarPlot(self.dataArray)
        elif dataType == "single-continuous":
            self.getDistPlot(self.dataArray)
        elif dataType == "categorical-categorical":
            self.getHeatMap(self.dataArray)
        else:
            raise ValueError("This data type not yet implemented!")

        # TODO add remaining graph types
        # elif dataType == "categorical-continuous":
        #     self.getLinePlot(self.dataArray)
        # elif dataType == "continuous-categorical":
        #     self.getAverageBarPlot(self.dataArray)
        # elif dataType == "continuous-continuous":
        #     self.getScatterPlot(self.dataArray)
        # return

    def categoricalArrayToDataFrame(self, array):
        '''Converts a 2D array (list of lists) of categorical objects
         to a 2D pandas DataFrame'''
        # By convention in the rest of the code, the first row is the primary
        # labels, the first column is the secondary labels, and the rest is the
        # count of responses with each pair of values
        data = [row[1:] for row in array[1:]]
        rowHeaders = [row[0] for row in array[1:]]
        columnHeaders = array[0][1:]
        name = self.primary
        theDataFrame = pd.DataFrame(data = data,
                                    index = rowHeaders,
                                    columns = columnHeaders,)
        return theDataFrame

    def categoricalArrayToSeries(self, array):
        '''Converts a 2-element list of lists (i.e. for a single variable
        query) to a 1D pandas Series, where the data is categorical'''
        # By convention in the rest of the code, the first row is the value
        # labels, and the second row is the numbers of responses for each value
        name = self.primary
        values = array[0]
        counts = array[1]
        theSeries = pd.Series(data=counts, index=values, name=name)
        return theSeries

    def continuousArrayToSeries(self, array):
        '''Converts a 2-element list of lists (i.e. for a single variable
        query) to a 1D pandas Series, where the data is continuous'''
        name = self.primary
        values = []
        for i in range(len(array)+1):
            for j in range(int(array[1][i])):
                values.append(int(array[0][i]))
        theSeries = pd.Series(data = values, index = values, name = name)
        return theSeries

    def getHeatMap(self, theDataFrame):
        '''Creates a heatmap for two categorical variable queries'''
        f, ax = plt.subplots(figsize=(9, 6))
        self.theDataFrame = self.arrayToDataFrame(self.dataArray)
        plot = sns.heatmap(self.theDataFrame, annot=True, fmt="d", linewidths=.5, ax=ax, cmap="Blues")
        picture = plot.get_figure()
        picture.savefig("output.png")
        return

    def getDistPlot(self, array):
        '''Creates a seaborn-style distplot (similar to a histogram) for
        single continuous variable queries'''
        self.theDataSeries=self.continuousArrayToSeries(array)
        f, plot = plt.subplots(figsize=(9, 6))
        plot = sns.distplot(self.theDataSeries)
        picture = plot.get_figure()
        picture.savefig("output.png")
        return

    def getBarPlot(self, array):
        '''Creates a bar plot for single categorical variable queries'''
        f, plot = plt.subplots(figsize=(9, 6))
        plot = sns.barplot(array[0], array[1])
        picture = plot.get_figure()
        picture.savefig("output.png")

    def getDataType(self, array):
        if len(array) == 2:
            if array[0][0].isdigit():
                return "single-continuous"
            else:
                return "single-categorical"
        else:
            if array[0][1].isdigit():
                if array[1][0].isdigit():
                    return "continuous-continuous"
                else:
                    return "continuous-categorical"
            else:
                if array[1][0].isdigit():
                    return "categorical-continuous"
                else:
                    return "categorical-categorical"

    def getStats(self, array):
        return
        
x = ["SEX","CONFINAN","AGE", "RACE"]
db = DataSource()
db.getQueryFromWebsite(x)
y = db.dataFrame()
dataSource.getGraph(y)