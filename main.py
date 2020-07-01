
import sys
from operator import itemgetter, attrgetter

#0 define standard note class
class Note:
	def __init__(self,m,x,p,t,d,s):
		self.measure=int(m)
		self.default_x=int(x)
		self.weight_x=0
		self.pitch=p
		self.pitch2=''
		self.type=t
		self.duration=int(d) if d != '' else 0
		self.staff=int(s)
		self.connect2=-1
		
		# becase the pitch name with # or b is different from played note, translate it to be the same
		# ex. A3# --> A#3  , A3b --> G#3
		down_scale_dict = {'C':'B','D':'C','E':'D','F':'E','G':'F','A':'G','B':'A'}
		if self.pitch[2:3]=='#':
			self.pitch2=self.pitch[0:1]+self.pitch[2:3]+self.pitch[1:2] 
		elif self.pitch[2:3] == 'b':
			self.pitch2=down_scale_dict[self.pitch[0:1]]+'#'+self.pitch[1:2]
		else:
			self.pitch2 = self.pitch		

	def __str__(self):
		return str(self.__dict__)

#1 define played note class	
class Note_p:
	def __init__(self,p,ont,offt,d,vel):
		self.pitch=p
		self.onsettime=float(ont)
		self.offsettime=float(offt)
		self.duration=float(d)
		self.velocity=int(vel)
		self.connect2=-1
		
	def __str__(self):
		return str(self.__dict__)


#2 read standard notes from file
f=open('1_Bach_WellTemperedClavier_Prelude_No.5_BWV846_Cmajor_全曲.csv')
#f=open('2_Bach_WellTemperedClavier_Prelude_No.5_BWV850_Dmajor_全曲.csv')
datalist = []
i=0
for line in f:
	# skip first line (the title) 
	if i==0:
		i+=1
		continue
	data = line.split(',')
	n=Note(*data)
	datalist.append(n)

#3 read played notes from file 
f=open('pio01_Bach1_S1_T1.csv')
#f=open('pio01_Bach2_S1_T1.csv')
datalist_p = []
i=0
for line in f:
	# skip first line (the title) 
	if i==0:
		i+=1
		continue
	data = line.split(',')
	n=Note_p(*data)
	datalist_p.append(n)


#4 sort standard notes by meausure and default_x
	# we knew the maximium of default_x is less than 500 in each measure.
	# , so we can use 500 as base multiply number to calculate the weight of x value.
	# Ex, measure 1 is (500*0)+x. measure 2 is (500*1)+x. meausre 3 is (500*2)+x, etc...
	# After that we can sort the list by the weighted x value. 
for n in datalist:
	n.weight_x = (n.measure-1)*500 + n.default_x
# do the sorting
datalist.sort(key=attrgetter('measure','default_x'))


#5 sort played notes by onset time
	# it is easy to do the sort just by onset time value	
datalist_p.sort(key=attrgetter('onsettime'))



#6 you can check notes now each by each. Basically sequence of pitches are almost aligned. 
# But you can find the played notes just miss one E4 in line 5.
# Next step, you need to insert a patch(E4) in the correct place in played notes.
#note 0: C4  note_p 0: C4  (same)
#note 1: E4  note_p 1: E4  (same)
#note 2: G4  note_p 2: G4  (same)
#note 3: C5  note_p 3: C5  (same)
#note 4: E5  note_p 4: E5  (same)
#note 5: E4  note_p 5: G4  (not same, miss E4) 
#note 6: G4  note_p 6: C5   
#note 7: C5  note_p 7: E5
#note 8: E5  note_p 8: C4
#note 9: C4  note_p 9: E4

#7 define compare fucntion
def compareNote(n1,n2):
	# rule 1: pitch must be the same.
	if n1.pitch2==n2.pitch:
		return True
		# rule 2: duration is in a acceptable range.
		# the range may not very accurate. need to adjust by certain situation.
		#if n1.duration == 64 and n2.duration < 1.5:
			#return True
		#elif n1.duration == 192 and (n2.duration < 5.0 and n2.duration > 0.8):
			#return True  
		#elif n1.duration == 256 and (n2.duration < 5.5 and n2.duration > 0.9):
			#return True
		#elif n1.duration == 512 and (n2.duration < 6.0 and n2.duration > 1.0):
			#return True  
		#elif n1.duration == 1024 and (n2.duration < 7.0 and n2.duration > 1.0):
			#return True 
	else:
		return False        
		#return False

def getPrevNode(current, hand):
	for i in range(current-1,-1,-1):
		if datalist[i].staff == hand:
			return datalist[i]
	return None

def findTie(index, node, prev_node):
	tie = getTieList(index, node.staff)
	if node.pitch in tie:
		print("skipping tie {} {} {}".format(i, node.pitch, node.staff))
		node.connect2 = prev_node.connect2
		datalist_m.append(datalist_p[node.connect2])
		return True
	return False

def getTieKey(index, hand):
	return "{}{}".format(index, hand)

tie_list = {}
def getTieList(index, hand):
	key = getTieKey(index, hand)
	if key not in tie_list:
		tie_list[key] = []
	return tie_list[key]

def addNode(index, node):
	tie = getTieList(index, node.staff)
	tie.append(node.pitch)

def switchTieList(node):
	last_key = getTieKey("last", node.staff)
	current_key = getTieKey("current", node.staff)
	tie_list[last_key] = getTieList("current", node.staff)
	tie_list[current_key] = []
	tie_list[current_key].append(node.pitch)


#8 start to comapre notes one on one
datalist_m = []
for i in range(len(datalist)):
	node = datalist[i]
	prev_node = getPrevNode(i, node.staff)
	if prev_node != None:
		if node.default_x == prev_node.default_x:
			if findTie("current", node, prev_node):
				continue
			addNode("current", node)
		else:
			switchTieList(node)
			if findTie("last", node, prev_node):
				continue

	for j in range(len(datalist_p)):
		# check if the note has been connected to 
		if datalist[i].connect2 == -1 and datalist_p[j].connect2 == -1:
			# compare the played note if we can find the same pitch within 0.3 seconds onset time.
			curOnsetTime = datalist_p[datalist[i-1].connect2 -1].onsettime if i >0 else 0
			print("{}({}) {} {} {}".format(i, node.measure, node.pitch, node.staff, curOnsetTime))
			k=j
			isFound=False
			while k<len(datalist_p) and (curOnsetTime == 0 or datalist_p[k].onsettime-curOnsetTime < 1.5 ):
            # Bach1 = 0.3, Bach 2 = 0.3,
				node_p = datalist_p[k]
				not_checked = datalist_p[k].connect2 == -1
				not_too_old = datalist_p[k].onsettime-curOnsetTime > -1 
				if not_checked and not_too_old:
					print("  checking {}({}) {}".format(node_p.pitch, k, node_p.onsettime))
				if not_checked and not_too_old and compareNote(datalist[i],datalist_p[k])==True:
					print("   Found!")
					# we found the same note. Add it to the datalist_m
					datalist[i].connect2=k+1
					datalist_p[k].connect2=i+1
					datalist_m.append(datalist_p[k])
					isFound=True
					break
				else:
					k+=1				
			
			if isFound==False:
				print("   note out of range {}", datalist_p[k].onsettime)
				# we cannot find the same note. Create a patch note and add to the datalist_m
				n = Note_p(datalist[i].pitch,0,0,0,0)
				datalist[i].connect2=datalist[i-1].connect2
				n.connect2=i+1
				datalist_m.append(n)

			break				

			
#9 write the result to a csv file
f = open("compare.csv", "w")
f.write('Standard Notes,,,,,,,,,Played Notes\n')
f.write('measure,default_x,weight_x,pitch,type,duration,staff,,,pitch,onset time,offset time, duration,velocity\n')
for i in range(len(datalist_m)):
	f.write(f'{datalist[i].measure:1d},{datalist[i].default_x:3d},{datalist[i].weight_x:4d},{datalist[i].pitch:3s},{datalist[i].type:3s},{datalist[i].duration:3d},{datalist[i].staff:1d}')
	f.write(f',,,')
	if datalist_m[i].duration==0:
		f.write(f'{datalist_m[i].pitch:3s}(patch),{datalist_m[i].onsettime:8.3f},{datalist_m[i].offsettime:8.3f},{datalist_m[i].duration:8.3f},{datalist_m[i].velocity:8.3f},\n')
	else:
		f.write(f'{datalist_m[i].pitch:3s},{datalist_m[i].onsettime:8.3f},{datalist_m[i].offsettime:8.3f},{datalist_m[i].duration:8.3f},{datalist_m[i].velocity:8.3f},\n')
f.close()

