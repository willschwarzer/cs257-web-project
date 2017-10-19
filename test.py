import datasource

x = ["SEX","","AGE", "RACE"]
db = datasource.DataSource()
db.getQueryFromWebsite(x)
y = db.getDataArray()
db.createGraph()
print (y)