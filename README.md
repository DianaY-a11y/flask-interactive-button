# Diana's CS50 Final Project

This app allows a user to send SMS messages to phone numbers. There are a total of 7 templates. Apology.html is called when an user's input is insufficient and we want to ask them to write or do something else (I thought the finance apology was so cute!). Layout.html demonstrates a standardized layout for all pages, such as the navigation bar. Index.html is the homepage. It introduces the user to the purpose of the app with some simple UI designs. Login.html is where the user logs in. If the user doesn't have an account, she/he is directed to register.html, which can also then lead them to login. Once they've logged in, the user is led to message.html which allows them to send messages. They have to put in the recipient's phone number and the message that they want to send. Becuase of the nature of Button, there's a word limit of 30 characters (so emojis are encouraged). When one hovers over the button, it looks like it's been pressed. Then on click, a message is sent. If the user wants to see past messages, he/she can click on that tab in the navigation bar and all past messages and its recipients will be shown. 

To see my webapp, the person should first type in:
    /source venv/bin/activate
After (venv) shows up, then install dependencies: 
    pip3 install -r requirements.txt
Recreate the SQlite database
    python3 manage.py recreate_db
Then, run the manage script
    python3 manage.py runserver

After running these lines, you can open localhost:5000 on chrome, safari, another web browser too look at my webapp. By opening the webapp, it leads you to index.html, and then you can choose to register or signup. Afterwards, all the features and functions of the webapp wouold be in the navigation bar and with detailed descriptions above. 