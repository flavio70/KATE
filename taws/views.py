from django.shortcuts import render
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from django.contrib import auth
from django.views.decorators.csrf import requires_csrf_token
from django.http import JsonResponse
from django.conf import settings

# Create your views here.

from django.http import HttpResponse

def get_testinfo(testpath):
	""" 
		get metadata from testcase
		:param testpath: Full testcase path
		
		:return: Dictionary containing availables info fields
		
		Description,Topology,Dependency,Lab,TPS,RUnSections,Author
	"""
	import ast,re,os
	res=None
	#testFullName = os.path.abspath(testpath).decode('ascii')
	#testFullname = testpath
	try:
		if not os.path.exists(testpath):return res
		M = ast.parse(''.join(open(testpath)))
		doc=ast.get_docstring(M)
			
		if doc is not None:
			docre = re.findall(':field (.*)?',doc,re.MULTILINE)
			docre=[i.split(':') for i in docre]
			res={}
			res['Description']=''
			res['TPS']=''
			for elem in docre:
				if (elem[0] == "Description"):
					#print('Description %s'%elem[1])
					res['Description'] =  res['Description']  + re.sub('["\']+','',elem[1]) + '\n'
				elif (elem[0] == "TPS"):
					if res['TPS'] != '': res['TPS']+='<br>'
					res['TPS'] =  res['TPS']  + re.sub('["\']+','',elem[1])
				else:
					res[elem[0]]=re.sub('["\']+','',elem[1].strip())
					#print( '%s %s' %(elem[0],elem[1]))
	except Exception as xxx:
		print('ERROR on get_testinfo')
		print(str(xxx))
	return res


def check_testinfo_format(f,testinfo):
	"""
		check testcase metadata format for mandatory fields
		:Description,Dependency,LAB,TPS,Author,Topology: String without escape chars
		:RunSections:[0|1] len=5
		
		
		:returns: True|False
		
	"""
	import re
	res = True
	
	if not testinfo: return False
	
	if 'RunSections' not in testinfo: return False
	if 'Description' not in testinfo: return False
	if 'Dependency' not in testinfo: return False
	if 'Lab' not in testinfo: return False
	if 'TPS' not in testinfo: return False
	if 'Author' not in testinfo: return False
	if 'Topology' not in testinfo: return False
	if not re.match('^[01]{5}$',testinfo['RunSections'].strip()): return False
	
	
	return res

def index(request):
	context = RequestContext(request)
	context_dict = {'nothing':'nothing'}
	if 'login' in request.session:
		login=request.session['login']
		#context_dict = {'login':login,'thread_jenkins':request.session['thread_jenkins']}
		context_dict = {'login':login}
	return render_to_response('taws/index.html', context_dict, context)

def login(request):
	context = RequestContext(request)
	context_dict={'fromPage':'index'}
	return render_to_response('taws/login.html',context_dict,context)
	#render_template_block(get_template("taws/template_menu.html"),'body',context)


def logout(request):
	if 'login' in request.session:del request.session['login']
	auth.logout(request)
	context = RequestContext(request)
	context_dict={'nothing':'nothing'}
	return render_to_response('taws/index.html',context_dict,context)

def check_login(request):
	context = RequestContext(request)
	username = request.POST['username']
	password = request.POST['password']
	fromPage = request.POST.get('url','')

	user = auth.authenticate(username=username, password=password)

	if user is not None:
		# the password user is verified
		auth.login(request, user)
		if user.is_staff:
			request.session['role']='ADMIN'
		else:
			request.session['role']='POWERUSER'
		request.session['login']=username
		request.session['password']=password

		context_dict={'login':username}
	else:
		context_dict={'nothing':'nothing'}
	if fromPage != '':
		url="taws/"+fromPage+'.html'
	else:
		url="taws/index.html"
	context_dict.update({'fromPage':url})
	return render_to_response(url,context_dict,context)

def development_index(request):
	context = RequestContext(request)
	context_dict={'nothing':'nothing'}
	if 'login' not in request.session:
		context_dict={'fromPage':'development_index'}
		return render_to_response('taws/login.html',context_dict,context)
	else:
		context_dict={'login':request.session['login']}
		return render_to_response('taws/development_index.html',context_dict,context)

def suite_creator(request):
	context = RequestContext(request)
	context_dict={'nothing':'nothing'}
	import mysql.connector

	if 'login' not in request.session:
		context_dict={'fromPage':'suite_creator'}
		return render_to_response('taws/login.html',context_dict,context)
	else:
		dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
		myRecordSet=dbConnection.cursor(dictionary=True)
		myRecordSet.execute("SET group_concat_max_len = 200000")
		dbConnection.commit()
		#myRecordSet.execute("select product,CONVERT(group_concat(concat(areaConcat,'$',sw_rel_name) order by sw_rel_name desc separator '@') using utf8) as productConcat from (select product,sw_rel_name,group_concat(concat(area_name,'!',area_name) order by area_name separator '#') as areaConcat from T_DOMAIN join T_AREA on(T_AREA_id_area=id_area) join T_PROD on(T_PROD_id_prod=id_prod) join T_SW_REL on(T_SW_REL_id_sw_rel=id_sw_rel) group by product,sw_rel_name order by product asc,sw_rel_name desc) as tableArea group by product")
		myRecordSet.execute("select product,group_concat(release_scope_area separator '@') as productConcat from (select product,concat(sw_rel_name,'?',group_concat(scope_area separator '%')) as release_scope_area from (select product,sw_rel_name,concat(T_SCOPE.description,'#',group_concat(area_name order by area_name separator '|')) as scope_area from T_DOMAIN join T_SCOPE on(T_SCOPE_id_scope=id_scope) join T_AREA on(T_AREA_id_area=id_area) join T_PROD on(T_PROD_id_prod=id_prod) join T_SW_REL on(T_SW_REL_id_sw_rel=id_sw_rel) group by product,sw_rel_name,T_SCOPE.description order by product asc,sw_rel_name desc,T_SCOPE.description asc) as release_scope_area group by product,sw_rel_name order by product asc,sw_rel_name desc) as product_release_scope_area group by product order by product asc")
		productAry=[{'product':row["product"],'productConcat':row["productConcat"]} for row in myRecordSet]

		userSuiteAry = ''
		sharedSuiteAry = ''

		myRecordSet.execute("SELECT * from T_SUITES where owner = '"+request.session['login']+"' order by name")
		userSuiteAry=[{'suiteName':row["name"],'suiteID':row["id_suite"],'suiteDesc':row["description"]} for row in myRecordSet]

		myRecordSet.execute("SELECT * from T_SUITES where owner = 'SHARED' order by name")
		sharedSuiteAry=[{'suiteName':row["name"],'suiteID':row["id_suite"],'suiteDesc':row["description"]} for row in myRecordSet]

		myRecordSet.execute("SELECT * from T_TOPOLOGY join T_SCOPE on(T_SCOPE_id_scope=id_scope) where T_SCOPE.description='VIRTUAL'")
		virtualTopoAry=[{'virtualTopoID':row["id_topology"],'virtualTopoName':row["title"]} for row in myRecordSet]

		myRecordSet.execute("SELECT * from T_TOPOLOGY join T_SCOPE on(T_SCOPE_id_scope=id_scope) where T_SCOPE.description='DATA'")
		dataTopoAry=[{'dataTopoID':row["id_topology"],'dataTopoName':row["title"]} for row in myRecordSet]

		myRecordSet.execute("SELECT * from T_TOPOLOGY join T_SCOPE on(T_SCOPE_id_scope=id_scope) where T_SCOPE.description='TDM'")
		tdmTopoAry=[{'tdmTopoID':row["id_topology"],'tdmTopoName':row["title"]} for row in myRecordSet]

		myRecordSet.execute("SELECT * from T_TOPOLOGY join T_SCOPE on(T_SCOPE_id_scope=id_scope) where T_SCOPE.description='WDM'")
		wdmTopoAry=[{'wdmTopoID':row["id_topology"],'wdmTopoName':row["title"]} for row in myRecordSet]

		myRecordSet.execute("SELECT distinct lab from T_TEST_REVS order by lab")
		labAry=[{'labName':row["lab"]} for row in myRecordSet]

		context_dict={'login':request.session['login'].upper(),
			'permission':1,
			'productAry': productAry,
			'userSuiteAry': userSuiteAry,
			'sharedSuiteAry': sharedSuiteAry,
			'virtualTopoAry':virtualTopoAry,
			'dataTopoAry':dataTopoAry,
			'tdmTopoAry':tdmTopoAry,
			'wdmTopoAry':wdmTopoAry,
			'labAry':labAry,
			'settings':settings.DATABASES['default']['USER']}
		return render_to_response('taws/suite_creator.html',context_dict,context)

def test_development(request):
	context = RequestContext(request)
	context_dict={'nothing':'nothing'}
	import mysql.connector
	import json

	if 'login' not in request.session:
		context_dict={'fromPage':'test_development'}
		return render_to_response('taws/login.html',context_dict,context)
	userBranches=getUserRepoBranch(request.session['login'])
	dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
	myRecordSet=dbConnection.cursor(dictionary=True)
	myRecordSet.execute("SET group_concat_max_len = 200000")
	dbConnection.commit()
	context_dict={'login':request.session['login'].upper(),
		'permission':1,
		'activebranch':userBranches['current'],
		'branchlist':json.dumps(userBranches['list'])}

	return render_to_response('taws/test_development.html',context_dict,context)

def tuning(request):

	import mysql.connector

	context = RequestContext(request)
	context_dict={'nothing':'nothing'}
	if 'login' not in request.session:
		context_dict={'fromPage':'tuning'}
		return render_to_response('taws/login.html',context_dict,context)

	presetChoice=request.GET.get('choice','')
	suiteID = request.POST.get('savingName','')

	dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
	myRecordSet=dbConnection.cursor(dictionary=True)
	myRecordSet.execute("SET group_concat_max_len = 200000")
	dbConnection.commit()
	#myRecordSet.execute("select concat(presetName,'[',convert(group_concat(distinct topoID separator ',') using utf8),']') as presetname,presetID from presets join presetbody using(presetID) join topologybody using(label) join topologies using(topoID) where username='"+Session("login")+"' group by presetID")
	myRecordSet.execute("select concat(T_PRESETS.preset_title,'[',convert(group_concat(distinct id_topology separator ',') using utf8),']') as description,id_preset,preset_title from T_PRESETS join T_PST_ENTITY on(id_preset=T_PRESETS_id_preset) join T_TPY_ENTITY on(id_entity=T_TPY_ENTITY_id_entity) join T_TOPOLOGY on(id_topology=T_TOPOLOGY_id_topology) where owner='"+request.session['login']+"' group by id_preset")
	userPreset=[{'userPresetName':row["description"],'userPresetID':row["id_preset"],'userPresetTitle':row["preset_title"]} for row in myRecordSet]
	myRecordSet.execute("select concat(T_PRESETS.preset_title,'[',convert(group_concat(distinct id_topology separator ',') using utf8),']') as description,id_preset,preset_title from T_PRESETS join T_PST_ENTITY on(id_preset=T_PRESETS_id_preset) join T_TPY_ENTITY on(id_entity=T_TPY_ENTITY_id_entity) join T_TOPOLOGY on(id_topology=T_TOPOLOGY_id_topology) where owner='SHARED' group by id_preset")
	sharedPreset=[{'sharedPresetName':row["description"],'sharedPresetID':row["id_preset"],'sharedPresetTitle':row["preset_title"]} for row in myRecordSet]

	if presetChoice == '':
		myRecordSet.execute("SELECT convert(GROUP_CONCAT(distinct topology separator '-') using utf8) as topologyNeeded,name from T_SUITES join T_SUITES_BODY on(id_suite=T_SUITES_id_suite) join T_TEST_REVS on(id_TestRev=T_TEST_REVS_id_TestRev) where id_suite="+suiteID)
		myRecord=myRecordSet.fetchone()
		fileName=myRecord["name"]
	else:
		myRecordSet.execute("SELECT convert(GROUP_CONCAT(distinct id_topology order by id_topology separator '-') using utf8) as topologyNeeded from T_TOPOLOGY")
		myRecord=myRecordSet.fetchone()
		fileName=''		
	#myRecordSet.execute("SELECT convert(GROUP_CONCAT(distinct topology separator '-') using utf8) as topologyNeeded,suitename from jsuites join jsuiteBody using(jsuiteID) join  Jenkinslist using(JID,livraison) where jsuiteID='"+fileName+"'")
	
	suiteOwner='SERVER'
	myTopologies=myRecord["topologyNeeded"].split('-')
	topoAry='';
	for myTopology in myTopologies:
		#myRecordSet.execute("SELECT if(group_concat(concat(description,'$',label) order by indice separator '$') is null,'topoerror',group_concat(concat(description,'$',label) order by indice separator '$')) as dataValues,numNE from topologyBody join topologies using(topoID) where topoID ='"+myTopology+"'")
		myRecordSet.execute("SELECT if(group_concat(concat(elemDescription,'$',entityName,'$',elemName,'$',id_entity) order by id_entity separator '$') is null,'topoerror',group_concat(concat(elemDescription,'$',entityName,'$',elemName,'$',id_entity) order by id_entity separator '$')) as dataValues,title from T_TPY_ENTITY join T_TOPOLOGY on(id_topology=T_TOPOLOGY_id_topology) where id_topology="+myTopology)
		#myRecord=myRecordSet.fetchall()
		for myRecord in myRecordSet:
			dataValues=myRecord['dataValues']
			topoAry+="topologies.push(new Array());"
			topoAry+="topologies[topologies.length-1].push('"+myTopology+"');"
			topoAry+="topologies[topologies.length-1].push(new Array());"
			topoAry+="topologies[topologies.length-1].push(new Array());"
			topoAry+="topologies[topologies.length-1].push(new Array());"
			topoAry+="topologies[topologies.length-1].push(new Array());"
			topoAry+="topologies[topologies.length-1].push(new Array());"
			topoAry+="topologies[topologies.length-1].push(new Array());"
			topoAry+="topologies[topologies.length-1].push('"+myRecord['title']+"');"
		if myTopology != '000':
			if dataValues != 'topoerror':
				tempLabels = dataValues.split("$")
				for labelIndex in range(0,len(tempLabels),4):
					topoAry+="topologies[topologies.length-1][1].push('"+tempLabels[labelIndex+2]+"');"
					topoAry+="topologies[topologies.length-1][2].push('"+tempLabels[labelIndex]+"');"
					topoAry+="topologies[topologies.length-1][3].push('');"
					topoAry+="topologies[topologies.length-1][4].push('"+tempLabels[labelIndex+3]+"');"
					topoAry+="topologies[topologies.length-1][5].push('');"
					topoAry+="topologies[topologies.length-1][6].push('"+tempLabels[labelIndex+1]+"');"
			else:
				topoAry+="topologies.length=0;"
				topoAry+="alert('Warning!\nUnable to tune a test case of your suite due to a not registered topology.\nPlease check correct topology insertion or contact TAWS Administration Staff.');"
				topoAry+="location.href='suitecreator.asp';"
	dbConnection.close()
	context_dict={"login":request.session['login'],
		"choice": presetChoice,
		"userPreset": userPreset,
		"sharedPreset":sharedPreset,
		"topoAry":topoAry,
		"fileName":fileName,
		"suiteOwner":suiteOwner,
		"suiteID":suiteID}

	#return  JsonResponse(context_dict, safe=False)
	#return render_to_response('taws/tuning.html',context_dict)
	return render(request,'taws/tuning.html',context_dict)

def selectEqpt(request):
	import mysql.connector

	context = RequestContext(request)
	context_dict={'nothing':'nothing'}
	if 'login' not in request.session:
		context_dict={'fromPage':'selectEqpt'}
		return render_to_response('taws/login.html',context_dict,context)

	context_dict={'login':request.session['login']}
	myVars=request.GET.get('myVars')
	tempVars=myVars.split('$')

	dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
	myRecordSet=dbConnection.cursor(dictionary=True)

	#myRecordSet.execute("SELECT id_equipment,T_EQUIPMENT.name,owner,T_EQUIP_TYPE.description as equipDescription,site,room,row,rack,pos,IP,NM,GW,T_SCOPE.description as scopeDescription FROM T_EQUIPMENT join T_EQUIP_TYPE on(id_type=T_EQUIP_TYPE_id_type) join T_LOCATION on(id_location=T_LOCATION_id_location) join T_NET on(id_equipment=T_EQUIPMENT_id_equipment) join T_SCOPE on(id_scope=T_SCOPE_id_scope) left join T_SERIAL on(T_SERIAL.T_EQUIPMENT_id_equipment=id_equipment) where T_EQUIP_TYPE.name='"+tempVars[1]+"' group by id_equipment")
	myRecordSet.execute("SELECT id_equipment,T_EQUIPMENT.name,T_EQUIPMENT.owner,T_EQUIP_TYPE.description as equipDescription,site,room,row,rack,pos,IP,NM,GW,T_SCOPE.description as scopeDescription,runtime.status FROM T_EQUIPMENT join T_EQUIP_TYPE on(id_type=T_EQUIP_TYPE_id_type) join T_LOCATION on(id_location=T_LOCATION_id_location) join T_NET on(id_equipment=T_EQUIPMENT_id_equipment) join T_SCOPE on(id_scope=T_SCOPE_id_scope) left join T_SERIAL on(T_SERIAL.T_EQUIPMENT_id_equipment=id_equipment) left join (select * from T_RUNTIME join T_RTM_BODY on(id_run=T_RUNTIME_id_run)) as runtime on(id_equipment=runtime.T_EQUIPMENT_id_equipment) where T_EQUIP_TYPE.name='"+tempVars[1]+"' and (runtime.status<>'RUNNING' or runtime.status is null) group by id_equipment")
	eqptAry=[{'myVars':myVars,
		'eqptID':row["id_equipment"],
		'eqptName':row["name"],
		'owner':row["owner"],
		'equipDescription':row["equipDescription"],
		'scopeDescription':row["scopeDescription"],
		'site':row["site"],
		'room':row["room"],
		'row':row["row"],
		'rack':row["rack"],
		'pos':row["pos"],
		'IP':row["IP"],
		'NM':row["NM"],
		'GW':row["GW"]} for row in myRecordSet]

	dbConnection.close()
	context_dict={"eqptAry": eqptAry}

	return render_to_response('taws/selectEqpt.html',context_dict)

def tuningEngine(request):

	import mysql.connector,os,shutil
	from os.path import expanduser
	import json,ast

	context = RequestContext(request)
	context_dict={'nothing':'nothing'}
	suiteID=request.POST.get('tuningBundle')
	savingString = request.POST.get('changeValues','')
	description = request.POST.get('description','')
	sharedJob = request.POST.get('sharedJob','off')
	localTesting = request.POST.get('localTesting','off')
	tuningLabel = request.POST.get('tuningLabel','').replace(' ','_')

	if 'login' not in request.session:
		context_dict={'fromPage':'tuningEngine'}
		return render_to_response('taws/login.html',context_dict,context)


	dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
	myRecordSet = dbConnection.cursor(dictionary=True)

	myRecordSet.execute("SELECT count(preset_title) as myCount from T_PRESETS WHERE preset_title='"+request.session['login']+"' and owner='HIDDEN'")
	row=myRecordSet.fetchone()
	if row['myCount']==0:
		myRecordSet.execute("INSERT INTO T_PRESETS (preset_title,owner,preset_description) VALUES('"+request.session['login']+"','HIDDEN','')")
		dbConnection.commit()
	myRecordSet.execute("SELECT id_preset from T_PRESETS where preset_title='"+request.session['login']+"' and owner='HIDDEN'")
	row=myRecordSet.fetchone()
	presetID = row['id_preset']

	myRecordSet.execute("DELETE from T_PST_ENTITY where T_PRESETS_id_preset="+str(presetID))
	dbConnection.commit()

	nibble = savingString.split("?")
	for myVar in nibble:
		tempNibble = myVar.split("|")
		myRecordSet.execute("INSERT into T_PST_ENTITY (T_PRESETS_id_preset,T_TPY_ENTITY_id_entity,pstvalue,T_EQUIPMENT_id_equipment) VALUES ('"+str(presetID)+"','"+tempNibble[0]+"','"+tempNibble[1]+"','"+tempNibble[2]+"')")
		dbConnection.commit()

	tempStr=''
	#tempStr+="PresetID :"+str(presetID)+"\n"
	#tempStr+="SuiteID :"+str(suiteID)+"\n"
	tempStr+="Tuning Test Cases for Jenkins...\n\n"
	global TAWS_path,os
	myRecordSet.execute("select name from T_SUITES where id_suite="+str(suiteID))
	myRecord=myRecordSet.fetchone()

	if localTesting == 'off':
		suiteName=request.session['login']+'_'+myRecord['name']+'-'+tuningLabel
	else:
		suiteName=request.session['login']+'_Development'

	suiteFolder=settings.JENKINS['SUITEFOLDER']

	from jenkinsapi.jenkins import Jenkins
	server = Jenkins(settings.JENKINS['HOST'],username=request.session['login'],password=request.session['password'])
	#server = Jenkins('151.98.52.72:7001',username=request.session['login'],password=request.session['password'])
	
	tempStr+='Working folder : '+suiteFolder+suiteName+settings.JENKINS['JOB_STRUCT']+'\n\n'
	
	if localTesting == 'off':
		tempStr+='Creating workspace structure...\n'
		tempStr+='Check Job '+suiteName+' not present...\n'
		if os.path.exists(suiteFolder+suiteName):
			tempStr+='Job '+suiteName+' already present,deleting workspace...'
			shutil.rmtree(suiteFolder+suiteName)
			tempStr+='DONE!\n'
		if not (server.has_job(suiteName)):
			tempStr+='Job '+suiteName+' creating...'
			tempProperties=''
			if sharedJob == 'off':
				out_file = open(settings.JOB_PROPS_TEMPLATE,"rb")
				tempProperties=out_file.read().decode('UTF-8').replace('[TAWSUSER]',request.session['login'])
				out_file.close()
			out_file = open(settings.JOB_TEMPLATE,"rb")
			templateXML=out_file.read()
			templateXML=templateXML.decode('UTF-8').replace('[PROPERTIES]',tempProperties)
			templateXML=templateXML.replace('[JOBDESCRIPTION]',description)
			out_file.close()
			#job_instance.update_config(templateXML)
			#job_instance.update_config(job_instance.get_config())
			server.create_job(suiteName,templateXML)
			tempStr+='DONE!\n'
			#job_instance = server.get_job(suiteName)
			#tempStr+='Disabling Jenkins Job : '+suiteName+' ...'
			#job_instance.disable()
			#tempStr+='DONE!\n'
			#tempStr+= 'Name:%s,Is Job Disabled ?:%s' %(suiteName,job_instance.is_enabled())
			#tempStr+='Enabling Jenkins Job : '+suiteName+' ...'
			#job_instance.enable()
			#tempStr+='DONE!\n'
			#tempStr+= 'Name:%s,Is Job Enabled ?:%s' %(suiteName,job_instance.is_enabled())

		#server.build_job(suiteName)
		#server.stop(suiteName)
		#os.chmod(suiteFolder+suiteName,511)
		os.makedirs(suiteFolder+suiteName+settings.JENKINS['JOB_STRUCT'])
		os.chmod(suiteFolder+suiteName+settings.JENKINS['JOB_STRUCT'],511)
		#os.makedirs(suiteFolder+suiteName+'/workspace/suite')
		#os.chmod(suiteFolder+suiteName+'/workspace/suite',511)
		os.makedirs(suiteFolder+suiteName+'/workspace/test-reports')
		os.chmod(suiteFolder+suiteName+'/workspace/test-reports',511)


	myIDX=1
	tempStr+=tune_suite(presetID,suiteID,localTesting,suiteName,request.session['login'],'off',myIDX)
	tempStr+='*************'
	tempStr+=create_node_list(presetID,suiteFolder,suiteName)
	tempStr+='\n\nTUNING COMPLETE!\nHAVE A NICE DAY!\n'
	
	context_dict={'login':request.session['login'],'tuningReport':tempStr.replace('\n','\\n')}

	return render_to_response('taws/tuningEngine.html',context_dict)
	#return render_to_response('taws/tuningEngine.html',context_dict,context_instance=RequestContext(request))

def tune_suite(presetID,suiteID,localTesting,suiteName,username,preview,currIDX):
	import os
	import mysql.connector,ntpath,shutil,json,ast
	from git import Repo
	
	suiteFolder=settings.JENKINS['SUITEFOLDER']
	
	dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
	myRecordSet = dbConnection.cursor(dictionary=True)

	myRecordSet.execute("SET group_concat_max_len = 200000")
	dbConnection.commit()
	#myRecordSet.execute("select test_id,id_TestRev,test_name,revision,topology,run_sectionconcat('{',myTuple,'}') as presets from T_TEST join T_TEST_REVS on(test_id=T_TEST_test_id) join T_SUITES_BODY on(id_TestRev=T_TEST_REVS_id_TestRev) left join (SELECT entityName,T_PRESETS_id_preset,T_TOPOLOGY_id_topology,group_concat(if(elemName like '%#%',concat(char(39),entityName,char(39),':',char(39),T_EQUIPMENT_id_equipment,char(39)),concat(char(39),entityName,'_',elemName,char(39),':',char(39),pstValue,char(39)))) as myTuple FROM T_PST_ENTITY join T_TPY_ENTITY on(id_entity=T_TPY_ENTITY_id_entity) where T_PRESETS_id_preset="+str(presetID)+" group by T_TOPOLOGY_id_topology,entityName) as presets on(topology=T_TOPOLOGY_id_topology) where T_SUITES_id_suite="+str(suiteID)+" group by id_TestRev,TCOrder")
	#SELECT entityName,if(elemName like '%#%',concat('"TYPE":"',replace(elemName,'#',''),'","ID":"',T_EQUIPMENT_id_equipment,'"'),concat('"',elemName,'":"',pstValue,'"')) from T_TPY_ENTITY join T_PST_ENTITY on(T_TPY_ENTITY_id_entity=id_entity) where T_TOPOLOGY_id_topology=1 and T_PRESETS_id_preset=62
	#SELECT entityName,T_TOPOLOGY_id_topology,T_PRESETS_id_preset,group_concat(if(elemName like '%#%',concat('\'TYPE\':\'',replace(elemName,'#',''),'\',\'ID\':\'',T_EQUIPMENT_id_equipment,'\''),concat('\'',elemName,'\':\'',pstValue,'\'')) order by elemName) as myTuple from T_TPY_ENTITY join T_PST_ENTITY on(T_TPY_ENTITY_id_entity=id_entity) where T_TOPOLOGY_id_topology=1 and T_PRESETS_id_preset=62 group by entityName
	myRecordSet.execute("select test_id,id_TestRev,test_name,revision,topology,T_SUITES_BODY.run_section,concat('{',group_concat(myTuple),'}') as presets from T_TEST join T_TEST_REVS on(test_id=T_TEST_test_id) join T_SUITES_BODY on(id_TestRev=T_TEST_REVS_id_TestRev) left join (SELECT entityName,T_TOPOLOGY_id_topology,T_PRESETS_id_preset,concat(char(39),entityName,char(39),':[',group_concat(if(elemName like '%#%',concat('[',char(39),'TYPE',char(39),',',char(39),replace(elemName,'#',''),char(39),'],[',char(39),'ID',char(39),',',char(39),T_EQUIPMENT_id_equipment,char(39),']'),concat('[',char(39),elemName,char(39),',',char(39),pstValue,char(39),']')) order by elemName),']') as myTuple from T_TPY_ENTITY join T_PST_ENTITY on(T_TPY_ENTITY_id_entity=id_entity) where T_PRESETS_id_preset="+str(presetID)+" group by T_TOPOLOGY_id_topology,entityName) as presets on(topology=T_TOPOLOGY_id_topology) where T_SUITES_id_suite="+str(suiteID)+" group by id_TestRev,TCOrder order by TCOrder")
	rows = myRecordSet.fetchall()
	#tuningPath=TAWS_path+"Test Case ATM\\TUNED\\"+suiteName+"-TUNED-"+tuningName
	tempStr=''
	test_plan=''
	myIDX=currIDX
	myRepo=Repo(settings.BASE_DIR + settings.GIT_REPO_PATH + settings.GIT_REPO_NAME)
	git=myRepo.git
	for row in rows:
		test_name=str(myIDX).zfill(6)+'_'+str(row['id_TestRev'])+'_'+ntpath.basename(row['test_name'])
		if localTesting == 'off':
			tempStr+='GETTING '+test_name+'...'
			if preview=='off':
				out_file = open(suiteFolder+suiteName+settings.JENKINS['JOB_STRUCT']+test_name,"w")
				out_file.write(git.show(row['revision']+':'+row['test_name']))
				out_file.close()
				os.chmod(suiteFolder+suiteName+settings.JENKINS['JOB_STRUCT']+test_name,511)
		else:
			tempStr+='CREATING LINK FOR '+test_name+'...'
			if os.path.exists(suiteFolder+suiteName+settings.JENKINS['JOB_STRUCT']+test_name):
				tempStr+='Link '+suiteFolder+suiteName+settings.JENKINS['JOB_STRUCT']+test_name+' already present,deleting...'
				shutil.rmtree(suiteFolder+suiteName+settings.JENKINS['JOB_STRUCT']+test_name)
				tempStr+='DONE!\n'
			localPath=suiteFolder+suiteName+settings.JENKINS['JOB_STRUCT']+test_name
			remotePath='/users/'+username+settings.GIT_REPO_PATH + settings.GIT_REPO_NAME+'/'+row['test_name']
			os.symlink(remotePath,localPath)
		if preview=='off':
			with open(suiteFolder+suiteName+settings.JENKINS['JOB_STRUCT']+test_name+'.prs',"w") as out_file:
				#tempStr+=row["presets"]
				json.dump(ast.literal_eval(row["presets"]),out_file,ensure_ascii=False,indent=4,separators=(',',':'))
				#json.dump(row["presets"],out_file,ensure_ascii=False,indent=4,separators=(',',':'))
			out_file.close()
			os.chmod(suiteFolder+suiteName+settings.JENKINS['JOB_STRUCT']+test_name+'.prs',511)
		myIDX+=1
		runSection=row["run_section"]
		runSectonStr=''
		if runSection[0]=='2':runSectonStr+=' --DUTSet'
		if runSection[1]=='2':runSectonStr+=' --testSet'
		if runSection[2]=='2':runSectonStr+=' --testBody'
		if runSection[3]=='2':runSectonStr+=' --testClean'
		if runSection[4]=='2':runSectonStr+=' --DUTClean'
		test_plan+=suiteFolder+suiteName+settings.JENKINS['JOB_STRUCT']+test_name+runSectonStr+'\n'
		#test_plan+=suiteFolder+suiteName+'/workspace/suite/'+test_name+' --pattern '+row["run_section"]+'\n'
		tempStr+='DONE!\n'
	if localTesting == 'off':
		tempStr+='Adding Test Cases to Test plan...'
		out_file = open(suiteFolder+suiteName+settings.JENKINS['JOB_STRUCT']+'suite.txt',"a")
		out_file.write(test_plan)
		out_file.close()
		os.chmod(suiteFolder+suiteName+settings.JENKINS['JOB_STRUCT']+'suite.txt',511)
		tempStr+='DONE!\n\n'
	tempStr+=create_node_list(presetID,suiteFolder,suiteName)

	return {'tuningReport':tempStr,'myIDX':myIDX}

def create_node_list(presetID,suiteFolder,suiteName):

	import mysql.connector
	
	dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
	myRecordSet = dbConnection.cursor(dictionary=True)
	
	tempStr=''
	tempStr+='\nCreating Node List...'
	myRecordSet.execute("SELECT group_concat(distinct T_EQUIPMENT_id_equipment order by T_EQUIPMENT_id_equipment asc) as nodeList FROM T_PST_ENTITY join T_TPY_ENTITY on(T_TPY_ENTITY_id_entity=id_entity) join T_PROD on(replace(elemName,'#','')=T_PROD.product) where T_PRESETS_id_preset="+str(presetID)+" and elemName like '%#%' group by T_EQUIPMENT_id_equipment")
	nodeList=myRecordSet.fetchone()['nodeList']

	out_file = open(suiteFolder+suiteName+settings.JENKINS['JOB_STRUCT']+'nodeList.info',"w")
	out_file.write(nodeList)
	out_file.close()

	tempStr+='DONE!\n'
	
	return tempStr

def createJenkinsENV(suiteName,username,password,localTesting,sharedJob,description):
	import shutil,os
	from jenkinsapi.jenkins import Jenkins
	server = Jenkins(settings.JENKINS['HOST'],username=username,password=password)
	#server = Jenkins('151.98.52.72:7001',username=request.session['login'],password=request.session['password'])
	
	suiteFolder=settings.JENKINS['SUITEFOLDER']
	
	tempStr=''
	
	tempStr+='Working folder : '+suiteFolder+suiteName+settings.JENKINS['JOB_STRUCT']+'\n\n'
	
	if localTesting == 'off':
		tempStr+='Creating workspace structure...\n'
		tempStr+='Check Job '+suiteName+' presence...\n'
		if os.path.exists(suiteFolder+suiteName):
			tempStr+='Job '+suiteName+' already present,deleting workspace...'
			shutil.rmtree(suiteFolder+suiteName)
			tempStr+='DONE!\n'
		if not (server.has_job(suiteName)):
			tempStr+='Job '+suiteName+' creating...'
			tempProperties=''
			if sharedJob == 'off':
				out_file = open(settings.JOB_PROPS_TEMPLATE,"rb")
				tempProperties=out_file.read().decode('UTF-8').replace('[TAWSUSER]',username)
				out_file.close()
			out_file = open(settings.JOB_TEMPLATE,"rb")
			templateXML=out_file.read()
			templateXML=templateXML.decode('UTF-8').replace('[PROPERTIES]',tempProperties)
			templateXML=templateXML.replace('[JOBDESCRIPTION]',description)
			out_file.close()
			#job_instance.update_config(templateXML)
			#job_instance.update_config(job_instance.get_config())
			server.create_job(suiteName,templateXML)
			tempStr+='DONE!\n'
			#job_instance = server.get_job(suiteName)
			#tempStr+='Disabling Jenkins Job : '+suiteName+' ...'
			#job_instance.disable()
			#tempStr+='DONE!\n'
			#tempStr+= 'Name:%s,Is Job Disabled ?:%s' %(suiteName,job_instance.is_enabled())
			#tempStr+='Enabling Jenkins Job : '+suiteName+' ...'
			#job_instance.enable()
			#tempStr+='DONE!\n'
			#tempStr+= 'Name:%s,Is Job Enabled ?:%s' %(suiteName,job_instance.is_enabled())

		#server.build_job(suiteName)
		#server.stop(suiteName)
		#os.chmod(suiteFolder+suiteName,511)
		tempStr+='Setting Permission to folder : '+suiteFolder+suiteName+settings.JENKINS['JOB_STRUCT']+'...'
		os.makedirs(suiteFolder+suiteName+settings.JENKINS['JOB_STRUCT'])
		os.chmod(suiteFolder+suiteName+settings.JENKINS['JOB_STRUCT'],511)
		tempStr+='DONE!\n'
		#os.makedirs(suiteFolder+suiteName+'/workspace/suite')
		#os.chmod(suiteFolder+suiteName+'/workspace/suite',511)
		tempStr+='Setting Permission to folder : '+suiteFolder+suiteName+settings.JENKINS['JOB_STRUCT']+'test-reports...'
		os.makedirs(suiteFolder+suiteName+settings.JENKINS['JOB_STRUCT']+'test-reports')
		os.chmod(suiteFolder+suiteName+settings.JENKINS['JOB_STRUCT']+'test-reports',511)
		tempStr+='DONE!\n'
		tempStr+='Creating Test plan...'
		out_file = open(suiteFolder+suiteName+settings.JENKINS['JOB_STRUCT']+'suite.txt',"w+")
		out_file.write('')
		out_file.close()
		os.chmod(suiteFolder+suiteName+settings.JENKINS['JOB_STRUCT']+'suite.txt',511)
		tempStr+='DONE!\n\n'
	
	return tempStr

def runJenkins(request):

	from jenkinsapi.jenkins import Jenkins
	import shutil

	context = RequestContext(request)
	if 'login' not in request.session:
		context_dict={'fromPage':'runJenkins'}
		return render_to_response('taws/login.html',context_dict,context)

	suiteFolder=settings.JENKINS['SUITEFOLDER']

	jobAction=request.POST.get('jobAction')
	jobName=request.POST.get('jobName')


	server = Jenkins(settings.JENKINS['HOST'],username=request.session['login'],password=request.session['password'])

	if jobAction=='stopJob':
		job_instance = server.get_job(jobName)
		job_instance.disable()
		buildNumber=job_instance.get_last_build()
		buildNumber.stop()

	if jobAction=='deleteJob':
		job_instance = server.get_job(jobName)
		shutil.rmtree(suiteFolder+jobName)
		server.delete_job(jobName)

	jobMatrix=[]
	for j in server.get_jobs():
		job_instance=server.get_job(j[0])
		jobMatrix.append({'name':job_instance.name,'description':job_instance.get_description(),'status':job_instance.is_running(),'enabled':job_instance.is_enabled()})

	context_dict={'login':request.session['login'],'jobMatrix':jobMatrix}

	return render(request,'taws/runJenkins.html',context_dict)

def viewJobDetails(request):

	from jenkinsapi.jenkins import Jenkins
	import os.path,time,re
	import xml.etree.ElementTree as ET

	buildMatrix=[]

	context = RequestContext(request)
	if 'login' not in request.session:
		context_dict={'fromPage':'viewJobDetails'}
		return render_to_response('taws/login.html',context_dict,context)

	server = Jenkins(settings.JENKINS['HOST'],username=request.session['login'],password=request.session['password'])
	suiteFolder=settings.JENKINS['SUITEFOLDER']

	job_name=request.GET.get('jobName')
	buildNumber=0
	
	if (server.has_job(job_name)):
		print('Getting Job '+job_name+' build number...')
		job_instance = server.get_job(job_name)
		buildNumber=job_instance.get_next_build_number()
		print(str(buildNumber)+' build(s) retrieved...')
		for buildId in range(buildNumber-1,0,-1):
			bgcolor=""
			if os.path.isfile(suiteFolder+job_name+'/builds/'+str(buildId)+'/junitResult.xml'):
				#build_instance=job_instance.get_build(buildId)
				#in_file = open(suiteFolder+job_name+'/builds/'+str(buildId)+'/junitResult.xml',"r")
				#tempFile=in_file.read()
				#in_file.close()
				tempFile=''
				tree = ET.parse(suiteFolder+job_name+'/builds/'+str(buildId)+'/junitResult.xml')
				root = tree.getroot()
				total=1
				failed=0
				passed=0
				for suites in root[0]:
					if not re.match('.*_main.*',suites[1].text):
						total+=1
						#Response.Write(suites.text)
						for stderr in suites.iter('stderr'):
							#stderr+=''
							failed+=1
							#Response.Write("	<td style='width:50px'>KO</td>")
							break
						else:
							passed+=1
							#Response.Write("	<td style='width:50px'>OK</td>")
				onClickFunction=chr(34)+"window.open('viewBuildDetails.asp?job="+job_name+"&build='+this.id.replace(/&/g,\'%26\'),'BuildDetails','height=800,width=1000,resizable=no');"+chr(34)
				#buildStatus=build_instance.get_status()
				if failed == 0: buildStatus="SUCCESS"
				if failed != 0: buildStatus="UNSTABLE"
				if buildStatus == "SUCCESS":bgcolor="info"
				#if buildStatus == "ABORTED":bgcolor="yellow"
				if buildStatus == "UNSTABLE":bgcolor="danger"
				#buildDuration=build_instance.get_duration()
				#buildUrl=build_instance.get_result_url()
				#buildTimeStamp=build_instance.get_timestamp()
				buildDuration="0"
				buildUrl=settings.JENKINS['HOST']+"/job/"+job_name+"/"+str(buildId)+"/"
				buildTimeStamp=time.ctime(os.path.getmtime(suiteFolder+job_name+'/builds/'+str(buildId)+'/junitResult.xml'))
			else:
				bgcolor='warning'
				buildStatus = "ABORTED"
				#failed=build_instance['failCount']
				#total=build_instance['totalCount']
				#passed=int(build_instance['totalCount'])-int(build_instance['failCount'])-int(build_instance['skipCount'])
				failed=0
				total=0
				passed=0
				buildTimeStamp="NA"
				buildUrl="NA"
				tempFile=''
				buildDuration="0"
			#	buildStatus="NA"
			#	buildDuration=0
			#	buildUrl=""
			#	buildTimeStamp=0
				onClickFunction=""

			buildMatrix.append({'instance': str(buildId),'status':buildStatus,'duration':buildDuration,'failed':failed,'total':total,'passed':passed,'xmlFile':tempFile,'url':buildUrl,'timeStamp':buildTimeStamp,'onClickFunction':onClickFunction,'bgcolor':bgcolor})
			#print buildMatrix[buildId-1]
	
	
	
	context_dict={'login':request.session['login'],'buildMatrix':buildMatrix,'job_name':job_name,'pageNum':0,'pageList':"NA"}
	return render(request,'taws/viewJobDetails.html',context_dict)

def viewBuildDetails(request):

	import mysql.connector
	import xml.etree.ElementTree as ET
	from os.path import basename
	from datetime import timedelta, datetime
	from jenkinsapi.jenkins import Jenkins

	context = RequestContext(request)
	if 'login' not in request.session:
		context_dict={'fromPage':'viewBuildDetails'}
		return render_to_response('taws/login.html',context_dict,context)

	job_name=request.POST.get('jobName')
	buildId=request.POST.get('buildId')
	target='NA'
	owner='NA'
	KateDB="KO"

	dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
	myRecordSet = dbConnection.cursor(dictionary=True)

	#myRecordSet.execute("select *,count(*) as myCount,if(T_EQUIPMENT_id_equipment is null,'NA',T_EQUIPMENT_id_equipment) as checkNode from T_RUNTIME join T_RTM_BODY on(id_run=T_RUNTIME_id_run) where job_name='"+job_name+"' and job_iteration="+str(buildId))
	myRecordSet.execute("select *,if(T_EQUIPMENT_id_equipment is null,'NA',T_EQUIPMENT_id_equipment) as checkNode,T_EQUIPMENT.name as nodeName,T_EQUIP_TYPE.name as nodeType,T_PACKAGES.label_ref as nodeSWP,T_RUNTIME.owner as suiteOwner,if(id_report is null,'KO','OK') as KateDB from T_RUNTIME left join T_RTM_BODY on(id_run=T_RUNTIME_id_run) join T_EQUIPMENT on(id_equipment=T_EQUIPMENT_id_equipment) join T_EQUIP_TYPE on(id_type=T_EQUIP_TYPE_id_type) join T_PACKAGES on(id_pack=T_RTM_BODY.T_PACKAGES_id_pack) left join (select * from T_REPORT group by T_RUNTIME_id_run) as myReport on(id_run=myReport.T_RUNTIME_id_run) where job_name='"+job_name+"' and job_iteration="+str(buildId))
	
	swp_ref = {}

	for row in myRecordSet:
		owner=row['suiteOwner']
		KateDB=row['KateDB']
		if row['checkNode'] != 'NA': swp_ref[str(row['T_EQUIPMENT_id_equipment'])] = (row['nodeName'],row['nodeType'],row['nodeSWP'],row['id_pack'])

	#row=myRecordSet.fetchone()
	
	#if row['myCount'] > 0:
	#	owner=row['owner']

	server = Jenkins(settings.JENKINS['HOST'],username=request.session['login'],password=request.session['password'])
	suiteFolder=settings.JENKINS['SUITEFOLDER']
	job_instance = server.get_job(job_name)
	build_instance=job_instance.get_build(int(buildId))
	#print build_instance
	#print build_instance.get_status()
	#print build_instance.get_timestamp()
	#print build_instance.get_duration()
	#print build_instance.get_artifacts()
	#print build_instance.get_result_url()
	#print build_instance.get_actions()
	#if 'parameters' in build_instance.get_actions():
	#	for myTuple in build_instance.get_actions()['parameters']:
	#		if myTuple['name']=='TB_NODE_IP':
	#			target=myTuple['value']
	#			break
	#else:
	#	target='NA'
	#print build_instance.get_resultset().keys()
	tree = ET.parse(suiteFolder+job_name+'/builds/'+str(buildId)+'/junitResult.xml')
	root = tree.getroot()

	buildMatrix=[]
	counter=1
	#for suites in root[0]:
	for suites in root.findall(".suites/suite"):
		if (suites.find('name').text.rfind('_main')>=0 or suites.find('name').text.rfind('_Main')>=0) and suites.find('name').text.rfind('EnvSettings')<0:
			testName=suites.find('name').text.replace('(','').replace('.XML)','').replace('._main','').replace('._Main','')
			for myCase in suites.findall('.cases/case'):
				if myCase.find('skipped').text=='false' and myCase.find('stderr')!=None:
					testStatus='Failed'
					bgcolor='danger'
					fontcolor="white"
					break
				else:
					testStatus='Passed'
					bgcolor='info'
					fontcolor="black"
			tpsList=[]
			for tps in root.findall(".suites/suite"):
				if tps.find('name').text.rfind(testName)>=0 and tps.find('name').text.rfind('_main')<0 and tps.find('name').text.rfind('_Main')<0:
					tpsTemp=tps.find('name').text.replace('(','').replace('.XML)','').replace(testName+'.','').split('_')
					tpsName=tpsTemp[2].replace('-','.')
					tpsArea=tpsTemp[1]

					#myRecordSet.execute("select T_EQUIP_TYPE.name as eType from T_EQUIPMENT join T_EQUIP_TYPE on(id_type=T_EQUIP_TYPE_id_type) where id_equipment="+tpsTemp[0].replace('[','').replace(']','')+" limit 1")
					
					nodeName='NA'
					nodeType='NA'
					nodeSWP='NA'
					id_pack="NA"
					if tpsTemp[0].replace('[','').replace(']','') in swp_ref:
						nodeName=swp_ref[tpsTemp[0].replace('[','').replace(']','')][0]
						nodeType=swp_ref[tpsTemp[0].replace('[','').replace(']','')][1]
						nodeSWP=swp_ref[tpsTemp[0].replace('[','').replace(']','')][2]
						id_pack=swp_ref[tpsTemp[0].replace('[','').replace(']','')][3]
						

					#tpsProd=myRecordSet.fetchone()['eType']
					tpsBgcolor='info'
					tpsFontcolor="black"
					tpsTestStatus='Passed'
					for stderr in tps.iter('stderr'):
						#stderr+=''
						tpsBgcolor='danger'
						tpsFontcolor="white"
						tpsTestStatus='Failed'
						break
					tpsList.append({'nodeName':nodeName,'nodeType':nodeType,'nodeSWP':nodeSWP,'id_pack':id_pack,'tpsName':tpsName,'tpsArea':tpsArea,'tpsBgcolor':tpsBgcolor,'tpsFontcolor':tpsFontcolor})
			buildMatrix.append({'bgcolor':bgcolor,
				'fontcolor':fontcolor,
				'counter':counter,
				'testName':testName,
				'testStatus':testStatus,
				'testDuration':suites.find('duration').text,
				'tpsList':tpsList,
				'numTps':len(tpsList)})
			counter+=1

	context_dict={'login':request.session['login'],
		'job_name':job_name,
		'instance': str(buildId),
		'owner':owner,
		'KateDB':KateDB,
		'status':build_instance.get_status(),
		'duration':str(build_instance.get_duration()),
		'failCount':str(build_instance.get_actions()['failCount']),
		'totalCount':str(build_instance.get_actions()['totalCount']),
		'skipCount':str(build_instance.get_actions()['skipCount']),
		'url':build_instance.get_result_url(),
		'target':target,
		'timeStamp':build_instance.get_timestamp(),
		'buildMatrix':buildMatrix}
	return render(request,'taws/viewBuildDetails.html',context_dict)

def collectReports(request):

	import mysql.connector
	import xml.etree.ElementTree as ET
	from jenkinsapi.jenkins import Jenkins
	from django.utils.safestring import mark_safe
	from os.path import basename
	from datetime import timedelta, datetime

	context = RequestContext(request)
	if 'login' not in request.session:
		context_dict={'fromPage':'collectReports'}
		return render_to_response('taws/login.html',context_dict,context)

	job_name=request.POST.get('jobName')
	buildId=request.POST.get('buildId')
	azione=request.POST.get('azione')
	KateDB="KO"


	dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
	myRecordSet = dbConnection.cursor(dictionary=True)

	myRecordSet.execute("select *,if(T_EQUIPMENT_id_equipment is null,'NA',T_EQUIPMENT_id_equipment) as checkNode,T_EQUIPMENT.name as nodeName,T_EQUIP_TYPE.name as nodeType,T_PACKAGES.label_ref as nodeSWP,T_RUNTIME.owner as suiteOwner,if(id_report is null,'KO','OK') as KateDB from T_RUNTIME left join T_RTM_BODY on(id_run=T_RUNTIME_id_run) join T_EQUIPMENT on(id_equipment=T_EQUIPMENT_id_equipment) join T_EQUIP_TYPE on(id_type=T_EQUIP_TYPE_id_type) join T_PACKAGES on(id_pack=T_RTM_BODY.T_PACKAGES_id_pack) left join (select * from T_REPORT group by T_RUNTIME_id_run) as myReport on(id_run=myReport.T_RUNTIME_id_run) where job_name='"+job_name+"' and job_iteration="+str(buildId))
	
	swp_ref = {}

	for row in myRecordSet:
		id_run=row['id_run']
		KateDB=row['KateDB']
		if row['checkNode'] != 'NA': swp_ref[str(row['T_EQUIPMENT_id_equipment'])] = (row['nodeName'],row['nodeType'],row['nodeSWP'],row['id_pack'])

	server = Jenkins(settings.JENKINS['HOST'],username=request.session['login'],password=request.session['password'])
	suiteFolder=settings.JENKINS['SUITEFOLDER']
	job_instance = server.get_job(job_name)
	build_instance=job_instance.get_build(int(buildId))

	tree = ET.parse(suiteFolder+job_name+'/builds/'+str(buildId)+'/junitResult.xml')
	root = tree.getroot()

	buildMatrix=[]
	counter=1
	noteCounter=1
	JIRAcsv=''
	myReport=''
	numRowsAffected=0
	#for suites in root[0]:
	for suites in root.findall(".suites/suite"):
		if (suites.find('name').text.rfind('_main')>=0 or suites.find('name').text.rfind('_Main')>=0) and suites.find('name').text.rfind('EnvSettings')<0:
			testName=suites.find('name').text.replace('(','').replace('.XML)','').replace('._main','').replace('._Main','')
			testID=testName.split('_')[1]
			for stderr in suites.iter('stderr'):
				testStatus='Failed'
				bgcolor='danger'
				bgimage='thumbs-down'
				fontcolor="white"
				break
			else:
				testStatus='Passed'
				bgcolor='info'
				bgimage='thumbs-up'
				fontcolor="black"
			tpsList=[]
			for tps in root.findall(".suites/suite"):
				if tps.find('name').text.rfind(testName)>=0 and tps.find('name').text.rfind('_main')<0 and tps.find('name').text.rfind('_Main')<0:
					tpsTemp=tps.find('name').text.replace('(','').replace('.XML)','').replace(testName+'.','').split('_')
					tpsName=tpsTemp[2]
					tpsArea=tpsTemp[1]


					nodeName='NA'
					nodeType='NA'
					nodeSWP='NA'
					if tpsTemp[0].replace('[','').replace(']','') in swp_ref:
						nodeName=swp_ref[tpsTemp[0].replace('[','').replace(']','')][0]
						nodeType=swp_ref[tpsTemp[0].replace('[','').replace(']','')][1]
						nodeSWP=swp_ref[tpsTemp[0].replace('[','').replace(']','')][2]
						id_pack=swp_ref[tpsTemp[0].replace('[','').replace(']','')][3]


					tpsTestStatus='Passed'
					tpsBgcolor='info'
					tpsFontcolor="black"
					errMsg="NA"
					Tstr='PTNSW-19209'
					
					for stderr in tps.iter('stderr'):
						tpsTestStatus='Failed'
						tpsBgcolor='danger'
						tpsFontcolor="white"
						errMsg=stderr.text
						break

					if azione == "addResult":
						#myRecordSet.execute("INSERT INTO T_REPORT (SELECT '',"+str(id_pack)+",(SELECT * FROM T_TPS join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on(id_area=T_AREA_id_area ) where tps_reference='"+tpsName+"' and area_name='"+tpsArea+"'),'"+errMsg+"','"+tpsTestStatus+"','"+request.POST.get('note'+str(noteCounter),"NA")+"')")
						myCursor=myRecordSet.execute("INSERT INTO T_REPORT (SELECT null,"+str(id_pack)+",id_tps,"+str(id_run)+",'"+errMsg.replace('\\','\\\\').replace('\'','\\\'')+"','"+tpsTestStatus+"','"+request.POST.get('note'+str(noteCounter),"NA")+"','"+request.session['login']+"',null FROM T_TPS join T_TEST_REVS on(id_TestRev=T_TEST_REVS_id_TestRev) join T_DOMAIN on(T_DOMAIN_id_domain=id_domain) join T_AREA on(id_area=T_AREA_id_area ) join T_PROD on(T_PROD_id_prod=id_prod) where tps_reference='"+tpsName+"' and area_name='"+tpsArea+"' and id_TestRev="+testID+")")
						numRowsAffected+=myCursor.rowcount
						#myReport+="INSERT INTO T_REPORT (SELECT null,"+str(id_pack)+",id_tps,"+str(id_run)+",'"+errMsg.replace('\\','\\\\').replace('\'','\\\'')+"','"+tpsTestStatus+"','"+request.POST.get('note'+str(noteCounter),"NA")+"','"+request.session['login']+"',null FROM T_TPS join T_TEST_REVS on(id_TestRev=T_TEST_REVS_id_TestRev) join T_DOMAIN on(T_DOMAIN_id_domain=id_domain) join T_AREA on(id_area=T_AREA_id_area ) join T_PROD on(T_PROD_id_prod=id_prod) where tps_reference='"+tpsName+"' and area_name='"+tpsArea+"' and id_TestRev="+testID+")<br>"
						#nodeType="INSERT INTO T_REPORT (SELECT '',"+str(id_pack)+",(SELECT * FROM T_TPS join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on(id_area=T_AREA_id_area ) where tps_reference='"+tpsName+"' and area_name='"+tpsArea+"'),'"+errMsg+"','"+tpsTestStatus+"','"+request.POST.get('note'+str(noteCounter),"NA")+"')"
						#myRecordSet.execute("select *,if(T_EQUIPMENT_id_equipment is null,'NA',T_EQUIPMENT_id_equipment) as checkNode,T_EQUIPMENT.name as nodeName,T_EQUIP_TYPE.name as nodeType,T_PACKAGES.label_ref as nodeSWP,T_RUNTIME.owner as suiteOwner from T_RUNTIME left join T_RTM_BODY on(id_run=T_RUNTIME_id_run) join T_EQUIPMENT on(id_equipment=T_EQUIPMENT_id_equipment) join T_EQUIP_TYPE on(id_type=T_EQUIP_TYPE_id_type) join T_PACKAGES on(id_pack=T_RTM_BODY.T_PACKAGES_id_pack)  where job_name='"+job_name+"' and job_iteration="+str(buildId))
						dbConnection.commit()

					if azione == "exportJIRA":
						userJIRA='ptnsvtaut'
						pwdJIRA='ptnsvtaut'
						zq_comment = nodeSWP+" - "+nodeType+" - ("+tpsTestStatus+")"
						myRecordSet.execute("SELECT story_reference FROM T_TPS join T_TEST_REVS on(id_TestRev=T_TEST_REVS_id_TestRev) join T_DOMAIN on(T_DOMAIN_id_domain=id_domain) join T_AREA on(id_area=T_AREA_id_area ) join T_PROD on(T_PROD_id_prod=id_prod) join T_JIRA_STORY using(T_DOMAIN_id_domain) where tps_reference='"+tpsName+"' and area_name='"+tpsArea+"' and id_TestRev="+testID)
						row=myRecordSet.fetchone()
						JIRAcsv+="call jira -s \"http://sts.app.alcatel-lucent.com\" -u \""+userJIRA+"\" -p \""+pwdJIRA+"\" -a runFromIssueList --common \"--action progressIssue --issue @issue@ --step \\\\\"Re Run\\\\\"\" --search \"project=PTNSW and issuetype=\\\\\"Test Case Sub-Task\\\\\" and issuefunction in subtasksOf(\\\\\"issueKey="+row['story_reference']+"\\\\\") and status!= \\\\\""+tpsTestStatus+"\\\\\" and summary ~ \\\\\""+tpsName.replace('-','.')+" \\\\\"\"\\n"
						if tpsTestStatus == 'Failed':
							JIRAcsv+="call jira -s \"http://sts.app.alcatel-lucent.com\" -u \""+userJIRA+"\" -p \""+pwdJIRA+"\" -a runFromIssueList --common \"--action linkIssue --issue @issue@ --toIssue \\\\\""+Tstr+"\\\\\" --link \\\\\"Related\\\\\"\" --search \"project=PTNSW and issuetype=\\\\\"Test Case Sub-Task\\\\\" and issuefunction in subtasksOf(\\\\\"issueKey="+row['story_reference']+"\\\\\") and status!= \\\\\""+tpsTestStatus+"\\\\\" and summary ~ \\\\\""+tpsName.replace('-','.')+" \\\\\"\"\\n"
						JIRAcsv+="call jira -s \"http://sts.app.alcatel-lucent.com\" -u \""+userJIRA+"\" -p \""+pwdJIRA+"\" -a runFromIssueList --common \"--action progressIssue --issue @issue@ --step \\\\\""+tpsTestStatus+"\\\\\"\" --search \"project=PTNSW and issuetype=\\\\\"Test Case Sub-Task\\\\\" and issuefunction in subtasksOf(\\\\\"issueKey="+row['story_reference']+"\\\\\") and status!= \\\\\""+tpsTestStatus+"\\\\\" and summary ~ \\\\\""+tpsName.replace('-','.')+" \\\\\"\"\\n"
						JIRAcsv+="call jira -s \"http://sts.app.alcatel-lucent.com\" -u \""+userJIRA+"\" -p \""+pwdJIRA+"\" -a runFromIssueList --common \"--action addComment --issue @issue@ --comment \\\\\""+zq_comment+"\\\\\"\" --search \"project=PTNSW and issuetype=\\\\\"Test Case Sub-Task\\\\\" and issuefunction in subtasksOf(\\\\\"issueKey="+row['story_reference']+"\\\\\") and summary ~ \\\\\""+tpsName.replace('-','.')+" \\\\\"\"\\n"




					tpsList.append({'nodeName':nodeName,'nodeType':nodeType,'nodeSWP':nodeSWP,'noteCounter':noteCounter,'tpsName':tpsName,'tpsArea':tpsArea,'tpsBgcolor':tpsBgcolor,'tpsFontcolor':tpsFontcolor})
					noteCounter+=1
			buildMatrix.append({'bgcolor':bgcolor,
				'fontcolor':fontcolor,
				'counter':counter,
				'testName':testName,
				'testStatus':testStatus,
				'testDuration':suites.find('duration').text,
				'tpsList':tpsList,
				'bgimage':bgimage,
				'numRowsAffected':numRowsAffected,
				'numTps':len(tpsList)})
			counter+=1

	context_dict={'login':request.session['login'],
		'status':build_instance.get_status(),
		'duration':str(build_instance.get_duration()),
		'failCount':str(build_instance.get_actions()['failCount']),
		'totalCount':str(build_instance.get_actions()['totalCount']),
		'skipCount':str(build_instance.get_actions()['skipCount']),
		'job_name':job_name,
		'azione':azione,
		'KateDB':KateDB,
		'instance': str(buildId),
		'JIRAcsv':mark_safe(JIRAcsv),
		'buildMatrix':buildMatrix,
		'myReport':myReport}
	return render(request,'taws/collectReports.html',context_dict)


def createRunJenkins(request):

	from jenkinsapi.jenkins import Jenkins
	import mysql.connector
	import json
	import os,glob
	import shutil
	from django.http import HttpResponseRedirect

	context = RequestContext(request)
	if 'login' not in request.session:
		context_dict={'fromPage':'createRunJenkins'}
		return render_to_response('taws/login.html',context_dict,context)

	job_name=request.POST.get('jobName')
	action=request.POST.get('azione')
	target=request.POST.get('target','')
	swRelMatrix=[]
	runID=''
	reportPath=settings.JENKINS['SUITEFOLDER']+job_name+settings.JENKINS['JOB_STRUCT']+'test-reports/'
	
	
	suiteFolder=settings.JENKINS['SUITEFOLDER']

	in_file = open(suiteFolder+job_name+'/workspace/nodeList.info',"r")
	nodeFile=in_file.read()
	in_file.close()

	tempFile=nodeFile.split(',')

	sqlStr=''
	for myFile in tempFile:
		if sqlStr != '':sqlStr+=' OR '
		sqlStr+='id_equipment='+myFile

	dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
	myRecordSet = dbConnection.cursor(dictionary=True)

	myRecordSet.execute("SET group_concat_max_len = 200000")
	dbConnection.commit()

	#myRecordSet.execute("select *,group_concat(piddu) as swRelList from (select id_equipment,T_EQUIP_TYPE.name as prodName,concat(sw_rel_name,'#',group_concat(concat(T_PACKAGES.label_ref,'|',id_pack) separator '%')) as piddu,T_EQUIPMENT.name as eqptName,owner,T_EQUIPMENT.description,T_PACKAGES.label_ref from T_EQUIPMENT join T_EQUIP_TYPE on(T_EQUIP_TYPE_id_type=id_type) left join T_PROD on(T_EQUIP_TYPE.name=T_PROD.product) left join T_PACKAGES on(T_PROD.id_prod=T_PACKAGES.T_PROD_id_prod) left join T_SW_REL on(id_sw_rel=T_SW_REL_id_sw_rel) where id_equipment=1 or id_equipment=3 or id_equipment=4 or id_equipment=6 group by T_PROD.product,sw_rel_name) as mytable group by prodName")
	myRecordSet.execute("select *,group_concat(packList) as packList ,group_concat(sw_rel_name) as swRelList from (select id_equipment,T_EQUIP_TYPE.name as prodName,sw_rel_name,group_concat(concat(T_PACKAGES.label_ref,'|',id_pack) separator '%') as packList,T_EQUIPMENT.name as eqptName,owner,T_PACKAGES.label_ref from T_EQUIPMENT join T_EQUIP_TYPE on(T_EQUIP_TYPE_id_type=id_type) left join T_PROD on(T_EQUIP_TYPE.name=T_PROD.product) left join T_PACKAGES on(T_PROD.id_prod=T_PACKAGES.T_PROD_id_prod) left join T_SW_REL on(id_sw_rel=T_SW_REL_id_sw_rel) where "+sqlStr+" group by T_PROD.product,sw_rel_name) as mytable group by prodName")

	for row in myRecordSet:
		if str(row['swRelList'])!='None':
			tempStr1=str(row['swRelList']).split(',')
			tempStr2=str(row['packList']).split(',')
			packageList=[]
			for myIndex in range(0,len(tempStr1)):
				packageList.append({'swRelList':tempStr1[myIndex],'packList':tempStr2[myIndex]})
		else:
			packageList='None'
		swRelMatrix.append({'prodName':row['prodName'],
			'packageList':packageList,
			'eqptName':row['eqptName'],
			'owner':row['owner'],
			'id_equipment':row['id_equipment']})

	if action == 'runTest':
		
		tempTarget=target.split('$')
		myRecordSet.execute("SELECT if(MAX(id_run) is null,0,MAX(id_run)) as maxId from T_RUNTIME")
		runID=myRecordSet.fetchone()['maxId']+1
		myRecordSet.execute("INSERT INTO T_RUNTIME (id_run,job_name,job_iteration,owner,status) VALUES("+str(runID)+",'"+job_name+"',1,'"+request.session['login']+"','READY')")
		dbConnection.commit()
		for myItem in tempTarget:
			tempValue=myItem.split('#')
			myRecordSet.execute("INSERT INTO T_RTM_BODY (T_RUNTIME_id_run,T_EQUIPMENT_id_equipment,T_PACKAGES_id_pack,forceLoad) VALUES("+str(runID)+","+tempValue[0]+","+tempValue[1]+","+tempValue[2]+")")
			dbConnection.commit()

		server = Jenkins(settings.JENKINS['HOST'],username=request.session['login'],password=request.session['password'])
		if (server.has_job(job_name)):
			job_instance = server.get_job(job_name)
			if os.path.exists(reportPath):
				files = glob.glob(reportPath + '*.XML')
				for f in files: os.remove(f)
			job_instance.invoke(securitytoken='tl-token',build_params={'KateRunId':runID})
		
		return HttpResponseRedirect('/taws/runJenkins/')
	else:
		context_dict={'login':request.session['login'],
			'job_name':job_name,
			'action': action,
			'swRelMatrix':swRelMatrix,
			'target':target,
			'runID':runID}

		#return render(request,'taws/createRunJenkins.html',context_dict)

		return HttpResponse(json.dumps(context_dict),
							content_type="application/json"
					)

def add_bench(request):

	import mysql.connector

	context = RequestContext(request)
	if 'login' not in request.session:
		context_dict={'fromPage':'add_bench'}
		return render_to_response('taws/login.html',context_dict,context)

	dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
	myRecordSet = dbConnection.cursor(dictionary=True,buffered=True)

	bench=request.GET.get('bench','NONE')
	action=request.GET.get('action','')

	POSTname=request.POST.get('name','')

	POSTip1=request.POST.get('ip1','')
	POSTip2=request.POST.get('ip2','')
	POSTip3=request.POST.get('ip3','')
	POSTip4=request.POST.get('ip4','')

	POSTnm1=request.POST.get('nm1','')
	POSTnm2=request.POST.get('nm2','')
	POSTnm3=request.POST.get('nm3','')
	POSTnm4=request.POST.get('nm4','')

	POSTgw1=request.POST.get('gw1','')
	POSTgw2=request.POST.get('gw2','')
	POSTgw3=request.POST.get('gw3','')
	POSTgw4=request.POST.get('gw4','')
	
	POSTreference=request.POST.get('reference','')
	POSTsite=request.POST.get('site','')
	POSTroom=request.POST.get('room','')
	POSTrow=request.POST.get('row','')
	POSTrack=request.POST.get('rack','')
	POSTpos=request.POST.get('pos','')
	POSTproduct=request.POST.get('product','')
	POSTscope=request.POST.get('scope','')
	POSTnote=request.POST.get('note','')
	POSTdescription=request.POST.get('description','')

	if action == 'create': bench=''

	debugInterface=request.POST.get('debugInterface','')
	credList=request.POST.get('credList','')

	name=''
	ip='...'
	nm='...'
	gw='...'
	reference=''
	site=''
	room=''
	product=''
	scope=''
	row=''
	rack=''
	pos=''
	serials=[]
	credentials=[]
	createReport=''
	rowID=''
	note=''
	description=''

	if action == 'create' or action == 'update':
		myRecordSet.execute("SELECT count(*) as myCount from T_EQUIPMENT WHERE name='"+POSTname+"' and id_equipment<>'"+bench+"' limit 1")
		#createReport+="SELECT count(*) as myCount from T_EQUIPMENT WHERE name='"+POSTname+"' and id_equipment<>'"+bench+"'"
		row=myRecordSet.fetchone()
		if row['myCount'] > 0:createReport+='Bench Name '+POSTname+' already present\\n'
		myRecordSet.execute("SELECT count(*) as myCount from T_NET WHERE IP='"+POSTip1+'.'+POSTip2+'.'+POSTip3+'.'+POSTip4+"' and inUse=1 and T_EQUIPMENT_id_equipment<>'"+bench+"' limit 1")
		#createReport+="SELECT count(*) as myCount from T_NET WHERE IP='"+POSTip1+'.'+POSTip2+'.'+POSTip3+'.'+POSTip4+"' and inUse=1 and T_EQUIPMENT_id_equipment<>'"+bench+"'"
		row=myRecordSet.fetchone()
		if row['myCount'] > 0:createReport+='IP ADDRESS '+POSTip1+'.'+POSTip2+'.'+POSTip3+'.'+POSTip4+' already in use\\n'
		if debugInterface != '':
			if debugInterface.rfind('$')>=0:
				debugInterfaceAry=debugInterface.split('$')
			else:
				debugInterfaceAry=[debugInterface]
			for myITF in debugInterfaceAry:
				tempFields=myITF.split('#')
				myRecordSet.execute("SELECT count(*) as myCount FROM T_SERIAL join T_NET on(id_ip=T_NET_id_ip) WHERE IP='"+tempFields[0]+"' and port="+tempFields[1]+" and T_NET.inUse=1 and T_SERIAL.T_EQUIPMENT_id_equipment<>'"+bench+"' limit 1")
				#createReport+="SELECT count(*) as myCount FROM T_SERIAL join T_NET on(id_ip=T_NET.id_ip) WHERE IP='"+tempFields[0]+"' and port="+tempFields[1]+" and T_NET.inUse=1 and T_NET.T_EQUIPMENT_id_equipment<>'"+bench+"'"
				row=myRecordSet.fetchone()
				if row['myCount'] > 0:createReport+='SERIAL IP ADDRESS '+tempFields[0]+' port '+tempFields[1]+' already in use\\n'
	if createReport!='': bench=request.GET.get('bench','')
	if createReport=='' and (action == 'create' or action == 'update'):
		myRecordSet.execute("SELECT id_type from T_EQUIP_TYPE WHERE name='"+POSTproduct+"' limit 1")
		id_type=myRecordSet.fetchone()['id_type']
		myRecordSet.execute("SELECT id_location,count(*) as locationCounter from T_LOCATION WHERE site='"+POSTsite+"' and room='"+POSTroom+"' and row='"+POSTrow+"' and rack='"+POSTrack+"' and pos='"+POSTpos+"' limit 1")
		row=myRecordSet.fetchone()
		if row['locationCounter'] == 0:
			myRecordSet.execute("INSERT INTO T_LOCATION (site,room,row,rack,pos) VALUES ('"+POSTsite+"','"+POSTroom+"','"+POSTrow+"','"+POSTrack+"','"+POSTpos+"')")
			dbConnection.commit()
			myRecordSet.execute("SELECT id_location from T_LOCATION WHERE site='"+POSTsite+"' and room='"+POSTroom+"' and row='"+POSTrow+"' and rack='"+POSTrack+"' and pos='"+POSTpos+"'")
			row=myRecordSet.fetchone()
		id_location=row['id_location']
		myRecordSet.execute("SELECT id_scope from T_SCOPE WHERE description='"+POSTscope+"' limit 1")
		id_scope=myRecordSet.fetchone()['id_scope']
		if action == 'create':
			myRecordSet.execute("INSERT INTO T_EQUIPMENT (name, T_EQUIP_TYPE_id_type, T_LOCATION_id_location, T_SCOPE_id_scope, T_PACKAGES_id_pack, owner, inUse, description, note) VALUES ('"+POSTname+"', "+str(id_type)+", "+str(id_location)+", "+str(id_scope)+", null, '"+POSTreference+"', 0, '"+POSTdescription+"', '"+POSTnote+"')")
			dbConnection.commit()
			myRecordSet.execute("SELECT id_equipment from T_EQUIPMENT WHERE name='"+POSTname+"' limit 1")
			id_equipment=myRecordSet.fetchone()['id_equipment']
		else:
			myRecordSet.execute("UPDATE T_EQUIPMENT set name='"+POSTname+"', T_EQUIP_TYPE_id_type="+str(id_type)+", T_LOCATION_id_location="+str(id_location)+", T_SCOPE_id_scope="+str(id_scope)+", owner='"+POSTreference+"', inUse=1, description='"+POSTdescription+"', note='"+POSTnote+"' WHERE id_equipment="+bench)
			dbConnection.commit()
			id_equipment=bench
		myRecordSet.execute("DELETE FROM T_NET WHERE T_EQUIPMENT_id_equipment='"+str(id_equipment)+"'")
		dbConnection.commit()
		myRecordSet.execute("SELECT count(*) as netCounter FROM T_NET where IP='"+POSTip1+"."+POSTip2+"."+POSTip3+"."+POSTip4+"' and NM='"+POSTnm1+"."+POSTnm2+"."+POSTnm3+"."+POSTnm4+"' and GW='"+POSTgw1+"."+POSTgw2+"."+POSTgw3+"."+POSTgw4+"' and T_EQUIPMENT_id_equipment="+str(id_equipment))
		row=myRecordSet.fetchone()
		if row['netCounter'] == 0:
			myRecordSet.execute("SELECT count(*) as netCounter FROM T_NET where IP='"+POSTip1+"."+POSTip2+"."+POSTip3+"."+POSTip4+"' and NM='"+POSTnm1+"."+POSTnm2+"."+POSTnm3+"."+POSTnm4+"' and GW='"+POSTgw1+"."+POSTgw2+"."+POSTgw3+"."+POSTgw4+"'")
			row=myRecordSet.fetchone()
			if row['netCounter'] == 0:
				myRecordSet.execute("INSERT INTO T_NET (inUse,description,T_EQUIPMENT_id_equipment,protocol,IP,NM,GW) VALUES (1,'',"+str(id_equipment)+",'v4','"+POSTip1+"."+POSTip2+"."+POSTip3+"."+POSTip4+"','"+POSTnm1+"."+POSTnm2+"."+POSTnm3+"."+POSTnm4+"','"+POSTgw1+"."+POSTgw2+"."+POSTgw3+"."+POSTgw4+"')")
				dbConnection.commit()
		#myRecordSet.execute("SELECT id_ip from T_NET WHERE IP='"+POSTip1+"."+POSTip2+"."+POSTip3+"."+POSTip4+"'")
		#id_ip=myRecordSet.fetchone()['id_ip']
		myRecordSet.execute("UPDATE T_NET SET T_EQUIPMENT_id_equipment="+str(id_equipment)+" WHERE IP='"+POSTip1+"."+POSTip2+"."+POSTip3+"."+POSTip4+"' AND NM='"+POSTnm1+"."+POSTnm2+"."+POSTnm3+"."+POSTnm4+"' AND GW='"+POSTgw1+"."+POSTgw2+"."+POSTgw3+"."+POSTgw4+"'")
		dbConnection.commit()
		myRecordSet.execute("DELETE from T_SERIAL where T_EQUIPMENT_id_equipment="+str(id_equipment))
		dbConnection.commit()
		if debugInterface != '':
			if debugInterface.rfind('$')>=0:
				debugInterfaceAry=debugInterface.split('$')
			else:
				debugInterfaceAry=[debugInterface]
			for myITF in debugInterfaceAry:
				tempFields=myITF.split('#')
				myRecordSet.execute("SELECT id_ip from T_NET WHERE IP='"+tempFields[0]+"'")
				id_ip=str(myRecordSet.fetchone()['id_ip'])
				myRecordSet.execute("UPDATE T_NET SET inUse=1 where id_ip="+id_ip)
				dbConnection.commit()
				#myRecordSet.execute("SELECT count(*) as myCount FROM T_SERIAL  WHERE T_NET_id_ip="+id_ip+" and port="+tempFields[1]+" and inUse=1")
				#if myRecordSet.fetchone()['myCount']>0:
				#	myRecordSet.execute("UPDATE T_SERIAL SET inUse=1 where id_ip="+id_ip+" and port="+tempFields[1])
				#	dbConnection.commit()
				#else:
				if tempFields[2] == '':tempFields[2]='0'
				if tempFields[3] == '':tempFields[3]='0'
				myRecordSet.execute("INSERT INTO T_SERIAL (inUse, T_NET_id_ip, port, T_EQUIPMENT_id_equipment, slot, subslot, note) VALUES (1,'"+id_ip+"','"+tempFields[1]+"',"+str(id_equipment)+",'"+tempFields[2]+"','"+tempFields[3]+"','')")
				dbConnection.commit()
		
		if credList != '':
			credList=credList.split('$')
			myRecordSet.execute("DELETE from T_EQPT_CRED where T_EQUIPMENT_id_equipment="+str(id_equipment))
			dbConnection.commit()
			for myITF in credList:
				tempFields=myITF.split('#')
				#if tempFields[1] == '':tempFields[1]='0'
				#if tempFields[2] == '':tempFields[2]='0'
				myRecordSet.execute("INSERT INTO T_EQPT_CRED (T_EQPT_CRED_TYPE_id_cred_type, T_EQUIPMENT_id_equipment, usr, pwd) VALUES ("+str(tempFields[0])+", "+str(id_equipment)+", '"+str(tempFields[1])+"','"+str(tempFields[2])+"')")
				dbConnection.commit()
		
		bench=id_equipment


	if bench != 'NONE' and bench != '':
		SQL="SELECT *,T_NET.IP as benchIP,T_NET.NM as benchNM,T_NET.GW as benchGW,T_EQUIPMENT.description as benchDescription,T_EQUIPMENT.note as benchNote,group_concat(concat(ip1.ip,'#',port,'#',if(slot is null,'-',slot),'#',if(subslot is null,'-',subslot)) separator '|') as serials,T_SCOPE.description as scope,T_EQUIP_TYPE.name as type,T_EQUIPMENT.name as benchName,if(status like '%ING%',status,'IDLE') as benchStatus,T_EQUIPMENT.owner as reference,runtime.owner as author FROM T_EQUIPMENT LEFT JOIN (select * from T_RTM_BODY left join T_RUNTIME on(id_run=T_RUNTIME_id_run) where status='RUNNING') as runtime on(id_equipment=T_EQUIPMENT_id_equipment) left join T_EQUIP_TYPE on(id_type=T_EQUIP_TYPE_id_type) left join T_NET on(T_NET.T_EQUIPMENT_id_equipment=id_equipment) LEFT JOIN T_LOCATION on(T_LOCATION_id_location=id_location) LEFT JOIN T_SERIAL on(T_SERIAL.T_EQUIPMENT_id_equipment=id_equipment) LEFT JOIN T_SCOPE on(T_SCOPE_id_scope=id_scope) LEFT JOIN T_NET as ip1 on(T_SERIAL.T_NET_id_ip=ip1.id_ip) where id_equipment="+str(bench)+" group by id_equipment"
		SQL="SELECT *,T_NET.IP as benchIP,T_NET.NM as benchNM,T_NET.GW as benchGW,serials,T_EQUIPMENT.description as benchDescription,T_EQUIPMENT.note as benchNote,T_SCOPE.description as scope,T_EQUIP_TYPE.name as type,T_EQUIPMENT.name as benchName,if(status like '%ING%',status,'IDLE') as benchStatus,T_EQUIPMENT.owner as reference,runtime.owner as author FROM T_EQUIPMENT LEFT JOIN (select * from T_RTM_BODY left join T_RUNTIME on(id_run=T_RUNTIME_id_run) where status='RUNNING') as runtime on(id_equipment=T_EQUIPMENT_id_equipment) left join T_EQUIP_TYPE on(id_type=T_EQUIP_TYPE_id_type) left join T_NET on(T_NET.T_EQUIPMENT_id_equipment=id_equipment) LEFT JOIN T_LOCATION on(T_LOCATION_id_location=id_location) LEFT JOIN (select group_concat(concat(ip,'#',port,'#',if(slot is null,'-',slot),'#',if(subslot is null,'-',subslot)) separator '|') as serials,T_SERIAL.T_EQUIPMENT_id_equipment from T_SERIAL JOIN T_NET on(T_NET_id_ip=id_ip) where T_SERIAL.T_EQUIPMENT_id_equipment="+str(bench)+") as serials on(serials.T_EQUIPMENT_id_equipment=id_equipment) LEFT JOIN T_SCOPE on(T_SCOPE_id_scope=id_scope)  left join T_EQPT_CRED on(T_EQPT_CRED.T_EQUIPMENT_id_equipment=id_equipment) left join T_EQPT_CRED_TYPE on(T_EQPT_CRED_TYPE_id_cred_type=idT_EQPT_CRED_TYPE) where id_equipment="+str(bench)
		SQL="SELECT *,T_NET.IP as benchIP,T_NET.NM as benchNM,T_NET.GW as benchGW,serials,credentials,T_EQUIPMENT.description as benchDescription,T_EQUIPMENT.note as benchNote,T_SCOPE.description as scope,T_EQUIP_TYPE.name as type,T_EQUIPMENT.name as benchName,if(status like '%ING%',status,'IDLE') as benchStatus,T_EQUIPMENT.owner as reference,runtime.owner as author FROM T_EQUIPMENT LEFT JOIN (select * from T_RTM_BODY left join T_RUNTIME on(id_run=T_RUNTIME_id_run) where status='RUNNING') as runtime on(id_equipment=T_EQUIPMENT_id_equipment) left join T_EQUIP_TYPE on(id_type=T_EQUIP_TYPE_id_type) left join T_NET on(T_NET.T_EQUIPMENT_id_equipment=id_equipment) LEFT JOIN T_LOCATION on(T_LOCATION_id_location=id_location) LEFT JOIN (select group_concat(concat(ip,'#',port,'#',if(slot is null,'-',slot),'#',if(subslot is null,'-',subslot)) separator '|') as serials,T_SERIAL.T_EQUIPMENT_id_equipment from T_SERIAL JOIN T_NET on(T_NET_id_ip=id_ip) where T_SERIAL.T_EQUIPMENT_id_equipment="+str(bench)+") as serials on(serials.T_EQUIPMENT_id_equipment=id_equipment) LEFT JOIN T_SCOPE on(T_SCOPE_id_scope=id_scope)  left join (select T_EQUIPMENT_id_equipment,group_concat(concat(cr_type,'#',usr,'#',pwd) separator '|') as credentials from T_EQPT_CRED join T_EQPT_CRED_TYPE on(T_EQPT_CRED_TYPE_id_cred_type=idT_EQPT_CRED_TYPE) where T_EQPT_CRED.T_EQUIPMENT_id_equipment="+str(bench)+") as credentials on(credentials.T_EQUIPMENT_id_equipment=id_equipment) where id_equipment="+str(bench)
		#SQL="SELECT * from T_EQUIPMENT join T_NET on(id_equipment=T_EQUIPMENT_id_equipment) where id_equipment="+str(bench)
		myRecordSet.execute(SQL)
		row=myRecordSet.fetchone()
		name = row['benchName']
		ip = row['benchIP']
		nm = row['benchNM']
		gw = row['benchGW']
		reference=row['reference']
		site=row['site']
		room=row['room']
		product=row['type']
		scope=row['scope']
		rowID=row['row']
		rack=row['rack']
		pos=row['pos']
		description=row['benchDescription']
		note=row['benchNote']
		if row['serials'] != None:
			serialAry=row['serials'].split('|')
			for myId,serial in enumerate(serialAry):
				tempSerial=serial.split('#')
				serials.append({'ip':tempSerial[0],
					'port':tempSerial[1],
					'slot':tempSerial[2],
					'subslot':tempSerial[3]})
		if row['credentials'] != None:
			credAry=row['credentials'].split('|')
			for myId,credential in enumerate(credAry):
				tempCred=credential.split('#')
				credentials.append({'cred_type':tempCred[0],
					'user':tempCred[1],
					'pwd':tempCred[2]})

	ip = ip.split('.') if ip != None else '...'.split('.')
	nm = nm.split('.') if nm != None else '...'.split('.')
	gw = gw.split('.') if gw != None else '...'.split('.')

	myRecordSet.execute("SELECT distinct(site) as site FROM T_LOCATION")
	locations=[row["site"] for row in myRecordSet]

	myRecordSet.execute("SELECT distinct(room) as room FROM T_LOCATION")
	rooms=[row["room"] for row in myRecordSet]

	myRecordSet.execute("SELECT distinct(username) as user FROM auth_user where first_name <> ''")
	users=[row["user"].upper() for row in myRecordSet]

	myRecordSet.execute("SELECT distinct(name) as product FROM T_EQUIP_TYPE")
	products=[row["product"] for row in myRecordSet]

	myRecordSet.execute("SELECT distinct(description) as scope FROM T_SCOPE")
	scopes=[row["scope"] for row in myRecordSet]

	myRecordSet.execute("SELECT distinct(family) as family FROM T_EQUIP_TYPE")
	families=[row["family"] for row in myRecordSet]

	myRecordSet.execute("SELECT distinct(ip) as consoleServer FROM T_EQUIP_TYPE join T_EQUIPMENT on(id_type=T_EQUIP_TYPE_id_type) join T_NET on(id_equipment=T_EQUIPMENT_id_equipment) where family='CONSOLE SERVER'")
	consoleServers=[row["consoleServer"] for row in myRecordSet]

	myRecordSet.execute("SELECT cr_type,idT_EQPT_CRED_TYPE FROM T_EQPT_CRED_TYPE")
	cr_type=[{'cr_name':row["cr_type"],'cr_id':row["idT_EQPT_CRED_TYPE"]} for row in myRecordSet]

	context_dict={'login':request.session['login'],
		'bench':bench,
		'role':request.session['role'],
		'name':name,
		'ip1':ip[0],
		'ip2':ip[1],
		'ip3':ip[2],
		'ip4':ip[3],
		'nm1':nm[0],
		'nm2':nm[1],
		'nm3':nm[2],
		'nm4':nm[3],
		'gw1':gw[0],
		'gw2':gw[1],
		'gw3':gw[2],
		'gw4':gw[3],
		'locations':locations,
		'rooms':rooms,
		'users':users,
		'products':products,
		'scopes':scopes,
		'reference':reference,
		'families':families,
		'site':site,
		'room':room,
		'product':product,
		'scope':scope,
		'row':rowID,
		'rack':rack,
		'pos':pos,
		'serials':serials,
		'credentials':credentials,
		'createReport':createReport,
		'description':description,
		'note':note,
		'consoleServers':consoleServers,
		'cr_type':cr_type
	}

	return render(request,'taws/add_bench.html',context_dict)

def bench(request):

	deleteBench=request.POST.get('deleteBench','')
	action=request.GET.get('action','')

	import mysql.connector
	from django.utils.safestring import mark_safe

	context = RequestContext(request)
	if 'login' not in request.session:
		context_dict={'fromPage':'bench'}
		return render_to_response('taws/login.html',context_dict,context)

	dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
	myRecordSet = dbConnection.cursor(dictionary=True)

	if action == 'delete':
		myRecordSet.execute("DELETE from T_SERIAL where T_EQUIPMENT_id_equipment="+deleteBench)
		dbConnection.commit()
		myRecordSet.execute("DELETE from T_NET where T_EQUIPMENT_id_equipment="+deleteBench)
		dbConnection.commit()
		myRecordSet.execute("DELETE from T_EQUIPMENT where id_equipment="+deleteBench)
		dbConnection.commit()
		

	#SQL="SELECT *,T_SCOPE.description as scope,T_EQUIP_TYPE.name as type,T_EQUIPMENT.name as benchName,if(status like '%ING%',status,'IDLE') as benchStatus,T_EQUIPMENT.owner as reference,runtime.owner as author FROM T_EQUIPMENT LEFT JOIN (select * from T_RTM_BODY left join T_RUNTIME on(id_run=T_RUNTIME_id_run) where status='RUNNING') as runtime on(id_equipment=T_EQUIPMENT_id_equipment) left join T_EQUIP_TYPE on(id_type=T_EQUIP_TYPE_id_type) left join T_NET on(T_NET.T_EQUIPMENT_id_equipment=id_equipment) LEFT JOIN T_LOCATION on(T_LOCATION_id_location=id_location) LEFT JOIN T_SERIAL on(T_SERIAL.T_EQUIPMENT_id_equipment=id_equipment) LEFT JOIN T_SCOPE on(T_SCOPE_id_scope=id_scope)"
	SQL="SELECT *,netBench.IP as benchIP,netBench.NM as benchNM,netBench.GW as benchGW,group_concat(concat(ip1.ip,':',port,' ','Slot ',if(slot is null,'-',slot),' SubSlot ',if(subslot is null,'-',subslot)) separator '<br>') as serials,T_SCOPE.description as scope,T_EQUIP_TYPE.name as type,T_EQUIPMENT.name as benchName,if(status like '%ING%',status,'IDLE') as benchStatus,T_EQUIPMENT.owner as reference,runtime.owner as author FROM T_EQUIPMENT LEFT JOIN (select * from T_RTM_BODY left join T_RUNTIME on(id_run=T_RUNTIME_id_run) where status='RUNNING') as runtime on(id_equipment=T_EQUIPMENT_id_equipment) left join T_EQUIP_TYPE on(id_type=T_EQUIP_TYPE_id_type) left join T_NET as netBench on(netBench.T_EQUIPMENT_id_equipment=id_equipment) LEFT JOIN T_LOCATION on(T_LOCATION_id_location=id_location) LEFT JOIN T_SERIAL on(T_SERIAL.T_EQUIPMENT_id_equipment=id_equipment) LEFT JOIN T_SCOPE on(T_SCOPE_id_scope=id_scope) LEFT JOIN T_NET as ip1 on(T_SERIAL.T_NET_id_ip=ip1.id_ip) group by id_equipment"
	myRecordSet.execute(SQL)
	benches=[]
	numBenches=0
	for row in myRecordSet:
		numBenches+=1
		benches.append({'name':row["benchName"],
			'owner':row["owner"],
			'inUse':row["inUse"],
			'description':row["description"],
			'reference':row["owner"],
			'job_name':row["job_name"],
			'job_iteration':row["job_iteration"],
			'starting_date':row["starting_date"],
			'errCount':row["errCount"],
			'runCount':row["runCount"],
			'status':row['benchStatus'],
			'reference':row['reference'],
			'author':row['author'],
			'SWP':row['T_PACKAGES_id_pack'],
			'site':row['site'],
			'room':row['room'],
			'row':row['row'],
			'rack':row['rack'],
			'pos':row['pos'],
			'id':row['id_equipment'],
			'type':row['type'],
			'family':row['family'],
			'scope':row['scope'],
			'serials':mark_safe(row['serials']),
			'ip':row['benchIP'],
			'nm':row['benchNM'],
			'gw':row['benchGW']
		})

	context_dict={'login':request.session['login'],
		'role':request.session['role'],
		'benches':benches,
		'numBenches':numBenches
	}

	return render(request,'taws/bench.html',context_dict)


def getProducts(recordSet,request):
	print('calling getProducts funct...')
	recordSet.execute("SELECT * FROM KATE.T_PROD where id_prod <> 0")
	productAry=[{'productId':row["id_prod"],'product':row["product"]} for row in recordSet]

	return productAry

def getReleases(recordSet,request):

	product = request.POST.get('selectedProduct','')
	print('calling getReleases funct for ' + str(product) + ' ...')

	recordSet.execute("SELECT id_sw_rel,sw_rel_name from T_DOMAIN join T_PROD on(T_PROD_id_prod=id_prod) join T_SW_REL on(T_SW_REL_id_sw_rel=id_sw_rel) where product='"+ str(product) + "' group by id_sw_rel")
	swAry=[{'swName':row["sw_rel_name"],'swID':row["id_sw_rel"]} for row in recordSet]

	return swAry



def getDomains(recordSet,request):

	product = request.POST.get('selectedProduct','')
	release = request.POST.get('selectedRelease','')

	print('calling getDomains funct for ' + str(product) + ' release ' + str(release) + ' ...')
	
	recordSet.execute("SELECT id_scope,description FROM T_SCOPE join T_DOMAIN  on (T_SCOPE_id_scope = id_scope) join T_PROD on (T_PROD_id_prod = id_prod) join T_SW_REL on ( T_SW_REL_id_sw_rel = id_sw_rel) where product = '" + str(product) + "' and  sw_rel_name = '" + str(release) + "' group by id_scope")
	domainAry=[{'domainName':row["description"],'domainID':row["id_scope"]} for row in recordSet]
	return domainAry

def getArea(recordSet,request):
	product = request.POST.get('selectedProduct','')
	release = request.POST.get('selectedRelease','')
	domain = request.POST.get('selectedDomain','')

	print('calling getDomains funct for ' + str(product) + ' release ' + str(release) + ' domain ' + str(domain) + ' ...')
	recordSet.execute("SELECT id_area,area_name FROM T_AREA join T_DOMAIN  on (T_area_id_area = id_area) join T_SCOPE on (T_SCOPE_id_scope = id_scope) join T_PROD on (T_PROD_id_prod = id_prod) join T_SW_REL on ( T_SW_REL_id_sw_rel = id_sw_rel) where product = '" + str(product) + "' and sw_rel_name = '" + str(release) + "' and description = '" + str(domain) + "' group by id_area")
	areaAry=[{'areaName':row["area_name"],'areaID':row["id_area"]} for row in recordSet]
	return areaAry


def createNewTest(request):
	
	import mysql.connector
	import json
	
	context = RequestContext(request)
	if 'login' not in request.session:
		fromPage = request.META.get('HTTP_REFERER')
		context_dict={'fromPage':'createNewTest'}
		return render_to_response('taws/login.html',context_dict,context)
		
	test_name=request.GET.get('testName')
	username=request.session['login']
	phase=request.POST.get('phase','')
	selectedProduct=request.POST.get('selectedProduct','')
	
	dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
	myRecordSet = dbConnection.cursor(dictionary=True)

	runPhase = {'product' : getProducts, 'release': getReleases, 'domain': getDomains, 'area': getArea}

	queryRes=runPhase[phase](myRecordSet,request)
	myRecordSet.execute("select concat(T_PRESETS.preset_title,'[',convert(group_concat(distinct id_topology separator ',') using utf8),']') as description,id_preset from T_PRESETS join T_PST_ENTITY on(id_preset=T_PRESETS_id_preset) join T_TPY_ENTITY on(id_entity=T_TPY_ENTITY_id_entity) join T_TOPOLOGY on(id_topology=T_TOPOLOGY_id_topology) where owner='"+request.session['login']+"' group by id_preset")
	userPreset=[{'userPresetName':row["description"],'userPresetID':row["id_preset"]} for row in myRecordSet]
	myRecordSet.execute("SELECT * from T_TOPOLOGY join T_SCOPE on(T_SCOPE_id_scope=id_scope) order by T_SCOPE.description")
	topoAry=[{'topoID':row["id_topology"],'topoName':row["title"]} for row in myRecordSet]

	context_dict={'login':request.session['login'],
				'phase':phase,
				'userPreset':userPreset,
				'topoAry':topoAry,
				'queryRes':queryRes}

	return HttpResponse(json.dumps(context_dict),
            content_type="application/json"
        )


def viewReport(request):

	#import MySQLdb
	import xml.etree.ElementTree as ET
	from os.path import basename
	from datetime import timedelta, datetime
	from django.utils.safestring import mark_safe
	#from django.utils.html import *
	#from jenkinsapi.jenkins import Jenkins

	context = RequestContext(request)
	if 'login' not in request.session:
		fromPage = request.META.get('HTTP_REFERER')
		context_dict={'fromPage':'viewReport'}
		return render_to_response('taws/login.html',context_dict,context)

	job_name=request.POST.get('jobName','')
	buildId=request.POST.get('buildId','')
	testName=request.POST.get('testName','')

	suiteFolder=settings.JENKINS['SUITEFOLDER']
	tree = ET.parse(suiteFolder+job_name+'/builds/'+str(buildId)+'/junitResult.xml')
	root = tree.getroot()

	treeView=''
	tempTreeView=''
	for suites in root.findall(".suites/suite"):
		counter1=0
		if suites.find('name').text.rfind(testName)>=0 and suites.find('name').text.rfind('_Main')<0 and suites.find('name').text.rfind('_main')<0:
			#tempTreeView+="<li><label for='folder"+str(counter1)+"'>"+suites.find('name').text.replace('(','').replace('.XML)','')+"([MAINRESULT])</label> <input type='checkbox' id='folder"+str(counter1)+"' />"
			#tempTreeView+="<ol>"
			tempTreeView+="{text:'"+suites.find('name').text.replace('(','').replace('.XML)','')+"',"+\
				"href:'#"+suites.find('name').text.replace('(','').replace('.XML)','')+"',"+\
				"tags:['[counterMain]'],"+\
				"nodes:["
			mainResult="<span style='color:green;font-weight: bold;'>Passed</span>"
			for case in suites.findall('cases/case'):
				counter2=0
				testStatus="<span style='color:green;font-weight: bold;'>Passed</span>"
				if case.find('stderr')!=None:
					testStatus="<span style='color:red;font-weight: bold;'>Failed</span>"
					mainResult="<span style='color:red;font-weight: bold;'>Failed</span>"
				if case.find('skipped').text=='true':
					testStatus="<span style='color:gray;font-weight: bold;'>Skipped</span>"
					if mainResult.rfind('Failed')<0:mainResult="<span style='color:gray;font-weight: bold;'>Skipped</span>"
				#tempTreeView+="<li><label for='subfolder"+str(counter2)+"'>"+case.find('testName').text+" ("+testStatus+")</label> <input type='checkbox' id='subfolder"+str(counter2)+"' />"
				#tempTreeView+="<ol>"
				tempTreeView+="{text:'"+case.find('testName').text+"',"+\
					"href:'#"+case.find('testName').text+"',"+\
					"tags:['[counterPartial]'],"+\
					"nodes:["
				#tempTreeView+="<ol>"
				#tempTreeView+="<li><label for='subsubfolder"+str(counter2)+"'>STDOUT:\n"+case.find('stdout').text+"</label> <input type='checkbox' id='subsubfolder"+str(counter2)+"' />"
				#tempTreeView+="</li>"
				tempTreeView+="{text:'STDOUT',"+\
					"href:'#STDOUT',"+\
					"tags:[],"+\
					"nodes:[{"+\
					"text:'"+case.find('stdout').text.replace("'","\\'")+"',"+\
					"href:'#"+case.find('stdout').text.replace("'","\\'")+"',"+\
					"tags:[]}]},"
				if testStatus.rfind('Failed')>=0:
					counter2+=1
					counter1+=1
					#tempTreeView+="<li><label for='subsubfolder"+str(counter2)+"'>STDERR:\n"+case.find('stderr').text+"</label> <input type='checkbox' id='subsubfolder"+str(counter2)+"' />"
					#tempTreeView+="</li>"
					tempTreeView+="{text:'STDERR',"+\
						"href:'#STDERR',"+\
						"tags:[],"+\
						"nodes:[{"+\
						"text:'"+case.find('stderr').text+"',"+\
						"href:'#"+case.find('stderr').text+"',"+\
						"tags:[]}]},"
				#counter2+=1
				#tempTreeView+="<li><label for='subsubfolder"+str(counter2)+"'>DURATION:\n"+case.find('duration').text+"</label> <input type='checkbox' id='subsubfolder"+str(counter2)+"' />"
				#tempTreeView+="</li>"
				#tempTreeView+="</ol>"
				#tempTreeView+="</li>"
				tempTreeView+="{text:'DURATION',"+\
						"href:'#DURATION',"+\
						"tags:[],"+\
						"nodes:[{"+\
						"text:'"+case.find('duration').text+"',"+\
						"href:'#"+case.find('duration').text+"',"+\
						"tags:[]}]}"
				tempTreeView+="]},"
				#counter2+=2
				#counter1+=2
				if counter2 > 0:
					counter2='i'
				else:
					counter2=''
				tempTreeView=tempTreeView.replace('[counterPartial]',str(counter2))
			#tempTreeView+="</ol>"
			#tempTreeView+="</li>"
			tempTreeView=tempTreeView[:-1]
			tempTreeView+="]},"
			#counter1+=1
		if counter1 > 0:
			counter1='i'
		else:
			counter1=''
		tempTreeView=tempTreeView.replace('\n','\\n').replace('[counterMain]',str(counter1))
	treeView+=tempTreeView[:-1]

	context_dict={'login':request.session['login'],
		'job_name':job_name,
		'buildId': str(buildId),
		'treeView':mark_safe(treeView),
		'testName':testName}
	return render(request,'taws/viewReport.html',context_dict)

def statistics_sw_executed(request):

	import mysql.connector
	from django.utils.safestring import SafeText,mark_safe
	import json

	context = RequestContext(request)
	if 'login' not in request.session:
		fromPage = request.META.get('HTTP_REFERER')
		context_dict={'fromPage':'statistics_sw_executed'}
		return render_to_response('taws/login.html',context_dict,context)

	id_pack1=request.POST.get('id_pack1','0')
	id_pack2=request.POST.get('id_pack2','0')
	id_pack3=request.POST.get('id_pack3','0')
	val_pack1=request.POST.get('id_pack1_val','')
	val_pack2=request.POST.get('id_pack2_val','')
	val_pack3=request.POST.get('id_pack3_val','')

	#id_pack1='0'
	#id_pack2='0'
	#id_pack3='0'

	dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
	myRecordSet = dbConnection.cursor(dictionary=True,buffered=True)

	#myRecordSet.execute("select concat('<li class="dropdown"><a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">',product,'<span class="caret"></span></a><ul class="dropdown-menu">',group_concat(myPackages separator ''),'</ul></li>') from (SELECT T_PROD_id_prod,concat('<li><a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">',sw_rel_name,'<span class="caret"></span></a><ul class="dropdown-menu">',group_concat(concat('<li><a href="#">',T_PACKAGES.label_ref,'</a></li>') order by T_PACKAGES.label_ref separator ''),'</ul></li>') as myPackages FROM T_PACKAGES join T_SW_REL on(id_sw_rel=T_SW_REL_id_sw_rel) where id_pack<>0 group by T_SW_REL_id_sw_rel) as packages join T_PROD on(id_prod=T_PROD_id_prod) group by product
	#myRecordSet.execute("select concat('<li class=',char(39),'dropdown',char(39),'><a href=',char(39),'#',char(39),' class=',char(39),'dropdown-toggle',char(39),' data-toggle=',char(39),'dropdown',char(39),' role=',char(39),'button',char(39),' aria-haspopup=',char(39),'true',char(39),' aria-expanded=',char(39),'false',char(39),'>',product,' <span class=',char(39),'caret',char(39),'></span></a><ul class=',char(39),'dropdown-menu',char(39),'>',group_concat(myPackages separator ''),'</ul></li>') as swp_dropdown from (SELECT T_PROD_id_prod,concat('<li><a href=',char(39),'#',char(39),' class=',char(39),'dropdown-toggle',char(39),' data-toggle=',char(39),'dropdown',char(39),' role=',char(39),'button',char(39),' aria-haspopup=',char(39),'true',char(39),' aria-expanded=',char(39),'false',char(39),'>',sw_rel_name,' <span class=',char(39),'caret',char(39),'></span></a><ul class=',char(39),'dropdown-menu',char(39),'>',group_concat(concat('<li><a onclick=',char(39),'document.getElementById(\\\'[dropdown-selection]\\\')=',id_pack,char(39),'>',T_PACKAGES.label_ref,'</a></li>') order by T_PACKAGES.label_ref separator ''),'</ul></li>') as myPackages FROM T_PACKAGES join T_SW_REL on(id_sw_rel=T_SW_REL_id_sw_rel) where id_pack<>0 group by T_SW_REL_id_sw_rel) as packages join T_PROD on(id_prod=T_PROD_id_prod) group by product")
	#myRecordSet.execute("select concat('<li class=',char(34),'dropdown',char(34),'><a href=',char(34),'#',char(34),' class=',char(34),'dropdown-toggle',char(34),' data-toggle=',char(34),'dropdown',char(34),' role=',char(34),'button',char(34),' aria-haspopup=',char(34),'true',char(34),' aria-expanded=',char(34),'false',char(34),'>',product,' <span class=',char(34),'caret',char(34),'></span></a><ul class=',char(34),'dropdown-menu',char(34),'>',group_concat(myPackages separator ''),'</ul></li>') as swp_dropdown from (SELECT T_PROD_id_prod,concat('<li><a href=',char(34),'#',char(34),' class=',char(34),'dropdown-toggle',char(34),' data-toggle=',char(34),'dropdown',char(34),' role=',char(34),'button',char(34),' aria-haspopup=',char(34),'true',char(34),' aria-expanded=',char(34),'false',char(34),'>',sw_rel_name,' <span class=',char(34),'caret',char(34),'></span></a><ul class=',char(34),'dropdown-menu',char(34),'>',group_concat(concat('<li><a onclick=',char(34),'filtro.[dropdown-selection].value=',id_pack,';filtro.[dropdown-selection]_val.value=',char(39),T_PACKAGES.label_ref,char(39),';filtro.submit();',char(34),'>',T_PACKAGES.label_ref,'</a></li>') order by T_PACKAGES.label_ref separator ''),'</ul></li>') as myPackages FROM T_PACKAGES join T_SW_REL on(id_sw_rel=T_SW_REL_id_sw_rel) where id_pack<>0 group by T_SW_REL_id_sw_rel) as packages join T_PROD on(id_prod=T_PROD_id_prod) group by product")
	myRecordSet.execute("SET group_concat_max_len = 200000")
	dbConnection.commit()

	#myRecordSet.execute("select concat('<li class=',char(34),'dropdown-submenu',char(34),'><a href=',char(34),'#',char(34),' tabindex=',char(34),'-1',char(34),'>',product,'</a><ul class=',char(34),'dropdown-menu',char(34),'>',group_concat(myPackages separator ''),'</ul></li>') as swp_dropdown from (SELECT T_PROD_id_prod,concat('<li class=',char(34),'dropdown-submenu',char(34),'><a href=',char(34),'#',char(34),' tabindex=',char(34),'-1',char(34),'>',sw_rel_name,'</a><ul class=',char(34),'dropdown-menu',char(34),'>',group_concat(concat('<li><a onclick=',char(34),'filtro.[dropdown-selection].value=',id_pack,';filtro.submit();',char(34),'>',T_PACKAGES.label_ref,'</a></li>') order by T_PACKAGES.label_ref separator ''),'</ul></li>') as myPackages FROM T_PACKAGES join T_SW_REL on(id_sw_rel=T_SW_REL_id_sw_rel) where id_pack<>0 group by T_SW_REL_id_sw_rel) as packages join T_PROD on(id_prod=T_PROD_id_prod) group by product")
	myRecordSet.execute("select concat('<li class=',char(34),'dropdown-submenu',char(34),'><a href=',char(34),'#',char(34),' tabindex=',char(34),'-1',char(34),'>',product,'</a><ul class=',char(34),'dropdown-menu',char(34),'>',group_concat(myPackages separator ''),'</ul></li>') as swp_dropdown from (SELECT T_PROD_id_prod,concat('<li class=',char(34),'dropdown-submenu',char(34),'><a href=',char(34),'#',char(34),' tabindex=',char(34),'-1',char(34),'>',sw_rel_name,'</a><ul class=',char(34),'dropdown-menu',char(34),'>',group_concat(concat('<li><a onclick=',char(34),'filtro.[dropdown-selection].value=',id_pack,';filtro.submit();',char(34),'>',T_PACKAGES.label_ref,'</a></li>') order by T_PACKAGES.label_ref separator ''),'</ul></li>') as myPackages FROM T_PACKAGES join T_SW_REL on(id_sw_rel=T_SW_REL_id_sw_rel) where id_pack<>0 group by T_PROD_id_prod,T_SW_REL_id_sw_rel) as packages join T_PROD on(id_prod=T_PROD_id_prod) group by product")
	
	swp_dropdown=''
	
	for row in myRecordSet:
		swp_dropdown+=row['swp_dropdown']
		
	#swp_dropdown="select concat('<li class=',char(39),'dropdown',char(39),'><a href=',char(39),'#',char(39),' class=',char(39),'dropdown-toggle',char(39),' data-toggle=',char(39),'dropdown',char(39),' role=',char(39),'button',char(39),' aria-haspopup=',char(39),'true',char(39),' aria-expanded=',char(39),'false',char(39),'>',product,' <span class=',char(39),'caret',char(39),'></span></a><ul class=',char(39),'dropdown-menu',char(39),'>',group_concat(myPackages separator ''),'</ul></li>') as swp_dropdown from (SELECT T_PROD_id_prod,concat('<li><a href=',char(39),'#',char(39),' class=',char(39),'dropdown-toggle',char(39),' data-toggle=',char(39),'dropdown',char(39),' role=',char(39),'button',char(39),' aria-haspopup=',char(39),'true',char(39),' aria-expanded=',char(39),'false',char(39),'>',sw_rel_name,' <span class=',char(39),'caret',char(39),'></span></a><ul class=',char(39),'dropdown-menu',char(39),'>',group_concat(concat('<li><a onclick=',char(39),'document.getElementById(\'[dropdown-selection]\')=',id_pack,char(39),'>',T_PACKAGES.label_ref,'</a></li>') order by T_PACKAGES.label_ref separator ''),'</ul></li>') as myPackages FROM T_PACKAGES join T_SW_REL on(id_sw_rel=T_SW_REL_id_sw_rel) where id_pack<>0 group by T_SW_REL_id_sw_rel) as packages join T_PROD on(id_prod=T_PROD_id_prod) group by product"
	#myRecordSet.execute("SELECT group_concat(distinct concat('<li><a href=',char(39),'#',lcase(description),'-tab',char(39),' data-toggle=',char(39),'tab',char(39),'>',ucase(description),'</a></li>')) as selected_tab,group_concat(distinct concat('<div class=',char(39),'tab-pane',char(39),' id=',char(39),'',lcase(description),'-tab',char(39),'></div>')) as selected_div FROM T_DOMAIN JOIN T_PACKAGES using(T_SW_REL_id_sw_rel,T_PROD_id_prod) join T_SCOPE on(T_SCOPE_id_scope=id_scope) where id_pack="+id_pack1)
	#myRecordSet.execute("SELECT distinct(description) as myTab FROM T_DOMAIN JOIN T_PACKAGES using(T_SW_REL_id_sw_rel,T_PROD_id_prod) join T_SCOPE on(T_SCOPE_id_scope=id_scope) where id_pack=1")
	#tab_list=[{'tab':row["myTab"]} for row in myRecordSet]
	#myRecordSet.execute("select description,area_name,count(*) as numTPS from (select * from T_TPS group by T_DOMAIN_id_domain,tps_reference) as T_TPS join T_DOMAIN on(T_DOMAIN_id_domain=id_domain) join T_PACKAGES using(T_PROD_id_prod,T_SW_REL_id_sw_rel) join T_SCOPE on(T_SCOPE_id_scope=id_scope) join T_AREA on(id_area=T_AREA_id_area) where id_pack="+id_pack1+" group by id_domain,id_area")
	#myRecordSet.execute("select description,area_name,count(*) as numTPS,sum(if(T_REPORT1.result='Failed',1,0)) as KO1,sum(if(T_REPORT1.result='Passed',1,0)) as OK1,sum(if(T_REPORT1.result<>'',1,0)) as TOT1,sum(if(T_REPORT2.result='Failed',1,0)) as KO2,sum(if(T_REPORT2.result='Passed',1,0)) as OK2,sum(if(T_REPORT2.result<>'',1,0)) as TOT2,sum(if(T_REPORT3.result='Failed',1,0)) as KO3,sum(if(T_REPORT3.result='Passed',1,0)) as OK3,sum(if(T_REPORT3.result<>'',1,0)) as TOT3 from (select * from T_TPS group by T_DOMAIN_id_domain,tps_reference) as T_TPS join T_DOMAIN on(T_DOMAIN_id_domain=id_domain) join T_PACKAGES using(T_PROD_id_prod,T_SW_REL_id_sw_rel) join T_SCOPE on(T_SCOPE_id_scope=id_scope) join T_AREA on(id_area=T_AREA_id_area) left join (select * from (select * from T_REPORT where T_PACKAGES_id_pack="+id_pack1+" order by T_RUNTIME_id_run desc) as T_REPORT group by T_TPS_id_tps) as T_REPORT1 on(id_tps=T_REPORT1.T_TPS_id_tps) left join (select * from (select * from T_REPORT where T_PACKAGES_id_pack="+id_pack2+" order by T_RUNTIME_id_run desc) as T_REPORT group by T_TPS_id_tps) as T_REPORT2 on(id_tps=T_REPORT2.T_TPS_id_tps) left join (select * from (select * from T_REPORT where T_PACKAGES_id_pack="+id_pack3+" order by T_RUNTIME_id_run desc) as T_REPORT group by T_TPS_id_tps) as T_REPORT3 on(id_tps=T_REPORT3.T_TPS_id_tps) where id_pack="+id_pack1+" group by id_domain,id_area order by description")
	myRecordSet.execute("select name1,name2,name3,description,if(numTest1 is null,0,numTest1) as numTest1,if(numTest2 is null,0,numTest2) as numTest2,if(numTest3 is null,0,numTest3) as numTest3,area_name,numTPS1,if(numTPS2 is null,0,numTPS2) as numTPS2,if(numTPS3 is null,0,numTPS3) as numTPS3,OK1,KO1,TOT1,if(OK2 is null,0,OK2) as OK2,if(KO2 is null,0,KO2) as KO2,if(TOT2 is null,0,TOT2) as TOT2,if(OK3 is null,0,OK3) as OK3,if(KO3 is null,0,KO3) as KO3,if(TOT3 is null,0,TOT3) as TOT3 from (select T_PACKAGES.label_ref as name1,description,area_name,count(distinct tps_reference) as numTPS1,sum(if(report1.result='Failed',1,0)) as KO1,sum(if(report1.result='Passed',1,0)) as OK1,sum(if(report1.result<>'',1,0)) as TOT1,planned_test as numTest1 from T_TPS as tps1 join T_DOMAIN on(T_DOMAIN_id_domain=id_domain) join T_PACKAGES using(T_PROD_id_prod,T_SW_REL_id_sw_rel) join T_SCOPE on(T_SCOPE_id_scope=id_scope) join T_AREA on(id_area=T_AREA_id_area) left join (select * from (select * from T_REPORT where T_PACKAGES_id_pack="+id_pack1+" order by report_date desc) as tempReport1 group by T_TPS_id_tps) as report1 on(id_tps=report1.T_TPS_id_tps) where id_pack="+id_pack1+" group by id_domain,id_area order by description) as rep1 left join (select T_PACKAGES.label_ref as name2,description,area_name,count(distinct tps_reference) as numTPS2,sum(if(report2.result='Failed',1,0)) as KO2,sum(if(report2.result='Passed',1,0)) as OK2,sum(if(report2.result<>'',1,0)) as TOT2,planned_test as numTest2 from T_TPS as tps2 join T_DOMAIN on(T_DOMAIN_id_domain=id_domain) join T_PACKAGES using(T_PROD_id_prod,T_SW_REL_id_sw_rel) join T_SCOPE on(T_SCOPE_id_scope=id_scope) join T_AREA on(id_area=T_AREA_id_area) left join (select * from (select * from T_REPORT where T_PACKAGES_id_pack=1 order by report_date desc) as tempReport2 group by T_TPS_id_tps) as report2 on(id_tps=report2.T_TPS_id_tps) where id_pack="+id_pack2+" group by id_domain,id_area order by description) as rep2 using(description,area_name) left join (select T_PACKAGES.label_ref as name3,description,area_name,count(distinct tps_reference) as numTPS3,sum(if(report3.result='Failed',1,0)) as KO3,sum(if(report3.result='Passed',1,0)) as OK3,sum(if(report3.result<>'',1,0)) as TOT3,planned_test as numTest3 from T_TPS as tps3 join T_DOMAIN on(T_DOMAIN_id_domain=id_domain) join T_PACKAGES using(T_PROD_id_prod,T_SW_REL_id_sw_rel) join T_SCOPE on(T_SCOPE_id_scope=id_scope) join T_AREA on(id_area=T_AREA_id_area) left join (select * from (select * from T_REPORT where T_PACKAGES_id_pack=1 order by report_date desc) as tempReport3 group by T_TPS_id_tps) as report3 on(id_tps=report3.T_TPS_id_tps) where id_pack="+id_pack3+" group by id_domain,id_area order by description) as rep3 using(description,area_name)")
	rows=myRecordSet.fetchall()
	#selected_tab=row['selected_tab']
	#selected_div=row['selected_div']

	tab_list=[]
	curr_list={}
	curr_tab=''
	for row in rows:
		if row["description"] != curr_tab:
			if curr_tab!='':tab_list.append(curr_list)
			curr_list={'domain':row["description"],'name1':row['name1'],'name2':row['name2'],'name3':row['name3'],'values':[]}
			curr_tab=row["description"]
		curr_list['values'].append({'area_name':row['area_name'],'numTest1':row['numTest1'],'numTest2':row['numTest2'],'numTest3':row['numTest3'],'numTPS1':row['numTPS1'],'numTPS2':row['numTPS2'],'numTPS3':row['numTPS3'],'OK1': str(row['OK1']),'KO1':str(row['KO1']),'TOT1':str(row['TOT1']),'OK2':str(row['OK2']),'KO2':str(row['KO2']),'TOT2':str(row['TOT2']),'OK3':str(row['OK3']),'KO3':str(row['KO3']),'TOT3':str(row['TOT3'])})
	tab_list.append(curr_list)


	context = RequestContext(request)
	

	#context_dict={'swp_dropdown1':mark_safe(swp_dropdown.replace('[dropdown-selection]','id_pack1')),'swp_dropdown2':mark_safe(swp_dropdown.replace('[dropdown-selection]','id_pack2')),'swp_dropdown3':mark_safe(swp_dropdown.replace('[dropdown-selection]','id_pack3')),'selected_tab':mark_safe(selected_tab),'selected_div':mark_safe(selected_div),'id_pack1':id_pack1,'id_pack2':id_pack2,'id_pack3':id_pack3}
	context_dict={'login':request.session['login'].upper(),'swp_dropdown1':mark_safe(swp_dropdown.replace('[dropdown-selection]','id_pack1')),'swp_dropdown2':mark_safe(swp_dropdown.replace('[dropdown-selection]','id_pack2')),'swp_dropdown3':mark_safe(swp_dropdown.replace('[dropdown-selection]','id_pack3')),'tab_list':tab_list,'id_pack1':id_pack1,'id_pack2':id_pack2,'id_pack3':id_pack3,'val_pack1':val_pack1,'val_pack2':val_pack2,'val_pack3':val_pack3}


	return render(request,'taws/statistics_sw_executed.html',context_dict)

def statistics_sw_executed_details(request):

	import mysql.connector,os
	from django.utils.safestring import SafeText,mark_safe

	id_pack1=request.POST.get('id_pack1','1')
	id_pack2=request.POST.get('id_pack2','0')
	id_pack3=request.POST.get('id_pack3','0')
	area_name=request.POST.get('area','-').split('-')[1]
	description=request.POST.get('area','-').split('-')[0]

	dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
	myRecordSet = dbConnection.cursor(dictionary=True, buffered=True)

	myRecordSet.execute("select concat('<li class=',char(34),'dropdown-submenu',char(34),'><a href=',char(34),'#',char(34),' tabindex=',char(34),'-1',char(34),'>',product,'</a><ul class=',char(34),'dropdown-menu',char(34),'>',group_concat(myPackages separator ''),'</ul></li>') as swp_dropdown from (SELECT T_PROD_id_prod,concat('<li class=',char(34),'dropdown-submenu',char(34),'><a href=',char(34),'#',char(34),' tabindex=',char(34),'-1',char(34),'>',sw_rel_name,'</a><ul class=',char(34),'dropdown-menu',char(34),'>',group_concat(concat('<li><a onclick=',char(34),'filtro.[dropdown-selection].value=',id_pack,';filtro.submit();',char(34),'>',T_PACKAGES.label_ref,'</a></li>') order by T_PACKAGES.label_ref separator ''),'</ul></li>') as myPackages FROM T_PACKAGES join T_SW_REL on(id_sw_rel=T_SW_REL_id_sw_rel) where id_pack<>0 group by T_SW_REL_id_sw_rel) as packages join T_PROD on(id_prod=T_PROD_id_prod) group by product")
	swp_dropdown=myRecordSet.fetchone()['swp_dropdown']

	myRecordSet.execute("select * from (select concat(product,'-',T_PACKAGES.label_ref) as tpack1,tps_reference,test_name,T_SCOPE.description,area_name,result as result1,id_report as id_report1,report_date as date1,T_REPORT1.author as author1,convert(info using utf8) as dump1 from (select * from T_TPS group by T_DOMAIN_id_domain,tps_reference) as T_TPS join T_DOMAIN on(T_DOMAIN_id_domain=id_domain) join T_PACKAGES using(T_PROD_id_prod,T_SW_REL_id_sw_rel) join T_SCOPE on(T_SCOPE_id_scope=id_scope) join T_AREA on(id_area=T_AREA_id_area) join T_TEST_REVS on(id_TestRev=T_TEST_REVS_id_TestREv) join T_TEST on(test_id=T_TEST_test_id) left join (select * from (select * from T_REPORT where T_PACKAGES_id_pack="+id_pack1+" order by report_date desc) as T_REPORT group by T_TPS_id_tps) as T_REPORT1 on(id_tps=T_REPORT1.T_TPS_id_tps) join T_PROD on(id_prod=T_PROD_id_prod)  where id_pack="+id_pack1+" and T_SCOPE.description='"+description+"' and area_name='"+area_name+"') as rep1 left join (select concat(product,'-',T_PACKAGES.label_ref) as tpack2,tps_reference,description,area_name,result as result2,id_report as id_report2,report_date as date2,T_REPORT2.author as author2 from (select * from T_TPS group by T_DOMAIN_id_domain,tps_reference) as T_TPS join T_DOMAIN on(T_DOMAIN_id_domain=id_domain) join T_PACKAGES using(T_PROD_id_prod,T_SW_REL_id_sw_rel) join T_SCOPE on(T_SCOPE_id_scope=id_scope) join T_AREA on(id_area=T_AREA_id_area) left join (select * from (select * from T_REPORT where T_PACKAGES_id_pack="+id_pack2+" order by report_date desc) as T_REPORT group by T_TPS_id_tps) as T_REPORT2 on(id_tps=T_REPORT2.T_TPS_id_tps) join T_PROD on(id_prod=T_PROD_id_prod) where id_pack="+id_pack2+" and description='"+description+"' and area_name='"+area_name+"') as rep2 using(tps_reference,description,area_name) left join (select concat(product,'-',T_PACKAGES.label_ref) as tpack3,tps_reference,description,area_name,result as result3,id_report as id_report3,report_date as date3,T_REPORT3.author as author3 from (select * from T_TPS group by T_DOMAIN_id_domain,tps_reference) as T_TPS join T_DOMAIN on(T_DOMAIN_id_domain=id_domain) join T_PACKAGES using(T_PROD_id_prod,T_SW_REL_id_sw_rel) join T_SCOPE on(T_SCOPE_id_scope=id_scope) join T_AREA on(id_area=T_AREA_id_area) left join (select * from (select * from T_REPORT where T_PACKAGES_id_pack="+id_pack3+" order by report_date desc) as T_REPORT group by T_TPS_id_tps) as T_REPORT3 on(id_tps=T_REPORT3.T_TPS_id_tps) join T_PROD on(id_prod=T_PROD_id_prod) where id_pack="+id_pack3+" and description='"+description+"' and area_name='"+area_name+"') as rep3 using(tps_reference,description,area_name)")
	details_row=[{'tps_reference':row["tps_reference"],'test_name':os.path.basename(row["test_name"]),'result1':row["result1"],'author1':row["author1"],'date1':row["date1"],'dump1':row["dump1"],'id_report1':row["id_report1"],'tpack1':row["tpack1"],'result2':row["result2"],'id_report2':row["id_report2"],'tpack2':row["tpack2"],'result3':row["result3"],'id_report3':row["id_report3"],'tpack3':row["tpack3"]} for row in myRecordSet]

	myRecordSet.execute("SELECT distinct(concat(description,'-',area_name)) as myTab FROM T_DOMAIN JOIN T_PACKAGES using(T_SW_REL_id_sw_rel,T_PROD_id_prod) join T_SCOPE on(T_SCOPE_id_scope=id_scope) join T_AREA on(T_AREA_id_area=id_area) where id_pack="+id_pack1+" order by description")
	area_row=[{'features':row["myTab"]} for row in myRecordSet]

	area=area_name+'-'+description
	if area == '-':area=''
	context_dict={'login':request.session['login'].upper(),
		'swp_dropdown1':mark_safe(swp_dropdown.replace('[dropdown-selection]','id_pack1')),
		'swp_dropdown2':mark_safe(swp_dropdown.replace('[dropdown-selection]','id_pack2')),
		'swp_dropdown3':mark_safe(swp_dropdown.replace('[dropdown-selection]','id_pack3')),
		'area':area,
		'details_row':details_row,
		'area_row':area_row,
		'id_pack1':id_pack1,
		'id_pack2':id_pack2,
		'id_pack3':id_pack3}

	return render(request,'taws/statistics_sw_executed_details.html',context_dict)

def the_doctor(request):
	context = RequestContext(request)
	context_dict={'nothing':'nothing'}
	import mysql.connector

	if 'login' not in request.session:
		context_dict={'fromPage':'the_doctor'}
		return render_to_response('taws/login.html',context_dict,context)
	else:
		dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
		myRecordSet=dbConnection.cursor(dictionary=True)
		myRecordSet.execute("SET group_concat_max_len = 200000")
		dbConnection.commit()
		#myRecordSet.execute("select product,CONVERT(group_concat(concat(areaConcat,'$',sw_rel_name) order by sw_rel_name desc separator '@') using utf8) as productConcat from (select product,sw_rel_name,group_concat(concat(area_name,'!',area_name) order by area_name separator '#') as areaConcat from T_DOMAIN join T_AREA on(T_AREA_id_area=id_area) join T_PROD on(T_PROD_id_prod=id_prod) join T_SW_REL on(T_SW_REL_id_sw_rel=id_sw_rel) group by product,sw_rel_name order by product asc,sw_rel_name desc) as tableArea group by product")
		myRecordSet.execute("select product,group_concat(release_scope_area separator '@') as productConcat from (select product,concat(sw_rel_name,'?',group_concat(scope_area separator '%')) as release_scope_area from (select product,sw_rel_name,concat(T_SCOPE.description,'#',group_concat(area_name order by area_name separator '|')) as scope_area from T_DOMAIN join T_SCOPE on(T_SCOPE_id_scope=id_scope) join T_AREA on(T_AREA_id_area=id_area) join T_PROD on(T_PROD_id_prod=id_prod) join T_SW_REL on(T_SW_REL_id_sw_rel=id_sw_rel) group by product,sw_rel_name,T_SCOPE.description order by product asc,sw_rel_name desc,T_SCOPE.description asc) as release_scope_area group by product,sw_rel_name order by product asc,sw_rel_name desc) as product_release_scope_area group by product order by product asc")
		productAry=[{'product':row["product"],'productConcat':row["productConcat"]} for row in myRecordSet]

		myRecordSet.execute("select concat(T_PRESETS.preset_title,'[',convert(group_concat(distinct id_topology separator ',') using utf8),']') as description,id_preset,preset_title from T_PRESETS join T_PST_ENTITY on(id_preset=T_PRESETS_id_preset) join T_TPY_ENTITY on(id_entity=T_TPY_ENTITY_id_entity) join T_TOPOLOGY on(id_topology=T_TOPOLOGY_id_topology) group by id_preset")
		sharedPreset=[{'sharedPresetName':row["description"],'sharedPresetID':row["id_preset"],'sharedPresetTitle':row["preset_title"]} for row in myRecordSet]

		myRecordSet.execute("SELECT distinct lab from T_TEST_REVS order by lab")
		labAry=[{'labName':row["lab"]} for row in myRecordSet]

		context_dict={'login':request.session['login'].upper(),
			'permission':1,
			'productAry': productAry,
			'labAry':labAry,
			'sharedPreset':sharedPreset,
			'settings':settings.DATABASES['default']['USER']}
		return render_to_response('taws/theDoctor.html',context_dict,context)


def morgue(request):

	import mysql.connector
	from django.utils.safestring import SafeText,mark_safe

	context = RequestContext(request)
	if 'login' not in request.session:
		fromPage = request.META.get('HTTP_REFERER')
		context_dict={'fromPage':'morgue'}
		return render_to_response('taws/login.html',context_dict,context)

	id_pack=request.POST.get('id_pack','1')
	action=request.GET.get('action','')
	
	dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
	myRecordSet = dbConnection.cursor(dictionary=True, buffered=True)

	if action == 'update':
		for key in request.POST:
			if key.rfind('note')>=0:
				myRecordSet.execute("UPDATE T_REPORT set notes='"+request.POST[key]+"' where id_report="+key.replace('note',''))
				dbConnection.commit()


	myRecordSet.execute("select concat('<li class=',char(34),'dropdown-submenu',char(34),'><a href=',char(34),'#',char(34),' tabindex=',char(34),'-1',char(34),'>',product,'</a><ul class=',char(34),'dropdown-menu',char(34),'>',group_concat(myPackages separator ''),'</ul></li>') as swp_dropdown from (SELECT T_PROD_id_prod,concat('<li class=',char(34),'dropdown-submenu',char(34),'><a href=',char(34),'#',char(34),' tabindex=',char(34),'-1',char(34),'>',sw_rel_name,'</a><ul class=',char(34),'dropdown-menu',char(34),'>',group_concat(concat('<li><a onclick=',char(34),'filtro.[dropdown-selection].value=',id_pack,';filtro.submit();',char(34),'>',T_PACKAGES.label_ref,'</a></li>') order by T_PACKAGES.label_ref separator ''),'</ul></li>') as myPackages FROM T_PACKAGES join T_SW_REL on(id_sw_rel=T_SW_REL_id_sw_rel) where id_pack<>0 group by T_SW_REL_id_sw_rel) as packages join T_PROD on(id_prod=T_PROD_id_prod) group by product")
	swp_dropdown=myRecordSet.fetchone()['swp_dropdown']

	myRecordSet.execute("select id_report,description,area_name,tps_reference,result,info,report1.notes,concat(product,'-',T_PACKAGES.label_ref) as tpack from T_TPS as tps1 join T_DOMAIN on(T_DOMAIN_id_domain=id_domain) join T_PACKAGES using(T_PROD_id_prod,T_SW_REL_id_sw_rel) join T_SCOPE on(T_SCOPE_id_scope=id_scope) join T_AREA on(id_area=T_AREA_id_area) left join (select * from (select * from T_REPORT where T_PACKAGES_id_pack="+id_pack+" order by report_date desc) as tempReport1 group by T_TPS_id_tps) as report1 on(id_tps=report1.T_TPS_id_tps) join T_PROD on(id_prod=T_PROD_id_prod) where id_pack="+id_pack+" and result='Failed' order by description,area_name,tps_reference")
	morgue_row=[{'id_report':row["id_report"],'tpack':row["tpack"],'description':row["description"],'area_name':row['area_name'],'tps_reference':row['tps_reference'],'info':row['info'],'notes':row['notes']} for row in myRecordSet]

	context_dict={'swp_dropdown1':mark_safe(swp_dropdown.replace('[dropdown-selection]','id_pack')),
		'morgue_row':morgue_row,
		'id_pack':id_pack}

	return render(request,'taws/morgue.html',context_dict)

def viewTestCase(request):

	import mysql.connector
	from git import Repo

	idTestRev=request.POST.get('idTestRev')
	action=request.GET.get('action','')

	context = RequestContext(request)
	if 'login' not in request.session:
		fromPage = request.META.get('HTTP_REFERER')
		context_dict={'fromPage':'viewTestCase'}
		return render_to_response('taws/login.html',context_dict,context)

	if idTestRev.isdigit():
		dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
		myRecordSet = dbConnection.cursor(dictionary=True)

		myRecordSet.execute("select revision,test_name,test_id from T_TEST_REVS join T_TEST on (T_TEST_test_id=test_id) where id_TestRev="+idTestRev)
		myTest=myRecordSet.fetchone()

		
		myRepo=Repo(settings.BASE_DIR + settings.GIT_REPO_PATH + settings.GIT_REPO_NAME)
		git=myRepo.git
		myFile=git.show(myTest['revision']+':'+myTest['test_name'])
		
		print

		myRecordSet.execute("select revision,id_TestRev from T_TEST_REVS join T_TEST on (T_TEST_test_id=test_id) where test_id="+str(myTest['test_id']))
		revList=[{'rev':row["revision"],'revId':row["id_TestRev"]} for row in myRecordSet]

		context_dict={'login':request.session['login'],'myFile':myFile,'testName':myTest['test_name'],'revision':myTest['revision'],'revList':revList}
	else:
		if action == 'update':
			tempMyFile = open(idTestRev,"w")
			tempMyFile.write(request.POST.get('testBody'))
			tempMyFile.close()

		tempMyFile = open(idTestRev,"r")
		myFile=tempMyFile.read()
		tempMyFile.close()

		context_dict={'login':request.session['login'],'myFile':myFile,'testName':idTestRev,'revision':"NA",'revList':"NA"}

	return render(request,'taws/viewTestCase.html',context_dict)

def topology(request):

	import mysql.connector

	dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
	myRecordSet = dbConnection.cursor(dictionary=True)

	myRecordSet.execute("select topology,scope_description,count(*) as numTPS,numEntity,topo_description from T_TPS join T_TEST_REVS on(id_TestRev=T_TEST_REVS_id_TestRev) join (select id_topology,T_TOPOLOGY.description as topo_description,count(*) as numEntity,T_SCOPE.description as scope_description from T_TOPOLOGY join T_TPY_ENTITY on(id_topology=T_TOPOLOGY_id_topology) join T_SCOPE on(id_scope=T_SCOPE_id_scope) where elemName like '%#%' group by id_topology) as concat_topology on(id_topology=topology) group by topology")
	topoList=[{'topology':row["topology"],'type':row["scope_description"],'numTPS':row["numTPS"],'numEntity':row["numEntity"],'topo_description':row["topo_description"]} for row in myRecordSet]

	context_dict={'topoList':topoList}

	return render(request,'taws/topology.html',context_dict)

def modify_job(request):
	context = RequestContext(request)
	context_dict={'nothing':'nothing'}
	import mysql.connector
	import glob,os,ntpath

	if 'login' not in request.session:
		fromPage = request.META.get('HTTP_REFERER')
		context_dict={'fromPage':'test_development'}
		return render_to_response('taws/login.html',context_dict,context)


	job_name=request.GET.get('jobName','')
	suiteFolder=settings.JENKINS['SUITEFOLDER']
	savingStr=request.POST.get('savingStr','')

	dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
	myRecordSet=dbConnection.cursor(dictionary=True)
	myRecordSet.execute("SET group_concat_max_len = 200000")
	dbConnection.commit()
  
	username=request.session['login']
	password=request.session['password']

	testString=[]
	localString=""
	#localPath=settings.JENKINS['SUITEFOLDER']+username+'_Development/workspace/'
	localPath=settings.JENKINS['SUITEFOLDER']+job_name+settings.JENKINS['JOB_STRUCT']

	if savingStr != '':
		localSuite = open(localPath+'suite.txt',"w")
		savingStringBody=''
		for myString in savingStr.split('$'):
			tempStr=myString.split('#')
			savingStringBody+=tempStr[0]
			if tempStr[1][0]=='2':savingStringBody+=' --DUTSet'
			if tempStr[1][1]=='2':savingStringBody+=' --testSet'
			if tempStr[1][2]=='2':savingStringBody+=' --testBody'
			if tempStr[1][3]=='2':savingStringBody+=' --testClean'
			if tempStr[1][4]=='2':savingStringBody+=' --DUTClean'
			savingStringBody+='\n'
		localSuite.write(savingStringBody[0:-1])
		localSuite.close()


	if os.path.isfile(localPath+'suite.txt'):
		localSuite = open(localPath+'suite.txt',"r")
		suiteFile=localSuite.read()
		localSuite.close() 

  
	for f in sorted(glob.glob(localPath+'*.py')):
		if os.path.isfile(f+'.prs'):
			iteration=ntpath.basename(f).split('_')[1]
			myRecordSet.execute("select * from T_TEST join T_TEST_REVS on (test_id=T_TEST_test_id) join (select T_TEST_REVS_id_TestRev,group_concat(concat(area_name,'-',tps_reference) order by id_tps separator '!') as tps,T_DOMAIN_id_domain from T_TPS join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on (id_area=T_AREA_id_area) group by T_TEST_REVS_id_TestRev) as T_TPS on(id_TestRev=T_TEST_REVS_id_TestRev) join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on(T_AREA_id_area=id_area) join T_PROD on(id_prod=T_PROD_id_prod) join T_SW_REL on(T_SW_REL_id_sw_rel=id_sw_rel) where id_TestRev="+iteration+" group by id_TestRev")
			row=myRecordSet.fetchone()

			myDict={'idTestRev':f,
				'product':row['product'],
				'sw_rel_name':row['sw_rel_name'],
				'area_name':row['area_name'],
				'tps':row['tps'].replace('!','\r\n'),
				'test_name':ntpath.basename(f),
	  			'duration':str(row['duration']),
	  			'metric':str(row['metric']),
	  			'topology':row['topology'],
	  			'dependency':row['dependency'],
	  			'author':row['author'],
	  			'description':row['description'],
	  			'last_update':str(row['last_update']),
	  			'sect1':'disabled' if row['run_section'][0]==0 else '',
	  			'sect2':'disabled' if row['run_section'][1]==0 else '',
	  			'sect3':'disabled' if row['run_section'][2]==0 else '',
	  			'sect4':'disabled' if row['run_section'][3]==0 else '',
	  			'sect5':'disabled' if row['run_section'][4]==0 else '',
	 			'lab':row['lab'],
	  			'revision':row['revision']}

			active=""
			tempActive=suiteFile.split(f)
			if len(tempActive)>1:
				active="checked"
				tempSect=tempActive[1].split('\n')
				myDict.update({'sectCheck1':'checked' if tempSect[0].rfind('--DUTSet')>=0 or tempSect[0].rfind(' --')<0 else '',
		  			'sectCheck2':'checked' if tempSect[0].rfind('--testSet')>=0 or tempSect[0].rfind(' --')<0 else '',
		  			'sectCheck3':'checked' if tempSect[0].rfind('--testBody')>=0 or tempSect[0].rfind(' --')<0 else '',
		  			'sectCheck4':'checked' if tempSect[0].rfind('--testClean')>=0 or tempSect[0].rfind(' --')<0 else '',
		  			'sectCheck5':'checked' if tempSect[0].rfind('--DUTClean')>=0 or tempSect[0].rfind(' --')<0 else '',
					'active':active})

     
			testString.append(myDict)
      

	#return  JsonResponse({'testString':testString,'localString':localString,'debug':localString}, safe=False)
	context_dict={'login':request.session['login'].upper(),'job_name':job_name,'test_list':testString,'debug':''}

	return render_to_response('taws/modify_job.html',context_dict,context)

def checkTestStatus(testpath,testfile):
	import os,ntpath
	import xml.etree.ElementTree as ET
	reportPath = testpath + 'test-reports/'
	testname = ntpath.splitext(testfile)[0]
	reportfile = reportPath + testname + '._main.XML'
	if os.path.isfile(reportfile):
		try:
			'''
			trying to parse the xml test file
			if no exception occours we assume the report completed and right formatted
			'''
			tree = ET.parse(reportfile)
			return 'Done'
		except:
			return 'Running'
			
	else:
		return 'Ready to Run'	
		
		
	'''	
		if os.stat(reportfile).st_size == 0:
			print('Running:%i'%os.stat(reportfile).st_size)
			return "Running"
		else:
			print('Done:%i'%os.stat(reportfile).st_size)
			return "Done"
			
	else:
		return "Ready to Run"
	'''

def checkTPSStatus(testpath,testfile,tps):
	import os,ntpath,glob,re
	import xml.etree.ElementTree as ET
	reportPath = testpath + 'test-reports/'
	testname = ntpath.splitext(testfile)[0]
	reportfile = reportPath + testname
	#checking the XML tps report file presence
	res=''
	print('\n\nchecking XML for tps:%s'%tps)
	for f in sorted(glob.glob(reportPath+'*.XML')):
		cmatch = re.match(reportfile+'.*'+tps+'\.XML',f)
		if cmatch: #found tps XMl file
			rfile = cmatch.group(0)
			if os.path.isfile(rfile):
				print('found match: %s'%rfile)
				try:
					'''
					trying to parse the xml test file
					if no exception occours we assume the report completed and right formatted
					'''
					
					tree = ET.parse(rfile)
					root = tree.getroot()
					print('XML Parsed!')
					res='list-group-item-info'
					for el in root.findall('testcase'):
						elerror = el.find('system-err')
						if not elerror is None:
							res='list-group-item-danger'
							break
					
					print(res)
				except Exception as eee:
		
					'''
					the XML parsing fails we assume the XML tps report file not completed yet.
					We leave blank
					'''
					print('error parsing')
					print(str(eee))
					break
				
			break
	
	return res



def updateJobStatus(request):
	import mysql.connector
	import glob,os,ntpath
	job_name=request.POST.get('jobName','')
	job_action=request.POST.get('jobAction','')
	
	
	dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
	myRecordSet=dbConnection.cursor(dictionary=True)
	myRecordSet.execute("SET group_concat_max_len = 200000")
	dbConnection.commit()
	
	
	
	
	testString=[]
	localString=""
	#localPath=settings.JENKINS['SUITEFOLDER']+username+'_Development/workspace/'
	localPath=settings.JENKINS['SUITEFOLDER']+job_name+settings.JENKINS['JOB_STRUCT']
	print('\n\ncalled updateJobStatus...')
	print('jenkins job path: %s'%localPath)


	if os.path.isfile(localPath+'suite.txt'):
		localSuite = open(localPath+'suite.txt',"r")
		suiteFile=localSuite.read()
		localSuite.close() 

  
	for f in sorted(glob.glob(localPath+'*.py')):
		if os.path.isfile(f+'.prs'):
			iteration=ntpath.basename(f).split('_')[1]
			myRecordSet.execute("select * from T_TEST join T_TEST_REVS on (test_id=T_TEST_test_id) join (select T_TEST_REVS_id_TestRev,group_concat(concat(area_name,'_',tps_reference) order by id_tps separator '!') as tps,T_DOMAIN_id_domain from T_TPS join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on (id_area=T_AREA_id_area) group by T_TEST_REVS_id_TestRev) as T_TPS on(id_TestRev=T_TEST_REVS_id_TestRev) join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on(T_AREA_id_area=id_area) join T_PROD on(id_prod=T_PROD_id_prod) join T_SW_REL on(T_SW_REL_id_sw_rel=id_sw_rel) where id_TestRev="+iteration+" group by id_TestRev")
			row=myRecordSet.fetchone()
			tpslist=row['tps'].split('!')
			tpsreturnlist = '<ul class="list-group">'
			
			for tps in tpslist:
				res=checkTPSStatus(localPath, ntpath.basename(f),tps)
				tpsreturnlist = tpsreturnlist + '<li class="list-group-item '+res+'">'+tps+'</li>'
				
				
			tpsreturnlist = tpsreturnlist + '</ul>'
			#"tps":row['tps'].replace('!','<br>'),

			myDict={"ctrl":"",
					"tps":tpsreturnlist,
					"test":ntpath.basename(f),
					"rev":row['revision'],
					"duration":str(row['duration']),
					"tpgy":row['topology'],
					"status":checkTestStatus(localPath, ntpath.basename(f)),
					"testId":f,
					"dependency":row['dependency'],
					"metric":str(row['metric']),
					"author":row['author'],
					"description":row['description']
					}
			#testString.append(myDict)
			testString.append(myDict)
	print('\n\n...updateJobStatus Done!!') 
	return JsonResponse({"job_name":job_name,"data":testString}, safe=True)


	#if job_action == "ajaxpoll":
	#return  JsonResponse({'testString':testString,'localString':localString,'debug':localString}, safe=False)
	#	return JsonResponse({"job_name":job_name,"test_list":testString}, safe=True)
	#else:
	#	return testString



def getCurrentBuild(request):
	
	context = RequestContext(request)
	context_dict={'nothing':'nothing'}
	

	if 'login' not in request.session:
		fromPage = request.META.get('HTTP_REFERER')
		context_dict={'fromPage':'test_development'}
		return render_to_response('taws/login.html',context_dict,context)


	job_name=request.POST.get('jobName','')

	
  
	username=request.session['login']
	password=request.session['password']
	test_list=updateJobStatus(request)
	
	context_dict={'login':request.session['login'].upper(),'job_name':job_name,'test_list':test_list,'debug':''}
	return render_to_response('taws/getCurrentBuild.html',context_dict,context)

def changeManualStatus(request):
	
	import xmlrpc.client
	import json
	import mysql.connector
	
	context = RequestContext(request)
	idPowerMngmt=request.POST.get('idPowerMngmt','')
	modifier=request.POST.get('modifier','')
	newStatus=request.POST.get('newStatus','')
	newStatusStr="Manual"
	if newStatus == "1": newStatusStr="Auto"
	
	dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'],port=settings.DATABASES['default']['PORT'])
	myRecordSet = dbConnection.cursor(dictionary=True)
	SQL="insert into T_POWER_STATUS (select "+idPowerMngmt+",power_status,null,'"+modifier+"','Change Rack Mode to "+newStatusStr+"',"+newStatus+" from T_POWER_STATUS where T_POWER_MNGMT_id_powerMngmt="+idPowerMngmt+" order by last_change desc limit 1)"
	
	myRecordSet.execute(SQL)
	dbConnection.commit()

	context_dict={}
	print('Change Manual Status')
	return HttpResponse(json.dumps(context_dict),content_type="application/json")

def changePowerStatus(request):
	
	import xmlrpc.client
	import json
	import mysql.connector
	
	context = RequestContext(request)
	idPowerMngmt=request.POST.get('idPowerMngmt','')
	modifier=request.POST.get('modifier','')
	newStatus=request.POST.get('newStatus','')
	
	dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'],port=settings.DATABASES['default']['PORT'])
	myRecordSet = dbConnection.cursor(dictionary=True)
	SQL="SELECT ip,pin FROM T_POWER_MNGMT join T_NET using(T_EQUIPMENT_id_equipment) where id_powerMngmt="+idPowerMngmt
	myRecordSet.execute(SQL)
	row=myRecordSet.fetchone()

	proxy = xmlrpc.client.ServerProxy("http://"+row['ip']+":8080/")
	switchReport = proxy.setGPIO([{'gpio':row['pin'],'status':newStatus,'idPowerMngmt':idPowerMngmt,'modifier':modifier}])

	context_dict={'switchReport':switchReport}
	print('Change Power Status')
	return HttpResponse(json.dumps(context_dict),content_type="application/json")
	#return {'switchReport':switchReport}

def getScheduledTasks(request):
	
	import json
	import mysql.connector
	
	#context = RequestContext(request)
	idPowerMngmt=request.POST.get('idPowerMngmt','')
	
	dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'],port=settings.DATABASES['default']['PORT'])
	myRecordSet = dbConnection.cursor(dictionary=True)
	#SQL="SELECT ip,pin FROM T_POWER_MNGMT join T_NET using(T_EQUIPMENT_id_equipment) where id_powerMngmt="+idPowerMngmt
	SQL="select * from T_POWER_SCHEDULE where T_POWER_MNGMT_id_powerMngmt="+idPowerMngmt
	myRecordSet.execute(SQL)
	scheduled=[]
	for row in myRecordSet:
		scheduled.append({'id_powerSchedule':str(row["idT_POWER_SCHEDULE"]),
			'start_time':str(row["start_time"]),
			'stop_time':str(row["stop_time"]),
			'interval':str(int(row["interval"])/1440)
		})

	context_dict={'login':request.session['login'],
		'scheduled':scheduled,
		'idPowerMngmt':idPowerMngmt
	}
	print('Get Scheduled Task')
	return HttpResponse(json.dumps(context_dict),content_type="application/json")


def getRackLog(request):
	
	import json
	import mysql.connector
	
	#context = RequestContext(request)
	idPowerMngmt=request.POST.get('idPowerMngmt','')
	
	dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'],port=settings.DATABASES['default']['PORT'])
	myRecordSet = dbConnection.cursor(dictionary=True)
	myRecordSet.execute("SET group_concat_max_len = 200000")
	dbConnection.commit()
	#SQL="SELECT ip,pin FROM T_POWER_MNGMT join T_NET using(T_EQUIPMENT_id_equipment) where id_powerMngmt="+idPowerMngmt
	SQL="select group_concat(concat('<tr><td>',last_change,'</td><td>',modifier,'</td><td>',remarks,'</td></tr>') order by last_change desc separator '') as log from T_POWER_STATUS where T_POWER_MNGMT_id_powerMngmt="+idPowerMngmt
	#SQL="select group_concat(concat(last_change,' - ',modifier,' ',if(remarks='Change Rack Mode',concat(remarks,' to ',manual_status),if(remarks='Change Power Status',concat(remarks,' to ',power_status),remarks))) order by last_change desc separator '<br>') as log from T_POWER_STATUS where T_POWER_MNGMT_id_powerMngmt="+idPowerMngmt
	myRecordSet.execute(SQL)
	row=myRecordSet.fetchone()

	context_dict={'login':request.session['login'],
			'log':row["log"]
		}
	#location=row["T_LOCATION_id_location"]
	#SQL="select * from T_EQUIPMENT where T_LOCATION_id_location="+location
	#myRecordSet.execute(SQL)
	#row=myRecordSet.fetchone()

	print('Get Rack Details')
	return HttpResponse(json.dumps(context_dict),content_type="application/json")

def getRackDetails(request):
	
	import json
	import mysql.connector
	
	#context = RequestContext(request)
	idPowerMngmt=request.POST.get('idPowerMngmt','')
	
	dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'],port=settings.DATABASES['default']['PORT'])
	myRecordSet = dbConnection.cursor(dictionary=True)
	#SQL="SELECT ip,pin FROM T_POWER_MNGMT join T_NET using(T_EQUIPMENT_id_equipment) where id_powerMngmt="+idPowerMngmt
	SQL="select * from T_POWER_MNGMT join T_NET using(T_EQUIPMENT_id_equipment) join T_LOCATION on(id_location=T_LOCATION_id_location) join T_EQUIPMENT on(id_equipment=T_EQUIPMENT_id_equipment) where id_powerMngmt="+idPowerMngmt
	myRecordSet.execute(SQL)
	row=myRecordSet.fetchone()

	context_dict={'login':request.session['login'],
			'idPowerMngmt':idPowerMngmt,
			'name':str(row["name"]),
			'pin':str(row["pin"]),
			'ip':row["IP"],
			'owner':row["owner"]
		}
	#location=row["T_LOCATION_id_location"]
	#SQL="select * from T_EQUIPMENT where T_LOCATION_id_location="+location
	#myRecordSet.execute(SQL)
	#row=myRecordSet.fetchone()

	print('Get Rack Details')
	return HttpResponse(json.dumps(context_dict),content_type="application/json")

def deleteScheduledTasks(request):
	
	import json
	import mysql.connector
	
	#context = RequestContext(request)
	idPowerMngmt=request.POST.get('idPowerMngmt','')
	idPowerSchedule=request.POST.get('idPowerSchedule','')
	
	dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'],port=settings.DATABASES['default']['PORT'])
	myRecordSet = dbConnection.cursor(dictionary=True)
	#SQL="SELECT ip,pin FROM T_POWER_MNGMT join T_NET using(T_EQUIPMENT_id_equipment) where id_powerMngmt="+idPowerMngmt
	SQL="delete from T_POWER_SCHEDULE where idT_POWER_SCHEDULE="+idPowerSchedule
	myRecordSet.execute(SQL)
	dbConnection.commit()
	
	SQL="select * from T_POWER_SCHEDULE where T_POWER_MNGMT_id_powerMngmt="+idPowerMngmt
	myRecordSet.execute(SQL)
	scheduled=[]
	for row in myRecordSet:
		scheduled.append({'id_powerSchedule':str(row["idT_POWER_SCHEDULE"]),
			'start_time':str(row["start_time"]),
			'stop_time':str(row["stop_time"]),
			'interval':row["interval"]
		})

	context_dict={'login':request.session['login'],
		'scheduled':scheduled,
		'idPowerMngmt':idPowerMngmt
	}
	print('Delete Scheduled Task')
	return HttpResponse(json.dumps(context_dict),content_type="application/json")

def createScheduledTasks(request):
	
	import json
	import mysql.connector
	
	#context = RequestContext(request)
	idPowerMngmt=request.POST.get('idPowerMngmt','')
	txtNewStartDate=request.POST.get('txtNewStartDate','')
	#txtNewStartHour=request.POST.get('txtNewStartHour','')
	txtNewStopDate=request.POST.get('txtNewStopDate','')
	#txtNewStopHour=request.POST.get('txtNewStopHour','')
	txtInterval=request.POST.get('txtInterval','')
	
	dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'],port=settings.DATABASES['default']['PORT'])
	myRecordSet = dbConnection.cursor(dictionary=True)
	#SQL="SELECT ip,pin FROM T_POWER_MNGMT join T_NET using(T_EQUIPMENT_id_equipment) where id_powerMngmt="+idPowerMngmt
	SQL="insert into T_POWER_SCHEDULE (T_POWER_MNGMT_id_powerMngmt, start_time, stop_time, T_POWER_SCHEDULE.interval) VALUES('"+idPowerMngmt+"','"+txtNewStartDate+":00','"+txtNewStopDate+":00','"+str(int(txtInterval)*1440)+"')"
	myRecordSet.execute(SQL)
	dbConnection.commit()
	
	SQL="select * from T_POWER_SCHEDULE where T_POWER_MNGMT_id_powerMngmt="+idPowerMngmt
	myRecordSet.execute(SQL)
	scheduled=[]
	for row in myRecordSet:
		scheduled.append({'id_powerSchedule':str(row["idT_POWER_SCHEDULE"]),
			'start_time':str(row["start_time"]),
			'stop_time':str(row["stop_time"]),
			'interval':row["interval"]
		})

	context_dict={'login':request.session['login'],
		'scheduled':scheduled,
		'idPowerMngmt':idPowerMngmt
	}
	print('Create Scheduled Task')
	return HttpResponse(json.dumps(context_dict),content_type="application/json")

def power_management(request):
	
	import mysql.connector

	context_dict={'nothing':'nothing'}
	powerLevel=request.GET.get('powerLevel','')

	context = RequestContext(request)
	if 'login' not in request.session:
		fromPage = request.META.get('HTTP_REFERER')
		context_dict={'fromPage':'power_management'}
		return render_to_response('taws/login.html',context_dict,context)

	dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'],port=settings.DATABASES['default']['PORT'])
	myRecordSet = dbConnection.cursor(dictionary=True)
	
	if powerLevel == '':
		SQL="select room,count(row) as numRow,sum(racks) as numRacks from (SELECT room,row,count(*) as racks FROM T_LOCATION group by room,row) as myTable group by room"
		myRecordSet.execute(SQL)
		labs=[]
		for row in myRecordSet:
			labs.append({'room':row["room"],
				'numRow':row["numRow"],
				'numRacks':row["numRacks"]
			})
	
		context_dict={'login':request.session['login'],
			'labs':labs,
			'powerLevel':powerLevel
		}
		return render_to_response('taws/power_management.html',context_dict,context)

	if powerLevel == 'row':
		lab=request.POST.get('lab','')
		SQL="SELECT row,count(*)-1 as numRacks FROM T_LOCATION where room='"+lab+"' group by row order by row"
		myRecordSet.execute(SQL)
		rows=[]
		for row in myRecordSet:
			rows.append({'row':row["row"],
				'lab':lab,
				'numRacks':row["numRacks"]
			})
	
		context_dict={'login':request.session['login'],
			'rows':rows,
			'powerLevel':powerLevel
		}
		return render_to_response('taws/power_management.html',context_dict,context)

	if powerLevel == 'rack':
		lab=request.POST.get('lab','')
		myrow=request.POST.get('row','')
		#SQL="select powerTable.owner,pin,rack,T_EQUIPMENT.name,id_equipment,id_location,ip,if(power_status=1,'danger','success') as power_status from (select * from (SELECT * FROM T_POWER_MNGMT order by last_change desc) as myTable group by T_EQUIPMENT_id_equipment,pin) as powerTable join T_EQUIPMENT on(id_equipment=T_EQUIPMENT_id_equipment) join T_LOCATION on(id_location=powerTable.T_LOCATION_id_location) join T_NET on(id_equipment=T_NET.T_EQUIPMENT_id_equipment)"
		#SQL="select powerTable.owner,pin,rack,T_EQUIPMENT.name,id_equipment,id_location,ip,if(power_status=1,'danger','success') as power_status,log from (select *,group_concat(concat(last_change,' - ',remarks) separator '<br>') as log from (SELECT * FROM T_POWER_MNGMT order by last_change desc) as myTable group by T_EQUIPMENT_id_equipment,pin) as powerTable join T_EQUIPMENT on(id_equipment=T_EQUIPMENT_id_equipment) join T_LOCATION on(id_location=powerTable.T_LOCATION_id_location) join T_NET on(id_equipment=T_NET.T_EQUIPMENT_id_equipment)"
		SQL="select id_powerMngmt,powerTable.owner,manual_status,pin,rack,T_EQUIPMENT.name,id_equipment,id_location,ip,power_status from (select *,1 as log from (SELECT * FROM T_POWER_MNGMT left join T_POWER_STATUS on(id_powerMngmt=T_POWER_MNGMT_id_powerMngmt) order by last_change desc) as myTable group by T_EQUIPMENT_id_equipment,pin) as powerTable join T_EQUIPMENT on(id_equipment=T_EQUIPMENT_id_equipment) join T_LOCATION on(id_location=powerTable.T_LOCATION_id_location) join T_NET on(id_equipment=T_NET.T_EQUIPMENT_id_equipment) where room='"+lab+"' and row='"+myrow+"'"
		#SQL="select scheduling,id_powerMngmt,powerTable.owner,manual_status,pin,rack,T_EQUIPMENT.name,id_equipment,id_location,ip,if(power_status=1,'danger','success') as power_status,log from (select *,group_concat(concat(last_change,' - ',remarks) separator '<br>') as log from (SELECT * FROM T_POWER_MNGMT join T_POWER_STATUS on(id_powerMngmt=T_POWER_MNGMT_id_powerMngmt) order by last_change desc) as myTable group by T_EQUIPMENT_id_equipment,pin) as powerTable join T_EQUIPMENT on(id_equipment=T_EQUIPMENT_id_equipment) join T_LOCATION on(id_location=powerTable.T_LOCATION_id_location) join T_NET on(id_equipment=T_NET.T_EQUIPMENT_id_equipment) left join (select T_POWER_MNGMT_id_powerMngmt,group_concat(concat('<tr><td>',start_time,'</td><td>',stop_time,'</td><td>',T_POWER_SCHEDULE.interval,'</td><td><button type=\\\\'button\\\\' onclick=\\\"deleteSchedule(this);\\\" class=\\\"btn btn-primary\\\"><span class=\\\"glyphicon glyphicon-trash\\\" aria-hidden=\\\"true\\\"></span></button></td></tr>') separator '') as scheduling from T_POWER_SCHEDULE group by T_POWER_MNGMT_id_powerMngmt) as T_POWER_SCHEDULE using(T_POWER_MNGMT_id_powerMngmt)"
		#SQL="SELECT *,netBench.IP as benchIP,netBench.NM as benchNM,netBench.GW as benchGW,group_concat(concat(ip1.ip,':',port,' ','Slot ',if(slot is null,'-',slot),' SubSlot ',if(subslot is null,'-',subslot)) separator '<br>') as serials,T_SCOPE.description as scope,T_EQUIP_TYPE.name as type,T_EQUIPMENT.name as benchName,if(status like '%ING%',status,'IDLE') as benchStatus,T_EQUIPMENT.owner as reference,runtime.owner as author FROM T_EQUIPMENT LEFT JOIN (select * from T_RTM_BODY left join T_RUNTIME on(id_run=T_RUNTIME_id_run) where status='RUNNING') as runtime on(id_equipment=T_EQUIPMENT_id_equipment) left join T_EQUIP_TYPE on(id_type=T_EQUIP_TYPE_id_type) left join T_NET as netBench on(netBench.T_EQUIPMENT_id_equipment=id_equipment) LEFT JOIN T_LOCATION on(T_LOCATION_id_location=id_location) LEFT JOIN T_SERIAL on(T_SERIAL.T_EQUIPMENT_id_equipment=id_equipment) LEFT JOIN T_SCOPE on(T_SCOPE_id_scope=id_scope) LEFT JOIN T_NET as ip1 on(T_SERIAL.T_NET_id_ip=ip1.id_ip) group by id_equipment"
		
		myRecordSet.execute(SQL)
		benches={'3A':{},
				'3B':{},
				'4A':{},
				'4B':{},
				'5A':{},
				'5B':{},
				'6A':{},
				'6B':{},
				'7A':{},
				'7B':{},
				'8A':{},
				'8B':{},
				'9A':{},
				'9B':{},
				'10A':{},
				'10B':{},
				'11A':{},
				'11B':{},
				'12A':{},
				'12B':{},
				'13A':{},
				'13B':{},
				'14A':{},
				'14B':{},
				'15A':{},
				'15B':{},
				'16A':{},
				'16B':{}
				}
		numBenches=0
		for row in myRecordSet:
			numBenches+=1
			benches[row["rack"]].update({'rack':row["rack"],
				'id_powerMngmt':row['id_powerMngmt'],
				'manual_status':row['manual_status'],
				'name':row["name"],
				'ip':row["ip"],
				'pin':row["pin"],
				'owner':row["owner"],
				'id_equipment':row["id_equipment"],
				'id_location':row["id_location"],
				'power_status':row["power_status"]
			})
	
		context_dict={'login':request.session['login'],
			'role':request.session['role'],
			'lab':lab,
			'row':myrow,
			'benches':benches,
			'powerLevel':powerLevel
		}
		return render_to_response('taws/power_management.html',context_dict,context)

def getUserRepoBranch(userId):
	from git import Repo
	import re
	currbranch = None
	blist=[]
	repoPath='/users/'+userId+ settings.GIT_REPO_PATH + settings.GIT_REPO_NAME
	try:
		myRepo=Repo(repoPath)
		currbranch=myRepo.active_branch.name.split(settings.GIT_DEVBRANCH_SPLIT)[0]
		print('\n\nCurrent User GIT Repo checkout on branch: %s\n\n'%currbranch)
		for itembr in myRepo.heads:
			if re.match('.*'+settings.GIT_DEVBRANCH_SPLIT+userId+'_dev.*',itembr.name):
				blist.append(itembr.name.split(settings.GIT_DEVBRANCH_SPLIT)[0])
				
		return {'current':currbranch,'list':blist}
	except Exception as xxx:
		print('ERROR on getUserRepoBranch')
		print(str(xxx))
		return {'current':currbranch,'list':blist}


def setUserRepo(userId,branch):
	from git import Repo, RemoteProgress
	
	class MyProgressPrinter(RemoteProgress):
		def update(self, op_code, cur_count, max_count=None, message=''):
			print(op_code, cur_count, max_count, cur_count / (max_count or 100.0), message or "NO MESSAGE")
	# end
	
	#setting the development branch name i.e. '7.2#ippolf_dev' for main branch 7.2 and user ippolf
	dev_branch = branch + settings.GIT_DEVBRANCH_SPLIT + userId + "_dev"
	
	res = "Setting GIT Repository for " + userId + " on branch " + dev_branch + " ..."
	print(res)
	try:
		repoPath='/users/'+userId+ settings.GIT_REPO_PATH + settings.GIT_REPO_NAME
		myRepo=Repo(repoPath)
		git=myRepo.git
		
		#check if the user is already using the dev_branch branch
		
		if myRepo.active_branch.name == dev_branch:
			#no more check, just exit in a right way
			print("GIT Repository for " + userId + " Already SET on branch " + dev_branch)
			res = "OK"
			return res
		
		#check if repository is in a clean status
		#if we have modified files we cannot checkout to master branch and we exit with git status message
		#if myRepo.is_dirty(): return str(git.status()).replace('\n','<br>')
		#print("checking out the GIT Repository " + repoPath + " to master branch ...")
		
		
		# check if dev_branch already exists
		bfound=False
		
		for myitem in myRepo.heads:
			if myitem.name == dev_branch:
				bfound=True
				break
				
		if bfound:
			print (dev_branch + " found")
			#checkout the development branch
			#myRepo.head.ref = myRepo.heads[dev_branch]
			myRepo.heads[dev_branch].checkout()
		else:
			print (dev_branch + " NOT found")
			#we have to checkout from release branch...
			# check if release branch exists
			bfound=False
		
			for myitem in myRepo.heads:
				if myitem.name == branch:
					bfound=True
					break
			
			if not bfound:return " GIT release branch " + branch + " doesn't exist. Please align your local GIT Repository"

			#here we come if the release branch exists an
			
			# checkout the master branch and pull the content_type
			#
		
			#changing repo head to release branch
			myRepo.head.ref = myRepo.heads[branch]
			#getting origin reference
			origin = myRepo.remotes.origin
			if not origin.exists(): return "remote origin not found for GIT repository " + repoPath + " Please check your GIT Repository configuration"
			# try to pull from origin
	
			for pull_info in origin.pull(progress=MyProgressPrinter()):
				print("Updated %s to %s " % (pull_info.ref, pull_info.commit))
	
			# here the check  the pull result is missing, we are assuming no errors in pull operation
			
			
			
			#checkout the new develpment branch from branch release just updated
			
			myRepo.heads[branch].checkout(b=dev_branch)
			
			#myRepo.create_head(dev_branch)
			#myRepo.head.ref = myRepo.heads[dev_branch]
			#myRepo.heads[dev_branch].checkout()
			
		#At this point we are set the Rpository to the correct development branch
		#we have to align/merge with main release branch?
		
		print("GIT Repository for " + userId + " SET on branch " + dev_branch)
		res = "OK"
		return res
	except Exception as xxx:
		print('ERROR on setUserRepo')
		print(str(xxx))
		return str(xxx).replace('\n','<br>')
		
def accesso(request):
	from taws.models import TTest,TTestRevs
	from django.core import serializers
	import mysql.connector

	myAction=request.POST.get('action','')

	if myAction=='loadSuite':

		import ntpath

		owner=request.POST.get('owner','')
		loadID=request.POST.get('loadID','')
		myVar=''

		dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
		myRecordSet=dbConnection.cursor(dictionary=True)
		#myRecordSet.execute("select *,T_SUITES_BODY.run_section as section from T_SUITES join T_SUITES_BODY on(id_suite=T_SUITES_id_suite) join T_TEST_REVS on(id_TestRev=T_TEST_REVS_id_TestRev) join T_TEST on(test_id=T_TEST_test_id) join (select T_TEST_REVS_id_TestRev,group_concat(concat(area_name,'-',tps_reference) separator '<br>') as tps from T_TPS join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on (id_area=T_AREA_id_area) group by T_TEST_REVS_id_TestRev) as T_TPS on(id_TestRev=T_TPS.T_TEST_REVS_id_TestRev) join T_TEST_COMPATIBILITY on(id_TestRev=T_TEST_COMPATIBILITY.T_TEST_REVS_id_TestRev) join T_DOMAIN on(id_domain=T_TEST_COMPATIBILITY.T_DOMAIN_id_domain) join T_AREA on(T_AREA_id_area=id_area) join T_PROD on(id_prod=T_PROD_id_prod) join T_SW_REL on(T_SW_REL_id_sw_rel=id_sw_rel) where id_suite="+str(loadID)+" group by id_TestRev,TCOrder order by TCOrder")
		myRecordSet.execute("select *,T_SUITES_BODY.run_section as section from T_SUITES join T_SUITES_BODY on(id_suite=T_SUITES_id_suite) join T_TEST_REVS on(id_TestRev=T_TEST_REVS_id_TestRev) join T_TEST on(test_id=T_TEST_test_id) join (select T_TEST_REVS_id_TestRev,group_concat(concat(area_name,'-',tps_reference) separator '<br>') as tps,T_DOMAIN_id_domain from T_TPS join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on (id_area=T_AREA_id_area) group by T_TEST_REVS_id_TestRev) as T_TPS on(id_TestRev=T_TPS.T_TEST_REVS_id_TestRev) join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on(T_AREA_id_area=id_area) join T_PROD on(id_prod=T_PROD_id_prod) join T_SW_REL on(T_SW_REL_id_sw_rel=id_sw_rel) where id_suite="+str(loadID)+" group by id_TestRev,TCOrder order by TCOrder")
		rows=myRecordSet.fetchall()

		testString=''
		for row in rows:
			testString+=(str(row['id_TestRev'])+"#"+\
			row['product']+"#"+\
			row['sw_rel_name']+"#"+\
			"0#"+\
			row['area_name']+"#"+\
			row['tps']+"#"+\
			ntpath.basename(row['test_name'])+"#"+\
			str(row['duration'])+"#"+\
			str(row['metric'])+"#"+\
			row['topology']+"#"+\
			str(row['id_TestRev'])+"#"+\
			row['sw_rel_name']+"#"+\
			row['dependency']+"#"+\
			"NA#"+\
			row['author']+"#"+\
			row['description']+"#"+\
			str(row['last_update'])+"#"+\
			row['section']+"#"+\
			"[MY_REVISIONS]#"+\
			row['lab']+"#"+\
			row['revision']+'$')

			myRecordSet.execute("select group_concat(concat(revision,'|',id_TestRev) separator '!') as revisions from T_TEST join T_TEST_REVS on (test_id=T_TEST_test_id) join (select T_TEST_REVS_id_TestRev,group_concat(concat(area_name,'-',tps_reference) order by id_tps separator '!') as tps,T_DOMAIN_id_domain from T_TPS join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on (id_area=T_AREA_id_area) group by T_TEST_REVS_id_TestRev) as T_TPS on(id_TestRev=T_TEST_REVS_id_TestRev) join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on(T_AREA_id_area=id_area) join T_PROD on(id_prod=T_PROD_id_prod) join T_SW_REL on(T_SW_REL_id_sw_rel=id_sw_rel) where T_TEST_test_id="+str(row['T_TEST_test_id'])+" group by T_TEST_test_id")
			testString=testString.replace('[MY_REVISIONS]',myRecordSet.fetchone()['revisions'])

		dbConnection.close()
		myVar='finito'

		return  JsonResponse({'testString':testString,'myVar':myVar}, safe=False)

	if myAction=='queryDB':
		import ntpath

		queryProduct=request.POST.get('queryProduct','')
		querySW=request.POST.get('querySWRelease','')
		queryArea=request.POST.get('queryArea','')

		dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
		myRecordSet = dbConnection.cursor(dictionary=True,buffered=True)
		#myRecordSet.execute("select *,group_concat(concat(revision,'|',id_TestRev) separator '!') as revision from T_TEST join T_TEST_REVS on (test_id=T_TEST_test_id) join (select T_TEST_REVS_id_TestRev,group_concat(concat(area_name,'-',tps_reference) order by id_tps separator '!') as tps from T_TPS join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on (id_area=T_AREA_id_area) group by T_TEST_REVS_id_TestRev) as T_TPS on(id_TestRev=T_TEST_REVS_id_TestRev) join T_TEST_COMPATIBILITY on(id_TestRev=T_TEST_COMPATIBILITY.T_TEST_REVS_id_TestRev) join T_DOMAIN on(id_domain=T_TEST_COMPATIBILITY.T_DOMAIN_id_domain) join T_AREA on(T_AREA_id_area=id_area) join T_PROD on(id_prod=T_PROD_id_prod) join T_SW_REL on(T_SW_REL_id_sw_rel=id_sw_rel) where product='"+queryProduct+"' and sw_rel_name='"+querySW+"' and area_name='"+queryArea+"' group by T_TEST_test_id")
		#myRecordSet.execute("select *,group_concat(concat(revision,'|',id_TestRev) separator '!') as revisions from (select id_TestRev,product,sw_rel_name,run_section,area_name,tps,test_name,duration,metric,topology,dependency,author,description,last_update,revision,lab,test_id from T_TEST join T_TEST_REVS on (test_id=T_TEST_test_id) join (select T_TEST_REVS_id_TestRev,group_concat(concat(area_name,'-',tps_reference) order by id_tps separator '<br>') as tps from T_TPS join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on (id_area=T_AREA_id_area) group by T_TEST_REVS_id_TestRev) as T_TPS on(id_TestRev=T_TEST_REVS_id_TestRev) join T_TEST_COMPATIBILITY on(id_TestRev=T_TEST_COMPATIBILITY.T_TEST_REVS_id_TestRev) join T_DOMAIN on(id_domain=T_TEST_COMPATIBILITY.T_DOMAIN_id_domain) join T_AREA on(T_AREA_id_area=id_area) join T_PROD on(id_prod=T_PROD_id_prod) join T_SW_REL on(T_SW_REL_id_sw_rel=id_sw_rel) where product='"+queryProduct+"' and sw_rel_name='"+querySW+"' and area_name='"+queryArea+"' order by test_id,id_TestRev desc) as myTable group by test_id")
		#myRecordSet.execute("select *,group_concat(concat(revision,'|',id_TestRev) separator '!') as revisions from (select id_TestRev,product,sw_rel_name,run_section,area_name,tps,test_name,duration,metric,topology,dependency,author,description,last_update,revision,lab,test_id from T_TEST join T_TEST_REVS on (test_id=T_TEST_test_id) join (select T_TEST_REVS_id_TestRev,group_concat(concat(area_name,'-',tps_reference) order by id_tps separator '<br>') as tps,T_DOMAIN_id_domain from T_TPS join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on (id_area=T_AREA_id_area) group by T_TEST_REVS_id_TestRev) as T_TPS on(id_TestRev=T_TEST_REVS_id_TestRev) join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on(T_AREA_id_area=id_area) join T_PROD on(id_prod=T_PROD_id_prod) join T_SW_REL on(T_SW_REL_id_sw_rel=id_sw_rel) where product='"+queryProduct+"' and sw_rel_name='"+querySW+"' order by test_id,id_TestRev desc) as myTable group by test_id")
		#myRecordSet.execute("select *,group_concat(concat(revision,'|',id_TestRev) separator '!') as revisions from (select id_TestRev,product,sw_rel_name,run_section,area_name,tps,test_name,duration,metric,topology,dependency,author,description,last_update,revision,lab,test_id from T_TEST join T_TEST_REVS on (test_id=T_TEST_test_id) join (select tps,area_name,T_TEST_REVS_id_TestRev from T_TPS join (select T_TEST_REVS_id_TestRev,group_concat(concat(area_name,'-',tps_reference) order by id_tps separator '<br>') as tps from T_TPS join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on (id_area=T_AREA_id_area) group by T_TEST_REVS_id_TestRev) as myTest using(T_TEST_REVS_id_TestRev) join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on (id_area=T_AREA_id_area) where area_name='"+queryArea+"') as T_TPS on(id_TestRev=T_TEST_REVS_id_TestRev) join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on(T_AREA_id_area=id_area) join T_PROD on(id_prod=T_PROD_id_prod) join T_SW_REL on(T_SW_REL_id_sw_rel=id_sw_rel) where product='"+queryProduct+"' and sw_rel_name='"+querySW+"' order by test_id,id_TestRev desc) as myTable group by test_id")
		myRecordSet.execute("select *,group_concat(distinct concat(revision,'|',id_TestRev) separator '!') as revisions from (select id_TestRev,product,sw_rel_name,run_section,area_name,tps,test_name,duration,metric,topology,dependency,author,description,last_update,revision,lab,test_id from T_TEST join T_TEST_REVS on (test_id=T_TEST_test_id) join (select tps,T_DOMAIN_id_domain ,T_TEST_REVS_id_TestRev from T_TPS join (select T_TEST_REVS_id_TestRev,group_concat(concat(area_name,'-',tps_reference) order by id_tps separator '<br>') as tps from T_TPS join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on (id_area=T_AREA_id_area) group by T_TEST_REVS_id_TestRev) as myTest using(T_TEST_REVS_id_TestRev) join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on (id_area=T_AREA_id_area) where area_name='"+queryArea+"') as T_TPS on(id_TestRev=T_TEST_REVS_id_TestRev) join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on(T_AREA_id_area=id_area) join T_PROD on(id_prod=T_PROD_id_prod) join T_SW_REL on(T_SW_REL_id_sw_rel=id_sw_rel) where product='"+queryProduct+"' and sw_rel_name='"+querySW+"' order by test_id,id_TestRev desc) as myTable group by test_id")
		myStr="select *,group_concat(concat(revision,'|',id_TestRev) separator '!') as revisions from (select id_TestRev,product,sw_rel_name,run_section,area_name,tps,test_name,duration,metric,topology,dependency,author,description,last_update,revision,lab,test_id from T_TEST join T_TEST_REVS on (test_id=T_TEST_test_id) join (select T_TEST_REVS_id_TestRev,group_concat(concat(area_name,'-',tps_reference) order by id_tps separator '<br>') as tps,T_DOMAIN_id_domain from T_TPS join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on (id_area=T_AREA_id_area) group by T_TEST_REVS_id_TestRev) as T_TPS on(id_TestRev=T_TEST_REVS_id_TestRev) join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on(T_AREA_id_area=id_area) join T_PROD on(id_prod=T_PROD_id_prod) join T_SW_REL on(T_SW_REL_id_sw_rel=id_sw_rel) where product='"+queryProduct+"' and sw_rel_name='"+querySW+"' and area_name='"+queryArea+"' order by test_id,id_TestRev desc) as myTable group by test_id"
		rows=myRecordSet.fetchall()
		testString=''
		for row in rows:
			testString+=(str(row['id_TestRev'])+"#"+\
			row['product']+"#"+\
			row['sw_rel_name']+"#"+\
			"0#"+\
			row['area_name']+"#"+\
			row['tps']+"#"+\
			ntpath.basename(row['test_name'])+"#"+\
			str(row['duration'])+"#"+\
			str(row['metric'])+"#"+\
			row['topology']+"#"+\
			str(row['id_TestRev'])+"#"+\
			row['sw_rel_name']+"#"+\
			row['dependency']+"#"+\
			row['test_name']+"#"+\
			row['author']+"#"+\
			row['description']+"#"+\
			str(row['last_update'])+"#"+\
			row['run_section']+"#"+\
			row['revisions']+"#"+\
			row['lab']+"#"+\
			row['revision']+"$")

		dbConnection.close()

		return  JsonResponse({'testString':testString,'myStr':myStr}, safe=False)

	if myAction=='saveSuite':

		import ntpath

		owner=request.POST.get('owner','')
		savingString=request.POST.get('savingString','')
		saveID=request.POST.get('saveID','')

		dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
		myRecordSet=dbConnection.cursor(dictionary=True)
		if saveID.isdigit():
			suiteID=saveID
		else:
			myRecordSet.execute("INSERT INTO T_SUITES (name,owner,description) VALUES('"+saveID+"','"+owner+"','')")
			dbConnection.commit()
			myRecordSet.execute("SELECT MAX(id_suite) as id_suite from T_SUITES")
			row=myRecordSet.fetchone()
			suiteID = str(row['id_suite'])
				
		myRecordSet.execute("SELECT name from T_SUITES WHERE id_suite="+suiteID)
		row=myRecordSet.fetchone()
		fileName = row['name']

		myRecordSet.execute("DELETE from T_SUITES_BODY where T_SUITES_id_suite="+suiteID)
		dbConnection.commit()

		#myRecordSet.execute("UPDATE T_SUITES set creationDate=CURRENT_DATE where jsuiteID=" & suiteID)
		#dbConnection.commit()

		tempSuite = savingString.split("$")
		for myIndex in range(0,len(tempSuite)-1):
			tempValues=tempSuite[myIndex].split('#')
			myRecordSet.execute("INSERT into T_SUITES_BODY (T_SUITES_id_suite,T_TEST_REVS_id_TestRev,TCorder,run_section) VALUES ("+suiteID+","+tempValues[0]+","+str(myIndex+1)+",'"+tempValues[1]+"')")
			dbConnection.commit()

		myRecordSet.execute("SELECT if(owner='SHARED','serverSharedSuite','serverPersonalSuite') as suiteSelect,if(owner='SHARED','sharedSuite','personalSuite') as suiteAry from T_SUITES WHERE id_suite="+suiteID)
		row=myRecordSet.fetchone()
		tableName=row['suiteSelect']
		aryName=row['suiteAry']

		userSuiteAry = ''
		sharedSuiteAry = ''

		myRecordSet.execute("SELECT * from T_SUITES where owner = '"+request.session['login']+"' order by name")
		userSuiteAry=[{'suiteName':row["name"],'suiteID':row["id_suite"],'suiteDesc':row["description"]} for row in myRecordSet]

		myRecordSet.execute("SELECT * from T_SUITES where owner = 'SHARED' order by name")
		sharedSuiteAry=[{'suiteName':row["name"],'suiteID':row["id_suite"],'suiteDesc':row["description"]} for row in myRecordSet]

		#myRecordSet.execute("select *,T_SUITES_BODY.run_section as section from T_SUITES join T_SUITES_BODY on(id_suite=T_SUITES_id_suite) join T_TEST_REVS on(id_TestRev=T_TEST_REVS_id_TestRev) join T_TEST on(test_id=T_TEST_test_id) join (select T_TEST_REVS_id_TestRev,group_concat(concat(area_name,'-',tps_reference) order by id_tps separator '!') as tps from T_TPS join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on (id_area=T_AREA_id_area) group by T_TEST_REVS_id_TestRev) as T_TPS on(id_TestRev=T_TPS.T_TEST_REVS_id_TestRev) join T_TEST_COMPATIBILITY on(id_TestRev=T_TEST_COMPATIBILITY.T_TEST_REVS_id_TestRev) join T_DOMAIN on(id_domain=T_TEST_COMPATIBILITY.T_DOMAIN_id_domain) join T_AREA on(T_AREA_id_area=id_area) join T_PROD on(id_prod=T_PROD_id_prod) join T_SW_REL on(T_SW_REL_id_sw_rel=id_sw_rel) where id_suite="+str(suiteID)+" group by id_TestRev,TCOrder order by TCOrder")
		myRecordSet.execute("select *,T_SUITES_BODY.run_section as section,T_SUITES.name as suiteName from T_SUITES join T_SUITES_BODY on(id_suite=T_SUITES_id_suite) join T_TEST_REVS on(id_TestRev=T_TEST_REVS_id_TestRev) join T_TEST on(test_id=T_TEST_test_id) join (select T_TEST_REVS_id_TestRev,group_concat(concat(area_name,'-',tps_reference) order by id_tps separator '<br>') as tps,T_DOMAIN_id_domain from T_TPS join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on (id_area=T_AREA_id_area) group by T_TEST_REVS_id_TestRev) as T_TPS on(id_TestRev=T_TPS.T_TEST_REVS_id_TestRev) join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on(T_AREA_id_area=id_area) join T_PROD on(id_prod=T_PROD_id_prod) join T_SW_REL on(T_SW_REL_id_sw_rel=id_sw_rel) where id_suite="+str(suiteID)+" group by id_TestRev,TCOrder order by TCOrder")
		rows=myRecordSet.fetchall()

		testString=''
		for row in rows:
			testString+=(str(row['id_TestRev'])+"#"+\
			row['product']+"#"+\
			row['sw_rel_name']+"#"+\
			"0#"+\
			row['area_name']+"#"+\
			row['tps']+"#"+\
			ntpath.basename(row['test_name'])+"#"+\
			str(row['duration'])+"#"+\
			str(row['metric'])+"#"+\
			row['topology']+"#"+\
			str(row['id_TestRev'])+"#"+\
			row['sw_rel_name']+"#"+\
			row['dependency']+"#"+\
			row['test_name']+"#"+\
			row['author']+"#"+\
			row['description']+"#"+\
			str(row['last_update'])+"#"+\
			row['section']+"#"+\
			"[MY_REVISIONS]#"+\
			row['lab']+"#"+\
			row['revision']+'$')
			
			myRecordSet.execute("select group_concat(concat(revision,'|',id_TestRev) separator '!') as revisions from T_TEST join T_TEST_REVS on (test_id=T_TEST_test_id) join (select T_TEST_REVS_id_TestRev,group_concat(concat(area_name,'-',tps_reference) order by id_tps separator '!') as tps,T_DOMAIN_id_domain from T_TPS join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on (id_area=T_AREA_id_area) group by T_TEST_REVS_id_TestRev) as T_TPS on(id_TestRev=T_TEST_REVS_id_TestRev) join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on(T_AREA_id_area=id_area) join T_PROD on(id_prod=T_PROD_id_prod) join T_SW_REL on(T_SW_REL_id_sw_rel=id_sw_rel) where T_TEST_test_id="+str(row['T_TEST_test_id'])+" group by T_TEST_test_id")
			testString=testString.replace('[MY_REVISIONS]',myRecordSet.fetchone()['revisions'])

		suiteName=row['suiteName']
		dbConnection.close()

		return  JsonResponse({'testString':testString,'userSuiteAry': userSuiteAry,'sharedSuiteAry': sharedSuiteAry,'suiteID':suiteID,'suiteName':suiteName,'owner':owner}, safe=False)

	if myAction=='deleteSuite':

		owner=request.POST.get('owner','')
		deleteID=request.POST.get('deleteID','')

		dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
		myRecordSet=dbConnection.cursor(dictionary=True)

		myRecordSet.execute("DELETE from T_SUITES_BODY where T_SUITES_id_suite="+deleteID)
		dbConnection.commit()

		myRecordSet.execute("DELETE from T_SUITES where id_suite="+deleteID)
		dbConnection.commit()

		myRecordSet.execute("SELECT * from T_SUITES where owner = '"+request.session['login']+"' order by name")
		userSuiteAry=[{'suiteName':row["name"],'suiteID':row["id_suite"],'suiteDesc':row["description"]} for row in myRecordSet]

		myRecordSet.execute("SELECT * from T_SUITES where owner = 'SHARED' order by name")
		sharedSuiteAry=[{'suiteName':row["name"],'suiteID':row["id_suite"],'suiteDesc':row["description"]} for row in myRecordSet]

		dbConnection.close()

		return  JsonResponse({'userSuiteAry': userSuiteAry,'sharedSuiteAry': sharedSuiteAry}, safe=False)

	if myAction=='shareSuite':

		#NOT IMPLEMENTED YET

		owner=request.POST.get('owner','')
		deleteID=request.POST.get('shareID','')

		dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
		myRecordSet=dbConnection.cursor(dictionary=True)

		myRecordSet.execute("DELETE from T_SUITES_BODY where T_SUITES_id_suite="+deleteID)
		dbConnection.commit()

		myRecordSet.execute("DELETE from T_SUITES where id_suite="+deleteID)
		dbConnection.commit()

		myRecordSet.execute("SELECT * from T_SUITES where owner = '"+request.session['login']+"' order by name")
		userSuiteAry=[{'suiteName':row["name"],'suiteID':row["id_suite"],'suiteDesc':row["description"]} for row in myRecordSet]

		myRecordSet.execute("SELECT * from T_SUITES where owner = 'SHARED' order by name")
		sharedSuiteAry=[{'suiteName':row["name"],'suiteID':row["id_suite"],'suiteDesc':row["description"]} for row in myRecordSet]

		dbConnection.close()

		return  JsonResponse({'userSuiteAry': userSuiteAry,'sharedSuiteAry': sharedSuiteAry}, safe=False)

	if myAction=='queryIteration':

		import ntpath

		iteration=request.POST.get('iteration','')

		dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
		myRecordSet=dbConnection.cursor(dictionary=True)

		#myRecordSet.execute("select * from T_TEST join T_TEST_REVS on (test_id=T_TEST_test_id) join (select T_TEST_REVS_id_TestRev,group_concat(concat(area_name,'-',tps_reference) order by id_tps separator '!') as tps from T_TPS join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on (id_area=T_AREA_id_area) group by T_TEST_REVS_id_TestRev) as T_TPS on(id_TestRev=T_TEST_REVS_id_TestRev) join T_TEST_COMPATIBILITY on(id_TestRev=T_TEST_COMPATIBILITY.T_TEST_REVS_id_TestRev) join T_DOMAIN on(id_domain=T_TEST_COMPATIBILITY.T_DOMAIN_id_domain) join T_AREA on(T_AREA_id_area=id_area) join T_PROD on(id_prod=T_PROD_id_prod) join T_SW_REL on(T_SW_REL_id_sw_rel=id_sw_rel) where id_TestRev="+iteration+" group by id_TestRev")
		myRecordSet.execute("select * from T_TEST join T_TEST_REVS on (test_id=T_TEST_test_id) join (select T_TEST_REVS_id_TestRev,group_concat(concat(area_name,'-',tps_reference) order by id_tps separator '!') as tps,T_DOMAIN_id_domain from T_TPS join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on (id_area=T_AREA_id_area) group by T_TEST_REVS_id_TestRev) as T_TPS on(id_TestRev=T_TEST_REVS_id_TestRev) join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on(T_AREA_id_area=id_area) join T_PROD on(id_prod=T_PROD_id_prod) join T_SW_REL on(T_SW_REL_id_sw_rel=id_sw_rel) where id_TestRev="+iteration+" group by id_TestRev")
		row=myRecordSet.fetchone()

		testString=(str(row['id_TestRev'])+"#"+\
			row['product']+"#"+\
			row['sw_rel_name']+"#"+\
			"0#"+\
			row['area_name']+"#"+\
			row['tps']+"#"+\
			ntpath.basename(row['test_name'])+"#"+\
			str(row['duration'])+"#"+\
			str(row['metric'])+"#"+\
			row['topology']+"#"+\
			str(row['id_TestRev'])+"#"+\
			row['sw_rel_name']+"#"+\
			row['dependency']+"#"+\
			row['test_name']+"#"+\
			row['author']+"#"+\
			row['description']+"#"+\
			str(row['last_update'])+"#"+\
			row['run_section']+"#"+\
			"[MY_REVISIONS]#"+\
			row['lab']+"#"+\
			row['revision'])

		#myRecordSet.execute("select group_concat(concat(revision,'|',id_TestRev) separator '!') as revisions from T_TEST join T_TEST_REVS on (test_id=T_TEST_test_id) join (select T_TEST_REVS_id_TestRev,group_concat(concat(area_name,'-',tps_reference) order by id_tps separator '!') as tps from T_TPS join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on (id_area=T_AREA_id_area) group by T_TEST_REVS_id_TestRev) as T_TPS on(id_TestRev=T_TEST_REVS_id_TestRev) join T_TEST_COMPATIBILITY on(id_TestRev=T_TEST_COMPATIBILITY.T_TEST_REVS_id_TestRev) join T_DOMAIN on(id_domain=T_TEST_COMPATIBILITY.T_DOMAIN_id_domain) join T_AREA on(T_AREA_id_area=id_area) join T_PROD on(id_prod=T_PROD_id_prod) join T_SW_REL on(T_SW_REL_id_sw_rel=id_sw_rel) where T_TEST_test_id="+str(row['T_TEST_test_id'])+" group by T_TEST_test_id")
		myRecordSet.execute("select group_concat(concat(revision,'|',id_TestRev) separator '!') as revisions from T_TEST join T_TEST_REVS on (test_id=T_TEST_test_id) join (select T_TEST_REVS_id_TestRev,group_concat(concat(area_name,'-',tps_reference) order by id_tps separator '!') as tps,T_DOMAIN_id_domain from T_TPS join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on (id_area=T_AREA_id_area) group by T_TEST_REVS_id_TestRev) as T_TPS on(id_TestRev=T_TEST_REVS_id_TestRev) join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on(T_AREA_id_area=id_area) join T_PROD on(id_prod=T_PROD_id_prod) join T_SW_REL on(T_SW_REL_id_sw_rel=id_sw_rel) where T_TEST_test_id="+str(row['T_TEST_test_id'])+" group by T_TEST_test_id")
		row=myRecordSet.fetchone()

		testString=testString.replace('[MY_REVISIONS]',row['revisions'])
		dbConnection.close()


		return  JsonResponse({'testString': testString}, safe=False)

	if myAction=='savePreset':

		fileName = request.POST.get('presetName','')
		savingString = request.POST.get('presetBody','')
		#presetType = request.POST.get('presetType','')

		dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
		myRecordSet=dbConnection.cursor(dictionary=True,buffered=True)

		#myRecordSet.execute("SELECT count(preset_title) as myCount from T_PRESETS WHERE preset_title='"+fileName+"'")
		#row=myRecordSet.fetchone()
		if fileName.isdigit() == False:
			myRecordSet.execute("INSERT INTO T_PRESETS (preset_title,owner,preset_description) VALUES('"+fileName+"','"+request.session['login']+"','')")
			dbConnection.commit()
			myRecordSet.execute("SELECT id_preset from T_PRESETS where preset_title='"+fileName+"' and owner='"+request.session['login']+"'")
			row=myRecordSet.fetchone()
			presetID = row['id_preset']
		else:
			presetID = fileName

		myRecordSet.execute("DELETE from T_PST_ENTITY where T_PRESETS_id_preset="+str(presetID))
		dbConnection.commit()

		nibble = savingString.split("?")
		for myVar in nibble:
			tempNibble = myVar.split("|")
			myRecordSet.execute("INSERT into T_PST_ENTITY (T_PRESETS_id_preset,T_TPY_ENTITY_id_entity,pstvalue,T_EQUIPMENT_id_equipment) VALUES ('"+str(presetID)+"','"+tempNibble[0]+"','"+tempNibble[1]+"','"+tempNibble[2]+"')")
			dbConnection.commit()

		userPreset=''
		sharedPreset=''
		myRecordSet.execute("select concat(T_PRESETS.preset_title,'[',convert(group_concat(distinct id_topology separator ',') using utf8),']') as description,id_preset,preset_title from T_PRESETS join T_PST_ENTITY on(id_preset=T_PRESETS_id_preset) join T_TPY_ENTITY on(id_entity=T_TPY_ENTITY_id_entity) join T_TOPOLOGY on(id_topology=T_TOPOLOGY_id_topology) where owner='"+request.session['login']+"' group by id_preset")
		for row in myRecordSet:userPreset+=row["description"]+'|'+str(row["id_preset"])+'|'+str(row["preset_title"])+'?'
		myRecordSet.execute("select concat(T_PRESETS.preset_title,'[',convert(group_concat(distinct id_topology separator ',') using utf8),']') as description,id_preset,preset_title from T_PRESETS join T_PST_ENTITY on(id_preset=T_PRESETS_id_preset) join T_TPY_ENTITY on(id_entity=T_TPY_ENTITY_id_entity) join T_TOPOLOGY on(id_topology=T_TOPOLOGY_id_topology) where owner='SHARED' group by id_preset")
		for row in myRecordSet:sharedPreset+=row["description"]+'|'+str(row["id_preset"])+'|'+str(row["preset_title"])+'?' 

		myRecordSet.execute("SELECT group_concat(concat(T_TPY_ENTITY_id_entity,'|',T_EQUIPMENT_id_equipment,'|',pstValue) separator '?') as presetBody,owner,preset_title,id_preset,concat(T_PRESETS.preset_title,'[',convert(group_concat(distinct T_TOPOLOGY_id_topology separator ',') using utf8),']') as description FROM T_PST_ENTITY join T_PRESETS on(id_preset=T_PRESETS_id_preset) join T_TPY_ENTITY on(id_entity=T_TPY_ENTITY_id_entity) left join (select T_EQUIPMENT.name as name,T_EQUIP_TYPE.name as myType,id_equipment from T_EQUIPMENT join T_EQUIP_TYPE on(id_type=T_EQUIP_TYPE_id_type)) as myEquipment on(id_equipment=T_EQUIPMENT_id_equipment and replace(elemName,'#','')=myType) WHERE id_preset="+str(presetID))
		row=myRecordSet.fetchone()

				
		dbConnection.close()
		presetAry=""

		return  JsonResponse({'presetAry': row['presetBody'],'userPreset': userPreset[:-1],'sharedPreset': sharedPreset[:-1],'fileName':row['preset_title'],'fileID':row['id_preset'],'fileTitle':row['description'],'owner':row['owner']}, safe=False)

	if myAction=='loadPreset':

		presetID = request.POST.get('presetID','')

		dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
		myRecordSet=dbConnection.cursor(dictionary=True)

		myRecordSet.execute("SET group_concat_max_len = 200000")
		dbConnection.commit()
		
		#myRecordSet.execute("SELECT group_concat(concat(T_TPY_ENTITY_id_entity,'|',if(name is null,T_EQUIPMENT_id_equipment,concat(name,'$',T_EQUIPMENT_id_equipment)),'|',pstValue) separator '?') as presetBody,owner FROM T_PST_ENTITY join T_PRESETS on(id_preset=T_PRESETS_id_preset) join T_TPY_ENTITY on(id_entity=T_TPY_ENTITY_id_entity) left join (select T_EQUIPMENT.name as name,T_EQUIP_TYPE.name as myType,id_equipment from T_EQUIPMENT join T_EQUIP_TYPE on(id_type=T_EQUIP_TYPE_id_type)) as myEquipment on(id_equipment=T_EQUIPMENT_id_equipment and replace(elemName,'#','')=myType) WHERE id_preset="+presetID)
		myRecordSet.execute("SELECT group_concat(concat(T_TPY_ENTITY_id_entity,'|',T_EQUIPMENT_id_equipment,'|',pstValue) separator '?') as presetBody,owner FROM T_PST_ENTITY join T_PRESETS on(id_preset=T_PRESETS_id_preset) join T_TPY_ENTITY on(id_entity=T_TPY_ENTITY_id_entity) left join (select T_EQUIPMENT.name as name,T_EQUIP_TYPE.name as myType,id_equipment from T_EQUIPMENT join T_EQUIP_TYPE on(id_type=T_EQUIP_TYPE_id_type)) as myEquipment on(id_equipment=T_EQUIPMENT_id_equipment and replace(elemName,'#','')=myType) WHERE id_preset="+presetID)
		#pippo="SELECT group_concat(concat(T_TPY_ENTITY_id_entity,'|',if(name is null,T_EQUIPMENT_id_equipment,concat(name,'$',T_EQUIPMENT_id_equipment)),'|',pstValue) separator '?') as presetBody,owner FROM T_PST_ENTITY join T_PRESETS on(id_preset=T_PRESETS_id_preset) join T_TPY_ENTITY on(id_entity=T_TPY_ENTITY_id_entity) left join (select T_EQUIPMENT.name as name,T_EQUIP_TYPE.name as myType,id_equipment from T_EQUIPMENT join T_EQUIP_TYPE on(id_type=T_EQUIP_TYPE_id_type)) as myEquipment on(id_equipment=T_EQUIPMENT_id_equipment and replace(elemName,'#','')=myType) WHERE id_preset="+presetID
		row=myRecordSet.fetchone()

		dbConnection.close()

		return  JsonResponse({'presetAry': row['presetBody'],'username':row['owner']}, safe=False)

	if myAction=='deletePreset':

		presetID = request.POST.get('presetID','')
		presetName = request.POST.get('presetName','')

		dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
		myRecordSet=dbConnection.cursor(dictionary=True)

		myRecordSet.execute("DELETE FROM T_PST_ENTITY WHERE T_PRESETS_id_preset="+presetID)
		dbConnection.commit()

		myRecordSet.execute("DELETE FROM T_PRESETS WHERE id_preset="+presetID)
		dbConnection.commit()

		userPreset=''
		sharedPreset=''
		myRecordSet.execute("select concat(T_PRESETS.preset_title,'[',convert(group_concat(distinct id_topology separator ',') using utf8),']') as description,id_preset,preset_title from T_PRESETS join T_PST_ENTITY on(id_preset=T_PRESETS_id_preset) join T_TPY_ENTITY on(id_entity=T_TPY_ENTITY_id_entity) join T_TOPOLOGY on(id_topology=T_TOPOLOGY_id_topology) where owner='"+request.session['login']+"' group by id_preset")
		for row in myRecordSet:userPreset+=row["description"]+'|'+str(row["id_preset"])+'|'+str(row["preset_title"])+'?'
		myRecordSet.execute("select concat(T_PRESETS.preset_title,'[',convert(group_concat(distinct id_topology separator ',') using utf8),']') as description,id_preset,preset_title from T_PRESETS join T_PST_ENTITY on(id_preset=T_PRESETS_id_preset) join T_TPY_ENTITY on(id_entity=T_TPY_ENTITY_id_entity) join T_TOPOLOGY on(id_topology=T_TOPOLOGY_id_topology) where owner='SHARED' group by id_preset")
		for row in myRecordSet:sharedPreset+=row["description"]+'|'+str(row["id_preset"])+'|'+str(row["preset_title"])+'?' 
		#myRecordSet.execute("select concat(T_PRESETS.preset_title,'[',convert(group_concat(distinct id_topology separator ',') using utf8),']') as description,id_preset from T_PRESETS join T_PST_ENTITY on(id_preset=T_PRESETS_id_preset) join T_TPY_ENTITY on(id_entity=T_TPY_ENTITY_id_entity) join T_TOPOLOGY on(id_topology=T_TOPOLOGY_id_topology) where owner='"+request.session['login']+"' group by id_preset")
		#userSuiteAry=[{'presetName':row["description"],'presetID':row["id_preset"]} for row in myRecordSet]
		#myRecordSet.execute("select concat(T_PRESETS.preset_title,'[',convert(group_concat(distinct id_topology separator ',') using utf8),']') as description,id_preset from T_PRESETS join T_PST_ENTITY on(id_preset=T_PRESETS_id_preset) join T_TPY_ENTITY on(id_entity=T_TPY_ENTITY_id_entity) join T_TOPOLOGY on(id_topology=T_TOPOLOGY_id_topology) where owner='SHARED' group by id_preset")
		#sharedSuiteAry=[{'presetName':row["description"],'presetID':row["id_preset"]} for row in myRecordSet]

		dbConnection.close()

		return  JsonResponse({'userPreset': userPreset[:-1],'sharedPreset': sharedPreset[:-1],'presetName':presetName}, safe=False)


	if myAction=='localBrowsing':

		import glob,os,ntpath
    
		username=request.session['login']
		password=request.session['password']

		testString=""
		localString=""
		localPath=settings.JENKINS['SUITEFOLDER']+username+'_Development/workspace/'
		for f in glob.glob(localPath+'*.py'):
			if os.path.isfile(f+'.prs'):
				#tempTest = open(f,"r")
				#myFile=tempTest.read()
				if os.path.exists(f):
					print('Testcase %s found'%f)
					res=get_testinfo(f)
					check_testinfo_format(f,res)
					print('docinfo for %s: %s'%(f,res))
					if check_testinfo_format(f,res):
						print('docinfo format ok for file %s'%f)
					
						description=res['Description']
						topology=res['Topology']
						dependency=res['Dependency']
						lab=res['Lab']
						#tps=metaInfo[1].replace(',','<br>')
						tps=res['TPS']
						runsection=res['RunSections']
						author=res['Author']
					else:
						description="NA"
						topology="NA"
						dependency="NA"
						lab="NA"
						tps="NA"
						runsection='00000'
						author="NA"
				
					if(runsection.isdigit()==False):runsection='00000'
					print('Description %s' % description)
					print('topology %s' % topology)
					print('Dependency %s' % dependency)
					print('Lab %s' % lab)
					print('tps %s' % tps)
					print('runsections %s' % runsection)
					print('author %s' % author)
					#tempTest.close()
					testString+=f+"#"+\
					"NA#"+\
					"NA#"+\
					"0#"+\
					"NA#"+\
					tps+"#"+\
					ntpath.basename(f)+"#"+\
					"0#"+\
					"0#"+\
					topology+"#"+\
					"NA#"+\
					"NA#"+\
					dependency+"#"+\
					f+"#"+\
					author+"#"+\
					description+"#"+\
					"NA#"+\
					runsection+"#"+\
					"NA#"+\
					lab+"$"
					
		if os.path.isfile(localPath+'suite.txt'):
			localSuite = open(localPath+'suite.txt',"r")
			#localString=localSuite.read()
			for myLine in localSuite.read().split('\n'):
				tempLine=myLine.split('.py')
				if os.path.isfile(tempLine[0]+'.py'):
					res=get_testinfo(tempLine[0]+'.py')
					check_testinfo_format(tempLine[0]+'.py',res)
					print('docinfo for %s: %s'%(tempLine[0]+'.py',res))
					if check_testinfo_format(tempLine[0]+'.py',res):
						print('docinfo format ok for file %s'%tempLine[0]+'.py')
						description=res['Description']
						topology=res['Topology']
						dependency=res['Dependency']
						lab=res['Lab']
						#tps=metaInfo[1].replace(',','<br>')
						tps=res['TPS']
						runsection=res['RunSections']
						author=res['Author']
					else:
						description="NA"
						topology="NA"
						dependency="NA"
						lab="NA"
						tps="NA"
						runsection='00000'
						author="NA"

					if(runsection.isdigit()==False):runsection='00000'

					tempSection=list(runsection)
					if myLine.rfind(' --')>=0:
						if myLine.rfind('--DUTSet')>=0:tempSection[0]='2'
						if myLine.rfind('--testSet')>=0:tempSection[1]='2'
						if myLine.rfind('--testBody')>=0:tempSection[2]='2'
						if myLine.rfind('--testClean')>=0:tempSection[3]='2'
						if myLine.rfind('--DUTClean')>=0:tempSection[4]='2'
					
					localString+=tempLine[0]+".py#"+\
					"NA#"+\
					"NA#"+\
					"0#"+\
					"NA#"+\
					tps+"#"+\
					ntpath.basename(tempLine[0])+".py#"+\
					"0#"+\
					"0#"+\
					"NA#"+\
					"NA#"+\
					"NA#"+\
					dependency+"#"+\
					tempLine[0]+".py#"+\
					author+"#"+\
					description+"#"+\
					"NA#"+\
					''.join(tempSection)+"#"+\
					"NA#"+\
					lab+"$"
			

			localSuite.close()
		print('testString\n%s\nlocalString\n%s\n'%(testString,localString))
		return  JsonResponse({'testString':testString,'localString':localString,'debug':localString}, safe=False)

	if myAction=='job_browsing':

		import glob,os,ntpath
   
		job_name = request.POST.get('job_name','')
		suite_name = request.POST.get('suite_name','suite')

		testString=""
		localString=""
		localPath=settings.JENKINS['SUITEFOLDER']+job_name+settings.JENKINS['JOB_STRUCT']
		for f in glob.glob(localPath+'*.py'):
			if os.path.isfile(f+'.prs'):
				tempTest = open(f,"r")
				myFile=tempTest.read()
				if myFile.rfind('[DESCRIPTION]'):
					metaInfo=myFile.split('[DESCRIPTION]')
					description=metaInfo[1]
					metaInfo=myFile.split('[TOPOLOGY]')
					topology=metaInfo[1]
					metaInfo=myFile.split('[DEPENDENCY]')
					dependency=metaInfo[1]
					metaInfo=myFile.split('[LAB]')
					lab=metaInfo[1]
					metaInfo=myFile.split('[TPS]')
					tps=metaInfo[1].replace(',','<br>')
					metaInfo=myFile.split('[RUNSECTIONS]')
					runsection=metaInfo[1]
					#if runsection.isdigit()==False:runsection='11111'
					metaInfo=myFile.split('[AUTHOR]')
					author=metaInfo[1]
				else:
					description="NA"
					topology="NA"
					dependency="NA"
					lab="NA"
					tps="NA"
					runsection='00000'
					author="NA"

				if(runsection.isdigit()==False):runsection='00000'

				tempTest.close()
				testString+=f+"#"+\
				"NA#"+\
				"NA#"+\
				"0#"+\
				"NA#"+\
				tps+"#"+\
				ntpath.basename(f)+"#"+\
				"0#"+\
				"0#"+\
				topology+"#"+\
				"NA#"+\
				"NA#"+\
				dependency+"#"+\
				f+"#"+\
				author+"#"+\
				description+"#"+\
				"NA#"+\
				runsection+"#"+\
				"NA#"+\
				lab+"$"
        
		if os.path.isfile(localPath+suite_name+'.txt'):
			localSuite = open(localPath+suite_name+'.txt',"r")
			#localString=localSuite.read()
			for myLine in localSuite.read().split('\n'):
				tempLine=myLine.split('.py')
				if os.path.isfile(tempLine[0]+'.py'):
					tempTest = open(tempLine[0]+'.py',"r")
					myFile=tempTest.read()
					if myFile.rfind('[DESCRIPTION]'):
						metaInfo=myFile.split('[DESCRIPTION]')
						description=metaInfo[1]
						metaInfo=myFile.split('[TOPOLOGY]')
						topology=metaInfo[1]
						metaInfo=myFile.split('[DEPENDENCY]')
						dependency=metaInfo[1]
						metaInfo=myFile.split('[LAB]')
						lab=metaInfo[1]
						metaInfo=myFile.split('[TPS]')
						tps=metaInfo[1].replace(',','<br>')
						metaInfo=myFile.split('[RUNSECTIONS]')
						runsection=metaInfo[1]
						#if runsection.isdigit()==False:runsection='11111'
						metaInfo=myFile.split('[AUTHOR]')
						author=metaInfo[1]
					else:
						description="NA"
						topology="NA"
						dependency="NA"
						lab="NA"
						tps="NA"
						runsection='00000'
						author="NA"

					if(runsection.isdigit()==False):runsection='00000'

					tempSection=list(runsection)
					if myLine.rfind(' --')>=0:
						if myLine.rfind('--DUTSet')>=0:tempSection[0]='2'
						if myLine.rfind('--testSet')>=0:tempSection[1]='2'
						if myLine.rfind('--testBody')>=0:tempSection[2]='2'
						if myLine.rfind('--testClean')>=0:tempSection[3]='2'
						if myLine.rfind('--DUTClean')>=0:tempSection[4]='2'
					tempTest.close()
					localString+=tempLine[0]+".py#"+\
					"NA#"+\
					"NA#"+\
					"0#"+\
					"NA#"+\
					tps+"#"+\
					ntpath.basename(tempLine[0])+".py#"+\
					"0#"+\
					"0#"+\
					"NA#"+\
					"NA#"+\
					"NA#"+\
					dependency+"#"+\
					tempLine[0]+".py#"+\
					author+"#"+\
					description+"#"+\
					"NA#"+\
					''.join(tempSection)+"#"+\
					"NA#"+\
					lab+"$"
			
					tempTest.close()
		    
			localSuite.close()
		
   
		return  JsonResponse({'testString':testString,'localString':localString,'debug':localString}, safe=False)

	if myAction=='saveLocal':

		import ntpath, os
		username=request.session['login']
		savingString = request.POST.get('savingString','')
		localString=''
   
		localPath=settings.JENKINS['SUITEFOLDER']+username+'_Development/workspace/'
		localSuite = open(localPath+'suite.txt',"w")
		savingStringBody=''
		for myString in savingString.split('$'):
			tempStr=myString.split('#')
			savingStringBody+=tempStr[0]
			if tempStr[1][0]=='2':savingStringBody+=' --DUTSet'
			if tempStr[1][1]=='2':savingStringBody+=' --testSet'
			if tempStr[1][2]=='2':savingStringBody+=' --testBody'
			if tempStr[1][3]=='2':savingStringBody+=' --testClean'
			if tempStr[1][4]=='2':savingStringBody+=' --DUTClean'
			savingStringBody+='\n'
		localSuite.write(savingStringBody[0:-1])
		localSuite.close()
   
		localSuite = open(localPath+'suite.txt',"r")

		for myLine in localSuite.read().split('\n'):
			tempLine=myLine.split('.py')
			if os.path.isfile(tempLine[0]+'.py'):
				res=get_testinfo(tempLine[0]+'.py')
				check_testinfo_format(tempLine[0]+'.py',res)
				print('docinfo for %s: %s'%(tempLine[0]+'.py',res))
				if check_testinfo_format(tempLine[0]+'.py',res):
					print('docinfo format ok for file %s'%tempLine[0]+'.py')
					description=res['Description']
					topology=res['Topology']
					dependency=res['Dependency']
					lab=res['Lab']
					#tps=metaInfo[1].replace(',','<br>')
					tps=res['TPS']
					runsection=res['RunSections']
					author=res['Author']
				else:
					description="NA"
					topology="NA"
					dependency="NA"
					lab="NA"
					tps="NA"
					runsection='00000'
					author="NA"

				if(runsection.isdigit()==False):runsection='00000'

				tempSection=list(runsection)
				if myLine.rfind(' --')>=0:
					if myLine.rfind('--DUTSet')>=0:tempSection[0]='2'
					if myLine.rfind('--testSet')>=0:tempSection[1]='2'
					if myLine.rfind('--testBody')>=0:tempSection[2]='2'
					if myLine.rfind('--testClean')>=0:tempSection[3]='2'
					if myLine.rfind('--DUTClean')>=0:tempSection[4]='2'
				
				localString+=tempLine[0]+".py#"+\
				"NA#"+\
				"NA#"+\
				"0#"+\
				"NA#"+\
				tps+"#"+\
				ntpath.basename(tempLine[0])+".py#"+\
				"0#"+\
				"0#"+\
				"NA#"+\
				"NA#"+\
				"NA#"+\
				dependency+"#"+\
				tempLine[0]+".py#"+\
				author+"#"+\
				description+"#"+\
				"NA#"+\
				''.join(tempSection)+"#"+\
				"NA#"+\
				lab+"$"
    
		localSuite.close()

		return  JsonResponse({'testString':localString}, safe=False)


	if myAction=='getPresetTemplate':

		import mysql.connector,json,ast
   
		topoID = request.POST.get('topoID','')
		presetID = request.POST.get('presetID','')
   

		dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
		myRecordSet=dbConnection.cursor(dictionary=True)

		myRecordSet.execute("SET group_concat_max_len = 200000")
		dbConnection.commit()

		myRecordSet.execute("select concat('{',group_concat(myTuple),'}') as presets from (SELECT entityName,T_TOPOLOGY_id_topology,T_PRESETS_id_preset,concat(char(39),entityName,char(39),':[',group_concat(if(elemName like '%#%',concat('[',char(39),'TYPE',char(39),',',char(39),replace(elemName,'#',''),char(39),'],[',char(39),'ID',char(39),',',char(39),T_EQUIPMENT_id_equipment,char(39),']'),concat('[',char(39),elemName,char(39),',',char(39),pstValue,char(39),']')) order by elemName),']') as myTuple from T_TPY_ENTITY join T_PST_ENTITY on(T_TPY_ENTITY_id_entity=id_entity) where T_PRESETS_id_preset="+str(presetID)+" and T_TOPOLOGY_id_topology="+topoID+" group by entityName) as presets")
		#myRecordSet.execute("select concat('{',group_concat(myTuple),'}') as presets from (SELECT entityName,T_PRESETS_id_preset,T_TOPOLOGY_id_topology,group_concat(if(elemName like '%#%',concat(char(39),entityName,char(39),':',char(39),T_EQUIPMENT_id_equipment,char(39)),concat(char(39),entityName,'_',elemName,char(39),':',char(39),pstValue,char(39)))) as myTuple FROM T_PST_ENTITY join T_TPY_ENTITY on(id_entity=T_TPY_ENTITY_id_entity) where T_PRESETS_id_preset="+presetID+" and T_TOPOLOGY_id_topology="+topoID+" group by entityName) as presets")
		#myRecordSet.execute("select test_id,id_TestRev,test_name,revision,topology,T_SUITES_BODY.run_section,concat('{',group_concat(myTuple),'}') as presets from T_TEST join T_TEST_REVS on(test_id=T_TEST_test_id) join T_SUITES_BODY on(id_TestRev=T_TEST_REVS_id_TestRev) left join (SELECT entityName,T_TOPOLOGY_id_topology,T_PRESETS_id_preset,concat(char(39),entityName,char(39),':[',group_concat(if(elemName like '%#%',concat('[',char(39),'TYPE',char(39),',',char(39),replace(elemName,'#',''),char(39),'],[',char(39),'ID',char(39),',',char(39),T_EQUIPMENT_id_equipment,char(39),']'),concat('[',char(39),elemName,char(39),',',char(39),pstValue,char(39),']')) order by elemName),']') as myTuple from T_TPY_ENTITY join T_PST_ENTITY on(T_TPY_ENTITY_id_entity=id_entity) where T_PRESETS_id_preset="+str(presetID)+" group by T_TOPOLOGY_id_topology,entityName) as presets on(topology=T_TOPOLOGY_id_topology) where T_SUITES_id_suite="+str(suiteID)+" group by id_TestRev,TCOrder")
		row = myRecordSet.fetchone()
		myPreset=row['presets']   
#json.dump(ast.literal_eval(row["presets"]),out_file,ensure_ascii=False,indent=4,separators=(',',':'))

		return  JsonResponse({'templatePreset':json.dumps(ast.literal_eval(myPreset), ensure_ascii=False, indent=4, separators=(',', ':'))}, safe=False)

	if myAction=='getTopoTemplate':

		import mysql.connector,json,ast
   
		topoID = request.POST.get('topoID','')

		dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
		myRecordSet=dbConnection.cursor(dictionary=True)

		myRecordSet.execute("SET group_concat_max_len = 200000")
		dbConnection.commit()

		myRecordSet.execute("select concat('{',group_concat(myTuple),'}') as presets from (SELECT entityName,T_TOPOLOGY_id_topology,concat(char(39),entityName,char(39),':[',group_concat(if(elemName like '%#%',concat('[',char(39),'TYPE',char(39),',',char(39),replace(elemName,'#',''),char(39),'],[',char(39),'ID',char(39),',',char(39),'',char(39),']'),concat('[',char(39),elemName,char(39),',',char(39),'',char(39),']')) order by elemName),']') as myTuple from T_TPY_ENTITY where T_TOPOLOGY_id_topology="+topoID+" group by entityName) as presets")
		#myRecordSet.execute("select concat('{',group_concat(myTuple),'}') as presets from (SELECT entityName,T_TOPOLOGY_id_topology,T_PRESETS_id_preset,concat(char(39),entityName,char(39),':[',group_concat(if(elemName like '%#%',concat('[',char(39),'TYPE',char(39),',',char(39),replace(elemName,'#',''),char(39),'],[',char(39),'ID',char(39),',',char(39),T_EQUIPMENT_id_equipment,char(39),']'),concat('[',char(39),elemName,char(39),',',char(39),pstValue,char(39),']')) order by elemName),']') as myTuple from T_TPY_ENTITY join T_PST_ENTITY on(T_TPY_ENTITY_id_entity=id_entity) where T_PRESETS_id_preset="+str(presetID)+" and T_TOPOLOGY_id_topology="+topoID+" group by entityName) as presets")
		#myRecordSet.execute("select concat('{',group_concat(myTuple),'}') as presets from (SELECT entityName,T_PRESETS_id_preset,T_TOPOLOGY_id_topology,group_concat(if(elemName like '%#%',concat(char(39),entityName,char(39),':',char(39),T_EQUIPMENT_id_equipment,char(39)),concat(char(39),entityName,'_',elemName,char(39),':',char(39),pstValue,char(39)))) as myTuple FROM T_PST_ENTITY join T_TPY_ENTITY on(id_entity=T_TPY_ENTITY_id_entity) where T_PRESETS_id_preset="+presetID+" and T_TOPOLOGY_id_topology="+topoID+" group by entityName) as presets")
		#myRecordSet.execute("select test_id,id_TestRev,test_name,revision,topology,T_SUITES_BODY.run_section,concat('{',group_concat(myTuple),'}') as presets from T_TEST join T_TEST_REVS on(test_id=T_TEST_test_id) join T_SUITES_BODY on(id_TestRev=T_TEST_REVS_id_TestRev) left join (SELECT entityName,T_TOPOLOGY_id_topology,T_PRESETS_id_preset,concat(char(39),entityName,char(39),':[',group_concat(if(elemName like '%#%',concat('[',char(39),'TYPE',char(39),',',char(39),replace(elemName,'#',''),char(39),'],[',char(39),'ID',char(39),',',char(39),T_EQUIPMENT_id_equipment,char(39),']'),concat('[',char(39),elemName,char(39),',',char(39),pstValue,char(39),']')) order by elemName),']') as myTuple from T_TPY_ENTITY join T_PST_ENTITY on(T_TPY_ENTITY_id_entity=id_entity) where T_PRESETS_id_preset="+str(presetID)+" group by T_TOPOLOGY_id_topology,entityName) as presets on(topology=T_TOPOLOGY_id_topology) where T_SUITES_id_suite="+str(suiteID)+" group by id_TestRev,TCOrder")
		row = myRecordSet.fetchone()
		myPreset=row['presets']   
#json.dump(ast.literal_eval(row["presets"]),out_file,ensure_ascii=False,indent=4,separators=(',',':'))

		return  JsonResponse({'templatePreset':json.dumps(ast.literal_eval(myPreset), ensure_ascii=False, indent=4, separators=(',', ':'))}, safe=False)

	if myAction=='createTest':

		import shutil,os

		testName = request.POST.get('testName','')
		presetBody = request.POST.get('presetBody','')
		product=request.POST.get('product','')
		domain=request.POST.get('domain','')
		area=request.POST.get('area','')
		topoID=request.POST.get('topoID','')
		release=request.POST.get('release','')
		username=request.session['login']
		
		#Trying to set the user GIT Repository to the correct development branch, based on the release used
		gitRes =setUserRepo(username,release)
		if (gitRes == "OK"):
			#in this case the GIT Repository is correctly configured
			if testName[-4:] != '.py':testName+='.py'

			localPath=settings.JENKINS['SUITEFOLDER']+request.session['login']+'_Development/workspace/'+testName
			remotePath='/users/'+request.session['login']+settings.GIT_REPO_PATH + settings.GIT_REPO_NAME+'/TestCases/'+product+'/'+domain+'/'+area+'/'+testName
			testpath = '/TestCases/'+product+'/'+domain+'/'+area+'/'+testName
			if os.path.isfile(remotePath):
				#Test name already exists
				creationReport='Warning !!, Test '+remotePath+'.py already present in your GIT Repository. Please choose a different TestName'
				creationReportType='alert-warning'
				creationReportTitle='Warning!!'
				creationReportFooter=''
			else:
				#Test doesn'exist, we can proceed
				
				if not os.path.exists('/users/'+request.session['login']+settings.GIT_REPO_PATH + settings.GIT_REPO_NAME+'/TestCases/'+product+'/'+domain+'/'+area):
					if not os.path.exists('/users/'+request.session['login']+settings.GIT_REPO_PATH + settings.GIT_REPO_NAME+'/TestCases'):
						os.makedirs('/users/'+request.session['login']+settings.GIT_REPO_PATH + settings.GIT_REPO_NAME+'/TestCases')
						os.chmod('/users/'+request.session['login']+settings.GIT_REPO_PATH + settings.GIT_REPO_NAME+'/TestCases',511)
					if not os.path.exists('/users/'+request.session['login']+settings.GIT_REPO_PATH + settings.GIT_REPO_NAME+'/TestCases/'+product):
						os.makedirs('/users/'+request.session['login']+settings.GIT_REPO_PATH + settings.GIT_REPO_NAME+'/TestCases/'+product)
						os.chmod('/users/'+request.session['login']+settings.GIT_REPO_PATH + settings.GIT_REPO_NAME+'/TestCases/'+product,511)
					if not os.path.exists('/users/'+request.session['login']+settings.GIT_REPO_PATH + settings.GIT_REPO_NAME+'/TestCases/'+product+'/'+domain):
						os.makedirs('/users/'+request.session['login']+settings.GIT_REPO_PATH + settings.GIT_REPO_NAME+'/TestCases/'+product+'/'+domain)
						os.chmod('/users/'+request.session['login']+settings.GIT_REPO_PATH + settings.GIT_REPO_NAME+'/TestCases/'+product+'/'+domain,511)
					os.makedirs('/users/'+request.session['login']+settings.GIT_REPO_PATH + settings.GIT_REPO_NAME+'/TestCases/'+product+'/'+domain+'/'+area)
					os.chmod('/users/'+request.session['login']+settings.GIT_REPO_PATH + settings.GIT_REPO_NAME+'/TestCases/'+product+'/'+domain+'/'+area,511)
					
				if not os.path.exists(settings.JENKINS['SUITEFOLDER']+request.session['login']+'_Development/workspace/test-reports'):
					if not os.path.exists(settings.JENKINS['SUITEFOLDER']+request.session['login']+'_Development/workspace'):
						os.makedirs(settings.JENKINS['SUITEFOLDER']+request.session['login']+'_Development/workspace')
						os.chmod(settings.JENKINS['SUITEFOLDER']+request.session['login']+'_Development/workspace',511)
					os.makedirs(settings.JENKINS['SUITEFOLDER']+request.session['login']+'_Development/workspace/test-reports')
					os.chmod(settings.JENKINS['SUITEFOLDER']+request.session['login']+'_Development/workspace/test-reports',511)
				
				testTemplateFile = open(settings.TEST_TEMPLATE+topoID+'.txt',"r")
				testTemplate=testTemplateFile.read()
				testTemplateFile.close()
					
				localSuite = open(remotePath,"w")
				localSuite.write(testTemplate)
				localSuite.close()
				os.chmod(remotePath,511)

				localPreset = open(localPath+'.prs',"w")
				localPreset.write(presetBody)
				localPreset.close()
				os.chmod(localPath+'.prs',511)

				if os.path.exists(localPath):shutil.rmtree(localPath)

				os.symlink(remotePath,localPath)
				
				creationReport='Test: <font color="blue">'+testpath+' </font> successfully created in your GIT Repository.<br>'+\
					'Preset: <font color="blue">'+testName+'.prs </font> successfully created in your Development Environment.<br>'+\
					'Link: <font color="blue">'+testName+' </font> successfully created in your Development Environment.<br><br><br>'+\
					'<font color="red">GIT repository Path:</font> /users/'+request.session['login']+settings.GIT_REPO_PATH + settings.GIT_REPO_NAME+' <br>'+\
					'<font color="red">Development environment path:</font> '+settings.JENKINS['SUITEFOLDER']+request.session['login']+'_Development/workspace/<br>'
				creationReportType='alert-success'
				creationReportTitle='Create New Test Done!!'
				
				
				userBranch=getUserRepoBranch(request.session['login'])
				creationReportFooter='<h4>Your GIT Repository is set on <span class="label label-default">'+userBranch['current']+'</span> Release Branch.</h4>'+\
				'<p>Your local test browsing is referred to selected branch content!</p>'
				
		else:
			#failed to set the GIT Repository, just warning the user about that
			creationReport=gitRes
			creationReportType='alert-danger'
			creationReportTitle='Your GIT TestCase Repository must be manually Updated!!'
			creationReportFooter=''
			userBranch=getUserRepoBranch(request.session['login'])
			
		return  JsonResponse({'creationReportTitle':creationReportTitle,'creationReport':creationReport,'creationReportType':creationReportType,'creationReportFooter':creationReportFooter,'userBranch':userBranch['current'],'userBranchList':userBranch['list']}, safe=False)

	if myAction=='addSmartSuite':

		queryProduct=request.POST.get('queryProduct','')
		querySW=request.POST.get('querySWRelease','')
		queryArea=request.POST.get('queryArea','')
		presetID=request.POST.get('presetID','')
		excludedTopologies=request.POST.get('excludedTopologies','')
		
		presetStr=" AND id_preset='"+presetID+"'"
		topologyStr=""
		if excludedTopologies.rfind('#')>=0:
			for myTopology in excludedTopologies.split('#'):
				topologyStr+=" or topology="+myTopology
		else:
			if excludedTopologies != '':
				topologyStr+=" or topology="+excludedTopologies
		
		dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
		myRecordSet = dbConnection.cursor(dictionary=True,buffered=True)
		#myRecordSet.execute("select *,group_concat(distinct myTopology) as topology,sum(tTOTtps) as TOTtps,sum(tTOTtc) as TOTtc,sum(tCURRtps) as CURRtps,sum(tCURRtc) as CURRtc from (select area_name,if(id_preset is null,'','#')) as myTopology,test_name,product,sw_rel_name,tps,id_preset_entity,tps as tTOTtps,count(distinct test_id) as tTOTtc,if(id_preset is null,0,tps) as tCURRtps,if(id_preset is null,0,count(distinct test_id)) as tCURRtc from T_TEST join T_TEST_REVS on (test_id=T_TEST_test_id) join (select tps,T_DOMAIN_id_domain ,T_TEST_REVS_id_TestRev from T_TPS join (select T_TEST_REVS_id_TestRev,count(tps_reference) as tps from T_TPS join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on (id_area=T_AREA_id_area) group by T_TEST_REVS_id_TestRev) as myTest using(T_TEST_REVS_id_TestRev) join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on (id_area=T_AREA_id_area) where area_name='FM') as T_TPS on(id_TestRev=T_TEST_REVS_id_TestRev) join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on(T_AREA_id_area=id_area) join T_PROD on(id_prod=T_PROD_id_prod) join T_SW_REL on(T_SW_REL_id_sw_rel=id_sw_rel) join T_TOPOLOGY on(topology=id_topology) join T_TPY_ENTITY on(id_topology=T_TOPOLOGY_id_topology) left join (select * from T_PST_ENTITY left join T_PRESETS on(id_preset=T_PRESETS_id_preset) where owner='SMART') as presets on(id_entity=T_TPY_ENTITY_id_entity) where product='"+queryProduct+"' and sw_rel_name='"+querySW+"' and area_name='"+queryArea+"' group by test_id order by test_id,id_TestRev desc) as myTable")
		myRecordSet.execute("select *,group_concat(distinct myTopology) as topology,sum(tTOTtps) as TOTtps,sum(tTOTtc) as TOTtc,sum(tCURRtps) as CURRtps,sum(tCURRtc) as CURRtc,benches from (select area_name,group_concat(distinct elemName) as benches,concat(topology,if(id_preset is null,'','#')) as myTopology,test_name,T_PROD.product,sw_rel_name,tps,id_preset_entity,tps as tTOTtps,count(distinct test_id) as tTOTtc,if(id_preset is null "+topologyStr+",0,tps) as tCURRtps,if(id_preset is null "+topologyStr+",0,count(distinct test_id)) as tCURRtc from T_TEST join T_TEST_REVS on (test_id=T_TEST_test_id) join (select tps,T_DOMAIN_id_domain ,T_TEST_REVS_id_TestRev from T_TPS join (select T_TEST_REVS_id_TestRev,count(tps_reference) as tps from T_TPS join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on (id_area=T_AREA_id_area) group by T_TEST_REVS_id_TestRev) as myTest using(T_TEST_REVS_id_TestRev) join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on (id_area=T_AREA_id_area) where area_name='"+queryArea+"') as T_TPS on(id_TestRev=T_TEST_REVS_id_TestRev) join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on(T_AREA_id_area=id_area) join T_PROD on(id_prod=T_PROD_id_prod) join T_SW_REL on(T_SW_REL_id_sw_rel=id_sw_rel) join T_TOPOLOGY on(topology=id_topology) join T_TPY_ENTITY on(id_topology=T_TOPOLOGY_id_topology) join T_PROD as myProd on(replace(elemName,'#','')=myProd.product) left join (select * from T_PST_ENTITY left join T_PRESETS on(id_preset=T_PRESETS_id_preset) where id_preset='"+presetID+"') as presets on(id_entity=T_TPY_ENTITY_id_entity) where T_PROD.product='"+queryProduct+"' and sw_rel_name='"+querySW+"' and area_name='"+queryArea+"' group by test_id order by test_id,id_TestRev desc) as myTable")
		row=myRecordSet.fetchone()
		
		context_dict={'login':request.session['login'],'excludedTopologies':excludedTopologies,'benches':row['benches'],'area_name':row['area_name'],'topology':row['topology'],'product':row['product'],'sw_rel_name':row['sw_rel_name'],'TOTtps':row['TOTtps'],'TOTtc':row['TOTtc'],'CURRtps':row['CURRtps'],'CURRtc':row['CURRtc']}
		
		dbConnection.close()
		
		return  JsonResponse(context_dict, safe=False)


	if myAction=='deleteTest':

		import os 

		testList = request.POST.get('deleteList','').split('#')

		username=request.session['login']
		creationReport=''
		creationReportFooter=''

		for myTest in testList:
			if myTest.isdigit():
				pass
			else:
				try:
					os.remove(os.readlink(myTest))
				except:
					pass
				os.remove(myTest)
				os.remove(myTest + '.prs')
				creationReportType='alert-success'
				creationReportTitle='Delete TestCase Done!!'
				creationReport+='Test <font color="blue"> '+myTest+'</font> successfully deleted\n'
				userBranch=getUserRepoBranch(request.session['login'])
				

		#return  JsonResponse({'creationReport':creationReport}, safe=False)
		return  JsonResponse({'creationReportTitle':creationReportTitle,'creationReport':creationReport,'creationReportType':creationReportType,'creationReportFooter':creationReportFooter,'userBranch':userBranch['current'],'userBranchList':userBranch['list']}, safe=False)


	if myAction=='viewTestCase':

		import mysql.connector
		from git import Repo

		idTestRev=request.POST.get('idTestRev')
		action=request.GET.get('action','')

		context = RequestContext(request)
		if 'login' not in request.session:
			fromPage = request.META.get('HTTP_REFERER')
			context_dict={'fromPage':fromPage}
			return render_to_response('taws/login.html',context_dict,context)

		if idTestRev.isdigit():
			dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
			myRecordSet = dbConnection.cursor(dictionary=True)

			myRecordSet.execute("select revision,test_name,test_id from T_TEST_REVS join T_TEST on (T_TEST_test_id=test_id) where id_TestRev="+idTestRev)
			myTest=myRecordSet.fetchone()

			
			myRepo=Repo(settings.BASE_DIR + settings.GIT_REPO_PATH + settings.GIT_REPO_NAME)
			git=myRepo.git
			myFile=git.show(myTest['revision']+':'+myTest['test_name'])

			myRecordSet.execute("select revision,id_TestRev from T_TEST_REVS join T_TEST on (T_TEST_test_id=test_id) where test_id="+str(myTest['test_id']))
			revList=[{'rev':row["revision"],'revId':row["id_TestRev"]} for row in myRecordSet]

			context_dict={'login':request.session['login'],'myFile':myFile,'testName':myTest['test_name'],'revision':myTest['revision'],'revList':revList}
		else:
			if action == 'update':
				tempMyFile = open(idTestRev,"w")
				tempMyFile.write(request.POST.get('testBody'))
				tempMyFile.close()

			tempMyFile = open(idTestRev,"r")
			myFile=tempMyFile.read()
			tempMyFile.close()

			context_dict={'login':request.session['login'],'myFile':myFile,'testName':idTestRev,'revision':"NA",'revList':"NA"}

		#return render(request,'taws/viewTestCase.html',context_dict)
		return  JsonResponse(context_dict, safe=False)
#	if myAction=='editList':
#   
#		import os,ntpath
#
#		testList = request.POST.get('editList','').split('#')
#
#		username=request.session['login']
#		creationReport=''
#   
#		for myTest in testList:
#   
#			localPath='/tools/jksadmin/SERVER_POOL/JEN001/jobs/'+username+'_Development/workspace/suite/'+ntpath.basename(myTest)
#			remotePath='/users/'+username+'/GITREPOS/KATETESTS/'+myTest
#			os.symlink(remotePath,localPath)
#			creationReport+='Test '+myTest+' sent to Development Folder\n'
#			#creationReport+=localPath+'\n'+remotePath+'\n'
#
#		return  JsonResponse({'creationReport':creationReport}, safe=False)

	if myAction=='tuneSuite':
	
		import mysql.connector,os
		from os.path import expanduser
		import json,ast
	
		context = RequestContext(request)
		context_dict={'nothing':'nothing'}
		suiteID=request.POST.get('tuningBundle')
		savingString = request.POST.get('changeValues','')
		description = request.POST.get('description','')
		sharedJob = request.POST.get('sharedJob','off')
		localTesting = request.POST.get('localTesting','off')
		tuningLabel = request.POST.get('tuningLabel','').replace(' ','_')
	
		if 'login' not in request.session:
			context_dict={'fromPage':'tuningEngine'}
			return render_to_response('taws/login.html',context_dict,context)
	
	
		dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
		myRecordSet = dbConnection.cursor(dictionary=True)
	
		myRecordSet.execute("SELECT count(preset_title) as myCount from T_PRESETS WHERE preset_title='"+request.session['login']+"' and owner='HIDDEN'")
		row=myRecordSet.fetchone()
		if row['myCount']==0:
			myRecordSet.execute("INSERT INTO T_PRESETS (preset_title,owner,preset_description) VALUES('"+request.session['login']+"','HIDDEN','')")
			dbConnection.commit()
		myRecordSet.execute("SELECT id_preset from T_PRESETS where preset_title='"+request.session['login']+"' and owner='HIDDEN'")
		row=myRecordSet.fetchone()
		presetID = row['id_preset']
	
		myRecordSet.execute("DELETE from T_PST_ENTITY where T_PRESETS_id_preset="+str(presetID))
		dbConnection.commit()
	
		nibble = savingString.split("?")
		for myVar in nibble:
			tempNibble = myVar.split("|")
			myRecordSet.execute("INSERT into T_PST_ENTITY (T_PRESETS_id_preset,T_TPY_ENTITY_id_entity,pstvalue,T_EQUIPMENT_id_equipment) VALUES ('"+str(presetID)+"','"+tempNibble[0]+"','"+tempNibble[1]+"','"+tempNibble[2]+"')")
			dbConnection.commit()
	
		tempStr=''
		#tempStr+="PresetID :"+str(presetID)+"\n"
		#tempStr+="SuiteID :"+str(suiteID)+"\n"
		tempStr+="Tuning Test Cases for Jenkins...\n\n"
		#global TAWS_path,os
		myRecordSet.execute("select name from T_SUITES where id_suite="+str(suiteID))
		myRecord=myRecordSet.fetchone()
	
		if localTesting == 'off':
			suiteName=request.session['login']+'_'+myRecord['name']+'-'+tuningLabel
		else:
			suiteName=request.session['login']+'_Development'
	

		tempStr+=createJenkinsENV(suiteName,request.session['login'],request.session['password'],localTesting,sharedJob,description)
	
		myIDX=1
		tempStr+=tune_suite(presetID,suiteID,localTesting,suiteName,request.session['login'],'off',myIDX)['tuningReport']
		tempStr+='\n\nTUNING COMPLETE!\nHAVE A NICE DAY!\n'
		
		context_dict={'login':request.session['login'],'tuningReport':tempStr}
	
		return  JsonResponse(context_dict, safe=False)
		#return render_to_response('taws/tuningEngine.html',context_dict)
		#return render_to_response('taws/tuningEngine.html',context_dict,context_instance=RequestContext(request))

	if myAction=='smartTune':
		
		import mysql.connector,os
		from os.path import expanduser
		import json,ast
	
		context = RequestContext(request)

		presetID=request.POST.get('presetID')
		tuningLabel=request.POST.get('tuningLabel')
		product=request.POST.get('product')
		sw_rel = request.POST.get('sw_rel','')
		description = request.POST.get('description','')
		area = request.POST.get('area','')
		excludedTopologies = request.POST.get('excludedTopologies','')
		myIDX = int(request.POST.get('myIDX',''))
		owner=request.POST.get('owner')
		preview=request.POST.get('preview','on')
		localTesting='off'
		sharedJob='off'

		tempStr=""

		topologyStr=""
		if excludedTopologies.rfind('#')>=0:
			for myTopology in excludedTopologies.split('#'):
				topologyStr+=" and topology<>"+myTopology
		else:
			if excludedTopologies != '':
				topologyStr+=" and topology<>"+excludedTopologies
		
		if myIDX==1 and preview=='off':
			tempStr="Smart Suite Creation Started...\n\n"
			tempStr+=createJenkinsENV(request.session['login']+'_'+tuningLabel+'_SMART',request.session['login'],request.session['password'],localTesting,sharedJob,description)
		
		dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
		myRecordSet = dbConnection.cursor(dictionary=True,buffered=True)
		#myRecordSet.execute("select *,group_concat(distinct myTopology) as topology,sum(tTOTtps) as TOTtps,sum(tTOTtc) as TOTtc,sum(tCURRtps) as CURRtps,sum(tCURRtc) as CURRtc from (select area_name,if(id_preset is null,'','#')) as myTopology,test_name,product,sw_rel_name,tps,id_preset_entity,tps as tTOTtps,count(distinct test_id) as tTOTtc,if(id_preset is null,0,tps) as tCURRtps,if(id_preset is null,0,count(distinct test_id)) as tCURRtc from T_TEST join T_TEST_REVS on (test_id=T_TEST_test_id) join (select tps,T_DOMAIN_id_domain ,T_TEST_REVS_id_TestRev from T_TPS join (select T_TEST_REVS_id_TestRev,count(tps_reference) as tps from T_TPS join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on (id_area=T_AREA_id_area) group by T_TEST_REVS_id_TestRev) as myTest using(T_TEST_REVS_id_TestRev) join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on (id_area=T_AREA_id_area) where area_name='FM') as T_TPS on(id_TestRev=T_TEST_REVS_id_TestRev) join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on(T_AREA_id_area=id_area) join T_PROD on(id_prod=T_PROD_id_prod) join T_SW_REL on(T_SW_REL_id_sw_rel=id_sw_rel) join T_TOPOLOGY on(topology=id_topology) join T_TPY_ENTITY on(id_topology=T_TOPOLOGY_id_topology) left join (select * from T_PST_ENTITY left join T_PRESETS on(id_preset=T_PRESETS_id_preset) where owner='SMART') as presets on(id_entity=T_TPY_ENTITY_id_entity) where product='"+queryProduct+"' and sw_rel_name='"+querySW+"' and area_name='"+queryArea+"' group by test_id order by test_id,id_TestRev desc) as myTable")
		#myRecordSet.execute("select *,group_concat(distinct myTopology) as topology,sum(tTOTtps) as TOTtps,sum(tTOTtc) as TOTtc,sum(tCURRtps) as CURRtps,sum(tCURRtc) as CURRtc,benches from (select area_name,group_concat(distinct elemName) as benches,concat(topology,if(id_preset is null,'','#')) as myTopology,test_name,T_PROD.product,sw_rel_name,tps,id_preset_entity,tps as tTOTtps,count(distinct test_id) as tTOTtc,if(id_preset is null "+topologyStr+",0,tps) as tCURRtps,if(id_preset is null "+topologyStr+",0,count(distinct test_id)) as tCURRtc from T_TEST join T_TEST_REVS on (test_id=T_TEST_test_id) join (select tps,T_DOMAIN_id_domain ,T_TEST_REVS_id_TestRev from T_TPS join (select T_TEST_REVS_id_TestRev,count(tps_reference) as tps from T_TPS join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on (id_area=T_AREA_id_area) group by T_TEST_REVS_id_TestRev) as myTest using(T_TEST_REVS_id_TestRev) join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on (id_area=T_AREA_id_area) where area_name='"+queryArea+"') as T_TPS on(id_TestRev=T_TEST_REVS_id_TestRev) join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on(T_AREA_id_area=id_area) join T_PROD on(id_prod=T_PROD_id_prod) join T_SW_REL on(T_SW_REL_id_sw_rel=id_sw_rel) join T_TOPOLOGY on(topology=id_topology) join T_TPY_ENTITY on(id_topology=T_TOPOLOGY_id_topology) join T_PROD as myProd on(replace(elemName,'#','')=myProd.product) left join (select * from T_PST_ENTITY left join T_PRESETS on(id_preset=T_PRESETS_id_preset) where id_preset='"+presetID+"') as presets on(id_entity=T_TPY_ENTITY_id_entity) where T_PROD.product='"+queryProduct+"' and sw_rel_name='"+querySW+"' and area_name='"+queryArea+"' group by test_id order by test_id,id_TestRev desc) as myTable")
		#row=myRecordSet.fetchone()

		id_suite=0
		
		if preview == 'off':
			myRecordSet.execute("SELECT id_suite from T_SUITES where name='"+owner+"_SMART' and owner='"+owner+"'")
			if myRecordSet.rowcount!=0:
				id_suite=myRecordSet.fetchone()['id_suite']
				tempStr+="User Smart Suite found="+str(id_suite)+"...\n"
				myRecordSet.execute("DELETE FROM T_SUITES_BODY WHERE T_SUITES_id_suite='"+str(id_suite)+"'")
				dbConnection.commit()
			else:
				tempStr+="User Smart Suite creation..."
				myRecordSet.execute("INSERT INTO T_SUITES (name,owner,description) VALUES('"+owner+"_SMART','"+owner+"','')")
				dbConnection.commit()
				tempStr+="DONE\n"
				myRecordSet.execute("SELECT id_suite from T_SUITES where name='"+owner+"_SMART' and owner='"+owner+"'")
				id_suite=myRecordSet.fetchone()['id_suite']
				tempStr+="User Smart Suite found="+str(id_suite)+"...\n"
		
		if preview == 'on':
			tempStr+="Load preset ID="+str(presetID)+"...\n"
			myRecordSet.execute("select test_name,null,"+str(id_suite)+",id_TestRev,0,run_section from T_TEST join (select T_TEST_test_id,id_TestRev,run_section,topology from T_TEST_REVS order by T_TEST_test_id,id_TestRev desc) as T_TEST_REVS on (test_id=T_TEST_test_id) join (select tps,T_DOMAIN_id_domain ,T_TEST_REVS_id_TestRev from T_TPS join (select T_TEST_REVS_id_TestRev,count(tps_reference) as tps from T_TPS join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on (id_area=T_AREA_id_area) group by T_TEST_REVS_id_TestRev) as myTest using(T_TEST_REVS_id_TestRev) join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on (id_area=T_AREA_id_area) where area_name='"+area+"') as T_TPS on(id_TestRev=T_TEST_REVS_id_TestRev) join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on(T_AREA_id_area=id_area) join T_PROD on(id_prod=T_PROD_id_prod) join T_SW_REL on(T_SW_REL_id_sw_rel=id_sw_rel) join T_TOPOLOGY on(topology=id_topology) join T_TPY_ENTITY on(id_topology=T_TOPOLOGY_id_topology) join T_PROD as myProd on(replace(elemName,'#','')=myProd.product) left join (select * from T_PST_ENTITY left join T_PRESETS on(id_preset=T_PRESETS_id_preset) where id_preset='"+presetID+"') as presets on(id_entity=T_TPY_ENTITY_id_entity) where T_PROD.product='"+product+"' and sw_rel_name='"+sw_rel+"' and area_name='"+area+"' "+topologyStr+" and id_preset is not null group by test_id order by test_id,id_TestRev desc")
			for row in myRecordSet:
				tempStr+=str(myIDX)+' Revision '+str(row["id_TestRev"])+' '+row["test_name"]+'\n'
				myIDX=myIDX+1

		if preview == 'off':
			tempStr+="Check preset ID="+str(presetID)+"...\n"
			tempStr+="Adding Smart Suite Chapter for "+product+" "+sw_rel+" "+area+"..."
			myRecordSet.execute("insert into T_SUITES_BODY (select null,"+str(id_suite)+",id_TestRev,0,run_section from T_TEST join (select T_TEST_test_id,id_TestRev,run_section,topology from T_TEST_REVS order by T_TEST_test_id,id_TestRev desc) as T_TEST_REVS on (test_id=T_TEST_test_id) join (select tps,T_DOMAIN_id_domain ,T_TEST_REVS_id_TestRev from T_TPS join (select T_TEST_REVS_id_TestRev,count(tps_reference) as tps from T_TPS join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on (id_area=T_AREA_id_area) group by T_TEST_REVS_id_TestRev) as myTest using(T_TEST_REVS_id_TestRev) join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on (id_area=T_AREA_id_area) where area_name='"+area+"') as T_TPS on(id_TestRev=T_TEST_REVS_id_TestRev) join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on(T_AREA_id_area=id_area) join T_PROD on(id_prod=T_PROD_id_prod) join T_SW_REL on(T_SW_REL_id_sw_rel=id_sw_rel) join T_TOPOLOGY on(topology=id_topology) join T_TPY_ENTITY on(id_topology=T_TOPOLOGY_id_topology) join T_PROD as myProd on(replace(elemName,'#','')=myProd.product) left join (select * from T_PST_ENTITY left join T_PRESETS on(id_preset=T_PRESETS_id_preset) where id_preset='"+presetID+"') as presets on(id_entity=T_TPY_ENTITY_id_entity) where T_PROD.product='"+product+"' and sw_rel_name='"+sw_rel+"' and area_name='"+area+"' "+topologyStr+" and id_preset is not null group by test_id order by test_id,id_TestRev desc)")
			dbConnection.commit()
			tempStr+="DONE\n"
			#myRecordSet.execute("SELECT COUNT(*) as totTest from T_SUITES_BODY where T_SUITES_id_suite="+str(id_suite))
			#addIDX=myRecordSet.fetchone()['totTest']
			#tempStr+="Added "+str(addIDX)+" Test Cases\n"
		
			myTuning=tune_suite(presetID,id_suite,localTesting,request.session['login']+'_'+tuningLabel+'_SMART',request.session['login'],'off',myIDX)
			tempStr+=myTuning['tuningReport']
			myIDX+=myTuning['myIDX']
		#dbConnection.commit()
		#myRecordSet.execute("INSERT INTO T_SUITES (name,owner,description) VALUES('"+saveID+"','"+owner+"','')")
		#dbConnection.commit()
		#myRecordSet.execute("SELECT MAX(id_suite) as id_suite from T_SUITES")
		#row=myRecordSet.fetchone()
		#suiteID = str(row['id_suite'])
		
		#tempStr+=tune_suite(presetID,suiteID,localTesting,suiteName,request.session['login'],'off',myIDX)['tuningReport']
		
		#suiteName=request.session['login']+'_'+tuningLabel+'-SMART'
		
		context_dict={'login':request.session['login'],'tuningReport':tempStr,'tuningLabel':tuningLabel,'product':product,'sw_rel':sw_rel,'description':description,'area':area,'excludedTopologies':excludedTopologies,'myIDX':myIDX}
	
		return  JsonResponse(context_dict, safe=False)
		
def temp(request):
	context = RequestContext(request)
	context_dict={'nothing':'nothing'}
	return render_to_response('taws/temp.html',context_dict,context)




