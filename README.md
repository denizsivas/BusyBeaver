# Busy Beaver
![BusyBadger.png](static%2Fimg%2FBusyBadger.png)

# What is it?
A lightweight personal assistance tool built on Flask framework.

It tracks your,
 * to-dos
 * reminders
 * bookmarks
 * notes
 * statistics of productivity

# How to start?
1. Create the databases with below commands

```
python
from app import app, db
app.app_context().push() 
db.create_all() 
```
2. Upload your files to a server
3. app.py is your main app so make sure it runs first with your setup
4. Have fun using your assistant

