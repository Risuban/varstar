from astropy.table import Table
from astropy.io import fits
import numpy
from time import strftime

import re

def get_file_data(filename):
	"""
	Reads a file from the ASAS and returns a list of dictionaries containing all the pairs key-value
	from it. For each dictionary, for the tables, each column is represented as a list on the
	dictionary's key which name matchs the column's name.
	"""
	document= open(filename,'r')
	data=[]
	pairs={'ORIGIN':filename.replace('/','\\')}
	actuald=None #Will be used to save the magnitude's table
	for line in document:
		if line[0]=='#':
			key= re.match(r"#.*=",line)
			if key:
				#It's a key
				key= key.group()[1:-1]
				values= (line.strip()[len(key)+2:]).split(' ')
				values= [x for x in values if x!='']
				values= tuple(values)
				if len(values)==1:
					pairs[key]= values[0]
				else:
					pairs[key]= values
				#If a data block has been completely read, add it to the data. 
				if actuald!=None:
					pairs.update(actuald)
					data.append(pairs)
					actuald=None
					pairs={'ORIGIN':filename}
			else:
				#It's a multiple key description
				keys= re.findall(r"\s\S+",line)
				keys= map(lambda x: x[1:],keys)
				#Restart the current dictionary
				actuald={}
				for k in keys:
					actuald[k]=[]
		else:
			#Extract the values and append them to the dictionary of multiple keys.
			values= re.findall(r"\S+[\s$]",line)
			values= map(lambda x: x[:-1],values)
			#Try convertion to float, and if it doesn't work, append values as they are is.
			for i in xrange(len(values)):
				actuald[keys[i]].append(values[i])
	pairs.update(actuald)
	data.append(pairs)
	for dictionary in data:
		for key,val in dictionary.iteritems():
			#Try the conversion of columns to float
			if type(val)==list:
				try: dictionary[key]= map(float,val)
				except ValueError as er: pass
	return data


def get_files_data(filenames):
	"""
	The same as get_file_data but receibes multiple files.
	"""
	dict_list=[]
	for fip in filenames:
		dict_list= dict_list+ get_file_data(fip)
	return dict_list

def save_to_fits(dictionary_list,filename,type_to_format={float:"E",str:"20A"}):
	"""
	Saves all the dictionaries of the list onto a FITS file.
	"""
	hdus= fits.HDUList()
	#Creating the primary hdu to contain the meta
	primary_hdu = fits.PrimaryHDU()
	primary_hdu.header['history']= "From the ASAS records, parsed by ASASparser the "+str(strftime("%d/%m/%Y")+" (dd/mm/yyyy)")
	hdus.append(primary_hdu)
	#Creating the bintables HDUS for each dictionary
	for dictionary in dictionary_list:
		columns= []
		for key,val in dictionary.iteritems():
			if type(val)==list:
				#Goes to the table.
				columns.append( fits.Column(name=key, array=val, format=type_to_format[type(val[0])] ))
		column_definitions = fits.ColDefs(columns)
		tbhdu = fits.BinTableHDU.from_columns(column_definitions)
		for key,val in dictionary.iteritems():
			if not type(val)==list:
				#Goes to the HDU's header
				if type(val)!=tuple:
					tbhdu.header[key]= val 
				else:
					val= tuple(map(lambda x: ''.join(x),' '.join(val).split(';')))
					tbhdu.header[key]= val
		hdus.append(tbhdu)
		"""
		# The primary HDU for the dictionary.
		primary_hdu = fits.PrimaryHDU()
		# Creating the binary table HDU.
		columns= []
		for key,val in dictionary.iteritems():
			if type(val)==list:
				#Goes to the table.
				columns.append( fits.Column(name=key, array=val, format=type_to_format[type(val[0])] ))
			else:
				#Goes to the primary HDU
				if type(val)!=tuple:
					primary_hdu.header[key]= val 
				else:
					val= tuple(map(lambda x: ' '.join(x),' '.join(val).split(';')))
					primary_hdu.header[key]= val
		column_definitions = fits.ColDefs(columns)
		tbhdu = fits.BinTableHDU.from_columns(column_definitions)
		hdus.append(primary_hdu)
		hdus.append(tbhdu)
		"""
		"""
		dict_to_table={}
		for key,val in dictionary.iteritems():
			if type(val)==list:
				dict_to_table[key]= val
		table= Table(dict_to_table)
		hdu= fits.ASCITableHDU(table)
		"""
		#
		"""
		data_matrix=[]
		hdu = fits.PrimaryHDU()
		line_number=0
		for key,val in dictionary.items():
			if type(val) == list:
				hdu.header['LIN'+'0'*(5-len(str(line_number)))+str(line_number)]= key
				line_number+=1
				data_matrix.append(val)
			else:
				if type(val)!=tuple:
					hdu.header[key]= val 
				else:
					val= tuple(map(lambda x: ' '.join(x),' '.join(val).split(';')))
					hdu.header[key]= val
		
		#Saving the hdu:
		array= numpy.asarray(data_matrix)
		hdu.data= array
		hdus.append(hdu)
		"""
	output_file= open(filename,"w")
	hdus.writeto(output_file)
	output_file.close()

if __name__=="__main__":
	dictionary_list= get_files_data(["test/000006+2553.2","test/000007+1844.3"])
	print dictionary_list
	save_to_fits(dictionary_list,"test/output.fits")
	print "Tests done!"
