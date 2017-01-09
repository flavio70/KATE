from django.shortcuts import render
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from django.contrib import auth
from django.views.decorators.csrf import requires_csrf_token
from django.http import JsonResponse
from django.conf import settings
from django.http import HttpResponse


# Create your views here.

def power_management_table(request):
	
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
	
	SQL="select row,site,room,id_powerMngmt,ucase(powerTable.owner) as owner,manual_status,pin,rack,T_EQUIPMENT.name,id_equipment,id_location,ip,power_status from (select *,1 as log from (SELECT * FROM T_POWER_MNGMT left join T_POWER_STATUS on(id_powerMngmt=T_POWER_MNGMT_id_powerMngmt) order by last_change desc) as myTable group by T_EQUIPMENT_id_equipment,pin) as powerTable join T_EQUIPMENT on(id_equipment=T_EQUIPMENT_id_equipment) join T_LOCATION on(id_location=powerTable.T_LOCATION_id_location) join T_NET on(id_equipment=T_NET.T_EQUIPMENT_id_equipment) left join (select * from (select * from T_POWER_SCHEDULE order by start_time) as mytable group by T_POWER_MNGMT_id_powerMngmt) as scheduleTable on(id_powerMngmt=scheduleTable.T_POWER_MNGMT_id_powerMngmt) order by site,room,row,rack"
	myRecordSet.execute(SQL)
	
	benches=[]
	for row in myRecordSet:
		benches.append({'rack':row["rack"],
			'room':row["room"],
			'site':row["site"],
			'row':row["row"],
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
		'benches':benches,
		'powerLevel':powerLevel
	}
	return render_to_response('powerManagement/power_management_table.html',context_dict,context)

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
		return render_to_response('powerManagement/power_management.html',context_dict,context)

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
		return render_to_response('powerManagement/power_management.html',context_dict,context)

	if powerLevel == 'rack':
		lab=request.POST.get('lab','')
		myrow=request.POST.get('row','')
		#SQL="select powerTable.owner,pin,rack,T_EQUIPMENT.name,id_equipment,id_location,ip,if(power_status=1,'danger','success') as power_status from (select * from (SELECT * FROM T_POWER_MNGMT order by last_change desc) as myTable group by T_EQUIPMENT_id_equipment,pin) as powerTable join T_EQUIPMENT on(id_equipment=T_EQUIPMENT_id_equipment) join T_LOCATION on(id_location=powerTable.T_LOCATION_id_location) join T_NET on(id_equipment=T_NET.T_EQUIPMENT_id_equipment)"
		#SQL="select powerTable.owner,pin,rack,T_EQUIPMENT.name,id_equipment,id_location,ip,if(power_status=1,'danger','success') as power_status,log from (select *,group_concat(concat(last_change,' - ',remarks) separator '<br>') as log from (SELECT * FROM T_POWER_MNGMT order by last_change desc) as myTable group by T_EQUIPMENT_id_equipment,pin) as powerTable join T_EQUIPMENT on(id_equipment=T_EQUIPMENT_id_equipment) join T_LOCATION on(id_location=powerTable.T_LOCATION_id_location) join T_NET on(id_equipment=T_NET.T_EQUIPMENT_id_equipment)"
		SQL="select id_powerMngmt,if(manual_status=1,concat(concat('RACK OWNED BY ',ucase(powerTable.owner)),'\\\\n\\\\nACTUAL SCHEDULING:\\\\n\\\\tSHUT DOWN TIME\\\\t',start_time,'\\\\n\\\\tPOWER ON AT\\\\t\\\\t',stop_time),concat('RACK OWNED BY ',ucase(powerTable.owner))) as owner,manual_status,pin,rack,T_EQUIPMENT.name,id_equipment,id_location,ip,power_status from (select *,1 as log from (SELECT * FROM T_POWER_MNGMT left join T_POWER_STATUS on(id_powerMngmt=T_POWER_MNGMT_id_powerMngmt) order by last_change desc) as myTable group by T_EQUIPMENT_id_equipment,pin) as powerTable join T_EQUIPMENT on(id_equipment=T_EQUIPMENT_id_equipment) join T_LOCATION on(id_location=powerTable.T_LOCATION_id_location) join T_NET on(id_equipment=T_NET.T_EQUIPMENT_id_equipment) left join (select * from (select * from T_POWER_SCHEDULE order by start_time) as mytable group by T_POWER_MNGMT_id_powerMngmt) as scheduleTable on(id_powerMngmt=scheduleTable.T_POWER_MNGMT_id_powerMngmt) where room='"+lab+"' and row='"+myrow+"'"
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
		return render_to_response('powerManagement/power_management.html',context_dict,context)


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

def pingIP(request):
	
	import json, os
	
	#context = RequestContext(request)
	myIP=request.POST.get('myIP')
	
	response = os.system("ping -c 1 " + myIP)  
	if response == 0:
		pingStatus='OK'
	else:
		pingStatus='KO'		

	context_dict={'login':request.session['login'],
		'myIP':myIP,
		'pingStatus':pingStatus
	}
	print('Ping '+myIP+' '+pingStatus)
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
	
	import json, os
	import mysql.connector
	
	#context = RequestContext(request)
	idPowerMngmt=request.POST.get('idPowerMngmt','')
	
	dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'],port=settings.DATABASES['default']['PORT'])
	myRecordSet = dbConnection.cursor(dictionary=True)
	#SQL="SELECT ip,pin FROM T_POWER_MNGMT join T_NET using(T_EQUIPMENT_id_equipment) where id_powerMngmt="+idPowerMngmt
	SQL="select *,T_POWER_MNGMT.owner as rackOwner from T_POWER_MNGMT join T_NET using(T_EQUIPMENT_id_equipment) join T_LOCATION on(id_location=T_LOCATION_id_location) join T_EQUIPMENT on(id_equipment=T_EQUIPMENT_id_equipment) where id_powerMngmt="+idPowerMngmt
	myRecordSet.execute(SQL)
	row=myRecordSet.fetchone()
	
	SQL="select *,T_EQUIP_TYPE.name as type,T_EQUIPMENT.name as benchName from T_EQUIPMENT join T_LOCATION on(T_LOCATION_id_location=id_location) join T_EQUIP_TYPE on(id_type=T_EQUIP_TYPE_id_type) join T_NET on(id_equipment=T_EQUIPMENT_id_equipment) where site='"+row['site']+"' and room='"+row['room']+"' and row='"+str(row['row'])+"' and rack='"+row['rack']+"' order by pos"
	myRecordSet.execute(SQL)
	bench=[]
	for benches in myRecordSet:
		pingStatus='unused'
		#hostname = benches['IP']
		#response = os.system("ping -c 1 " + hostname)  
		#if response == 0:
		#	pingStatus='OK'
		#else:
		#	pingStatus='KO'		
		bench.append({'bench':benches["benchName"],'owner':benches['owner'],'type':benches['type'],'pingStatus':pingStatus,'IP':benches['IP']})
		
	SQL="SELECT * FROM auth_user where first_name is not null order by username"
	myRecordSet.execute(SQL)
	users=''
	for myUsers in myRecordSet:
		selectStr=""
		if myUsers['username'].upper() == row["rackOwner"].upper(): selectStr="selected"
		users+='<option value='+myUsers['username']+' '+selectStr+'>'+myUsers['username'].upper()+'</option>'

					
	context_dict={'login':request.session['login'],
			'rackName':row['rack'],
			'idPowerMngmt':idPowerMngmt,
			'name':str(row["name"]),
			'pin':str(row["pin"]),
			'ip':row["IP"],
			'owner':row["rackOwner"],
			'users':users,
			'bench':bench
		}
	#location=row["T_LOCATION_id_location"]
	#SQL="select * from T_EQUIPMENT where T_LOCATION_id_location="+location
	#myRecordSet.execute(SQL)
	#row=myRecordSet.fetchone()

	print('Get Rack Details')
	return HttpResponse(json.dumps(context_dict),content_type="application/json")

def changeRackOwner(request):
	
	import json
	import mysql.connector
	
	#context = RequestContext(request)
	idPowerMngmt=request.POST.get('idPowerMngmt','')
	newOwner=request.POST.get('newOwner')

	dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'],port=settings.DATABASES['default']['PORT'])
	myRecordSet = dbConnection.cursor(dictionary=True)

	SQL="update T_POWER_MNGMT set owner='"+newOwner+"' where id_powerMngmt="+idPowerMngmt
	myRecordSet.execute(SQL)
	dbConnection.commit()
	
	#SQL="SELECT ip,pin FROM T_POWER_MNGMT join T_NET using(T_EQUIPMENT_id_equipment) where id_powerMngmt="+idPowerMngmt
	SQL="select *,T_POWER_MNGMT.owner as rackOwner from T_POWER_MNGMT join T_NET using(T_EQUIPMENT_id_equipment) join T_LOCATION on(id_location=T_LOCATION_id_location) join T_EQUIPMENT on(id_equipment=T_EQUIPMENT_id_equipment) where id_powerMngmt="+idPowerMngmt
	myRecordSet.execute(SQL)
	row=myRecordSet.fetchone()
	
	SQL="select *,T_EQUIP_TYPE.name as type,T_EQUIPMENT.name as benchName from T_EQUIPMENT join T_LOCATION on(T_LOCATION_id_location=id_location) join T_EQUIP_TYPE on(id_type=T_EQUIP_TYPE_id_type) where site='"+row['site']+"' and room='"+row['room']+"' and rack='"+row['rack']+"' order by pos"
	myRecordSet.execute(SQL)
	bench=[]
	for benches in myRecordSet:
		bench.append({'bench':benches["benchName"],'owner':benches['owner'],'type':benches['type']})
		
	SQL="SELECT * FROM auth_user where first_name is not null order by username"
	myRecordSet.execute(SQL)
	users=''
	for myUsers in myRecordSet:
		selectStr=""
		if myUsers['username'].upper() == row["rackOwner"].upper(): selectStr="selected"
		users+='<option value='+myUsers['username']+' '+selectStr+'>'+myUsers['username'].upper()+'</option>'
					
	context_dict={'login':request.session['login'],
			'rackName':row['rack'],
			'idPowerMngmt':idPowerMngmt,
			'name':str(row["name"]),
			'pin':str(row["pin"]),
			'ip':SQL,
			'owner':row["rackOwner"],
			'users':users,
			'bench':bench
		}
	#location=row["T_LOCATION_id_location"]
	#SQL="select * from T_EQUIPMENT where T_LOCATION_id_location="+location
	#myRecordSet.execute(SQL)
	#row=myRecordSet.fetchone()

	print('Change Rack Owner')
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
			'interval':str(int(row["interval"])/1440)
		})

	context_dict={'login':request.session['login'],
		'scheduled':scheduled,
		'idPowerMngmt':idPowerMngmt
	}
	print('Create Scheduled Task')
	return HttpResponse(json.dumps(context_dict),content_type="application/json")

def setRackStatus(request):

	import xmlrpc.client
	import json
	import mysql.connector
	
	context = RequestContext(request)
	rackList=request.POST.get('rackList').split('#')
	modifier=request.POST.get('modifier')
	newStatus=request.POST.get('newStatus')
	rackStatus=request.POST.get('rackStatus')
	print('Change '+rackStatus+' Status on '+str(rackList))
	
	dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'],port=settings.DATABASES['default']['PORT'])
	myRecordSet = dbConnection.cursor(dictionary=True)

	if rackStatus == "power_status":
		for myRack in rackList:
			SQL="SELECT ip,pin FROM T_POWER_MNGMT join T_NET using(T_EQUIPMENT_id_equipment) join (select * from (select * from T_POWER_STATUS order by last_change desc) as yourTable group by T_POWER_MNGMT_id_powerMngmt) as myTable on(T_POWER_MNGMT_id_powerMngmt=id_powerMngmt) where manual_status=0 and id_powerMngmt="+myRack
			myRecordSet.execute(SQL)
			for row in myRecordSet:
	
				proxy = xmlrpc.client.ServerProxy("http://"+row['ip']+":8080/")
				switchReport = proxy.setGPIO([{'gpio':row['pin'],'status':newStatus,'idPowerMngmt':myRack,'modifier':modifier}])

	if rackStatus == "manual_status":
		for myRack in rackList:
			
			newStatusStr="Manual"
			if newStatus == "1": newStatusStr="Auto"
			
			SQL="insert into T_POWER_STATUS (select "+myRack+",power_status,null,'"+modifier+"','Change Rack Mode to "+newStatusStr+"',"+newStatus+" from T_POWER_STATUS where T_POWER_MNGMT_id_powerMngmt="+myRack+" order by last_change desc limit 1)"
			
			myRecordSet.execute(SQL)
			dbConnection.commit()

	context_dict={}
	print('Change '+rackStatus+' Status on '+str(rackList))
	return HttpResponse(json.dumps(context_dict),content_type="application/json")
	#return {'switchReport':switchReport}

