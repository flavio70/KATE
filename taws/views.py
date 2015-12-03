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

def index(request):
	context = RequestContext(request)
	context_dict = {'nothing':'nothing'}
	if 'login' in request.session:
		login=request.session['login']
		context_dict = {'login':login}
	return render_to_response('taws/index.html', context_dict, context)

def login(request):
	context = RequestContext(request)
	fromPage = request.META.get('HTTP_REFERER')
	context_dict={'fromPage':fromPage}
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
	if 'fromPage' in request.POST:
		 url=request.POST['fromPage']
		#url="taws/index.html"
	else:
		url="taws/index.html"
	context_dict.update({'fromPage':url})
	return render_to_response(url,context_dict,context)

def development_index(request):
	context = RequestContext(request)
	context_dict={'nothing':'nothing'}
	if 'login' not in request.session:
		fromPage = request.META.get('HTTP_REFERER')
		context_dict={'fromPage':fromPage}
		return render_to_response('taws/login.html',context_dict,context)
	else:
		context_dict={'login':request.session['login']}
		return render_to_response('taws/development_index.html',context_dict,context)

def suite_creator(request):
	context = RequestContext(request)
	context_dict={'nothing':'nothing'}
	import mysql.connector

	if 'login' not in request.session:
		fromPage = request.META.get('HTTP_REFERER')
		context_dict={'fromPage':fromPage}
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

	if 'login' not in request.session:
		fromPage = request.META.get('HTTP_REFERER')
		context_dict={'fromPage':fromPage}
		return render_to_response('taws/login.html',context_dict,context)
	else:
		dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
		myRecordSet=dbConnection.cursor(dictionary=True)
		myRecordSet.execute("SET group_concat_max_len = 200000")
		dbConnection.commit()
		#myRecordSet.execute("select product,CONVERT(group_concat(concat(areaConcat,'$',sw_rel_name) order by sw_rel_name desc separator '@') using utf8) as productConcat from (select product,sw_rel_name,group_concat(concat(area_name,'!',area_name) order by area_name separator '#') as areaConcat from T_DOMAIN join T_AREA on(T_AREA_id_area=id_area) join T_PROD on(T_PROD_id_prod=id_prod) join T_SW_REL on(T_SW_REL_id_sw_rel=id_sw_rel) group by product,sw_rel_name order by product asc,sw_rel_name desc) as tableArea group by product")
		#myRecordSet.execute("select product,group_concat(release_scope_area separator '@') as productConcat from (select product,concat(sw_rel_name,'?',group_concat(scope_area separator '%')) as release_scope_area from (select product,sw_rel_name,concat(T_SCOPE.description,'#',group_concat(area_name order by area_name separator '|')) as scope_area from T_DOMAIN join T_SCOPE on(T_SCOPE_id_scope=id_scope) join T_AREA on(T_AREA_id_area=id_area) join T_PROD on(T_PROD_id_prod=id_prod) join T_SW_REL on(T_SW_REL_id_sw_rel=id_sw_rel) group by product,sw_rel_name,T_SCOPE.description order by product asc,sw_rel_name desc,T_SCOPE.description asc) as release_scope_area group by product,sw_rel_name order by product asc,sw_rel_name desc) as product_release_scope_area group by product order by product asc")
		#productAry=[{'product':row["product"],'productConcat':row["productConcat"]} for row in myRecordSet]

		#userSuiteAry = ''
		#sharedSuiteAry = ''

		#myRecordSet.execute("SELECT * from T_SUITES where owner = '"+request.session['login']+"' order by name")
		#userSuiteAry=[{'suiteName':row["name"],'suiteID':row["id_suite"],'suiteDesc':row["description"]} for row in myRecordSet]

		#myRecordSet.execute("SELECT * from T_SUITES where owner = 'SHARED' order by name")
		#sharedSuiteAry=[{'suiteName':row["name"],'suiteID':row["id_suite"],'suiteDesc':row["description"]} for row in myRecordSet]

		#myRecordSet.execute("SELECT * from T_TOPOLOGY join T_SCOPE on(T_SCOPE_id_scope=id_scope) where T_SCOPE.description='VIRTUAL'")
		#virtualTopoAry=[{'virtualTopoID':row["id_topology"],'virtualTopoName':row["title"]} for row in myRecordSet]

		#myRecordSet.execute("SELECT * from T_TOPOLOGY join T_SCOPE on(T_SCOPE_id_scope=id_scope) where T_SCOPE.description='DATA'")
		#dataTopoAry=[{'dataTopoID':row["id_topology"],'dataTopoName':row["title"]} for row in myRecordSet]

		#myRecordSet.execute("SELECT * from T_TOPOLOGY join T_SCOPE on(T_SCOPE_id_scope=id_scope) where T_SCOPE.description='TDM'")
		#tdmTopoAry=[{'tdmTopoID':row["id_topology"],'tdmTopoName':row["title"]} for row in myRecordSet]

		#myRecordSet.execute("SELECT * from T_TOPOLOGY join T_SCOPE on(T_SCOPE_id_scope=id_scope) where T_SCOPE.description='WDM'")
		#wdmTopoAry=[{'wdmTopoID':row["id_topology"],'wdmTopoName':row["title"]} for row in myRecordSet]

		#myRecordSet.execute("SELECT distinct lab from T_TEST_REVS order by lab")
		#labAry=[{'labName':row["lab"]} for row in myRecordSet]

		#context_dict={'login':request.session['login'].upper(),
		#	'permission':1,
		#	'productAry': productAry,
		#	'userSuiteAry': userSuiteAry,
		#	'sharedSuiteAry': sharedSuiteAry,
		#	'virtualTopoAry':virtualTopoAry,
		#	'dataTopoAry':dataTopoAry,
		#	'tdmTopoAry':tdmTopoAry,
		#	'wdmTopoAry':wdmTopoAry,
		#	'labAry':labAry}

		context_dict={'login':request.session['login'].upper(),
			'permission':1}

		return render_to_response('taws/test_development.html',context_dict,context)

def tuning(request):

	import mysql.connector

	context = RequestContext(request)
	context_dict={'nothing':'nothing'}
	if 'login' not in request.session:
		fromPage = request.META.get('HTTP_REFERER')
		context_dict={'fromPage':fromPage}
		return render_to_response('taws/login.html',context_dict,context)

	suiteOwner=''
	suiteID = request.POST['savingName']

	dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
	myRecordSet=dbConnection.cursor(dictionary=True)
	myRecordSet.execute("SET group_concat_max_len = 200000")
	dbConnection.commit()
	#myRecordSet.execute("select concat(presetName,'[',convert(group_concat(distinct topoID separator ',') using utf8),']') as presetname,presetID from presets join presetbody using(presetID) join topologybody using(label) join topologies using(topoID) where username='"+Session("login")+"' group by presetID")
	myRecordSet.execute("select concat(T_PRESETS.preset_title,'[',convert(group_concat(distinct id_topology separator ',') using utf8),']') as description,id_preset,preset_title from T_PRESETS join T_PST_ENTITY on(id_preset=T_PRESETS_id_preset) join T_TPY_ENTITY on(id_entity=T_TPY_ENTITY_id_entity) join T_TOPOLOGY on(id_topology=T_TOPOLOGY_id_topology) where owner='"+request.session['login']+"' group by id_preset")
	userPreset=[{'userPresetName':row["description"],'userPresetID':row["id_preset"],'userPresetTitle':row["preset_title"]} for row in myRecordSet]
	myRecordSet.execute("select concat(T_PRESETS.preset_title,'[',convert(group_concat(distinct id_topology separator ',') using utf8),']') as description,id_preset,preset_title from T_PRESETS join T_PST_ENTITY on(id_preset=T_PRESETS_id_preset) join T_TPY_ENTITY on(id_entity=T_TPY_ENTITY_id_entity) join T_TOPOLOGY on(id_topology=T_TOPOLOGY_id_topology) where owner='SHARED' group by id_preset")
	sharedPreset=[{'sharedPresetName':row["description"],'sharedPresetID':row["id_preset"],'sharedPresetTitle':row["preset_title"]} for row in myRecordSet]

	myRecordSet.execute("SELECT convert(GROUP_CONCAT(distinct topology separator '-') using utf8) as topologyNeeded,name from T_SUITES join T_SUITES_BODY on(id_suite=T_SUITES_id_suite) join T_TEST_REVS on(id_TestRev=T_TEST_REVS_id_TestRev) where id_suite="+suiteID)
	#myRecordSet.execute("SELECT convert(GROUP_CONCAT(distinct topology separator '-') using utf8) as topologyNeeded,suitename from jsuites join jsuiteBody using(jsuiteID) join  Jenkinslist using(JID,livraison) where jsuiteID='"+fileName+"'")
	myRecord=myRecordSet.fetchone()
	fileName=myRecord["name"]
	suiteOwner='SERVER'
	myTopologies=myRecord["topologyNeeded"].split('-')
	topoAry=[]
#	for myTopology in myTopologies:
		#myRecordSet.execute("SELECT if(group_concat(concat(description,'$',label) order by indice separator '$') is null,'topoerror',group_concat(concat(description,'$',label) order by indice separator '$')) as dataValues,numNE from topologyBody join topologies using(topoID) where topoID ='"+myTopology+"'")
#		myRecordSet.execute("SELECT if(group_concat(concat(elemDescription,'$',entityName,'_',elemName) order by id_entity separator '$') is null,'topoerror',group_concat(concat(elemDescription,'$',entityName,'_',elemName) order by id_entity separator '$')) as dataValues,1 as numNE from T_TPY_ENTITY join T_TOPOLOGY on(id_topology=T_TOPOLOGY_id_topology) where id_topology="+myTopology)
		#myRecord=myRecordSet.fetchall()
#		for myRecord in myRecordSet:
#			dataValues=myRecord['dataValues']
#			if myTopology!='000' and dataValues != 'topoerror':
#				tempAry1=[]
#				tempAry2=[]
#				tempAry3=[]
#				tempLabels = dataValues.split("$")
#				for labelIndex in range(0,len(tempLabels),2):
#					tempAry1.append(tempLabels[labelIndex+1])
#					tempAry2.append(tempLabels[labelIndex])
#					tempAry3.append('')
#				topoAry.append({"myTopology":myTopology,
#					"tempAry1":tempAry1,
#					"tempAry2":tempAry2,
#					"tempAry3":tempAry3,
#					"numNE":myRecord['numNE']})
	topoAry='';
	for myTopology in myTopologies:
		#myRecordSet.execute("SELECT if(group_concat(concat(description,'$',label) order by indice separator '$') is null,'topoerror',group_concat(concat(description,'$',label) order by indice separator '$')) as dataValues,numNE from topologyBody join topologies using(topoID) where topoID ='"+myTopology+"'")
		myRecordSet.execute("SELECT if(group_concat(concat(elemDescription,'$',entityName,'$',elemName,'$',id_entity) order by id_entity separator '$') is null,'topoerror',group_concat(concat(elemDescription,'$',entityName,'$',elemName,'$',id_entity) order by id_entity separator '$')) as dataValues,1 as numNE from T_TPY_ENTITY join T_TOPOLOGY on(id_topology=T_TOPOLOGY_id_topology) where id_topology="+myTopology)
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
			topoAry+="topologies[topologies.length-1].push(parseInt('"+str(myRecord['numNE'])+"'));"
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
		fromPage = request.META.get('HTTP_REFERER')
		context_dict={'fromPage':fromPage}
		return render_to_response('taws/login.html',context_dict,context)

	context_dict={'login':request.session['login']}
	myVars=request.GET.get('myVars')
	tempVars=myVars.split('$')

	dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
	myRecordSet=dbConnection.cursor(dictionary=True)

	myRecordSet.execute("SELECT id_equipment,T_EQUIPMENT.name,owner,T_EQUIP_TYPE.description as equipDescription,site,room,row,rack,pos,IP,NM,GW,T_SCOPE.description as scopeDescription FROM T_EQUIPMENT join T_EQUIP_TYPE on(id_type=T_EQUIP_TYPE_id_type) join T_LOCATION on(id_location=T_LOCATION_id_location) join T_NET on(id_equipment=T_EQUIPMENT_id_equipment) join T_SCOPE on(id_scope=T_SCOPE_id_scope) join T_SERIAL on(T_SERIAL.T_EQUIPMENT_id_equipment=id_equipment) where T_EQUIP_TYPE.name='"+tempVars[1]+"'")
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

	import mysql.connector,os,shutil,ntpath
	from os.path import expanduser
	from git import Repo
	import json,ast

	context = RequestContext(request)
	context_dict={'nothing':'nothing'}
	suiteID=request.POST.get('tuningBundle')
	presetID = request.POST.get('presets','')
	savingString = request.POST.get('changeValues','')
	description = request.POST.get('description','')
	sharedJob = request.POST.get('sharedJob','off')
	localTesting = request.POST.get('localTesting','off')
	tuningLabel = request.POST.get('tuningLabel','').replace(' ','_')

	if 'login' not in request.session:
		fromPage = request.META.get('HTTP_REFERER')
		context_dict={'fromPage':fromPage}
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
	tempStr+="Tuning Test Cases for Jenkins...\n\n"
	tuningReport=''
	global TAWS_path,os
	myRecordSet.execute("select name from T_SUITES where id_suite="+str(suiteID))
	myRecord=myRecordSet.fetchone()

	if localTesting == 'off':
		suiteName=request.session['login']+'_'+myRecord['name']+'-'+tuningLabel
	else:
		suiteName=request.session['login']+'_Development'

	suiteFolder=settings.JENKINS['SUITEFOLDER']

	myRecordSet.execute("SET group_concat_max_len = 200000")
	dbConnection.commit()
	#myRecordSet.execute("select test_id,id_TestRev,test_name,revision,topology,run_sectionconcat('{',myTuple,'}') as presets from T_TEST join T_TEST_REVS on(test_id=T_TEST_test_id) join T_SUITES_BODY on(id_TestRev=T_TEST_REVS_id_TestRev) left join (SELECT entityName,T_PRESETS_id_preset,T_TOPOLOGY_id_topology,group_concat(if(elemName like '%#%',concat(char(39),entityName,char(39),':',char(39),T_EQUIPMENT_id_equipment,char(39)),concat(char(39),entityName,'_',elemName,char(39),':',char(39),pstValue,char(39)))) as myTuple FROM T_PST_ENTITY join T_TPY_ENTITY on(id_entity=T_TPY_ENTITY_id_entity) where T_PRESETS_id_preset="+str(presetID)+" group by T_TOPOLOGY_id_topology,entityName) as presets on(topology=T_TOPOLOGY_id_topology) where T_SUITES_id_suite="+str(suiteID)+" group by id_TestRev,TCOrder")
	myRecordSet.execute("select test_id,id_TestRev,test_name,revision,topology,T_SUITES_BODY.run_section,concat('{',group_concat(myTuple),'}') as presets from T_TEST join T_TEST_REVS on(test_id=T_TEST_test_id) join T_SUITES_BODY on(id_TestRev=T_TEST_REVS_id_TestRev) left join (SELECT entityName,T_PRESETS_id_preset,T_TOPOLOGY_id_topology,group_concat(if(elemName like '%#%',concat(char(39),entityName,char(39),':',char(39),T_EQUIPMENT_id_equipment,char(39)),concat(char(39),entityName,'_',elemName,char(39),':',char(39),pstValue,char(39)))) as myTuple FROM T_PST_ENTITY join T_TPY_ENTITY on(id_entity=T_TPY_ENTITY_id_entity) where T_PRESETS_id_preset="+str(presetID)+" group by T_TOPOLOGY_id_topology,entityName) as presets on(topology=T_TOPOLOGY_id_topology) where T_SUITES_id_suite="+str(suiteID)+" group by id_TestRev,TCOrder")
	rows = myRecordSet.fetchall()
	#tuningPath=TAWS_path+"Test Case ATM\\TUNED\\"+suiteName+"-TUNED-"+tuningName

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
		#os.makedirs(suiteFolder+suiteName+'/workspace/test-reports')
		#os.chmod(suiteFolder+suiteName+'/workspace/test-reports',511)
	myIDX=1
	test_plan=''
	myRepo=Repo('/tools/smotools'+settings.GIT_REPO)
	git=myRepo.git
	for row in rows:
		test_name=str(myIDX).zfill(6)+'_'+str(row['test_id'])+'_'+ntpath.basename(row['test_name'])
		if localTesting == 'off':
			tempStr+='GETTING '+test_name+'...'
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
			remotePath='/users/'+request.session['login']+settings.GIT_REPO+'/'+row['test_name']
			os.symlink(remotePath,localPath)
		with open(suiteFolder+suiteName+settings.JENKINS['JOB_STRUCT']+test_name+'.prs',"w") as out_file:
			json.dump(ast.literal_eval(row["presets"]),out_file,ensure_ascii=False,indent=4,separators=(',',':'))
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
		tempStr+='\nCreating Test plan...'
		out_file = open(suiteFolder+suiteName+settings.JENKINS['JOB_STRUCT']+'suite.txt',"w")
		out_file.write(test_plan)
		out_file.close()
		os.chmod(suiteFolder+suiteName+settings.JENKINS['JOB_STRUCT']+'suite.txt',511)
		tempStr+='DONE!\n'
	tempStr+='\nCreating Node List...'
	myRecordSet.execute("SELECT group_concat(T_EQUIPMENT_id_equipment order by T_EQUIPMENT_id_equipment asc) as nodeList FROM T_PST_ENTITY join T_TPY_ENTITY on(T_TPY_ENTITY_id_entity=id_entity) join T_PROD on(replace(elemName,'#','')=T_PROD.product) where T_PRESETS_id_preset="+str(presetID)+" and elemName like '%#%'")
	nodeList=myRecordSet.fetchone()['nodeList']
	out_file = open(suiteFolder+suiteName+settings.JENKINS['JOB_STRUCT']+'nodeList.txt',"w")
	out_file.write(nodeList)
	out_file.close()
	tempStr+='DONE!\n'

	tempStr+='\n\nTUNING COMPLETE!\nHAVE A NICE DAY!\n'
	context_dict={'login':request.session['login'],'tuningReport':tempStr.replace('\n','\\n')}

	return render_to_response('taws/tuningEngine.html',context_dict)
	#return render_to_response('taws/tuningEngine.html',context_dict,context_instance=RequestContext(request))

def runJenkins(request):

	from jenkinsapi.jenkins import Jenkins
	import shutil

	context = RequestContext(request)
	if 'login' not in request.session:
		fromPage = request.META.get('HTTP_REFERER')
		context_dict={'fromPage':fromPage}
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
	import os.path,time
	import xml.etree.ElementTree as ET

	buildMatrix=[]

	context = RequestContext(request)
	if 'login' not in request.session:
		fromPage = request.META.get('HTTP_REFERER')
		context_dict={'fromPage':fromPage}
		return render_to_response('taws/login.html',context_dict,context)

	server = Jenkins(settings.JENKINS['HOST'],username=request.session['login'],password=request.session['password'])
	suiteFolder=settings.JENKINS['SUITEFOLDER']

	job_name=request.GET.get('jobName')
	page_num=int(request.GET.get('pageNum',1))
	page_size=1000
	buildNumber=0
	
	if (server.has_job(job_name)):
		print('Getting Job '+job_name+' build number...')
		job_instance = server.get_job(job_name)
		buildNumber=job_instance.get_next_build_number()
		print(str(buildNumber)+' build(s) retrieved...')
		for buildId in range(buildNumber,0,-1):
			bgcolor=""
			if os.path.isfile(suiteFolder+job_name+'/builds/'+str(buildId)+'/junitResult.xml'):
				#build_instance=job_instance.get_build(buildId)
				#in_file = open(suiteFolder+job_name+'/builds/'+str(buildId)+'/junitResult.xml',"r")
				#tempFile=in_file.read()
				#in_file.close()
				tempFile=''
				tree = ET.parse(suiteFolder+job_name+'/builds/'+str(buildId)+'/junitResult.xml')
				root = tree.getroot()
				total=0
				failed=0
				passed=0
				for suites in root[0]:
					total+=1
					#Response.Write(suites.text)
					for stderr in suites.iter('stderr'):
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

	import MySQLdb
	import xml.etree.ElementTree as ET
	from os.path import basename
	from datetime import timedelta, datetime
	from jenkinsapi.jenkins import Jenkins

	context = RequestContext(request)
	if 'login' not in request.session:
		fromPage = request.META.get('HTTP_REFERER')
		context_dict={'fromPage':fromPage}
		return render_to_response('taws/login.html',context_dict,context)

	job_name=request.POST.get('jobName')
	buildId=request.POST.get('buildId')
	target='NA'

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
	if 'parameters' in build_instance.get_actions():
		for myTuple in build_instance.get_actions()['parameters']:
			if myTuple['name']=='TB_NODE_IP':
				target=myTuple['value']
				break
	else:
		target='NA'
	#print build_instance.get_resultset().keys()
	tree = ET.parse(suiteFolder+job_name+'/builds/'+str(buildId)+'/junitResult.xml')
	root = tree.getroot()

	buildMatrix=[]
	counter=1
	#for suites in root[0]:
	for suites in root.findall(".suites/suite"):
		if suites.find('name').text.rfind('_Main')>=0:
			testName=suites.find('name').text.replace('(','').replace('.XML)','').replace('._Main','')
			for stderr in suites.iter('stderr'):
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
				if tps.find('name').text.rfind(testName)>=0 and tps.find('name').text.rfind('_Main')<0:
					tpsTemp=tps.find('name').text.replace('(','').replace('.XML)','').replace(testName+'.','').split('_')
					tpsName=tpsTemp[1].replace('-','.')
					tpsArea=tpsTemp[0].replace('-','.')
					tpsTestStatus='Passed'
					tpsBgcolor='info'
					tpsFontcolor="black"
					for stderr in tps.iter('stderr'):
						tpsTestStatus='Failed'
						tpsBgcolor='danger'
						tpsFontcolor="white"
						break
					tpsList.append({'tpsName':tpsName,'tpsArea':tpsArea,'tpsBgcolor':tpsBgcolor,'tpsFontcolor':tpsFontcolor})
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

	import MySQLdb
	import xml.etree.ElementTree as ET
	from os.path import basename
	from datetime import timedelta, datetime
	from jenkinsapi.jenkins import Jenkins

	context = RequestContext(request)
	if 'login' not in request.session:
		fromPage = request.META.get('HTTP_REFERER')
		context_dict={'fromPage':fromPage}
		return render_to_response('taws/login.html',context_dict,context)

	job_name=request.POST.get('jobName')
	buildId=request.POST.get('buildId')
	azione=request.POST.get('azione')

#	server = Jenkins(settings.JENKINS['HOST'],username=request.session['login'],password=request.session['password'])
	suiteFolder=settings.JENKINS['SUITEFOLDER']
#	job_instance = server.get_job(job_name)
#	build_instance=job_instance.get_build(int(buildId))

#	if azione == "addResult1":
#		try:
#			note=req[str(testCount)].value
#		except:
#			note='NA'
#		myRecordSet.execute("INSERT INTO resultReporter (SELECT null as resultID,"+IDAry[testIndex]+" as ID,'"+result+"' as result,null as SWRelease,'"+Session("login")+"' as tester,'"+note+"' as notes,'"+endingDate+"' as executionDate,"+req['s1'].value+" as SWPID,'' as failedReport)")
#		dbConnection.commit()
#		myRecordSet.execute("UPDATE testlist set teststatus='A' where ID="+IDAry[testIndex])
#		dbConnection.commit()
#		myRecordSet.execute("SELECT MAX(resultID) as last from resultReporter")
#		myRecord=myRecordSet.fetchone()
#		lastID=myRecord['last']
#		for tpsIndex in range(1,len(tempTps)-1):
#			if tempTps[tpsIndex].rfind(','):
#				tpsreport=tempTps[tpsIndex].split(',')
#				myRecordSet.execute("INSERT INTO tpsreport (tps,area,result,resultID) VALUES('"+tpsreport[1]+"','"+tpsreport[0].strip()+"','"+tpsreport[2]+"','"+str(lastID)+"')")
#				dbConnection.commit()
#		myRecordSet.execute("UPDATE atmruntime set tawsdb='OK' where runID="+str(runID))
#		dbConnection.commit()

#if suiteName != '':
# 	myRecordSet.execute("select id,concat(product,' ',SWRelease,' SWPs ','<select onchange=\"if((\\\'"+azione+"\\\'==\\\'process\\\')&&(this.value!=\\'\\')){addResult.disabled=false;}else{addResult.disabled=true;}\" name=\"s1\"><option>Select SWP</option>',convert(group_concat(distinct concat('<option value=\"',swpid,'\">',swp,'</option>') order by product,SWRelease,convert(replace(SWP,'.',''),unsigned) desc separator '') using utf8),'</select>') as myresult from compatibility join testarea using(areaID) join availableSWP using(product,SWRelease) where ("+IDStr+") and ordine<>0 group by concat(product,SWRelease)")
#	myRecord=myRecordSet.fetchone()
#	Response.Write(myRecord['myresult'])

#	if 'parameters' in build_instance.get_actions():
#		for myTuple in build_instance.get_actions()['parameters']:
#			if myTuple['name']=='TB_NODE_IP':
#				target=myTuple['value']
#				break
#	else:
#		target='NA'
	#print build_instance.get_resultset().keys()
	tree = ET.parse(suiteFolder+job_name+'/builds/'+str(buildId)+'/junitResult.xml')
	root = tree.getroot()

	buildMatrix=[]
	counter=1
	#for suites in root[0]:
	for suites in root.findall(".suites/suite"):
		if suites.find('name').text.rfind('_Main')>=0:
			testName=suites.find('name').text.replace('(','').replace('.XML)','').replace('._Main','')
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
				if tps.find('name').text.rfind(testName)>=0 and tps.find('name').text.rfind('_Main')<0:
					tpsTemp=tps.find('name').text.replace('(','').replace('.XML)','').replace(testName+'.','').split('_')
					tpsName=tpsTemp[1].replace('-','.')
					tpsArea=tpsTemp[0].replace('-','.')
					tpsTestStatus='Passed'
					tpsBgcolor='info'
					tpsFontcolor="black"
					for stderr in tps.iter('stderr'):
						tpsTestStatus='Failed'
						tpsBgcolor='danger'
						tpsFontcolor="white"
						break
					tpsList.append({'tpsName':tpsName,'tpsArea':tpsArea,'tpsBgcolor':tpsBgcolor,'tpsFontcolor':tpsFontcolor})
			buildMatrix.append({'bgcolor':bgcolor,
				'fontcolor':fontcolor,
				'counter':counter,
				'testName':testName,
				'testStatus':testStatus,
				'testDuration':suites.find('duration').text,
				'tpsList':tpsList,
				'bgimage':bgimage,
				'numTps':len(tpsList)})
			counter+=1

	context_dict={'login':request.session['login'],
		'job_name':job_name,
		'azione':azione,
		'instance': str(buildId),
		'buildMatrix':buildMatrix}
	return render(request,'taws/collectReports.html',context_dict)


def createRunJenkins(request):

	import datetime
	from jenkinsapi.jenkins import Jenkins
	import mysql.connector

	context = RequestContext(request)
	if 'login' not in request.session:
		fromPage = request.META.get('HTTP_REFERER')
		context_dict={'fromPage':fromPage}
		return render_to_response('taws/login.html',context_dict,context)

	job_name=request.GET.get('jobName')
	action=request.GET.get('azione')
	target=request.POST.get('target','')
	swRelMatrix=[]
	runID=''

	suiteFolder=settings.JENKINS['SUITEFOLDER']

	in_file = open(suiteFolder+job_name+'/workspace/nodeList.txt',"r")
	tempFile=in_file.read()
	in_file.close()

	dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
	myRecordSet = dbConnection.cursor(dictionary=True)

	#myRecordSet.execute("select *,group_concat(piddu) as swRelList from (select id_equipment,T_EQUIP_TYPE.name as prodName,concat(sw_rel_name,'#',group_concat(concat(T_PACKAGES.name,'|',id_pack) separator '%')) as piddu,T_EQUIPMENT.name as eqptName,owner,T_EQUIPMENT.description,T_PACKAGES.name from T_EQUIPMENT join T_EQUIP_TYPE on(T_EQUIP_TYPE_id_type=id_type) left join T_PROD on(T_EQUIP_TYPE.name=T_PROD.product) left join T_PACKAGES on(T_PROD.id_prod=T_PACKAGES.T_PROD_id_prod) left join T_SW_REL on(id_sw_rel=T_SW_REL_id_sw_rel) where id_equipment=1 or id_equipment=3 or id_equipment=4 or id_equipment=6 group by T_PROD.product,sw_rel_name) as mytable group by prodName")
	myRecordSet.execute("select *,group_concat(packList) as packList ,group_concat(sw_rel_name) as swRelList from (select id_equipment,T_EQUIP_TYPE.name as prodName,sw_rel_name,group_concat(concat(T_PACKAGES.name,'|',id_pack) separator '%') as packList,T_EQUIPMENT.name as eqptName,owner,T_PACKAGES.name from T_EQUIPMENT join T_EQUIP_TYPE on(T_EQUIP_TYPE_id_type=id_type) left join T_PROD on(T_EQUIP_TYPE.name=T_PROD.product) left join T_PACKAGES on(T_PROD.id_prod=T_PACKAGES.T_PROD_id_prod) left join T_SW_REL on(id_sw_rel=T_SW_REL_id_sw_rel) where id_equipment=1 or id_equipment=3 or id_equipment=4 or id_equipment=6 group by T_PROD.product,sw_rel_name) as mytable group by prodName")

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
			'id_equipmet':row['id_equipment']})

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
			job_instance.invoke(securitytoken='tl-token',build_params={'KateRunId':runID})

	context_dict={'login':request.session['login'],
		'job_name':job_name,
		'action': action,
		'swRelMatrix':swRelMatrix,
		'target':target,
		'runID':runID}

	return render(request,'taws/createRunJenkins.html',context_dict)

def add_bench(request):

	import mysql.connector

	context = RequestContext(request)
	if 'login' not in request.session:
		fromPage = request.META.get('HTTP_REFERER')
		context_dict={'fromPage':fromPage}
		return render_to_response('taws/login.html',context_dict,context)

	dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
	myRecordSet = dbConnection.cursor(dictionary=True)

	bench=request.GET.get('bench','')
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

	name=''
	ip=''
	nm=''
	gw=''
	reference=''
	site=''
	room=''
	product=''
	scope=''
	row=''
	rack=''
	pos=''
	serials=[]
	createReport=''
	rowID=''
	note=''
	description=''

	if action == 'create' or action == 'update':
		myRecordSet.execute("SELECT count(*) as myCount from T_EQUIPMENT WHERE name='"+POSTname+"' and id_equipment<>'"+bench+"'")
		#createReport+="SELECT count(*) as myCount from T_EQUIPMENT WHERE name='"+POSTname+"' and id_equipment<>'"+bench+"'"
		row=myRecordSet.fetchone()
		if row['myCount'] > 0:createReport+='Bench Name '+POSTname+' already present\\n'
		myRecordSet.execute("SELECT count(*) as myCount from T_NET WHERE IP='"+POSTip1+'.'+POSTip2+'.'+POSTip3+'.'+POSTip4+"' and inUse=1 and T_EQUIPMENT_id_equipment<>'"+bench+"'")
		#createReport+="SELECT count(*) as myCount from T_NET WHERE IP='"+POSTip1+'.'+POSTip2+'.'+POSTip3+'.'+POSTip4+"' and inUse=1 and T_EQUIPMENT_id_equipment<>'"+bench+"'"
		row=myRecordSet.fetchone()
		if row['myCount'] > 0:createReport+='IP ADDRESS '+POSTip1+'.'+POSTip2+'.'+POSTip3+'.'+POSTip4+' already in use\\n'
		if debugInterface != '':
			debugInterface=debugInterface.split('$')
			for myITF in debugInterface:
				tempFields=myITF.split('#')
				myRecordSet.execute("SELECT count(*) as myCount FROM T_SERIAL join T_NET on(id_ip=T_NET_id_ip) WHERE IP='"+tempFields[0]+"' and port="+tempFields[1]+" and T_NET.inUse=1 and T_SERIAL.T_EQUIPMENT_id_equipment<>"+bench)
				#createReport+="SELECT count(*) as myCount FROM T_SERIAL join T_NET on(id_ip=T_NET.id_ip) WHERE IP='"+tempFields[0]+"' and port="+tempFields[1]+" and T_NET.inUse=1 and T_NET.T_EQUIPMENT_id_equipment<>'"+bench+"'"
				row=myRecordSet.fetchone()
				if row['myCount'] > 0:createReport+='SERIAL IP ADDRESS '+tempFields[0]+' port '+tempFields[1]+' already in use\\n'
	if createReport!='': bench=request.GET.get('bench','')
	if createReport=='' and (action == 'create' or action == 'update'):
		myRecordSet.execute("SELECT id_type from T_EQUIP_TYPE WHERE name='"+POSTproduct+"'")
		id_type=myRecordSet.fetchone()['id_type']
		myRecordSet.execute("SELECT id_location from T_LOCATION WHERE site='"+POSTsite+"' and room='"+POSTroom+"' and row='"+POSTrow+"' and rack='"+POSTrack+"' and pos='"+POSTpos+"'")
		row=myRecordSet.fetchone()
		if row['id_location'] == '':
			myRecordSet.execute("INSERT INTO T_LOCATION (site,room,row,rack,pos) VALUES ('"+POSTsite+"','"+POSTroom+"','"+POSTrow+"','"+POSTrack+"','"+POSTpos+"')")
			dbConnection.commit()
			myRecordSet.execute("SELECT id_location from T_LOCATION WHERE site='"+POSTsite+"' and room='"+POSTroom+"' and row='"+POSTrow+"' and rack='"+POSTrack+"' and pos='"+POSTpos+"'")
		id_location=row['id_location']
		myRecordSet.execute("SELECT id_scope from T_SCOPE WHERE description='"+POSTscope+"'")
		id_scope=myRecordSet.fetchone()['id_scope']
		if action == 'create':
			myRecordSet.execute("INSERT INTO T_EQUIPMENT (name, T_EQUIP_TYPE_id_type, T_LOCATION_id_location, T_SCOPE_id_scope, T_PACKAGES_id_pack, owner, inUse, description, note) VALUES ('"+POSTname+"', "+str(id_type)+", "+str(id_location)+", "+str(id_scope)+", null, '"+POSTreference+"', 1, '"+POSTdescription+"', '"+POSTnote+"')")
			dbConnection.commit()
			myRecordSet.execute("SELECT id_equipment from T_EQUIPMENT WHERE name='"+POSTname+"'")
			id_equipment=myRecordSet.fetchone()['id_equipment']
		else:
			myRecordSet.execute("UPDATE T_EQUIPMENT set name='"+POSTname+"', T_EQUIP_TYPE_id_type="+str(id_type)+", T_LOCATION_id_location="+str(id_location)+", T_SCOPE_id_scope="+str(id_scope)+", owner='"+POSTreference+"', inUse=1, description='"+POSTdescription+"', note='"+POSTnote+"' WHERE id_equipment="+bench)
			dbConnection.commit()
			id_equipment=bench
		myRecordSet.execute("SELECT count(id_ip) as myCount from T_NET WHERE IP='"+POSTip1+"."+POSTip2+"."+POSTip3+"."+POSTip4+"'")
		row=myRecordSet.fetchone()
		if row['myCount'] > 0:
			myRecordSet.execute("UPDATE T_NET SET inUse=1,T_EQUIPMENT_id_equipment="+str(id_equipment)+" where IP='"+POSTip1+"."+POSTip2+"."+POSTip3+"."+POSTip4+"'")
			dbConnection.commit()
		else:
			myRecordSet.execute("INSERT INTO T_NET (inUse,description,T_EQUIPMENT_id_equipment,protocol,IP,NM,GW) VALUES (1,'',"+str(id_equipment)+",'v4','"+POSTip1+"."+POSTip2+"."+POSTip3+"."+POSTip4+"','"+POSTnm1+"."+POSTnm2+"."+POSTnm3+"."+POSTnm4+"','"+POSTgw1+"."+POSTgw2+"."+POSTgw3+"."+POSTgw4+"')")
			dbConnection.commit()
		myRecordSet.execute("SELECT id_ip from T_NET WHERE IP='"+POSTip1+"."+POSTip2+"."+POSTip3+"."+POSTip4+"'")
		id_ip=myRecordSet.fetchone()['id_ip']
		myRecordSet.execute("DELETE from T_SERIAL where T_EQUIPMENT_id_equipment="+str(id_equipment))
		dbConnection.commit()
		for myITF in debugInterface:
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
		bench=id_equipment

	



	if bench != '':
		SQL="SELECT *,T_NET.IP as benchIP,T_NET.NM as benchNM,T_NET.GW as benchGW,T_EQUIPMENT.description as benchDescription,T_EQUIPMENT.note as benchNote,group_concat(concat(ip1.ip,'#',port,'#',if(slot is null,'-',slot),'#',if(subslot is null,'-',subslot)) separator '|') as serials,T_SCOPE.description as scope,T_EQUIP_TYPE.name as type,T_EQUIPMENT.name as benchName,if(status like '%ING%',status,'IDLE') as benchStatus,T_EQUIPMENT.owner as reference,runtime.owner as author FROM T_EQUIPMENT LEFT JOIN (select * from T_RTM_BODY left join T_RUNTIME on(id_run=T_RUNTIME_id_run) where status='RUNNING') as runtime on(id_equipment=T_EQUIPMENT_id_equipment) left join T_EQUIP_TYPE on(id_type=T_EQUIP_TYPE_id_type) left join T_NET on(T_NET.T_EQUIPMENT_id_equipment=id_equipment) LEFT JOIN T_LOCATION on(T_LOCATION_id_location=id_location) LEFT JOIN T_SERIAL on(T_SERIAL.T_EQUIPMENT_id_equipment=id_equipment) LEFT JOIN T_SCOPE on(T_SCOPE_id_scope=id_scope) LEFT JOIN T_NET as ip1 on(T_SERIAL.T_NET_id_ip=ip1.id_ip) where id_equipment="+str(bench)+" group by id_equipment"
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
				tempIP=tempSerial[0].split('.')
				serials.append({'ip':tempSerial[0],
					'port':tempSerial[1],
					'slot':tempSerial[2],
					'subslot':tempSerial[3]})

	ip = ip.split('.') if ip != '' else '...'.split('.')
	nm = nm.split('.') if nm != '' else '...'.split('.')
	gw = gw.split('.') if gw != '' else '...'.split('.')

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
		'createReport':createReport,
		'description':description,
		'note':note,
		'consoleServers':consoleServers
	}

	return render(request,'taws/add_bench.html',context_dict)

def bench(request):

	filters=request.POST.get('filters','')
	pattern=request.POST.get('pattern','')
	deleteBench=request.POST.get('deleteBench','')
	action=request.GET.get('action','')

	import mysql.connector
	from django.utils.safestring import mark_safe

	context = RequestContext(request)
	if 'login' not in request.session:
		fromPage = request.META.get('HTTP_REFERER')
		context_dict={'fromPage':fromPage}
		return render_to_response('taws/login.html',context_dict,context)

	if action == 'delete':
		myRecordSet.execute("DELETE from T_SERIAL where T_EQUIPMENT_id_equipment="+deleteBench)
		dbConnection.commit()
		myRecordSet.execute("DELETE from T_NET where T_EQUIPMENT_id_equipment="+deleteBench)
		dbConnection.commit()
		myRecordSet.execute("DELETE from T_EQUIPMENT where id_equipment="+deleteBench)
		dbConnection.commit()
		

	dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
	myRecordSet = dbConnection.cursor(dictionary=True)
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

def createNewTest(request):

  import mysql.connector

  context = RequestContext(request)
  if 'login' not in request.session:
    fromPage = request.META.get('HTTP_REFERER')
    context_dict={'fromPage':fromPage}
    return render_to_response('taws/login.html',context_dict,context)

  test_name=request.GET.get('testName')
  username=request.session['login']
  
  dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
  myRecordSet = dbConnection.cursor(dictionary=True)

  myRecordSet.execute("select concat(T_PRESETS.preset_title,'[',convert(group_concat(distinct id_topology separator ',') using utf8),']') as description,id_preset from T_PRESETS join T_PST_ENTITY on(id_preset=T_PRESETS_id_preset) join T_TPY_ENTITY on(id_entity=T_TPY_ENTITY_id_entity) join T_TOPOLOGY on(id_topology=T_TOPOLOGY_id_topology) where owner='"+request.session['login']+"' group by id_preset")
  userPreset=[{'userPresetName':row["description"],'userPresetID':row["id_preset"]} for row in myRecordSet]

  myRecordSet.execute("SELECT * from T_TOPOLOGY join T_SCOPE on(T_SCOPE_id_scope=id_scope) order by T_SCOPE.description")
  topoAry=[{'topoID':row["id_topology"],'topoName':row["title"]} for row in myRecordSet]

  myRecordSet.execute("select product,group_concat(scope_area separator '@') as productConcat from (select product,concat(T_SCOPE.description,'?',group_concat(distinct area_name order by area_name separator '%')) as scope_area from T_DOMAIN join T_SCOPE on(T_SCOPE_id_scope=id_scope) join T_AREA on(T_AREA_id_area=id_area) join T_PROD on(T_PROD_id_prod=id_prod) group by product,T_SCOPE.description order by product asc,T_SCOPE.description asc) as scope_area group by product order by product asc")
  productAry=[{'product':row["product"],'productConcat':row["productConcat"]} for row in myRecordSet]
  
  context_dict={'login':request.session['login'],
    'userPreset':userPreset,
    'topoAry':topoAry,
    'productAry':productAry}

  return render(request,'taws/createNewTest.html',context_dict)

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
		context_dict={'fromPage':fromPage}
		return render_to_response('taws/login.html',context_dict,context)

	job_name=request.POST.get('jobName','')
	buildId=request.POST.get('buildId','')
	testName=request.POST.get('testName','')

	suiteFolder=settings.JENKINS['SUITEFOLDER']
	tree = ET.parse(suiteFolder+job_name+'/builds/'+str(buildId)+'/junitResult.xml')
	root = tree.getroot()

	treeView=''
	counter1=1
	counter2=1
	for suites in root.findall(".suites/suite"):
		if suites.find('name').text.rfind(testName)>=0:
			tempTreeView=''
			tempTreeView+="<li><label for='folder"+str(counter1)+"'>"+suites.find('name').text.replace('(','').replace('.XML)','')+"([MAINRESULT])</label> <input type='checkbox' id='folder"+str(counter1)+"' />"
			tempTreeView+="<ol>"
			mainResult="<span style='color:green;font-weight: bold;'>Passed</span>"
			for case in suites.findall('cases/case'):
				testStatus="<span style='color:green;font-weight: bold;'>Passed</span>"
				if case.find('stderr')!=None:
					testStatus="<span style='color:red;font-weight: bold;'>Failed</span>"
					mainResult="<span style='color:red;font-weight: bold;'>Failed</span>"
				if case.find('skipped').text=='true':
					testStatus="<span style='color:gray;font-weight: bold;'>Skipped</span>"
					if mainResult.rfind('Failed')<0:mainResult="<span style='color:gray;font-weight: bold;'>Skipped</span>"
				tempTreeView+="<li><label for='subfolder"+str(counter2)+"'>"+case.find('testName').text+" ("+testStatus+")</label> <input type='checkbox' id='subfolder"+str(counter2)+"' />"
				tempTreeView+="<ol>"
				tempTreeView+="<li><label for='subsubfolder"+str(counter2)+"'>STDOUT:\n"+case.find('stdout').text+"</label> <input type='checkbox' id='subsubfolder"+str(counter2)+"' />"
				tempTreeView+="</li>"
				if testStatus.rfind('Failed')>=0:
					counter2+=1
					tempTreeView+="<li><label for='subsubfolder"+str(counter2)+"'>STDERR:\n"+case.find('stderr').text+"</label> <input type='checkbox' id='subsubfolder"+str(counter2)+"' />"
					tempTreeView+="</li>"
				counter2+=1
				tempTreeView+="<li><label for='subsubfolder"+str(counter2)+"'>DURATION:\n"+case.find('duration').text+"</label> <input type='checkbox' id='subsubfolder"+str(counter2)+"' />"
				tempTreeView+="</li>"
				tempTreeView+="</ol>"
				tempTreeView+="</li>"
				counter2+=1
			tempTreeView+="</ol>"
			tempTreeView+="</li>"
			treeView+=tempTreeView.replace('[MAINRESULT]',mainResult)
			counter1+=1

	context_dict={'login':request.session['login'],
		'job_name':job_name,
		'buildId': str(buildId),
		'treeView':mark_safe(treeView),
		'testName':testName}
	return render(request,'taws/viewReport.html',context_dict)

  
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
		myRecordSet.execute("select *,T_SUITES_BODY.run_section as section from T_SUITES join T_SUITES_BODY on(id_suite=T_SUITES_id_suite) join T_TEST_REVS on(id_TestRev=T_TEST_REVS_id_TestRev) join T_TEST on(test_id=T_TEST_test_id) join (select T_TEST_REVS_id_TestRev,group_concat(concat(area_name,'-',tps_reference) separator '!') as tps from T_TPS join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on (id_area=T_AREA_id_area) group by T_TEST_REVS_id_TestRev) as T_TPS on(id_TestRev=T_TPS.T_TEST_REVS_id_TestRev) join T_TEST_COMPATIBILITY on(id_TestRev=T_TEST_COMPATIBILITY.T_TEST_REVS_id_TestRev) join T_DOMAIN on(id_domain=T_TEST_COMPATIBILITY.T_DOMAIN_id_domain) join T_AREA on(T_AREA_id_area=id_area) join T_PROD on(id_prod=T_PROD_id_prod) join T_SW_REL on(T_SW_REL_id_sw_rel=id_sw_rel) where id_suite="+str(loadID)+" group by id_TestRev,TCOrder order by TCOrder")
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

		myRecordSet.execute("select group_concat(concat(revision,'|',id_TestRev) separator '!') as revisions from T_TEST join T_TEST_REVS on (test_id=T_TEST_test_id) join (select T_TEST_REVS_id_TestRev,group_concat(concat(area_name,'-',tps_reference) order by id_tps separator '!') as tps from T_TPS join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on (id_area=T_AREA_id_area) group by T_TEST_REVS_id_TestRev) as T_TPS on(id_TestRev=T_TEST_REVS_id_TestRev) join T_TEST_COMPATIBILITY on(id_TestRev=T_TEST_COMPATIBILITY.T_TEST_REVS_id_TestRev) join T_DOMAIN on(id_domain=T_TEST_COMPATIBILITY.T_DOMAIN_id_domain) join T_AREA on(T_AREA_id_area=id_area) join T_PROD on(id_prod=T_PROD_id_prod) join T_SW_REL on(T_SW_REL_id_sw_rel=id_sw_rel) where T_TEST_test_id="+str(row['T_TEST_test_id'])+" group by T_TEST_test_id")
		row=myRecordSet.fetchone()

		testString=testString.replace('[MY_REVISIONS]',row['revisions'])
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
		myRecordSet.execute("select *,group_concat(concat(revision,'|',id_TestRev) separator '!') as revisions from (select id_TestRev,product,sw_rel_name,run_section,area_name,tps,test_name,duration,metric,topology,dependency,author,description,last_update,revision,lab,test_id from T_TEST join T_TEST_REVS on (test_id=T_TEST_test_id) join (select T_TEST_REVS_id_TestRev,group_concat(concat(area_name,'-',tps_reference) order by id_tps separator '<br>') as tps from T_TPS join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on (id_area=T_AREA_id_area) group by T_TEST_REVS_id_TestRev) as T_TPS on(id_TestRev=T_TEST_REVS_id_TestRev) join T_TEST_COMPATIBILITY on(id_TestRev=T_TEST_COMPATIBILITY.T_TEST_REVS_id_TestRev) join T_DOMAIN on(id_domain=T_TEST_COMPATIBILITY.T_DOMAIN_id_domain) join T_AREA on(T_AREA_id_area=id_area) join T_PROD on(id_prod=T_PROD_id_prod) join T_SW_REL on(T_SW_REL_id_sw_rel=id_sw_rel) where product='"+queryProduct+"' and sw_rel_name='"+querySW+"' and area_name='"+queryArea+"' order by test_id,id_TestRev desc) as myTable group by test_id")
		myStr="select *,group_concat(concat(revision,'|',id_TestRev) separator '!') as revisions from (select id_TestRev,product,sw_rel_name,run_section,area_name,tps,test_name,duration,metric,topology,dependency,author,description,last_update,revision,lab,test_id from T_TEST join T_TEST_REVS on (test_id=T_TEST_test_id) join (select T_TEST_REVS_id_TestRev,group_concat(concat(area_name,'-',tps_reference) order by id_tps separator '<br>') as tps from T_TPS join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on (id_area=T_AREA_id_area) group by T_TEST_REVS_id_TestRev) as T_TPS on(id_TestRev=T_TEST_REVS_id_TestRev) join T_TEST_COMPATIBILITY on(id_TestRev=T_TEST_COMPATIBILITY.T_TEST_REVS_id_TestRev) join T_DOMAIN on(id_domain=T_TEST_COMPATIBILITY.T_DOMAIN_id_domain) join T_AREA on(T_AREA_id_area=id_area) join T_PROD on(id_prod=T_PROD_id_prod) join T_SW_REL on(T_SW_REL_id_sw_rel=id_sw_rel) order by test_id,revision desc) as myTable where product='"+queryProduct+"' and sw_rel_name='"+querySW+"' and area_name='"+queryArea+"' group by test_id"
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

		myRecordSet.execute("select *,T_SUITES_BODY.run_section as section from T_SUITES join T_SUITES_BODY on(id_suite=T_SUITES_id_suite) join T_TEST_REVS on(id_TestRev=T_TEST_REVS_id_TestRev) join T_TEST on(test_id=T_TEST_test_id) join (select T_TEST_REVS_id_TestRev,group_concat(concat(area_name,'-',tps_reference) order by id_tps separator '!') as tps from T_TPS join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on (id_area=T_AREA_id_area) group by T_TEST_REVS_id_TestRev) as T_TPS on(id_TestRev=T_TPS.T_TEST_REVS_id_TestRev) join T_TEST_COMPATIBILITY on(id_TestRev=T_TEST_COMPATIBILITY.T_TEST_REVS_id_TestRev) join T_DOMAIN on(id_domain=T_TEST_COMPATIBILITY.T_DOMAIN_id_domain) join T_AREA on(T_AREA_id_area=id_area) join T_PROD on(id_prod=T_PROD_id_prod) join T_SW_REL on(T_SW_REL_id_sw_rel=id_sw_rel) where id_suite="+str(suiteID)+" group by id_TestRev,TCOrder order by TCOrder")
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
			row['revision']+"#"+\
			row['lab']+"$")
		dbConnection.close()

		return  JsonResponse({'testString':testString,'userSuiteAry': userSuiteAry,'sharedSuiteAry': sharedSuiteAry,'suiteID':suiteID}, safe=False)

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

		myRecordSet.execute("select * from T_TEST join T_TEST_REVS on (test_id=T_TEST_test_id) join (select T_TEST_REVS_id_TestRev,group_concat(concat(area_name,'-',tps_reference) order by id_tps separator '!') as tps from T_TPS join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on (id_area=T_AREA_id_area) group by T_TEST_REVS_id_TestRev) as T_TPS on(id_TestRev=T_TEST_REVS_id_TestRev) join T_TEST_COMPATIBILITY on(id_TestRev=T_TEST_COMPATIBILITY.T_TEST_REVS_id_TestRev) join T_DOMAIN on(id_domain=T_TEST_COMPATIBILITY.T_DOMAIN_id_domain) join T_AREA on(T_AREA_id_area=id_area) join T_PROD on(id_prod=T_PROD_id_prod) join T_SW_REL on(T_SW_REL_id_sw_rel=id_sw_rel) where id_TestRev="+iteration+" group by id_TestRev")
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

		myRecordSet.execute("select group_concat(concat(revision,'|',id_TestRev) separator '!') as revisions from T_TEST join T_TEST_REVS on (test_id=T_TEST_test_id) join (select T_TEST_REVS_id_TestRev,group_concat(concat(area_name,'-',tps_reference) order by id_tps separator '!') as tps from T_TPS join T_DOMAIN on(id_domain=T_DOMAIN_id_domain) join T_AREA on (id_area=T_AREA_id_area) group by T_TEST_REVS_id_TestRev) as T_TPS on(id_TestRev=T_TEST_REVS_id_TestRev) join T_TEST_COMPATIBILITY on(id_TestRev=T_TEST_COMPATIBILITY.T_TEST_REVS_id_TestRev) join T_DOMAIN on(id_domain=T_TEST_COMPATIBILITY.T_DOMAIN_id_domain) join T_AREA on(T_AREA_id_area=id_area) join T_PROD on(id_prod=T_PROD_id_prod) join T_SW_REL on(T_SW_REL_id_sw_rel=id_sw_rel) where T_TEST_test_id="+str(row['T_TEST_test_id'])+" group by T_TEST_test_id")
		row=myRecordSet.fetchone()

		testString=testString.replace('[MY_REVISIONS]',row['revisions'])
		dbConnection.close()


		return  JsonResponse({'testString': testString}, safe=False)

	if myAction=='savePreset':

		fileName = request.POST.get('presetName','')
		savingString = request.POST.get('presetBody','')
		presetType = request.POST.get('presetType','')

		dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
		myRecordSet=dbConnection.cursor(dictionary=True)

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

		return  JsonResponse({'presetAry': row['presetBody'],'userPreset': userPreset[:-1],'sharedPreset': sharedPreset[:-1],'fileName':row['preset_title'],'fileID':row['id_preset'],'fileTitle':row['description'],'presetType':presetType}, safe=False)

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
		myRecordSet.execute("select concat(T_PRESETS.preset_title,'[',convert(group_concat(distinct id_topology separator ',') using utf8),']') as description,id_preset from T_PRESETS join T_PST_ENTITY on(id_preset=T_PRESETS_id_preset) join T_TPY_ENTITY on(id_entity=T_TPY_ENTITY_id_entity) join T_TOPOLOGY on(id_topology=T_TOPOLOGY_id_topology) where owner='"+request.session['login']+"' group by id_preset")
		userSuiteAry=[{'presetName':row["description"],'presetID':row["id_preset"]} for row in myRecordSet]
		myRecordSet.execute("select concat(T_PRESETS.preset_title,'[',convert(group_concat(distinct id_topology separator ',') using utf8),']') as description,id_preset from T_PRESETS join T_PST_ENTITY on(id_preset=T_PRESETS_id_preset) join T_TPY_ENTITY on(id_entity=T_TPY_ENTITY_id_entity) join T_TOPOLOGY on(id_topology=T_TOPOLOGY_id_topology) where owner='SHARED' group by id_preset")
		sharedSuiteAry=[{'presetName':row["description"],'presetID':row["id_preset"]} for row in myRecordSet]

		dbConnection.close()

		return  JsonResponse({'userSuiteAry': userSuiteAry,'sharedSuiteAry': sharedSuiteAry,'username':row['owner'],'presetName':presetName}, safe=False)


	if myAction=='localBrowsing':

		import glob,os,ntpath
    
		username=request.session['login']
		password=request.session['password']

		testString=""
		localString=""
		localPath=settings.JENKINS['SUITEFOLDER']+username+'_Development/workspace/suite/'
		for f in glob.glob(localPath+'*.py'):
			if os.path.isfile(f+'.prs'):
				tempTest = open(f,"r")
				tempMetaInfo=tempTest.read().split('<METAINFO>')
				if len(tempMetaInfo)>1:
					metaInfo=tempMetaInfo[1].split('<DESCRIPTION>')
					description=metaInfo[1]
					metaInfo=tempMetaInfo[1].split('<TOPOLOGY>')
					topology=metaInfo[1]
					metaInfo=tempMetaInfo[1].split('<DEPENDENCY>')
					dependency=metaInfo[1]
					metaInfo=tempMetaInfo[1].split('<LAB>')
					lab=metaInfo[1]
					metaInfo=tempMetaInfo[1].split('<TPS>')
					tps=metaInfo[1]
					metaInfo=tempMetaInfo[1].split('<RUNSECTIONS>')
					runsection=metaInfo[1]
					#if runsection.isdigit()==False:runsection='11111'
					metaInfo=tempMetaInfo[1].split('<AUTHOR>')
					author=metaInfo[1]
				else:
					description="NA"
					topology="NA"
					dependency="NA"
					lab="NA"
					tps="NA"
					runsection="NA"
					author="NA"

				tempTest.close()
				testString+="NA#"+\
				"NA#"+\
				"NA#"+\
				"0#"+\
				"NA#"+\
				tps+"#"+\
				ntpath.basename(f)+"#"+\
				"0#"+\
				"0#"+\
				"NA#"+\
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
					tempTest = open(tempLine[0]+'.py',"r")
					tempMetaInfo=tempTest.read().split('<METAINFO>')
					if len(tempMetaInfo)>1:
						metaInfo=tempMetaInfo[1].split('<DESCRIPTION>')
						description=metaInfo[1]
						metaInfo=tempMetaInfo[1].split('<TOPOLOGY>')
						topology=metaInfo[1]
						metaInfo=tempMetaInfo[1].split('<DEPENDENCY>')
						dependency=metaInfo[1]
						metaInfo=tempMetaInfo[1].split('<LAB>')
						lab=metaInfo[1]
						metaInfo=tempMetaInfo[1].split('<TPS>')
						tps=metaInfo[1]
						metaInfo=tempMetaInfo[1].split('<RUNSECTIONS>')
						runsection=metaInfo[1]
						if runsection.isdigit()==False:runsection='11111'
						metaInfo=tempMetaInfo[1].split('<AUTHOR>')
						author=metaInfo[1]
					else:
						description="NA"
						topology="NA"
						dependency="NA"
						lab="NA"
						tps="NA"
						runsection="11111"
						author="NA"

					tempSection=list(runsection)
					if myLine.rfind(' --')>=0:
						if myLine.rfind('--DUTSet')>=0:tempSection[0]='2'
						if myLine.rfind('--testSet')>=0:tempSection[1]='2'
						if myLine.rfind('--testBody')>=0:tempSection[2]='2'
						if myLine.rfind('--testClean')>=0:tempSection[3]='2'
						if myLine.rfind('--DUTClean')>=0:tempSection[4]='2'
					tempTest.close()
					localString+="NA#"+\
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
		
   
		return  JsonResponse({'testString':testString,'localString':localString}, safe=False)

	if myAction=='saveLocal':

		import ntpath
		username=request.session['login']
		savingString = request.POST.get('savingString','')
		localString=''
   
		localPath=settings.JENKINS['SUITEFOLDER']+username+'_Development/workspace/suite/'
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
		#localString=localSuite.read()
		for myLine in localSuite.readlines():
			tempLine=myLine.split('.py')
			tempTest = open(tempLine[0]+'.py',"r")
			tempMetaInfo=tempTest.read().split('<METAINFO>')
			if len(tempMetaInfo)>1:
				metaInfo=tempMetaInfo[1].split('<DESCRIPTION>')
				description=metaInfo[1]
				metaInfo=tempMetaInfo[1].split('<TOPOLOGY>')
				topology=metaInfo[1]
				metaInfo=tempMetaInfo[1].split('<DEPENDENCY>')
				dependency=metaInfo[1]
				metaInfo=tempMetaInfo[1].split('<LAB>')
				lab=metaInfo[1]
				metaInfo=tempMetaInfo[1].split('<TPS>')
				tps=metaInfo[1]
				metaInfo=tempMetaInfo[1].split('<RUNSECTIONS>')
				runsection=metaInfo[1]
				if runsection.isdigit()==False:runsection='11111'
				metaInfo=tempMetaInfo[1].split('<AUTHOR>')
				author=metaInfo[1]
			else:
				description="NA"
				topology="NA"
				dependency="NA"
				lab="NA"
				tps="NA"
				runsection="NA"
				author="NA"

			tempSection=list(runsection)
			if myLine.rfind(' --')>=0:
				if tempLine[1].rfind('--DUTSet')>=0:tempSection[0]='2'
				if tempLine[1].rfind('--testSet')>=0:tempSection[1]='2'
				if tempLine[1].rfind('--testBody')>=0:tempSection[2]='2'
				if tempLine[1].rfind('--testClean')>=0:tempSection[3]='2'
				if tempLine[1].rfind('--DUTClean')>=0:tempSection[4]='2'
			tempTest.close()
			localString+="NA#"+\
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

		myRecordSet.execute("select concat('{',group_concat(myTuple),'}') as presets from (SELECT entityName,T_PRESETS_id_preset,T_TOPOLOGY_id_topology,group_concat(if(elemName like '%#%',concat(char(39),entityName,char(39),':',char(39),T_EQUIPMENT_id_equipment,char(39)),concat(char(39),entityName,'_',elemName,char(39),':',char(39),pstValue,char(39)))) as myTuple FROM T_PST_ENTITY join T_TPY_ENTITY on(id_entity=T_TPY_ENTITY_id_entity) where T_PRESETS_id_preset="+presetID+" and T_TOPOLOGY_id_topology="+topoID+" group by entityName) as presets")
		row = myRecordSet.fetchone()
		myPreset=row['presets']   
#json.dump(ast.literal_eval(row["presets"]),out_file,ensure_ascii=False,indent=4,separators=(',',':'))

		return  JsonResponse({'templatePreset':json.dumps(ast.literal_eval(myPreset), sort_keys=True,indent=4, separators=(',', ':'))}, safe=False)

	if myAction=='createTest':
   
		import os 

		testName = request.POST.get('testName','')
		presetBody = request.POST.get('presetBody','')
		product=request.POST.get('product','')
		domain=request.POST.get('domain','')
		area=request.POST.get('area','')

		username=request.session['login']

		localPath=settings.JENKINS['SUITEFOLDER']+request.session['login']+'_Development/workspace/suite/'+testName
		remotePath='/users/'+request.session['login']+settings.GIT_REPO+'/TestCases/'+product+'/'+domain+'/'+area+'/'+testName
      
		testTemplateFile = open(settings.TEST_TEMPLATE,"r")
		testTemplate=testTemplateFile.read()
		testTemplateFile.close()
      
		localSuite = open(remotePath+'.py',"w")
		localSuite.write(testTemplate)
		localSuite.close()
		os.chmod(remotePath+'.py',511)

		localPreset = open(localPath+'.py.prs',"w")
		localPreset.write(presetBody)
		localPreset.close()
		os.chmod(localPath+testName+'.py.prs',511)

		if os.path.exists(localPath):shutil.rmtree(localPath)

		os.symlink(remotePath,localPath)
		
		creationReport='Test '+remotePath+'.py successfully created.\n'+\
			'Preset '+localPath+'.py.prs successfully created.\n'+\
			'Symbolic Link '+localPath+'.py successfully created.\n'

		return  JsonResponse({'creationReport':creationReport}, safe=False)

	if myAction=='deleteTest':
   
		import os 

		testList = request.POST.get('deleteList','').split('#')

		username=request.session['login']
		creationReport=''
   
		for myTest in testList:
   
			if myTest.isdigit():
				pass
			else:
				os.remove(myTest)
				creationReport+='Test '+myTest+' successfully deleted\n'

		return  JsonResponse({'creationReport':creationReport}, safe=False)

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
