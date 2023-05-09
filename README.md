# BusyBeaver
A lightweight todolist app


to start, create the database


```
python
from app import app, db
app.app_context().push() 
db.create_all() 
```
