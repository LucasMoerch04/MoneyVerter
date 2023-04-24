#This program called "MoneyVerter" uses an API url from APIlayer.com to convert up to 162 currencies. 
#The GUI has been made with CustomTkinter and picture of valutagraph has been made with pandas, PIL and matplotlib.

#Imports necessary modules
from tkinter import *
import customtkinter as CTk
import requests
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from currencies import valutalist_full
from PIL import Image

#Creates window, dynamic size and title
root = CTk.CTk()
width= root.winfo_screenwidth()               
height= root.winfo_screenheight()               
root.geometry("%dx%d" % (width, height))
root.title("MoneyVerter")
root.resizable(1,1)

#Sets the theme to green
CTk.set_default_color_theme("green")

#Weighs gridparts
root.columnconfigure(4, weight=3)
root.rowconfigure(6, weight=0)

#Declares variables
valuta1 = StringVar()
valuta2 = StringVar()
amount_of_days = StringVar()
amount = IntVar()


#The top 20 most traded currencies according to blog.scopemarkets.com
valutalist = ["USD","EUR","JPY","GBP","AUD", "CAD","CHF", "CNY", "HKD", "NZD","TRY","SGD","BRL","ILS","LYD","GIP","KWD","BHD","OMR","JOD"]

#creates and position typable dropdown with default value set to EURO
valuta1_dropdown = CTk.CTkComboBox(root, values=valutalist,width=300,height=100,fg_color="#4ed464",font=("Roboto", 36, "bold"),dropdown_fg_color="#5f6e5d",dropdown_font=("Roboto",14,"bold"))
valuta1_dropdown.set("EUR")
valuta1_dropdown.grid(row=2,column=0,padx=50,pady=10,rowspan=1,sticky=W)

#creates and position typable dropdown with default value set to DOLLARS
valuta2_dropdown = CTk.CTkComboBox(root, values=valutalist,width=300,height=100,fg_color="#4ed464",font=("Roboto", 36, "bold"),dropdown_fg_color="#5f6e5d",dropdown_font=("Roboto",14,"bold"))
valuta2_dropdown.set("USD")
valuta2_dropdown.grid(row=2,column=1,padx=50,pady=10,rowspan=1)
    
#Function to set dropdowns to top 20 list or Full list
def full():
    global valuta2_dropdown
    global valuta1_dropdown
    #If switch is off, dropdowns contains top 20 list
    if check1.get() == 0:
        valutalisttop20 = valutalist
        valuta1_dropdown.configure(values=valutalisttop20)
        valuta2_dropdown.configure(values=valutalisttop20)
    #If switch is on, dropdowns contains Full list and makes size 2px smaller
    else: 
        valutalist = valutalist_full
        valuta1_dropdown.configure(values=valutalist,dropdown_font=("Roboto",12,"bold"))
        valuta2_dropdown.configure(values=valutalist,dropdown_font=("Roboto",12,"bold"))


#Creates and positions the entry where user puts the wished amount.
from_amount_entry = CTk.CTkEntry(root,justify=RIGHT,width=710,height=100,font=("Roboto", 30, "bold"),placeholder_text="Amount ")
from_amount_entry.grid(row=3,column=0,columnspan=2,padx=50,sticky=N)

#Creates and positions the entry where the result are shown. The entry is only readable, so that user can select and copy, but not write.
money_frame = CTk.CTkEntry(root,justify=RIGHT,width=710,height=100,font=("Roboto", 30, "bold"),placeholder_text="Result ")
money_frame.configure(state='readonly')
money_frame.grid(row=3,column=0,columnspan=2,padx=50)

#Creates and positions green frame around graph picture
frame = CTk.CTkFrame(root,height=480,width=644,border_width=2,border_color="#4ed464",fg_color="Dark Blue").grid(row=3,column=5,columnspan=1,padx=30)

#Creates and positions scrollable frame for statistics
stats = CTk.CTkScrollableFrame(root,height=100,width=474,fg_color="#2e302f",orientation=HORIZONTAL,scrollbar_button_color="#4ed464",)
stats.grid(row = 2,column=5,columnspan=1,pady=10,ipadx=100)

#Creates, sizes and positions titlelogo image
titlelogolabelimage = CTk.CTkImage(Image.open("logo.png"),size=(208,50))
titlelogolabel = CTk.CTkLabel(master=root,image=titlelogolabelimage,text="")
titlelogolabel.grid(row=1, column=0,pady=10,sticky=W,padx=20)



slider_amount = 10
def get_parameters():
    global currency
    global converted_currency
    global amount
    global amount_of_days
    global slider_amount 
    
    #Gets chosen values and inputs from user
    currency = valuta1_dropdown.get()
    converted_currency = valuta2_dropdown.get()
    amount = from_amount_entry.get()

    amount_of_days = slider_amount
    
    #Puts ERROR in results-entry if amount entry contains non-numbers or currencies not in the Full list
    if amount != "" and amount.isdigit() != True or currency not in valutalist_full or converted_currency not in valutalist_full:
        print("Error")
        money_frame.configure(state='normal')
        money_frame.delete(0,'end')
        money_frame.insert(0,"ERROR ") 
        money_frame.configure(text_color="Red")
        money_frame.configure(state='readonly')
        

#Function to retrieve data from API
def get_data(currency, converted_currency, amount_of_days,amount=1):
    global currency_history
    global rate_history_array
    
    #Gets today's date
    today = datetime.datetime.now()
    #Gets start date
    date_variable = (today - datetime.timedelta(days=1* int(amount_of_days)))
    
    #API from APILayer
    url = f'https://api.exchangerate.host/timeseries'
    #Gets currency data from chosen variables
    payload = {'base': currency,'amount':amount,'start_date':date_variable.date(),'end_date':today.date()}
    response = requests.get(url, params= payload)
    data = response.json()
    
    #Empty lists and dicts
    currency_history = {}
    rate_history_array = []
    
    #Matches rates and dates of currencies
    for item in data['rates']:
        current_date = item
        currency_rate = data['rates'][item][converted_currency]
        
        currency_history[current_date] = [currency_rate]
        rate_history_array.append(currency_rate)
        
    
    
    
    #Creates 2D Dataframe of data    
    pd_data = pd.DataFrame(currency_history).transpose()
    pd_data.columns= ['Rate']
    pd.set_option('display.max_rows', None)


#List of times for statistics label
timelist = ["1 day", "30 days", "90 days", "180 days","1 year","2 years","5 years", "10 years"]
#Function to get growth percentage currency-pairs over amounts of days
def get_percentage(currency="EUR", converted_currency="USD", amount_of_days="10",count = 0):
    previous_rate = rate_history_array[-1]
    current_rate = rate_history_array[0]
    percentage = ((current_rate-previous_rate)/previous_rate)*100
    
    global text_stats1
    global text_stats2
    global REDorGREEN
    
    #Creates time variable for label
    text_stats1 = timelist[count] + '\n'
    #Creates rounded percentage variable
    text_stats2 = str(round(percentage,3)) + "%"
    
    #If percentage is positve, then uses green font and adds a "+" symbol
    if text_stats2[0] != "-":
        REDorGREEN = "Green2"
        text_stats2 = "+" + text_stats2
    #If percentage is negative, then uses red font
    else:
        REDorGREEN = "Red"
      
#Function to swap the two selected valutas
def swap_valuta():
    #saves the two chosen valutas as variables
    x = valuta1_dropdown.get()
    y = valuta2_dropdown.get()
    
    #Sets dropdown values as opposite variables
    valuta1_dropdown.set(y)
    valuta2_dropdown.set(x)

#Function to convert currency with chosen amount
def convert_amount(amount,currency, converted_currency):
    global converted_amount
    
    #Calls get_data function
    get_data(currency, converted_currency, amount_of_days, amount)
    #Saves result rounded to 2 decimals
    result = str(round(rate_history_array[-1],2))
    #If amount entry is empty, then do nothing
    if from_amount_entry.get() == "":
        pass
    #Else show result in money_frame entry
    else:
        money_text = str(result + " " + converted_currency)
        money_frame.configure(state='normal')
        money_frame.delete(0,'end')
        money_frame.insert(0,money_text) 
        money_frame.configure(text_color="White")
        money_frame.configure(state='readonly')

#Function to get rates over time
def get_yearly_rates(amount=1,currency="EUR",converted_currency="USD",amount_of_days="365"):
    global text_statslabel
    #Clears statistics label
    for widget in stats.winfo_children():
            widget.destroy()
    
    #Declares variables for count, x-position and list
    count = 0
    xpos = 5
    list = [1,30,90,180,365,730,1826,3652]
    
    #For loop to get data, calculate percentage, create and positions label for each percentage/time label
    for i in list:
        amount_of_days=i
        xpos += 1
        get_data(currency, converted_currency,amount_of_days,amount)
        
        get_percentage(currency, converted_currency,amount_of_days,count=count)
        
        
        CTk.CTkLabel(master=stats,text=text_stats1,font=("Roboto", 18, "bold")).grid(row=2,column=xpos,padx=20)
        text_statslabel = CTk.CTkLabel(master=stats,text=text_stats2,text_color=REDorGREEN,font=("Roboto", 18, "bold"))
        text_statslabel.grid(row=3,column=xpos,padx=20)
        count +=1
    #Creates and positions label for statistics header
    stats_title = currency + "/" + converted_currency + " Historical growth"
    CTk.CTkLabel(root,text=stats_title,font=("Roboto", 24, "bold")).grid(row=1,column=5,sticky=S,ipady=20)
    
 
#Function to plot graph
def plot(currency="EUR", converted_currency="USD",amount_of_days=365):
    global imagelabel
    #Calls functions to get chosen parameters, calculate the date and clear existing plot image
    get_parameters()
    get_data(currency, converted_currency,amount_of_days, amount=1)
    clear()
    
    #If current rate is bigger than the chosen days amount's rate, then line of plot is green
    if rate_history_array[0] < rate_history_array[-1]:
        winloss = "#05f02c"
    #If current rate is less than the chosen days amount's rate, then line of plot is red
    else:
        winloss = "Red"
    
    #Creates the plot with chosen data
    fig, ax = plt.subplots(facecolor="#2e302f")
    ax.set_facecolor(color="#424543")
    ax.plot(rate_history_array,color=winloss)
    #customises colors and labels
    ax.set_title(f'Current rate for 1 {currency} to {converted_currency} is {rate_history_array[-1]}', color="white")
    ax.set_xlabel('Days', color="white")
    ax.set_ylabel(f'1 {currency} to {converted_currency}', color="white")
    ax.tick_params(labelcolor='white')
    #Saves plot as png
    im = plt.savefig("plot.png")
    #clears and closes plot to save memory
    plt.clf()
    plt.close
    
    #Opens and saven image of plot
    im = Image.open("plot.png")
    im.save("plot.png")
    
    #Creates and positions plot image with given size
    image = CTk.CTkImage(Image.open("plot.png"),size=(640,480))  
    imagelabel = CTk.CTkLabel(frame,image=image,text="")
    imagelabel.grid(row=3,column=5)

#Function to plot graph image depending on slider value and configure label text
def slider (event):
    value = round(days_slider.get())
    slider_amount= value
    slider_amountlabel.configure(text=slider_amount)
    slider_amountlabel.grid(row=5, column=5,)
    plot(currency,converted_currency,amount_of_days=value)

#Creates and positions slider, sets default value to 365, and bind mouse release to slider, so that it only runs function when mouse1 is released (Makes it lot less laggy)
days_slider = CTk.CTkSlider(root, from_=7, to=365,number_of_steps=358,width=600,button_color="#4ed464")
days_slider.set(365)
days_slider.bind("<ButtonRelease-1>",slider)
days_slider.grid(row=5,column=5,sticky=N)    
#Creates and positions day-counter label
slider_amountlabel = CTk.CTkLabel(root,text="365",font=("Roboto", 14))
slider_amountlabel.grid(row=5, column=5,sticky=N,pady=20)

#Creates and positions tabview with the labels Information og About
tab = CTk.CTkTabview(root,width=700,height=140,segmented_button_selected_color="#4ed464")
tab1=tab.add("Information")
tab2=tab.add("About")
tab.grid(column=0,row=3,padx=50,rowspan=4,columnspan=2,sticky=SW)
tab.grid_propagate(False)

#Information text
information_text = """Exchange rates are updated every hour.
Choose between a list of the top 20 traded currencies or a full list of 162 currencies.
The dropdowns are also typable for quicker use.
Use the slider to see a graph of an exchange rate's development the last 7 to 365 days.
                    """

#About text
about_text = """MoneyVerter is a project made by a group of students from NEXT Sukkertoppen Gymnasium. 
The program is a product made for the final Informatik project.
The students focused on the design and interaction, 
which meant that relevant theories, testing and sketching was used in the development of the GUI.
The exchange rates is received from an API on https://apilayer.com/marketplace/exchangerates_data-api
"""

#Insert Information or About text in tabview
information = CTk.CTkLabel(tab1,text=information_text,font=("Roboto",14),justify=LEFT)
information.grid()
about = CTk.CTkLabel(tab2,text=about_text,font=("Roboto",14),justify=LEFT)
about.grid()


#Function to clear image if one exists
def clear():
    try: 
        imagelabel.destroy()
    except:
        pass
    
#Calls functions to calculate rates and plot image of graph
get_yearly_rates()
plot()

#Creates and positions label and switch choose dropdown lists
label = CTk.CTkLabel(root,text="Top 20",width=20,height=20,font=("Roboto", 14,"bold"))
label.grid(column=1,row=1,sticky=SW,ipadx=150)
check1 = CTk.CTkSwitch(root,width=30,height=20,text= "All",font=("Roboto", 14,"bold"),command=full,onvalue=1,offvalue=0,fg_color="#4ed464",progress_color="darkgreen")
check1.grid(column=1,row=1,sticky=S)

#Opens, creates and positions button with a swap-icon image
swap_image = CTk.CTkImage(Image.open("swap.png"),size=(30,30))
swap_button = CTk.CTkButton(root,fg_color="#4ed464",image=swap_image,text="",width=40,height=40,command=lambda:[swap_valuta(),get_parameters(),get_yearly_rates(amount,currency,converted_currency,amount_of_days),convert_amount(amount,currency,converted_currency),plot(currency,converted_currency)]).grid(row=2,column=0,columnspan=2)

#Creates and positions convert-button
convert_button = CTk.CTkButton(root,fg_color="#4ed464", text = "Convert",font=("Roboto", 30, "bold"),width=710,height=60,command =lambda:[get_parameters(),get_yearly_rates(amount,currency,converted_currency,amount_of_days),convert_amount(amount,currency,converted_currency),plot(currency,converted_currency)])
convert_button.grid(row=3,column=0,columnspan=2,sticky=N,pady=115)

#Makes the moneyframe non-dynamic
money_frame.grid_propagate(False)

#Makes widgets able to move when changing window size
root.grid_propagate(True)

#Executes window
root.mainloop()