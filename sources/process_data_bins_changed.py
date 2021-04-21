import pandas as pd
import math
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties
import csv
import sys
import optparse

def read_and_process(data):
    read_data = pd.read_csv(data, header=None)
    time_column = read_data.iloc[:,0]
    pre_processed_data = read_data.drop(read_data.columns[0], axis=1)
    data_diff = pre_processed_data.diff()
    data_diff['DIFF'] = data_diff.gt(0).sum(axis=1)
    data_diff.insert(0, "time", time_column, True)
    return data_diff


def tmp_plot(data):
	fig, ax = plt.subplots()
	ax.plot(data["time"].values, data['DIFF'], label='your label')

	ax.set_ylim(ymin=0)
	ax.set_xlim(xmin=0, right=900)
	ax.set_ylabel('no. of bins changed')
	ax.set_xlabel('time [s]')
	ax.legend()
	plt.grid()
	plt.show()

def save_final_data(data, output_file_path):
	with open(output_file_path, mode='w') as file:
	    writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
	    writer.writerow(['time', 'no. of bins changed'])
	    for x in range(len(data["time"].values)):
	        writer.writerow([str(data["time"].values[x]), str(data['DIFF'][x])])


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
		'-w',
		'--output_file',
		help='Specify the path of the output file.',
		action='store',
		type='string',
		dest='output_file')

	settings, args = parser.parse_args(argv)
		
	if not settings.csv:
		raise ValueError("The eBPF csv file must be specified.")
	if not settings.output_file:
		raise ValueError("The output file path must be specified.")


	return settings, args

#MAIN
settings, args = process_command_line(sys.argv)
processed_data = read_and_process(settings.csv)
save_final_data(processed_data, settings.output_file)
tmp_plot(processed_data)