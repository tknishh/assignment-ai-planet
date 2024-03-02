import requests
import json
from tkinter import *
 
window = Tk()
 

window.title("Covid-19")
 

window.geometry('240x150')
 

t=Entry(window)
t.grid(row=0,column=1,columnspan=10,pady=10)   

lbl1 = Label(window)
lbl = Label(window)
lbl3 = Label(window)
lbl4 = Label(window) 
lbl2 = Label(window) 
lbl4.grid(column = 1, row = 1)
lbl1.grid(column = 1, row = 2)
lbl.grid(column = 1, row = 3)
lbl3.grid(column = 1, row = 4)
lbl2.grid(column = 1, row = 5)

def clicked():

    url = "https://api.covid19india.org/data.json"
    page = requests.get(url)

    data = json.loads(page.text)

    name=t.get()

    c =0;
    for i in range(38):
      if (str((data["statewise"][i]["state"]).lower().replace(" ","")) == str(name).lower().replace(" ","") or str((data["statewise"][i]["statecode"]).lower().replace(" ","")) == str(name).lower().replace(" ","")):


        lbl1.configure(text ="Total Confirmed cases :- "
                       + data["statewise"][i]["confirmed"])

        lbl.configure(text ="Total active cases :- "
                      + data["statewise"][i]["active"])
         

        lbl3.configure(text ="Total deaths :- "
                       + data["statewise"][i]["deaths"])

        lbl4.configure(text ="State :- "
                       + data["statewise"][i]["state"]) 

        lbl2.configure(text ="Data Refreshed")
        c=1

    if c==0 :

      lbl.configure(text ="Total active cases :- 0")
         
      lbl1.configure(text ="Total Confirmed cases :- 0")

      lbl3.configure(text ="Total deaths :- 0")

      lbl4.configure(text ="State :- Enter valid state")
       
      lbl2.configure(text ="NO Data Found")

 
btn = Button(window, text ="Search", command = clicked)
btn.grid(column = 13, row = 0)

window.mainloop()