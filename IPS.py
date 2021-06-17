import tkinter
import random
from tkinter.filedialog import askopenfilename
import matplotlib
import shapefile as shp
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from functools import partial
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import math
import pandas as pd
import glob
from osgeo import ogr
from simpledbf import Dbf5
from tkinter import *
import tkinter.ttk as ttk
import sys
import shutil
from osgeo import ogr
import numpy as np
import scipy.spatial
import win32com.shell.shell as shell
import win32event
import functools
#import keyboard
import datetime


#Function to prompt open file window
def fileopen():
	# show an "Open" dialog box and return the path to the selected file
    filename = askopenfilename()
    Shapefile(filename)


#Load shape file
def Shapefile(filename):
    global sf
    sf = shp.Reader(filename)
    for shape in sf.shapeRecords():
        x = [i[0] for i in shape.shape.points[:]]
        y = [i[1] for i in shape.shape.points[:]]
        plot.plot(x,y)
    plt.show()
    canvas.draw_idle()
    filename = filename[:-4]
    read_file= Dbf5(filename+".dbf")
    Path_file= read_file.to_dataframe()
    #print(Path_file)
    Path_file=Path_file['prb1'].tolist()
    #print(Path_file)
    #print(Path_file[0])
    for i in Path_file:
        uploadedPath.append(i)

def askVersion():
    global version_var, master_new
    master_new = tkinter.Toplevel(window)
    master_new.geometry('350x300')
    version_var = tkinter.Variable()
    label_version = Label(master_new, text = 'ENTER QGIS VERSION:', font = ('bold', 16)).place(x = 60, y = 60)
    entry_version = Entry(master_new, textvariable = version_var).place(x = 60, y = 100)
    close_version_window = tkinter.Button(master_new, text = 'SUBMIT', command = openQgis).place(x = 60, y = 140)

#Open QGIS button func
def openQgis():
    global open1
    '''open1=1
    #master_new.quit()
    #master_new.destroy()
    command  = r"qgis %F"
    #os.system(command)
    displayData()
    #askVersion()'''



    master_new.quit()
    master_new.destroy()
    version_value = version_var.get()
    #print ('version', version_value)
    qgis_path_str = r"C:\Program Files\QGIS "+version_value+r"\bin\qgis-bin.exe"
    #root_path = os.path.dirname(os.path.abspath('ips12.py'))
    se_ret = shell.ShellExecuteEx(fMask=0x140, lpFile= r"{}".format(qgis_path_str), nShow=1)
    win32event.WaitForSingleObject(se_ret['hProcess'], -1)
    open1=1
    #print ("Display")
    displayData()


def Refresh():
    global tree
    plot.cla()
    canvas.draw_idle()
    tree.destroy()
    tree=ttk.Treeview(window)
    displayData()

#
def openImage():
    global my_label
    imagename = askopenfilename()
    #list_of_files = glob.glob('Data/*.png') # * means all if need specific format then *.csv
    #imagename = max(list_of_files, key=os.path.getmtime)
    #print (latest_file)
    img = ImageTk.PhotoImage(Image.open(imagename))
    my_label = tkinter.Label(image=img)
    my_label.image=img
    my_label.place(x = 60,y = 100)


#Enlarge a Beat
def openBeat(id,s=None):
    global plot1,figure1,canvas1

    canvas.get_tk_widget().destroy()
    figure1 = Figure()
    plot1 = figure1.add_subplot(1, 1, 1)
    canvas1 = FigureCanvasTkAgg(figure1, window)
    canvas1.get_tk_widget().place(x=60,y=60)
    #plotting the graphical axes where map ploting will be done
    ax = plt.axes()
    ax.set_aspect('equal')
    #storing the id number to be worked upon
    #print(sf)
    shape_ex = sf.shape(id)
    #print(shape_ex)
    x_lon = np.zeros((len(shape_ex.points),1))
    y_lat = np.zeros((len(shape_ex.points),1))
    for ip in range(len(shape_ex.points)):
        x_lon[ip] = shape_ex.points[ip][0]
        y_lat[ip] = shape_ex.points[ip][1]

    #print(x_lon,y_lat)
    plot1.plot(x_lon,y_lat)
    #print(plot1)

    #plt.show()
    #canvas1.draw_idle()
    #plt.plot(x_lon,y_lat)
    x0 = np.mean(x_lon)
    y0 = np.mean(y_lat)
    plt.text(x0, y0, s, fontsize=10)

    #plot1.plot(list[0], list[1],color="red", marker="o", linestyle="")
    #plt.xlim(shape_ex.bbox[0],shape_ex.bbox[2])
    return x0, y0


#
def my_upd(my_widget):
     my_w = my_widget.widget
     #print(my_w)
     index = my_w.selection()[0]
     index = int(index[-1])
     index -= 1
     #print (index)
     #value = my_w.get(index)
     beat = result.loc[1,'Beat']
     #print(index, beat)
     openBeat(index,beat)


#Function to display all data
def displayData():
    global result,sf,xcoords,ycoords, col_score, checkboxes, checkboxes_values,LayerName,index_xcoord,index_ycoord
    list_of_files = glob.glob('*.gpkg')
    imagename = max(list_of_files, key=os.path.getmtime)
    source = ogr.Open(imagename,update=False)
    drv = ogr.GetDriverByName( 'ESRI Shapefile' )
    LayerName=''
    for i in source:
        LayerName = i.GetName()
        inlyr = source.GetLayer( LayerName )
        outds = drv.CreateDataSource(LayerName + '.shp')
        outlyr = outds.CopyLayer(inlyr,LayerName)
    del inlyr,outlyr,outds
    filename= LayerName + '.shp'
    sf = shp.Reader(filename)
    for shape in sf.shapeRecords():
    	x = [i[0] for i in shape.shape.points[:]]
    	y = [i[1] for i in shape.shape.points[:]]
    	plot.plot(x,y,color="#0DEEEA")
    plt.show()
    canvas.draw_idle()
    #print(sf)
    #yscrollbar = Scrollbar(window)
    #yscrollbar.pack(side=RIGHT, fill=Y)
    read_dbf= Dbf5(LayerName+".dbf")
    result= read_dbf.to_dataframe()
    result= result.T.drop_duplicates().T
    result.drop(result.columns[0:2], axis=1, inplace=True)
    counter= len(result)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('expand_frame_repr', False)

    OBJECTIDAS = np.arange(len(result))
    last_index = len(result.columns)
    result.insert(last_index, 'OBJECTIDAS',OBJECTIDAS)

    index_xcoord = result.columns.get_loc('xcoord')
    index_ycoord = result.columns.get_loc('ycoord')
    ycoords = result.iloc[:, index_ycoord].values
    xcoords = result.iloc[:, index_xcoord].values
    #print(xcoords)

    cols= result.columns.values
    #newWindow()
    '''col_score = []
    checkboxes_values = []
    for i in range(len(cols)):
    	#print (scores[i].get())
    	#colname = str(cols[i])
    	col_score.append(scores[i].get())
    	#print ("test check", checkboxes[i].get())
    	checkboxes_values.append(checkboxes[i].get())'''

    #print (col_score)
    #print (checkboxes_values)
    if os.path.isfile(LayerName+'filepath.txt'):
        #print(LayerName+'filepath.txt')
            #f = open("filepath.txt", "r")
            #criticalities= f.readlines()
        criticalities=[]
        with open(LayerName+'filepath.txt') as f:
            for line in f:
                #line=line[:-2]
                criticalities.append(line)
            criticalities.pop(0)
            #print(criticalities)
            result['criticality'] =[float(i) for i in criticalities]

    else:
        newWindow()
        col_score = []
        checkboxes_values = []
        for i in range(len(cols)):
    	#print (scores[i].get())
    	#colname = str(cols[i])
    	    col_score.append(scores[i].get())
    	#print ("test check", checkboxes[i].get())
    	    checkboxes_values.append(checkboxes[i].get())
        result['criticality'] = computeCost()
        #result['criticality'] =np.random.uniform(low=0.0, high=12.0, size=len(result))
        result['criticality'].to_csv(LayerName+'filepath.txt', sep=' ', index=False)
    #result['criticality'] =np.random.uniform(low=0.0, high=12.0, size=len(result))

    cols = result.columns.values
    tree["columns"]= (cols)
    tree['show'] = 'headings'
    for x in range(len(cols)):
    	s= str(cols[x])
    	tree.column(x, width = 140, minwidth = 150, stretch = True)
    	tree.heading(x, text= cols[x])
    	for i in range(counter):
    		tree.insert('', i, values=result.iloc[i,:].tolist())
    tree.pack(expand = Y)
    tree.place(x=60, y=565)


#Fucntion performed on clicking the map
def onclick(event):
    global i, num_points
    x=event.xdata
    y=event.ydata
    i=i+1
    num_points += 1
    w = shp.Writer('Points/point'+LayerName+str(i)+'.shp',shp.POINT)
    w.field('name', 'C')
    w.record('point1')
    w.point(x,y)
    w.close()
    plotpoint()

def distance_check_window():
    new_window = tkinter.Toplevel(window)
    new_window.geometry('300x300')
    displayText = Message(new_window, text="WARNING!\n\nThe distance you have entered is less than the distance between the points.",font=14)
    displayText.place(x = 50, y = 50)
    Button(new_window, text='OK',width=17,bg='bisque2',fg='black',activebackground="SlateGray1", command=new_window.destroy).place(x=50,y=170)


#Function to get the closest centroid of a point
def getCentroid(x_point, y_point):
    global combined_centroid_array
    combined_centroid_array = np.dstack([xcoords, ycoords])[0]
    #print ("Combined centroid array")
    #print (combined_centroid_array)
    mytree = scipy.spatial.cKDTree(combined_centroid_array)
    dist, indexes = mytree.query((x_point, y_point))

    #print(combined_centroid_array)
	#result.round(4)
    #print ("dist ", dist)
    #print ("indexes ", indexes)
    #print ("Coordinates of centroid are: ", combined_centroid_array[indexes])
    objectid = result.query("xcoord == {} and ycoord == {}".format(combined_centroid_array[indexes][0], combined_centroid_array[indexes][1]))['OBJECTIDAS'].values
    #print ("Object id", objectid[0])
    #print('centrois test',combined_centroid_array[indexes], objectid[0])
    return combined_centroid_array[indexes], objectid[0]

#Function to get 8 neighbours of a point
def get8Neighbours(x, y):
    neighbours = np.array((getCentroid(x-1010, y)[0], getCentroid(x-1010, y+1010)[0], getCentroid(x, y+1010)[0], getCentroid(x+1010, y+1010)[0], getCentroid(x+1010, y)[0], getCentroid(x+1010, y-1010)[0], getCentroid(x, y-1010)[0], getCentroid(x-1010, y-1010)[0]))
    neighbours_id = np.array((getCentroid(x-1010, y)[1], getCentroid(x-1010, y+1010)[1], getCentroid(x, y+1010)[1], getCentroid(x+1010, y+1010)[1], getCentroid(x+1010, y)[1], getCentroid(x+1010, y-1010)[1], getCentroid(x, y-1010)[1], getCentroid(x-1010, y-1010)[1]))
    return neighbours,neighbours_id

#plotting the points clicked on the map
def plotpoint():
    global gridcounter,pathcounter,s,d, d1, d2, topv, entry_1, entry_2, label_2, arr_expo, pathcounter10, condis
    sf1 = shp.Reader('Points/point'+LayerName+str(i)+'.shp')
    for shape in sf1.shapeRecords():
    	x = [i[0] for i in shape.shape.points[:]]
    	y = [i[1] for i in shape.shape.points[:]]
    	plot.plot(x,y,color="red", marker="o", linestyle="")
    canvas.draw()
	#arr = []
    ans = getCentroid(x[0], y[0])[1]

    #print(x)
    #print(ans)
    topv = top_var.get()
    #arr.append(ans)
    if topv == 1 and v == 1:

        #global entry_1
        #global label_2
        #global entry_2
        #print('Consider-different')
        if num_points == 1:
            arr_expo = []
            s = ans
            pathcounter10 = pathcounter/2
            entry_1 = Label(window, text = ans, bg = '#00CED1').place(x = 1255, y = 217)
            #entry_1.configure()

        if num_points == 2:
            d1 = ans
            pathcounter /= 2
            pathcounter-=2
            pathCoordinates(s,d1)
            arr_expo.extend(path)
            destination3= result.loc[result['OBJECTIDAS']==d1,'xcoord':'ycoord'].values
            source3= result.loc[result['OBJECTIDAS']==s,'xcoord':'ycoord'].values

            condis=pathcounter10-2
            #print(condis)

        if num_points == 3:
            d2 = ans
            #pathCoordinates(d1, d2
            destination1= result.loc[result['OBJECTIDAS']==d2,'xcoord':'ycoord'].values
            source1= result.loc[result['OBJECTIDAS']==d1,'xcoord':'ycoord'].values
            dist1=math.sqrt((destination1[0][0] - source1[0][0])**2 + (destination1[0][1] - source1[0][1])**2)/1010
            #print(dist1)
            condis=condis+dist1
            #print(condis)
        if num_points == 4:
            d = ans
            entry_2 = Label(window, text = ans, bg = '#00CED1').place(x = 1255, y = 242)
            #entry_2.configure(bg = '#48D1CC')
            pathcounter = 2*pathcounter10-condis+2
            destination2= result.loc[result['OBJECTIDAS']==d,'xcoord':'ycoord'].values
            destination1= result.loc[result['OBJECTIDAS']==d2,'xcoord':'ycoord'].values
            if (math.sqrt((destination2[0][0] - destination1[0][0])**2 + (destination2[0][1] - destination1[0][1])**2)/1010 > (2*pathcounter10-condis+2)):
                distance_check_window()
                pathcounter=0
                s=0
                d=0
            else:
                pathCoordinates(d2,d)
                arr_expo.extend(path)
                #print ('path outside', arr_expo)
                expoGrowth(arr_expo)


    if topv == 1 and v == 2:
        #global entry_1
        #global label_2
        #global entry_2
        #entry_1.destroy()
        #print('Consider-same')
        if num_points == 1:
            arr_expo = []

            #entry_2.destroy()
            s = ans
            pathcounter10 = pathcounter/2
            entry1 = Label(window, text = ans, bg = '#00CED1').place(x = 1255, y = 217)
            #entry1.configure(bg = '#48D1CC')
        if num_points == 2:
            d1 = ans
            pathcounter /= 2
            pathCoordinates(s,d1)
            arr_expo.extend(path)
        if num_points == 3:
            d2 = ans
            #pathCoordinates(d1, d2)
            pathcounter = pathcounter10
            pathCoordinates(d2, s)
            arr_expo.extend(path)
            #print ('path outside', arr_expo)
            expoGrowth(arr_expo)

    if topv==2 and v==1:
        gridcounter = gridcounter+1
        #print("free-different")
        if gridcounter%2==1:
            s=ans
            entry_1 = Label(window,text=ans, bg = '#00CED1')
            entry_1.place(x=1255,y=217)
        #    try:
        #        entry_2
        #        entry_2.destroy()
            #except UnboundLocalError:
            #     print ("x doesn't exist")
            #get8Neighbours(x[0],y[0])
        else:
            d=ans
            entry_2 = Label(window,text=ans, bg = '#00CED1')
            entry_2.place(x=1255,y=242)
            #get8Neighbours(x[0],y[0])
            #print(count)

            destination= result.loc[result['OBJECTIDAS']==d,'xcoord':'ycoord'].values
            source= result.loc[result['OBJECTIDAS']==s,'xcoord':'ycoord'].values
            #print((destination[0][0] - source[0][0])**2 + (destination[0][1] - source[0][1])**2)
            if (math.sqrt((destination[0][0] - source[0][0])**2 + (destination[0][1] - source[0][1])**2)>=int(x4.get())):
                distance_check_window()
                pathcounter=0
                s=0
                d=0

            else:
                if(count==1):

                    pathCoordinates(s,d)
                    expoGrowth(path)
                else:

                    latLong()




    elif topv==2 and v==2:
        #print("free-same")
        gridcounter=1
        s=ans
        gridcounter = gridcounter+1
        entry1=Label(window,text=ans, bg = '#00CED1')
        entry1.place(x=1255,y=217)
        sameSource(s)
        #sget8Neighbours(x[0],y[0])


#Don't the coordinates of the path
def pathCoordinates(s,d):
    global pathcounter, topv, path
    #print(s,d)
    path=[]
    pathcoord=[]
    #print('pathcounter', pathcounter)
    destination= result.loc[result['OBJECTIDAS']==d,'xcoord':'ycoord'].values
    source= result.loc[result['OBJECTIDAS']==s,'xcoord':'ycoord'].values
    current = s
    #if v==2:
    #    pathcounter=pathcounter/2
    #print("pathcounter", pathcounter)
    remaining_dist = int(((math.sqrt((destination[0][0] - source[0][0])**2 + (destination[0][1] - source[0][1])**2)))/1010)
    excess=pathcounter-remaining_dist
    while(excess>1):
        #print("hello")
        current_dist=[]
        closest_grid=[]
        path.append(current)
        current_coord= result.loc[result['OBJECTIDAS']==current,'xcoord':'ycoord'].values
        pathcoord.append(current_coord)
        neighbours= get8Neighbours(current_coord[0][0],current_coord[0][1])[1]
        for i in range(8):
            current_dist.append(result.loc[result['OBJECTIDAS']==neighbours[i],'xcoord':'ycoord'].values)
        current_dist = np.array(current_dist)
        current_dist=current_dist.reshape((8,2))
        #print(current_dist)
        for i in range(5):
            mytree2 = scipy.spatial.cKDTree(current_dist)
            dist, indexes = mytree2.query((destination[0][0],destination[0][1]))
            objectid = result.query("xcoord == {} and ycoord == {}".format(current_dist[indexes][0], current_dist[indexes][1]))['OBJECTIDAS'].values

            current_dist[indexes][0]=math.inf
            current_dist[indexes][1]=math.inf
            closest_grid.append(objectid)
        closest_grid = np.array(closest_grid).reshape(5,)
        #print("Closest Grid ,", closest_grid)
                #result['criticality'] = ['1' if result['OBJECTID'] == current]


        closest_values = result.loc[result['OBJECTIDAS'].isin(closest_grid)].values
        #print(closest_values)
        current_index=np.argmax([_[result.columns.get_loc("criticality")] for _ in closest_values])

        current=closest_values[current_index][result.columns.get_loc("OBJECTIDAS")]

        base = np.random.uniform(low=0.6, high=0.9, size=1)
        score=result.loc[result['OBJECTIDAS']==current,'criticality']
        #print(base)
        if current not in path and result.loc[result['OBJECTIDAS']==current,'criticality'].item()>0:
            result.loc[result['OBJECTIDAS']==current,'criticality']=math.log(score,base) if math.log(score,base)>=-15 else -15
        elif current not in path and result.loc[result['OBJECTIDAS']==current,'criticality'].item()==0:
            result.loc[result['OBJECTIDAS']==current,'criticality']-=3

            #print("hello")
        #print(result.loc[result['OBJECTID']==current,'criticality'])
        #print(current)
        if(current==d):
            continue
        #print(current)
        pathcounter=pathcounter-1

        remaining_dist = int(((math.sqrt((destination[0][0] - closest_values[current_index][-4])**2 + (destination[0][1] - closest_values[current_index][-3])**2)))/1010)
        excess=pathcounter-remaining_dist
        #print(pathcounter,remaining_dist,excess)
        #sget8Neighbours(x[0],y[0])'''


#Don't the coordinates of the path
def pathCoordinates(s,d):
    global pathcounter, topv, path
    #print(s,d)
    path=[]
    pathcoord=[]
    #print('pathcounter', pathcounter)
    destination= result.loc[result['OBJECTIDAS']==d,'xcoord':'ycoord'].values
    source= result.loc[result['OBJECTIDAS']==s,'xcoord':'ycoord'].values
    current = s
    #if v==2:
    #    pathcounter=pathcounter/2
    #print("pathcounter", pathcounter)
    remaining_dist = int(((math.sqrt((destination[0][0] - source[0][0])**2 + (destination[0][1] - source[0][1])**2)))/1010)
    excess=pathcounter-remaining_dist
    while(excess>1):
        #print("hello")
        current_dist=[]
        closest_grid=[]
        path.append(current)
        current_coord= result.loc[result['OBJECTIDAS']==current,'xcoord':'ycoord'].values
        pathcoord.append(current_coord)
        neighbours= get8Neighbours(current_coord[0][0],current_coord[0][1])[1]
        for i in range(8):
            current_dist.append(result.loc[result['OBJECTIDAS']==neighbours[i],'xcoord':'ycoord'].values)
        current_dist = np.array(current_dist)
        current_dist=current_dist.reshape((8,2))
        #print(current_dist)
        for i in range(5):
            mytree2 = scipy.spatial.cKDTree(current_dist)
            dist, indexes = mytree2.query((destination[0][0],destination[0][1]))
            objectid = result.query("xcoord == {} and ycoord == {}".format(current_dist[indexes][0], current_dist[indexes][1]))['OBJECTIDAS'].values

            current_dist[indexes][0]=math.inf
            current_dist[indexes][1]=math.inf
            closest_grid.append(objectid)
        closest_grid = np.array(closest_grid).reshape(5,)
        #print("Closest Grid ,", closest_grid)
                #result['criticality'] = ['1' if result['OBJECTID'] == current]


        closest_values = result.loc[result['OBJECTIDAS'].isin(closest_grid)].values
        #print(closest_values)
        current_index=np.argmax([_[result.columns.get_loc("criticality")] for _ in closest_values])

        current=closest_values[current_index][result.columns.get_loc("OBJECTIDAS")]

        base = np.random.uniform(low=0.6, high=0.9, size=1)
        score=result.loc[result['OBJECTIDAS']==current,'criticality']
        #print(base)
        if current not in path and result.loc[result['OBJECTIDAS']==current,'criticality'].item()>0:
            result.loc[result['OBJECTIDAS']==current,'criticality']=math.log(score,base) if math.log(score,base)>=-15 else -15
        elif current not in path and result.loc[result['OBJECTIDAS']==current,'criticality'].item()==0:
            result.loc[result['OBJECTIDAS']==current,'criticality']-=3

            #print("hello")
        #print(result.loc[result['OBJECTID']==current,'criticality'])
        #print(current)
        if(current==d):
            continue
        #print(current)
        pathcounter=pathcounter-1

        remaining_dist = int(((math.sqrt((destination[0][0] - closest_values[current_index][-4])**2 + (destination[0][1] - closest_values[current_index][-3])**2)))/1010)
        excess=pathcounter-remaining_dist
        #print(pathcounter,remaining_dist,excess)


    while(current!=d):
        current_dist=[]
        closest_grid=[]
        path.append(current)
        current_coord= result.loc[result['OBJECTIDAS']==current,'xcoord':'ycoord'].values
        pathcoord.append(current_coord)
        neighbours= get8Neighbours(current_coord[0][0],current_coord[0][1])[1]
        for i in range(8):
            current_dist.append(result.loc[result['OBJECTIDAS']==neighbours[i],'xcoord':'ycoord'].values)

        current_dist = np.array(current_dist)
        current_dist=current_dist.reshape((8,2))

        mytree2 = scipy.spatial.cKDTree(current_dist)
        dist, indexes = mytree2.query((destination[0][0],destination[0][1]))
        objectid = result.query("xcoord == {} and ycoord == {}".format(current_dist[indexes][0], current_dist[indexes][1]))['OBJECTIDAS'].values

        remaining_dist = int(((math.sqrt((destination[0][0] -current_dist[indexes][0])**2 + (destination[0][1] -current_dist[indexes][1])**2)))/1010)
        excess=pathcounter-remaining_dist
        pathcounter=pathcounter-1
        #print(pathcounter,remaining_dist,excess)
        current=objectid[0]
        base = np.random.uniform(low=0.6, high=0.9, size=1)
        score=result.loc[result['OBJECTIDAS']==current,'criticality']
        if current not in path and result.loc[result['OBJECTIDAS']==current,'criticality'].item()>0:
            result.loc[result['OBJECTIDAS']==current,'criticality']=math.log(score,base) if math.log(score,base)>=-15 else -15
        elif current not in path and result.loc[result['OBJECTIDAS']==current,'criticality'].item()==0:
            result.loc[result['OBJECTIDAS']==current,'criticality']-=3

    path.append(d)
    pathcoord.append(destination)
    pathcoord = np.array(pathcoord)
    #print(path)

    if topv==1:

        PathGenerate(pathcoord)
        #expoGrowth(path)
    elif topv==2 and v!=2:
        PathGenerate(pathcoord)
        #expoGrowth(path)

    elif v==2:
        return path,pathcoord




#Generation of Path
def PathGenerate(path_coordinates):
    w = shp.Writer('Points/line'+LayerName+str(i-1)+'.shp',shp.POLYLINE)
    w.line(path_coordinates)
    w.field('name', 'C')
    w.record('line1')
    #w.save()
    w.close()
    sf2 = shp.Reader('Points/line'+LayerName+str(i-1)+'.shp')
    for shape in sf2.shapeRecords():
        x = [i[0] for i in shape.shape.points[:]]
        y = [i[1] for i in shape.shape.points[:]]
        plot.plot(x,y,color="black")
    plt.show()
    canvas.draw_idle()
    canvas.draw()

#LatLong of the vulnerabilities
def latLong():
    global count,pathcounter,s,d,latlong1,k,source,distlatlong,distance
    pathcounter2= pathcounter/(k+1)
    distance=int(x4.get())
    destination= result.loc[result['OBJECTIDAS']==d,'xcoord':'ycoord'].values
    source= result.loc[result['OBJECTIDAS']==s,'xcoord':'ycoord'].values
    try:
        for i in range(k):
            pathcounter=pathcounter2
            #print("pathcounter", pathcounter)
            #latlong1.reshape(len(latlong1),2)
            mytree = scipy.spatial.cKDTree(latlong1)
            dist, index = mytree.query((source[0][0], source[0][1]))
            x_pt=latlong1[index][0]
            y_pt=latlong1[index][1]

            plot.plot(int(x_pt),int(y_pt),color="green", marker="o", linestyle="")
            canvas.draw()
            mid = getCentroid(int(x_pt),int(y_pt))[1]
            middist= result.loc[result['OBJECTIDAS']==mid,'xcoord':'ycoord'].values
            source= result.loc[result['OBJECTIDAS']==s,'xcoord':'ycoord'].values
            #print("hello1")

            if (math.sqrt((middist[0][0] - source[0][0])**2 + (middist[0][1] - source[0][1])**2)>=distance):
                print("hello1")

                raise distance_check
            distance-=math.sqrt((middist[0][0] - source[0][0])**2 + (middist[0][1] - source[0][1])**2)

            pathCoordinates(s,mid)
            s=mid
            source[0][0]=latlong1[index][0]
            source[0][1]=latlong1[index][1]
            latlong1[index][0]=math.inf
            latlong1[index][1]=math.inf
            result.loc[result['OBJECTIDAS']==mid,'criticality']=20
        pathcounter=pathcounter2

        x_pt=source[0][0]
        y_pt=source[0][1]
        mid = getCentroid(int(x_pt),int(y_pt))[1]
        middist= result.loc[result['OBJECTIDAS']==mid,'xcoord':'ycoord'].values
        destination= result.loc[result['OBJECTIDAS']==d,'xcoord':'ycoord'].values
        if (math.sqrt((middist[0][0] - destination[0][0])**2 + (middist[0][1] - destination[0][1])**2)>=distance):
            print("hello12")

            raise distance_check
        pathCoordinates(mid,d)
        expoGrowth(path)
    except distance_check:
        distance_check_window()
        pathcounter=0
        s=0
        d=0
        mid=0


    for i in tree1.get_children():
        tree1.delete(i)
    latlong1.clear()
    k=0
    count=1

def sameSource(s):
    global pathcounter
    pathcounter1=pathcounter/2
    current=s
    path=[]
    pathcoord=[]
    #print(s)
    while(pathcounter1>0):
        path.append(current)
        #print(current)
        current_coord = result.loc[result['OBJECTIDAS']==current,'xcoord':'ycoord'].values
        pathcoord.append(current_coord)
        neighbours_coord,neighbours= get8Neighbours(current_coord[0][0],current_coord[0][1])

        neighbour_values = result.loc[result['OBJECTIDAS'].isin(neighbours)].values
        current_index=np.argmax([_[result.columns.get_loc("criticality")] for _ in neighbour_values])
        current=neighbour_values[current_index][result.columns.get_loc("OBJECTIDAS")]
        pathcounter1=pathcounter1-1
        base = np.random.uniform(low=0.6, high=0.9, size=1)
        score=result.loc[result['OBJECTIDAS']==current,'criticality']
        print('score', score)
        if current not in path and result.loc[result['OBJECTIDAS']==current,'criticality'].item()>0:
            result.loc[result['OBJECTIDAS']==current,'criticality']=math.log(score,base) if math.log(score,base)>=-15 else -15
        elif current not in path and result.loc[result['OBJECTIDAS']==current,'criticality'].item()==0:
            result.loc[result['OBJECTIDAS']==current,'criticality']-=3
    #print(current)

    restPathcoord= pathCoordinates(current,s)[1]
    restPath= pathCoordinates(current,s)[0]

    pathcoord = np.array(pathcoord)

    pathcoord=np.concatenate([pathcoord,restPathcoord])
    path=np.concatenate([path,restPath])
    #pathcoord = np.dstack([pathcoord.reshape(len(pathcoord)[0],2),restPath])[0]
    #print(pathcoord)

    PathGenerate(pathcoord)
    expoGrowth(path)


#Function to compute cost of all grids
'''def computeCost():
	#print (result)
	extra =[0]
	cost = np.zeros([len(result), 1])
	for i, row in result.iterrows():
		#print ((row['water1']))
		cost[i] = (row['WATER'] * col_score['WATER']) + (row['FOREST'] * col_score['FOREST'])
		if (row['ROADWAYS'] == 1):
			extra.append(col_score['ROADWAYS'])
			cost[i] += col_score['ROADWAYS']
			continue
		if (row['RAILWAYS'] == 1):
			extra.append(col_score['RAILWAYS'])
			cost[i] += col_score['RAILWAYS']
			continue
		neighbours = get8Neighbours(row['xcoord'], row['ycoord'])[0]
		#print (neighbours)
		for k in range(8):
			new_neighbours = get8Neighbours(neighbours[k][0], neighbours[k][1])[0]
			for j in range(8):
				if ((any(result.query("xcoord == {} and ycoord == {}".format(new_neighbours[j][0], new_neighbours[j][1]))['ROADWAYS'].values)) == 1):
					extra.append(col_score['ROADWAYS'] - 0.5)
				if ((any(result.query("xcoord == {} and ycoord == {}".format(new_neighbours[j][0], new_neighbours[j][1]))['RAILWAYS'].values)) == 1):
					extra.append(col_score['RAILWAYS'] - 0.5)
			if ((any(result.query("xcoord == {} and ycoord == {}".format(neighbours[k][0], neighbours[k][1]))['ROADWAYS'].values)) == 1):
					extra.append(col_score['ROADWAYS'] - 0.25)
			if ((any(result.query("xcoord == {} and ycoord == {}".format(neighbours[k][0], neighbours[k][1]))['RAILWAYS'].values)) == 1):
					extra.append(col_score['RAILWAYS'] - 0.25)
		cost[i] += max(extra)

	return cost'''

def computeCost():

	cost = [0] * len(result)
	idx = 0
	#print ('x,y idx', index_xcoord, index_ycoord)
	for row in result.itertuples():
		extra = [0]
		#print (row)
		for i in range(0, len(result.columns)):
			if checkboxes_values[i] == 0 and col_score[i] != 0:
				#print (type(row[i]), type(col_score[i]), type(cost[idx]))
				cost[idx] += (float(row[i+1]) * col_score[i])
				#print('multi check', result.columns[i], float(row[i+1]), col_score[i])
				#exit()
			if checkboxes_values[i] == 1:
				if float(row[i+1]) > 0 and col_score[i] != 0:
					extra.append(col_score[i])

		#print (row[index_xcoord], row[index_ycoord])
		neighbours, neighbours_id = get8Neighbours(float(row[index_xcoord]), float(row[index_ycoord]))
		for k in range(8):
			new_neighbours = get8Neighbours(neighbours[k][0], neighbours[k][1])[1]
			for j in range(8):
				check_idx = result.loc[result['OBJECTIDAS'] == new_neighbours[j]]
				#print (row[-1], check_idx, new_neighbours[j])
				#print (type(check_idx))
				#print (*(check_idx.iloc[:,-1].values))
				#exit()
				for m in range(0, len(result.columns)):
					if checkboxes_values[m] == 1:
						if (check_idx.iloc[:,m].values)[0] > 0 and col_score[m] != 0:
							extra.append(col_score[m] - 0.5)

			check_idx = result.loc[result['OBJECTIDAS'] == neighbours_id[k]]
			for m in range(0, len(result.columns)):
				if checkboxes_values[m] == 1:
					if (check_idx.iloc[:,m].values)[0] > 0 and col_score[m] != 0:
						extra.append(col_score[m] - 0.25)

		cost[idx] += max(extra)
		#print ('cost check', cost[idx])
		idx += 1
	return cost



def expoGrowth(path):
    #print(path)
    #print(uploadedPath)
    list=result.loc[(result['OBJECTIDAS'].isin(path) == False) & (result['prb1'].isin(uploadedPath) == False)].index
    #print(list)
    #index=np.argmax([_[-1] for _ in list])
    a = np.random.uniform(low=-1.6, high=-1.3, size=1)
    for i in list:
        x=result.loc[result['OBJECTIDAS']==i,'criticality'].item()

        result.loc[result['OBJECTIDAS']==i,'criticality']=x*math.pow(1.03,result.loc[result['OBJECTIDAS']==i,'criticality'] ) if (x*math.pow(1.03,result.loc[result['OBJECTIDAS']==i,'criticality']))<=20 else 20
    print("Done")


#
def func(x1,x2,x3,x4,x5,x6,x7):
	n1= x1.get()
	n2=x2.get()
	#n3=x3.get()
	n4=x4.get()
	#n5=x5.get()
	n6=x6.get()
	n7=x7.get()
	#print("Starting point: "+n1)
	#print("Ending point: "+n2)
	#print("Time: "+n3)
	#print("Distance: "+n4)
	#print("Speed: "+n5)
	#print("Latitude: "+n6)
	#print("Longitude: "+n7)

def count1():
    global count
    global tablecount
    tablecount=tablecount+1
    coord=[]
    coord.append(int(x6.get()))
    coord.append(int(x7.get()))
    latlong1.append(coord)
    #print(latlong1)
    tree1.insert('', i, values=coord)
    count=0

def multiLatLong():
    global k
    k=len(tree1.get_children())

def pathCount():
    global pathcounter, num_points
    pathcounter= int(int(x4.get())/1010)
    #print(pathcounter)
    num_points = 0

def sel(var,x1,x2):
    global entry2,v
    v=var.get()

    entry2=Entry(window,textvariable=x1)

    if v==1:
        global entry_1
        global label_2
        global entry_2
        entry2.delete(0,'end')
        label_1 = Label(window, text="START POINT",font=(16))
        label_1.place(x=1100,y=217)
        label_1.configure(bg = '#48D1CC')
        label_2 = Label(window, text="END POINT",font=(16))
        label_2.place(x=1100,y=242)
        label_2.configure(bg = '#48D1CC')

    elif v==2:
        label2= Label(window, text="START POINT",font=(16))
        label2.place(x=1100,y=217)
        label2.configure(bg = '#48D1CC')
        label_2.destroy()

def check():
    topv = top_var.get()
    #print (topv)
def reset():
    for i in tree1.get_children():
        tree1.delete(i)
    
    latlong1.clear()
    k=0
    count=1

#Infornmation
def inputs():
    global x6,x7,x4,entry_4, top_var
    x1=StringVar()
    x2=StringVar()
    x3=StringVar()
    x4=StringVar()
    x5=StringVar()
    x6=StringVar()
    x7=StringVar()
    #c= Canvas(window,height=475,width=800, borderwidth = 10)
    #c.place(x=800,y=60)
    #.configure(background = '#00CED1')
    #label_0 = Label(window, text="Information",width=20,font=("bold", 20))
    #label_0.place(x=1000,y=66)

    top_label = Label(window, text="PATH INFORMATION",font=("bold", 17))
    top_label.place(x = 820, y = 70)
    top_label.configure(background = '#00CED1')

    top_var = IntVar()
    top_R1 = Radiobutton(window, text="CONSIDER PATROL PATH", font= (16), background = '#00CED1', activebackground = '#00CED1', highlightthickness = 0, variable= top_var, value=1, command = check)
    top_R1.place(x=850,y=110)
    #top_R1.configure(background = '#00CED1')
    top_R2 = Radiobutton(window, text="FREE PATH", font= (16), activebackground = '#00CED1', highlightthickness = 0, variable= top_var, value=2, command = check)
    top_R2.place(x=850,y=135)
    top_R2.configure(background = '#00CED1')

    l1 = Label(window, text="STARTING AND END POINTS",font=("bold", 17))
    l1.place(x=820,y=175)
    l1.configure(background = '#00CED1')


    var = IntVar()
    R1 = Radiobutton(window, text="DIFFERENT POINTS", font= (16), activebackground = '#00CED1', highlightthickness = 0, variable=var, value=1, command=lambda: sel(var,x1,x2))
    R1.place(x=850,y=215)
    R1.configure(background = '#00CED1')
    R2 = Radiobutton(window, text="SAME POINTS", font= (16), activebackground = '#00CED1', highlightthickness = 0, variable=var, value=2, command=lambda: sel(var,x1,x2))
    R2.place(x=850,y=240)
    R2.configure(background = '#00CED1')

    l2 = Label(window, text= "PATROL INFORMATION",font=("bold", 17))
    l2.place(x=820, y= 280)
    l2.configure(background = '#00CED1')

    #label_3 = Label(window, text="TIME",width=15,font=("bold", 14))
    #label_3.place(x=880,y=290)

    #entry_3=Entry(window,textvariable=x3)
    #entry_3.place(x=1040,y=290)

    label_4 = Label(window, text="DISTANCE",width=15,font=(16))
    label_4.place(x=850,y= 320)
    label_4.configure(background = '#00CED1')

    entry_4=Entry(window,textvariable=x4)
    entry_4.place(x=1000,y=320)

    Button(window, text='RECORD',width=17,bg='bisque2',fg='black',activebackground="SlateGray1", activeforeground='red', command=pathCount).place(x=1000,y=360)

    '''label_5 = Label(window, text="SPEED",width=15,font=("bold", 14))
    label_5.place(x=880,y=350)

    entry_5=Entry(window,textvariable=x5)
    entry_5.place(x=1040,y=350)'''

    l3 = Label(window, text="LATITUDE AND LONGITUDE",font=("bold", 17))
    l3.place(x=820,y=400)
    l3.configure(background = '#00CED1')

    label_6 = Label(window, text="LATITUDE",width=15,font=(16))
    label_6.place(x=850,y=440)
    label_6.configure(background = '#00CED1')

    entry_6=Entry(window,textvariable=x6, width = 20)
    entry_6.place(x=1000,y=440)

    label_7 = Label(window, text="LONGITUDE",width=15,font=(16))
    label_7.place(x=850,y=470)
    label_7.configure(background = '#00CED1')

    entry_7=Entry(window,textvariable=x7, width = 20)
    entry_7.place(x=1000,y=470)

    func1= partial(func,x1,x2,x3,x4,x5,x6,x7)

    Button(window, text='RECORD',width=17,bg='bisque2',fg='black',activebackground="SlateGray1", activeforeground='red', command=count1).place(x=1000,y=505)
    Button(window, text='INCLUDE IN PATH',width=17,bg='bisque2',fg='black',activebackground="SlateGray1", activeforeground='red', command=multiLatLong).place(x=1150,y=505)
    Button(window, text='RESET',width=17,bg='bisque2',fg='black',activebackground="SlateGray1", activeforeground='red', command=reset).place(x=1300,y=505)

	#for wid in c.winfo_children():
     #   wid.configure(foreground = 'paleturquoise3')


def populate(frame):
	global scores, checkboxes

	cols = result.columns
	labels = []
	frames = []
	scores = []
	checkboxes_list = []
	checkboxes = [0]*len(cols)
	values = {"-10" : "-10",
		      "-9" : "-9",
		      "-8" : "-8",
		      "-7" : "-7",
		      "-6" : "-6",
		      "-5" : "-5",
		      "-4" : "-4",
		      "-3" : "-3",
		      "-2" : "-2",
		      "-1" : "-1",
		      "0" : "0",
		      "1" : "1",
		      "2" : "2",
		      "3" : "3",
		      "4" : "4",
		      "5" : "5",
		      "6" : "6",
		      "7" : "7",
		      "8" : "8",
		      "9" : "9",
		      "10" : "10"
		       }

	for i in range(0, len(cols)):
		#labels.append(Label(master, text="{}".format(cols[i]), font=("bold", 14)))
		#labels[i].grid(row = 0, column = i, ipadx = 20, pady = (30, 2))
		checkboxes[i] = IntVar()
		checkboxes_list.append(Checkbutton(frame, text = '{}'.format(cols[i]), font = ('bold', 14), variable = checkboxes[i], onvalue = 1, offvalue = 0))
		checkboxes_list[i].grid(row = 0, column = i, ipadx = 20, pady = (30, 2))
		frames.append(Frame(frame))
		frames[i].grid(row = 1, column = i, rowspan = 21)
		scores.append(IntVar(frames[i]))
		#j = 1
		for (text, value) in values.items():
			Radiobutton(frames[i], text = text, variable = scores[i], value = value).grid(column = i, sticky = W, ipadx = 20)
			#scores.append(v.get())
			#j += 1

	Button(frame, text='SUBMIT',width=20,bg='snow',fg='black',activebackground="SlateGray1", activeforeground='red', command = submitCall).grid(columnspan = 3, pady = (50,20))

def onFrameConfigure(canvas):
    '''Reset the scroll region to encompass the inner frame'''
    canvas.configure(scrollregion=canvas.bbox("all"))

def newWindow():
	global master
	master = tkinter.Toplevel(window)
	canvas = Canvas(master, borderwidth = 0)
	frame = Frame(canvas)
	vsb = Scrollbar(master, orient = 'horizontal', command = canvas.xview)
	canvas.configure(xscrollcommand = vsb.set)
	vsb.pack(side = 'bottom', fill = 'x')
	canvas.pack(side="left", fill="both", expand=True)
	canvas.create_window((4,4), window=frame, anchor="nw")
	frame.bind("<Configure>", lambda event, canvas=canvas: onFrameConfigure(canvas))

	populate(frame)

	master.mainloop()


def submitCall():
	master.quit()
	master.destroy()
	#computeCost()

def saveData():
    #print(open1)
    if open1==0:
        window.destroy()
    elif open1 ==1:
        #print('exiting')
        os.remove(LayerName+'filepath.txt')
        result['criticality'].to_csv(LayerName+'filepath.txt', sep=' ', index=False)
        window.destroy()

def delRowLat(event = None):
    print ("Del pressed")
    try:
        selected_item = tree1.selection()[0]
        #print('selected item is', tree1.item(tree1.focus())['values'])
        latlong1.remove(tree1.item(tree1.focus())['values'])
        tree1.delete(selected_item)
        print(latlong1)
        print ("Item deleted")
    except:
        print ("Handled")

#Main code

window=tkinter.Tk()
window.state('zoomed')
window.title("IPS")
window.geometry('1400x900')
window.configure(background = '#00CED1')

window.bind('<Delete>', delRowLat)

tree= ttk.Treeview(window)
treeScrolldd = ttk.Scrollbar(window, orient ="vertical", command = tree.yview)
#treeScrolldd.place(x = 1353, y = 430, height = 66)
treeScrolldd.pack(side ='right', fill = 'y')
treeScrolldd.configure(command=tree.yview)
#tree.configure(yscrollcommand=treeScrolldd.set)

treeScrollddho = ttk.Scrollbar(window, orient ="horizontal", command = tree.xview)
#treeScrollddho.place(x = 1353, y = 430, height = 66)
treeScrollddho.pack(side ='bottom', fill = 'x')
treeScrollddho.configure(command=tree.xview)
tree.configure(xscrollcommand=treeScrollddho.set, yscrollcommand=treeScrolldd.set)



tree1= ttk.Treeview(window, selectmode = 'browse')
tree1["columns"]= ['LATITUDE', 'LONGITUDE']
tree1['show'] = 'headings'
treeScroll = ttk.Scrollbar(window, orient ="vertical", command = tree1.yview)
treeScroll.place(x = 1353, y = 430, height = 66)
#treeScroll.pack(side ='right')
treeScroll.configure(command=tree1.yview)
tree1.configure(yscrollcommand=treeScroll.set)
tree1['height'] = 2
tree1.column(0, width=100)
tree1.heading(0, text= 'LATITUDE')
tree1.column(1, width=100)
tree1.heading(1, text= 'LONGITUDE')
tree1.pack(side = 'left')
tree1.place(x=1150, y=430)

Label1=tkinter.Label(window, text = "INTELLIGENT PATROL SYSTEM")
figure = Figure()
plot = figure.add_subplot(1, 1, 1)
canvas = FigureCanvasTkAgg(figure, window)
canvas.get_tk_widget().place(x=60,y=60)
k=0
uploadedPath=[]
latlong1=[]
tablecount=0
shapeFile= tkinter.Button(window, text="UPLOAD SHAPEFILE", bg='bisque2', command = fileopen)
shapeFile.place(x = 130,y = 10)
shapeFile1= tkinter.Button(window, text="REFRESH", bg='bisque2', command = Refresh)
shapeFile1.place(x = 300,y = 10)
gridcounter=0
open1 = 0
i=0
num_points = 0
count=1
Qgis= tkinter.Button(window, text="OPEN QGIS", bg='bisque2', command = askVersion)
Qgis.place(x = 10,y = 10)

list = figure.canvas.mpl_connect('button_press_event', onclick)
inputs()
B = tkinter.Button(window, text ="CLOSE WINDOW", bg='bisque2', command = saveData)
B.place(x = 1250,y = 10)


window.mainloop()

