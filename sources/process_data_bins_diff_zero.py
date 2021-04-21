import pandas as pd
import math
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties
import csv
import sys
import optparse

def read_data(data):
	read_data = pd.read_csv(data, header=None)
	first_time_seen = read_data.iloc[1,0]
	time_column = (read_data.iloc[:,0] - first_time_seen) / 1000000
	pre_processed_data = read_data.drop(read_data.columns[0], axis=1)
	pre_processed_data.insert(0, "time", time_column, True)
	return pre_processed_data

def time_window_suddivision(pre_processed_data, period):
	time_suddivision = [0] * math.ceil(len(pre_processed_data))
	#pre alloco spazio di zeri grande quanto pre_processed_data
	count = 1
	#colonna originale dei tempi
	times = pre_processed_data['time']
	for x in times:
		#controllo se il tempo del campione x-esimo rientra nel mio periodo (p=15s) considerato
		if x <= count*period*1000:
			#se si vuol dire che, e.g., tra 0 e 15 devo incrementare ho visto un campione in piu
			time_suddivision[count-1] += 1
		else:
			#altrimenti il mio campione è nel periodo successivo
			time_suddivision[count] += 1
			count += 1
	#boh
	time_suddivision = [i for i in time_suddivision if i != 0]

	no_time_numpy = []
	no_time = pre_processed_data.loc[:, pre_processed_data.columns != 'time']
	no_time_numpy.append(no_time.to_numpy())
	time_suddivision.insert(0,0)
	cumulative = np.cumsum(time_suddivision)

	new_structure = []
	for x in range(time_suddivision[1]):
	    new_structure.append(no_time_numpy[0][x])
	    
	for index in range(1, len(cumulative)):
	    if index + 1 < len(cumulative):
	        for x in range(cumulative[index], cumulative[index+1]):
	            new_structure.append(no_time_numpy[0][x] - no_time_numpy[0][cumulative[index] - 1])
	counters = []

	#for x in range(len(new_structure)):
	for x in new_structure:
		counters.append(np.count_nonzero(x))

	return counters

def sample_window_suddivision(pre_processed_data, number_of_samples):
	no_time_numpy = []
	no_time = pre_processed_data.loc[:, pre_processed_data.columns != 'time']
	no_time_numpy.append(no_time.to_numpy())

	samples = len(no_time_numpy[0])
	split = [0]
	for x in range(samples):
		if x != 0: 
			if x % number_of_samples == 0:
				split.append(number_of_samples)
	split.append(samples%number_of_samples)
	cumulative = np.cumsum(split)


	new_structure = [[]]
	for x in range(split[1]):
		new_structure[0].append(no_time_numpy[0][x])
	    
	for index in range(1, len(cumulative)):
		if index + 1 < len(cumulative):
			for x in range(cumulative[index], cumulative[index+1]):
				new_structure[0].append(no_time_numpy[0][x] - no_time_numpy[0][cumulative[index] - 1])

	tmp = 0
	counters = []
	for z in new_structure:
		for x in range(len(z)):
			tmp = 0
			for y in z[x]:
				if y > 0:
					tmp += 1
			counters.append(tmp)

	return counters

def save_final_data(counters, pre_processed_data, output_file_path):
	with open(output_file_path, mode='w') as file:
	    writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
	    writer.writerow(['time', 'fl != 0'])
	    for x in range(len(counters)):
	        writer.writerow([str(pre_processed_data["time"].values[x]), str(counters[x])])



def tmp_plot(pre_processed_data, counters):
	fig, ax = plt.subplots()
	ax.plot(pre_processed_data["time"].values, counters, label='your label')
	ax.set_ylim(ymin=0)
	ax.set_xlim(xmin=0, right=600000)
	ax.set_ylabel('no. of bins != 0')
	ax.set_xlabel('time [s]')
	# x = [0, 60000, 120000, 180000, 240000, 300000, 360000, 420000, 480000, 540000, 600000]
	# my_xticks = ['0', '60', '120', '180', '240', '300', '360', '420', '480', '540', '600']
	# plt.xticks(x, my_xticks)
	ax.legend()
	plt.grid()
	plt.show()
	#plt.savefig('your_path')

def process_command_line(argv):
	parser = optparse.OptionParser()
	parser.add_option(
		'-r',
		'--csv',
		help='Specify the eBPF csv to read.',
		action='store',
		type='string',
		dest='csv')

	parser.add_option(
		'-t',
		'--time_window',
		help='Specify the size of the time window to split the data.',
		action='store',
		type='int',
		dest='time_window')

	parser.add_option(
		'-s',
		'--sample_window',
		help='Specify the size of the sample window to split the data.',
		action='store',
		type='int',
		dest='sample_window')

	parser.add_option(
		'-w',
		'--output_file',
		help='Specify the path of the output file.',
		action='store',
		type='string',
		dest='output_file')

	settings, args = parser.parse_args(argv)
		
	if not settings.csv:
		raise ValueError("The eBPF csv file must be specified.")
	if not settings.time_window and not settings.sample_window:
		raise ValueError("A time or a sample window must be specified.")
	if settings.time_window and settings.sample_window:
		raise ValueError("Only a sample window or a time window needs to be specified.")
	if not settings.output_file:
		raise ValueError("The output file path must be specified.")


	return settings, args

#MAIN
settings, args = process_command_line(sys.argv)
pre_processed_data = read_data(settings.csv)
if settings.time_window:
	counters = time_window_suddivision(pre_processed_data, settings.time_window)
elif settings.sample_window:
	counters = sample_window_suddivision(pre_processed_data, settings.sample_window)
save_final_data(counters, pre_processed_data, settings.output_file)
tmp_plot(pre_processed_data, counters)

