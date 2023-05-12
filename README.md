# BusyBeaver
![BusyBadger.png](static%2Fimg%2FBusyBadger.png)

A lightweight to-do list app


to start, create the database

```
python
from app import app, db
app.app_context().push() 
db.create_all() 
```
