"""
Package dealing with ROOT or/and CMSSW in a compact and uniform way
"""

def printError( name, message, _exception ):
	""".. function:: printError(name, message, _exception) 

	Print a error message (in red color) and raise an exception

	:param name: module which call
	:type name: string
	:param message: message to print
	:type message: string
	:param _exception: exception to raise
	:type _exception: Exception
	"""
	_lines = message.split('\n')
	mess = ''
	for l in _lines:
		mess += '\033[1;31m'+name+' Error\033[1;m: '+l+'\n'
	raise _exception(mess)

def printWarning( name, message ):
	""".. function:: printWarning(name, message) 

	Print a warning message (in yellow color) and continue

	:param name: module which call
	:type name: string
	:param message: message to print
	:type message: string
	"""
	_lines = message.split('\n')
	mess = ''
	for l in _lines:
		mess = '\033[1;33m'+name+' WARNING\033[1;m: '+message+'\n'
	mess = mess[:-1]
	print mess

def printInfo( name, message ):
	""".. function:: printInfo(name, message) 

	Print a informational message (in blue color) and continue

	:param name: module which call
	:type name: string
	:param message: message to print
	:type message: string
	"""
	_lines = message.split('\n')
	mess = ''
	for l in _lines:
		mess = '\033[1;34m'+name+' INFO\033[1;m: '+message+'\n'
	mess = mess[:-1]
	print mess


class pycms( object ):
	""".. class: :pycms(rootfilename[,trees=[name1,..],edm=True,verbose=True])

	Wrapper to access a root file.
	"""
	def __init__( self, namerootfile, **keywords ):
		"""
		"""
		from ROOT import TFile
		
		self.totalTrees = 0
		self.treenames = []

		validkeywords = [ 'trees', 'edm', 'verbose' ]
		userTrees = False
		
		# Check if is EDM and initialize workspace 
		if keywords.has_key('edm') and keywords['edm']:
				self.__initworkspace__()
		
		# Check verbosity
		verbose = False
		if keywords.has_key('verbose') and keywords['verbose']:
			verbose=True

		
		# Initialize file (before decide the trees to be used)				
		if verbose:
			printInfo('pycms','Initializing root file "%s"' % namerootfile)
		self.__filename__ = namerootfile
		self.__rootfile__ = TFile.Open( self.__filename__ )
		try:
			# Method TFile::Open returns a null pointer 
			dummy = self.__rootfile__.IsZombie()
		except ReferenceError:
			printError( self.__module__+'.pycms', 'Something wrong. I cannot open the rootfile', IOError )

		for key, value in keywords.iteritems():
			if not key in validkeywords:
				message = "Not valid argument keyword '%s' in constructor " % key
				message += "\nValid keywords are: '%s'" % str(validkeywords)
				printError( self.__module__+'.pycms', message, AttributeError )

			if key == 'trees':
				#Only registring the trees introduced
				if type(value) == list:
					for treename in value:
						try:
							if self.__rootfile__.GetKey(treename).GetClassName() == 'TTree':
								self.__registryTree__( treename )
						except AttributeError:
							message = "No tree called '%s' in the rootfile '%s'" % (self.__filename__, treename )
							printError( self.__module__+'.pycms', message, AttributeError )
					userTrees = True
				elif type(value) == str:
					self.__registryTree__( value )
					userTrees = True
				else:
					message = "The value of the keyword argument trees must be a list of strings or a string. I parsed: '%s' --> '%s' " \
							% ( value, str(type(value)) )
					printError( self.__module__+'.pycms', message, AttributeError )
		# Storing info from the trees
		if not userTrees:
			for tree in self.__rootfile__.GetListOfKeys():
				if tree.GetClassName() == 'TTree':
					self.__registryTree__( tree.GetName() )

		# More info if the user asked for
		if verbose:
			mess = '+ Number of initialized trees:%i\n' % self.totalTrees
			for treename in self.treenames:
					mess += '            |- %s\n' % treename 
			printInfo('pycms',mess[:-1])

	def __initworkspace__(self):
		"""
		"""
		import ROOT
		printInfo('pycms','Initializing CMSSW Lite libraries')
		loadout = ROOT.gSystem.Load('libFWCoreFWLite.so') 
		if loadout == 0:
			ROOT.AutoLibraryLoader.enable()
			#ROOT.gSystem.Load("libDataFormats.so")
		elif loadout == 1:
			printInfo('pycms',"CMSSW Lite libraries already loaded")
		else:
			printWarning('pycms',"CMSSW environment variables not set."\
					" Have you forgotten 'cmsenv' or 'eval `scram runtime -sh`?")

	def __registryTree__( self, treeName ):
		"""
		"""
		#----- Avoiding get the same object with different cycle (getting an error)
		if treeName in self.treenames:
			return 

		tree = self.__rootfile__.Get( treeName )
		if not tree:
			message = "No tree called '%s' in the rootfile '%s'" % (self.__filename__, treeName )
			printError( self.__module__+'.__registryTree__', message, AttributeError )

		self.__setattr__( treeName, pytree(tree) )

		self.totalTrees += 1
		self.treenames.append( treeName )

	def getproduct( self, label, tree='' ):
		""".. method:: getproduct(label[,tree]) -> 
		"""
		# XXX TO BE DEPRECATED?? The product belongs to the tree, not to this file-wrapper class
		if tree == '' and self.totalTrees != 1:
			message = "I have more than one TTree. I explicity need the name of the tree"
			message += "\nCall the function 'get( label, treename )'"
			printError( self.__module__+'.get', message, AttributeError )
		elif tree == '':
			tree = self.treenames[0]

		if not tree in self.treenames:
			message = "'%s' is not a TTree of the '%s' rootfile " % (tree,self.__filename__)
			printError( self.__module__+'.get', message, AttributeError )
		#if not label in self.__getattribute__( tree )['classdict'].keys(): 
		#	message = "'%s' is not an instance of the '%s' TTree" % (label,tree)
		#	printError( self.__module__+'.get', message, AttributeError )

		# Calling the pytree get method
		return self.__getattribute__( tree ).getproduct( label )


class pytree(object):
	""".. class:: pytree(treeobject[,])
	Class to deal with the TTree content of a root file. 
	It acts as a wrapper, so the correct initialization 
	of the TTree does not fall on that class.
	"""
	def __init__( self, treeobject, **keywords ):
		""".. class:: tree( treeobject )

		:param treeobject: TTree object
		:type treeobject: ROOT.TTree
		"""
		self.tree = treeobject
		self.nentries = self.tree.GetEntries()
		self.currentry = -1
		self.isInit = False
		# Checking if is a TTree: FIXME
		#if self.tree.ClassName() != 'TTree':
		#	message = "Problem with the tree '%s'" % ( treeobject.GetName() )
		#	printError( self.__module__+'.pycms', message, RuntimeError )

		# Dictionary of collection name: python object
		branchesCol = self.tree.GetListOfBranches()
		# FIXED: Changed GetSize() -> GetLast() + 1 
		self.collections = dict( [ (branchesCol.At(i).GetName(),\
				pythonize(branchesCol.At(i).GetClassName()) ) \
				for i in xrange(branchesCol.GetLast()+1) ] )
		# Are there aliases?
		alias = self.tree.GetListOfAliases()
		if alias:   # It will be a null pointer if no alias
			self.alias = dict( [ (alias.At(i).GetName(), alias.At(i).GetTitle().rstrip('obj') )\
					for i in xrange(alias.GetSize()) ] )
		else:
			self.alias = None
		
		self.__mispelledbranches__ = {}
		for name, classname in self.collections.iteritems():
			# Plain Branches 
			if classname == 'ROOT.()':
				try:
					self.collections[name]  = self.tree.GetLeaf(name).GetTypeName()
				except (ReferenceError,AttributeError):
					#-- FIXED: Some versions of python raises an AttributeError exception
					#-- when the leaf is not found with the name forecast.
					# To deal with different names of the leaf and the branch
					# Assume the name of the leaf will be alphanumeric characters
					# and/or "_" and finalize when found a '[' or a '/' character
					leafname = self.tree.GetBranch( name ).GetTitle().partition('[')[0].partition('/')[0] 
					self.collections[name]  = self.tree.GetLeaf(leafname).GetTypeName()
					self.__mispelledbranches__[name] = leafname
		# All of the keys which its value is ROOT.() means that the leaf name is different from the branch name
		# so delete this keys and point this value in a dictionary in order to be transparent for the user
		for oldname,newname in self.__mispelledbranches__.iteritems():
			self.collections[newname] = self.collections[oldname] 
			self.collections.pop( oldname )

		if len(self.__mispelledbranches__) == 0:
			self.__mispelledbranches__ = None
		
		# The active collections what are going to be in use (when call getproduct method)
		self.__activeproducts__ = []

	def __str__(self):
		"""
		"""
		message = '\033[1;39m'+self.tree.GetName()+' Entries: '+str(self.nentries)+'\033[1;m\n'
		for name,_type_ in sorted(self.collections.iteritems()):
			message += '-- \033[1;29m'+name+' ('+ _type_ +')\033[1;m\n'

		return message

	def __iter__(self):
		"""
		"""
		return self

	def next(self):
		"""
		"""
		self.currentry = self.tree.GetReadEntry()
		if self.currentry < self.nentries - 1 :
			# Not initialized -> currentry = -1
			self.currentry += 1
			self.getentry( self.currentry )
		else:
			raise StopIteration

		return self.currentry


	def findcollection(self, pattern):
		"""
		"""

		normPattern = pattern.lower()

		matched = filter( lambda key: key.lower().find( normPattern ) != -1, self.collections.iterkeys() )
		
		return matched

	def getentry(self, entry):
		"""
		"""
		if entry >= self.nentries:
			message = "entry '%i' out of range" % (self.nentries)
			printError( self.__module__+'.pytree.getentry', message, IndexError )
		else:
			self.tree.GetEntry( entry )
			self.currentry=entry

		if not self.isInit:
			self.isInit = True

		# Update the active collections of the tree
		for col in self.__activeproducts__:
			col.__update__()

	def getproduct( self, label ):
		""".. method:: getproduct( label ) -> object
		"""
		PLAIN_TYPES = [ 'Bool_t', 'Int_t', 'Float_t' ]

		thelabel = label

		if self.alias:
			if label in self.alias.keys():
				thelabel = self.alias[label]

		if self.__mispelledbranches__:
			if label in self.__mispelledbranches__.keys():
				thelabel = self.__mispelledbranches__[label]

		if not thelabel in self.collections.keys(): 
			message = "'%s' is not an instance of the '%s' TTree" % (label,self.tree.GetName())
			printError( self.__module__+'.pytree.get', message, AttributeError )
		
		_type_ = self.collections[ thelabel ]
		#-- 3 ways : EDM-like with wrappers, std-like objects and plain TTrees
		# FIXME: Deberia registrar los productos que devuelve para actualizarlos
		#        cada vez que hay un getentry..a: syncronize o algo asi.
		#        Quien es el encargado de esto, los productos o el tree??
		theproduct = None
		if _type_ in PLAIN_TYPES:
			theproduct = pyleaf( self, thelabel, _type_ )
		elif _type_.find( 'Wrapper' ):
			theproduct = pywrapper( self, thelabel, _type_ )
		# Registring the product
		self.__activeproducts__.append( theproduct )

		return theproduct

	def draw( self, todraw, **keywords ): 
		""".. method:: draw( todraw[, cut=cutstring, option=optstring ] ) -> canvas

		:param todraw: what to draw with the tree
		:type todraw: str
		:keyword cut: cuts applied 
		:type keyword: str
		:keyword option: options to draw
		:type option: str
		
		:return: canvas used to plot 
		:rtype: ROOT.TCanvas
		"""
		# FIXME: Demasiados errores, hay que modificar esta funcion
		#import rootlogon
		from ROOT import TCanvas, gDirectory, gStyle

		validkeywords = [ 'cut', 'option','canvas','ranges' ]
		
		output=None
		outname = todraw.replace(':','_').replace('[','_').replace(']','')
		argumentsOrder = { 0: todraw+'>>'+outname, 1:'',2:'' }
		for key, value in keywords.iteritems():
			if not key in validkeywords:
				message="Not valid keyword '%s' as argument function" % key
				printError( self.__module__+'.pytree.draw', message, KeyError )
			if key == 'cut':
				argumentsOrder[1] = value
			elif key == 'option':
				argumentsOrder[2] = value
			elif key == 'canvas':
				# Check if is a canvas object
				message = "The argument of 'canvas' keyword is not a TCanvas object"
				try:
					if value.ClassName() != 'TCanvas':
						printError(self.__module__+'.pytree.draw', message, RuntimeError)
				except AttributeError:
					printError(self.__module__+'.pytree.draw', message, RuntimeError)
				output=value
			elif key == 'ranges':
				#FIXME: control de errores. Mostrar la sintaxis (N,xmin,xmax)
				N= str(int(value[0]))
				x_min = str(value[1])
				x_max = str(value[2])
				outname += '('+N+','+x_min+','+x_max+')'
				#Modifying
				argumentsOrder[0]=todraw+'>>'+outname					
			else:
				message="Unexpected error!! See the code 'cause you shouldn't see this!"
				printError( pytree.__module__+'.pytree.draw', message, UserWarning )
		
		arguments = ''
		for i in sorted(argumentsOrder.iterkeys()):
			arguments += "'"+argumentsOrder[i]+"', "
		arguments = arguments[:-2]

		if not output:
			output = TCanvas()
		eval( 'self.tree.Draw('+arguments+')' ) 

		return output, gDirectory.Get(outname)


class pycollection(object):
	""".. class:: pycollection

	Abstract class to deal with the contents of a TTree, i.e. up-to-now branches
	with plain leaves and comples (edm::wrappers, std::vector,...) objects. 
	This class can not be used directly, see pyleaf and pywrapper classes
	"""
	def __init__( self, _pytree_, label, _type_ ):
		"""
		"""
		self.label = label
		self.__pytree__ = _pytree_
		self.treename = self.__pytree__.tree.GetName()
		self.nentriestree = self.__pytree__.nentries
		
	def size(self):
		""".. method:: size() -> int

		Get the size of the collection
		"""
		return self.__len__()

	def __update__(self):
		""".. method:: __update__ 

		Dummy method (pyleaf) and need to be implemented for pywrapper
		"""
		pass



class pyleaf( pycollection ):
	"""
	"""
	def __init__( self, _pytree_, label, _type_ ):
		"""
		"""
		# Initialize base class
		pycollection.__init__(self,_pytree_,label,_type_)

		self.leaf = self.__pytree__.tree.GetLeaf(label)
		if not self.leaf:
			message = "'%s' is not an instance of the '%s' TTree" % (label,self.treename)
			printError( self.__module__+'.pyleaf', message, AttributeError )


	def __len__( self ):
		"""
		"""
		if not self.__pytree__.isInit:
			message = "The TTree '%s' is not initialized." % (self.treename)
			printError( self.__module__+'.__getitem__', message, RuntimeError )
		
		return self.leaf.GetLen()


	def __getitem__( self, index ):
		"""
		"""
		if not self.__pytree__.isInit:
			message = "The TTree '%s' is not initialized." % (self.treename)
			printError( self.__module__+'.__getitem__', message, RuntimeError )

		if index >= self.__len__():
			raise StopIteration

		return self.leaf.GetValue(index)


class pywrapper( pycollection ):
	"""
	"""
	def __init__( self, _pytree_, label, _type_ ):
		"""
		"""
		# I need the module in the eval
		import ROOT
		#--- Patch to deal with double and int stuff
		ROOT.double = ROOT.Double
		ROOT.int    = int

		# Initialize base class
		pycollection.__init__(self,_pytree_,label,_type_)
		self.wrapper = eval( _type_ )
		self.__pytree__.tree.SetBranchAddress( label, self.wrapper )
		#if not self.leaf:
		#	message = "'%s' is not an instance of the '%s' TTree" % (label,self.treename)
		#	printError( self.__module__+'.pywrapper', message, AttributeError )
		self.size = None
		self.product = None

	def __update__( self ):
		""".. method:: __update__()

		Update the product once a new entry is accessed 
		"""
		if not self.__pytree__.isInit:
			message = "The TTree '%s' is not initialized." % (self.treename)
			printError( self.__module__+'.__getitem__', message, RuntimeError )

		# FIXME: CHECKEAR SI EL currentry del tree es el mismo que el del pywrapper
		# Extract the product
		if not self.product:
			try:
				self.product = self.wrapper.product()
				# Checking if is in the Event
				if not self.wrapper.isPresent():
					message = "'%s' collection not present in the event" % ( self.label )
					printWarning( '', message )
			except AttributeError:
				# The Wrapper is directly the product: FIXME esto
				self.product = self.wrapper
		try:
			self.size = self.product.size()
		except AttributeError:
			#It's not a vector
			self.size = None

	def __len__(self):
		"""
		"""

		size = self.size
		if size:
			return size

		return 0


	def __repr__( self ):
		"""
		"""
		return self.product.__repr__()


	def __getitem__( self, index ):
		"""
		"""
		if not self.size:
			raise StopIteration

		if index >= self.size:
			raise StopIteration

		return self.product[index]


def pythonize( rootstring ):
	""".. function:: pythonize( rootstring ) -> pythonstring

	Gets a string describing the ROOT class in C++-like syntax
	and returns the name of this class in python-like syntax

	:param rootstring: Class in C++ syntax
	:type rootstring: string
	
	:return: Class in python syntax
	:rtype: string

	:raise :
	"""
	# FIXME: Missed the vector --> std.vector (although it's not necessary)
	return 'ROOT.'+rootstring.replace('::','.').replace('<','(ROOT.').replace('>',')')+'()'

