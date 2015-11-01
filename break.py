#!/usr/bin/python
import webbrowser
import time

i=1
while i<=5:
    time.sleep(10)
    webbrowser.open("http://www.nytimes.com")
    i=i+1

