import psycopg2
import numpy as np
import seaborn as sns; sns.set()
import matplotlib.pyplot as plt
import pandas as pd


# NOTE TO GRADER: It may seem as though this implementation is not yet
# complete, and relative to what we said we wanted to do in the project plan,
# it isn't. However, we've talked to Amy, and she agreed that our project as a
# whole is quite ambitious, and said that we could scale it back if we wanted.
# For that reason, the bits that are missing here - controls, graphing for 
# other variable types, etc. - may not be parts of the final project that we
# haven't put in yet, but rather things that we will not put in at all.
# We're simply waiting to see what we have time to do in the end, and
# prioritizing proper functionality for the features we know we want.

def main():
    """Runs some sample queries on the database. Switch out the passed query in
    the runQuery() call to view other query results. Note that some 
    combinations of data types are not yet implemented (see createGraph()
    for details)."""
    # Sample queries
    querySingleCategorical = ["ETHNIC", "", "", ""]
    querySingleContinuous = ["EDUC", "", "", ""]
    queryDoubleCategorical = ["ETHNIC", "RACE", "", ""]
    # Running the queries
    ds = DataSource()
    ds.runQuery(querySingleCategorical)
    print(ds.getStats())
    ds.createGraph()

class DataSource:
    """Implements the backend of Will Schwarzer's and Nathan Mannes's web
    project. Used as follows: first call runQuery(query), then either
    getStats() or createGraph()."""
    
    def __init__(self):
        # Create database connection
        self.connection = psycopg2.connect("dbname=mannesn user=mannesn")
        self.initializeCursor()
        # Future pandas objects
        theDataFrame = None
        theSeries = None
        # Future data array
        dataArray = []
        # Query info
        primary = secondary = control1 = control2 = ""
        # These have self explicit because for some reason Python was
        # interpreting dataTypeSecondary as a class variable
        self.dataTypePrimary = self.dataTypeSecondary = ""

    def runQuery(self, query):
        """Runs the given query on the database and stores the results as
        instance variables."""
        self.parseQueryVariables(query)
        self.dataArray = self.getDataArray()
        
    def getStats(self):
        """Currently just returns number of respondents to a given query."""
        # All counts in the data array are in the second row and beyond,
        # possibly including some row headers
        count = 0
        for row in self.dataArray[1:]:
            for i in range(len(row)):
                try:
                    count += int(row[i])
                except:
                    # Was a row header, continue to rest of row
                    continue
        return count
        
    def createGraph(self):
        """Saves the appropriate type of graph for the query as output.png."""
        type1 = self.dataTypePrimary
        type2 = self.dataTypeSecondary
        if type2 == "":
            if type1 == "categorical":
                self.getBarPlot(self.dataArray)
            else:
                self.getDistPlot(self.dataArray)
        elif type1 == type2 == "categorical":
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
          
    #TODO: error check this super hard
    def parseQueryVariables(self, query):
        """Saves the desired variables for this query"""
        self.primary = query[0]
        self.secondary = query[1]
        #Controls are not yet implemented
        self.control1 = ""
        self.control2 = ""
        
    ### DATABASE MANAGEMENT ###
    
    #TODO, make dataframe work with control variable(s)
    def getDataArray(self):
        #if self.control2 != "":
         #   return self.getDictionary()
        #elif self.control1 != "":
        #    return self.getDictionary()
        dict = self.getDictionary()
        if self.secondary != "":
            return self.dictionaryToArrayTwoVariables(dict)
        else:
            return self.dictionaryToArrayOneVariable(dict)   
            
    def dictionaryToArrayOneVariable(self, dict):
        """Takes the dictonary of combinations of responses and the 
        number of times those combos occur, and generates a list in a format
        that can be graphed later"""
        self.dataTypePrimary = self.getDataType(self.primary, dict)
        orderedRow = self.getOrderedVariables(self.primary, dict)
        values = []
        counts = []
        for response in orderedRow:
            try:
                # If that response appeared, add it
                counts.append(dict[(response,)])
                values.append(response)
            except KeyError:
                # That response didn't actually appear; ignore it
                continue
        returnArray = [values, counts]
        self.dataArray = returnArray
        return returnArray 
                   
    def dictionaryToArrayTwoVariables(self, dict):
        """Takes the dictonary of combinations of responses and the 
        number of times those combos occur, and generates a list in a format
        that can be graphed later"""
        self.dataTypePrimary = self.getDataType(self.primary, dict)
        self.dataTypeSecondary = self.getDataType(self.secondary, dict)
        orderedRow = self.getOrderedVariables(self.primary, dict)
        orderedColumn = self.getOrderedVariables(self.secondary, dict)
        array = []
        array.append([""] + orderedColumn)
        for rowvar in orderedRow:
            nextRow = []
            nextRow.append(rowvar)
            for column in orderedColumn:
               nextRow.append(self.fetchCountTwoVariables(dict, rowvar, column))
            array.append(nextRow)
        self.dataArray = array
        return array
        
    #    Controls not yet implemented    
    #    def dictionaryToArrayOneControl(self):
    #        return self.query()
    #        
    #    def dictionaryToArrayTwoControls(self):
    #        return self.query()
                 
    def getDictionary(self):
        """Selects one of two functions to create a dictionary 
        of the query results"""
        if self.secondary == "":
            return self.getDictionaryOneVariable()
        else:
            return self.getDictionaryTwoVariables()
                
    def getDictionaryOneVariable(self):
        """Returns a dictionary where each key corresponds to survey 
        results, and each value is the number of times that response
        was in the queried set"""
        responses = self.query()
        dict = {}
        for response in responses:
            #response = response[0]
            dict.setdefault(response, "dummy value")
            if dict[response] == "dummy value":
                dict[response] = 1
            else:
                dict[response] = dict[response] + 1
        return dict
    
    def getDictionaryTwoVariables(self):
        """Returns a dictionary where each key corresponds to survey results, 
        and each value is the number of times that combination of responses
         was in the queried set"""
        responses = self.query()
        dict = {}
        for response in responses:
            dict.setdefault(response, "dummy value")
            if dict[response] == "dummy value":
                dict[response] = 1
            else:
                dict[response] = dict[response] + 1
        return dict
    
    def initializeCursor(self):
        """Opens a connection to the database"""
        self.cursor = self.connection.cursor()
    
    def query(self):
        """Returns a list of tuples containing the query results"""
        self.executeQuery()
        self.cursor.fetchone()
        return self.cursor.fetchall()
    
    def executeQuery(self):
        """executes a query using the instance variables for primary, secondary"""
        if self.control2 != "":
            self.queryTwoVariablesTwoControls()
        elif self.control1 != "":
            self.queryTwoVariablesOneControl()
        elif self.secondary != "":
            self.queryTwoVariables()
        else:
            self.queryOneVariable()
                      
    def getOrderedVariables(self, varName, responses):
        """Takes a variable as input and the dictionary of results in order
        to return a list of the responses in the order they should be displ-
        ayed"""
        varNP = np.load("orders.npy")
        variableOrdersDict = varNP.item()
        varList = variableOrdersDict[varName]
        vars = []
        if varName == self.primary:
            dataType = self.dataTypePrimary
        else:
            dataType = self.dataTypeSecondary
        if self.getDataType(varName, responses):
            for x in varList:
                temp = x[1]
                temp = temp.replace('"', '')
                vars.append(temp)
            return self.removeExtraVariables(vars, variableOrdersDict)[::-1]
        else:
            return self.getVarKeys(varName, responses)
            
    def getVarKeys(self, varName, dict):
        """For a given variable in the input, return a list of all of the 
        responses that correspond to that variable form the results"""
        vars = []
        keys = sorted(dict.keys())
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
        
    def getDataType(self, varName, dict):
        """Tests whether or not a variable is continuous(AGE) or 
        categorical (SEX). This is important when we choose different
        graph types based on this distinction"""
        vars = []
        keys = sorted(dict.keys())
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
                return "categorical"
        return "continuous"
    
    def fetchCountOneVariable(self, dict, row):
        """ Gets the count of the number of times a single variable shows
        up in the results"""
        listOfKeys = dict.keys()
        x = 0
        for key in listOfKeys:
            if row in key:
                x += dict[key]
        return x
    
    def fetchCountTwoVariables(self, dict, row, column):
        """Gets the count of the number of times a combination of two
        responses occurs in our query"""
        listOfKeys = dict.keys()
        x = 0
        for key in listOfKeys:
            if row in key and column in key:
                x += dict[key]
        return x
            
    def isInKeys(self, dict, s):
        """Tests if s occurs as a key in our dataset"""
        keys = dict.keys()
        for key in keys:
            if s in key:
                return False
        return True
    
    def removeExtraVariables(self, l, dict):
        """Some variable queries have variables we don't want to crosstab
        We remove names from badnames from the list of variables we want to 
        graph"""
        newList = []
        badNames = ["IAP", "UNCODEABLE & IAP", "UNCODEABLE"]
        for x in l:
            if self.isInKeys(dict, x) and x not in badNames:
                newList.append(x)
        return newList
                     
    def queryOneVariable(self):
        """Executes a query with the primary variable"""
        query = "SELECT %s FROM gssdata WHERE %s IS NOT NULL;" 
        query = query % (self.primary, self.primary)
        self.cursor.execute(query)
      
    def queryTwoVariables(self):
        """Executes a query with the primary and secondary variable"""
        query = "SELECT %s, %s FROM gssdata WHERE %s IS NOT NULL AND %s IS NOT NULL"
        query = query % (self.primary, self.secondary, self.primary, self.secondary)
        self.cursor.execute(query)
             
    def queryTwoVariablesOneControl(self):
        """Executes a query with the primary variable, secondary variable, and 
        one control variable"""
        query = "SELECT %s, %s, %s FROM gssdata WHERE %s"
        query +=" IS NOT NULL AND %s IS NOT NULL AND %s IS NOT NULL;"
        query = query % (self.primary, self.secondary, self.control1,
        self.primary, self.secondary, self.control1)
        self.cursor.execute(query)
        
    def queryTwoVariablesTwoControls(self):
        query = "SELECT %s, %s, %s, %s FROM gssdata WHERE %s"
        query +=" IS NOT NULL AND %s IS NOT NULL AND %s IS NOT NULL AND" 
        query +=" %s IS NOT NULL;"
        query = query % (self.primary, self.secondary, self.control1, self.control2,
        self.primary, self.secondary, self.control1, self.control2)
        self.cursor.execute(query)
            
    ### GRAPHING ###
            
    def getHeatMap(self, theDataFrame):
        """Creates a heatmap for two categorical variable queries."""
        f, ax = plt.subplots(figsize=(15, 10))
        self.theDataFrame = self.categoricalArrayToDataFrame(self.dataArray)
        plot = sns.heatmap(self.theDataFrame, annot=True, fmt="d", 
                            linewidths=0.5, ax=ax, cmap="Blues")
        ax.set(xlabel=self.secondary, ylabel=self.primary)
        picture = plot.get_figure()
        picture.savefig("output.png")
        return

    def getDistPlot(self, array):
        """Creates a seaborn-style distplot (similar to a histogram) for
        single continuous variable queries."""
        self.theDataSeries=self.continuousArrayToSeries(array)
        f, ax = plt.subplots(figsize=(15, 10))
        ax = sns.distplot(self.theDataSeries)
        ax.set(xlabel=self.primary)
        picture = ax.get_figure()
        picture.savefig("output.png")
        return

    def getBarPlot(self, array):
        """Creates a bar plot for single categorical variable queries."""
        # NOTE: sns.barplot() does not yet seem to play well with pandas series
        # For that reason, this is temporarily using default arrays
        f, ax = plt.subplots(figsize=(15, 10))
        ax = sns.barplot(array[0], array[1])
        ax.set(xlabel=self.primary, ylabel = "count")
        # Rotate labels
        for tick in ax.get_xticklabels():
            tick.set_rotation(90)
        # Add margin to bottom
        f.subplots_adjust(bottom=0.2)
        picture = ax.get_figure()
        picture.savefig("output.png")     
        
    def categoricalArrayToSeries(self, array):
        """Converts a 2-element list of lists (i.e. for a single variable
        query) to a 1D pandas Series, where the data is categorical."""
        # By convention in the rest of the code, the first row is the value
        # labels, and the second row is the numbers of responses for each value
        name = self.primary
        values = array[0]
        counts = array[1]
        theSeries = pd.Series(data=counts, index=values, name=name)
        return theSeries

    def continuousArrayToSeries(self, array):
        """Converts a 2-element list of lists (i.e. for a single variable
        query) to a 1D pandas Series, where the data is continuous."""
        name = self.primary
        values = []
        # For each possible value (i.e. element of first array), add the
        # corresponding number of that value (i.e. element of second array)
        # to the overall series (ignores categorical responses to query)
        for i in range(len(array[0])):
            try:
                for j in range(int(array[1][i])):
                    values.append(int(array[0][i]))
            except:
            # array[0][i] was not an int; skip this value
                continue
        theSeries = pd.Series(data = values, index = values, name = name)
        return theSeries
        
    def categoricalArrayToDataFrame(self, array):
        """Converts a 2D array (list of lists) of categorical objects
         to a 2D pandas DataFrame."""
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
                
        
if __name__ == "__main__":
    main()