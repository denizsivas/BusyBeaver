# Busy Beaver
![BusyBadger.png](static%2Fimg%2FBusyBadger.png)

# What is it?
A lightweight personal assistance tool built on Flask framework.

It tracks your,
 * to-dos
 * reminders
 * bookmarks
 * notes
 * statistics
 * weather information

# How to start?
1. Create the databases with below commands

```
python
from app import app, db
app.app_context().push() 
db.create_all() 
```
2. Create your .env

The content for your dot env should be the following:
   * secret_key
   * weatherapi
   * lat_home
   * lon_home
   * lat_work
   * lon_work
   * api_key
      
3. Upload your files to a server
4. app.py is your main app so make sure it runs first with your setup
5. Have fun using your assistant

