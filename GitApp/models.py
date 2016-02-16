# coding=utf-8
from django.db import models
from django.db import connection
from django.utils.translation import ugettext as _
from taws.models import *
from django.conf import settings

# Create your models here.


testReport=''
testNotFound = False

class Gitlab_Webhook(models.Model):
    ''' Model for webhook of gitlab

    '''
    repo_name = models.CharField(
        verbose_name = _(u'repository name'),
        help_text = _(u' '),
        max_length = 255
    )
    repo_url = models.CharField(
        verbose_name = _(u'repository url'),
        help_text = _(u' '),
        max_length = 255
    )
    object_kind = models.CharField(
        verbose_name = _(u'object_kind value'),
        help_text = _(u'push, tag_push, issue, note'),
        max_length = 255
    )
    project_id = models.IntegerField(
        verbose_name = _(u'project_id value'),
        help_text = _(u'Your project id in gitlab'),
        default = 0
    )
    http_x_gitlab_event = models.CharField(
        verbose_name = _(u'X-Gitlab-Event in request header'),
        help_text = _(u'Push Hook, Tag Push Hook, Issue Hook, Note Hook'),
        max_length = 255
    )

    def __unicode__(self):
        return u'%s %s' % (self.repo_name, self.object_kind)
			
			
def addTestToDB(testDict):
	""" add test reference to KATE DB
		:param: testDict, Dictionary containing all test info to be stored into MySQL DB
		
		testDict['fullPath']:  tetspath reference related to GIT Repo i.e.'TestCases/1850TSS320/DATA/DATAQOS/pippo.py'
		
		testDict['tag']: test GIT Label i.e. '7.2@01'
		testDict['diff']:test difference against previous label, A|D|M|R i.e. 'A'
		testDict['dependency']:test dependencies 
		testDict['author']:test LDAP Author reference i.e.'COLOMX'
		testDict['lab']:test lab reference i.e.'SVT'
		testDict['description']:test summary
		testDict['topology']:test topolgy reference
		testDict['run_section']:test sections available i.e. '11111'
		testDict['tps']:tst TPS coverage (JIRA TASK) i.e.'Domain1__1.2.3*DomainX__4.5.6'
	
	"""
	import mysql.connector

	#dbConnection=mysql.connector.connect(user=settings.DATABASES['default']['USER'],password=settings.DATABASES['default']['PASSWORD'],host=settings.DATABASES['default']['HOST'],database=settings.DATABASES['default']['NAME'])
	#myRecordSet=dbConnection.cursor(dictionary=True)
	myRecordSet = connection.cursor()
	global testReport
	global testNotFound
	testReport = ''
	testNotFound = False
	
	try:
		
		def add_testCase(filename):
			"""add testcase to  T_TEST DB Table
			:params:
				filename: fullpath testcase name
			:return: None|int
			"""
			global testReport
			global testNotFound
			try:
				#------------------------Adding Test ID---------------------------------
				#print('\nAdding Test ID into T_TEST Table...')
				myRecordSet.execute("SELECT count(test_name) as myCount from T_TEST WHERE test_name='"+filename+"'")
				row=myRecordSet.fetchone()
				testNotFound=False
				if row[0]==0:
					testNotFound=True
					print('\n\tTest %s Not found into T_TEST table,adding...'%filename)
					testReport+='Test Name '+testDict['fullPath']+' not found in T_TEST adding...'
					myRecordSet.execute("INSERT INTO T_TEST (test_name,test_description) VALUES('"+filename+"','')")
					connection.commit()
					testReport+='DONE\n'
				myRecordSet.execute("SELECT test_id from T_TEST where test_name='"+filename+"'")
				row=myRecordSet.fetchone()
				test_id = row[0]
				print('\n\t%s TestID from T_TEST = %s'% (filename,str(test_id)))
				testReport+='%s Test ID = %s\n'%(filename,str(test_id))
				return test_id
			except Exception as eee:
				print('\nERROR Adding testID into T_TEST Table')
				print(str(eee))
				return None
		
		def rollback_test(test_id):
			""" deleting test id from KATE DB T_TEST
			:paramS:
				testid: int test ID to be deleted
			return: true|false
			"""
			global testReport
			global testNotFound
			if testNotFound==True:
				testReport+='Deleting Test ID '+str(test_id)+'...'
				myRecordSet.execute("DELETE FROM T_TEST WHERE test_id="+str(test_id))
				connection.commit()
				testReport+='DONE\n'
				print('\tDeleting test Id: %s from T_TEST...'%str(test_id))
				return True
			return False

		def add_testCase_revision(testId,tag,dependency,author,lab,description,topology,run_section):
			"""add testcase to  T_TEST_REVS DB Table
			:params:
				testId:T_TEST Table test identifier
				tag: GIT TAG revision
				dependency: test case dependencies
				author: KATE DB author
				lab: Lab reference
				description: test description
				topology: test topology identifier (T_TOPOLOGY)
				run_section: test sections mask
				
			:return: None|int
			"""
			global testReport
			try:
				myRecordSet.execute("INSERT INTO T_TEST_REVS (T_TEST_test_id,revision,duration,metric,assignment,dependency,author,release_date,lab,description,topology,run_section,last_update) VALUES("+str(testId)+",'"+tag+"',0,0,'','"+dependency+"','"+author+"',CURRENT_TIMESTAMP,'"+lab+"','"+description+"','"+topology+"','"+run_section+"',CURRENT_TIMESTAMP)")
				connection.commit()
			except Exception as err:
				testReport+='***ERROR*** Unable to add TEST REVS entry!!!\n'
				testReport+=str(err.args)
				testReport+='Rolling Back...\n'
				print('\t***ERROR*** Unable to add TEST REVS entry!!\n%s\n%s!'%(str(err),str(err.args)))
				rollback_test(testId)
				return None

			myRecordSet.execute("SELECT MAX(id_testRev) as id_testRev from T_TEST_REVS")
			row=myRecordSet.fetchone()
			id_testRev=row[0]
			testReport+='TEST ID %s REV ID = %s\n'%(str(testId),str(id_testRev))
			print('\tTest Id: %s Added to T_TEST_REVS Table with ID: %s'%(str(testId),str(id_testRev)))
			return id_testRev
				
		def rollback_test_revision(testRevId):
			""" deleting test revision reference from KATE DB T_TEST_REVS
			:paramS:
				testRevid: int test ID to be deleted
			return: true|false
			"""
			global testReport
			print('\tDeleting test revision Id: %s from T_TPS...'%str(testRevId))
			testReport+='Deleting Test Rev ID '+str(testRevId)+'...'
			myRecordSet.execute("DELETE FROM T_TEST_REVS WHERE test_id="+str(testRevId))
			connection.commit()
			testReport+='DONE\n'
			return True
		
		def rollback_test_tps(testRevId):
			""" deleting test revision reference from KATE DB T_TPS
			:paramS:
				testRevid: int test ID to be deleted
			return: true|false
			"""
			global testReport
			testReport+='Deleting TPS for Test Rev ID '+str(id_testRev)+'...'
			myRecordSet.execute("DELETE FROM T_TPS WHERE T_TEST_REVS_id_TestRev="+str(testRevId))
			connection.commit()
			testReport+='DONE\n'
			print('\tDeleting test revision Id: %s from T_TPS...'%str(testRevId))
			return True
		
		def get_product_id(productName):
			""" get product id from KATE DB
			:params:
				productName:str prduct name identification (i.e. 1850TSS320)
			
			:return: None|int
			"""
			global testReport
			
			try:
				#------------------------Checking Product ID---------------------------------
				myRecordSet.execute("SELECT count(id_prod) as myCount from T_PROD WHERE product='"+productName+"'")
				row=myRecordSet.fetchone()
				if row[0]==0:
					testReport=+'***ERROR*** product '+productName+' not found in DB!!!\n'
					testReport=+'Rolling Back...\n'
					print('\t***ERROR*** Product %s not found in DB!!!. Rolling back...'%productName)
					return None
				myRecordSet.execute("SELECT id_prod from T_PROD where product='"+productName+"'")
				row=myRecordSet.fetchone()
				id_prod = row[0]
				testReport+='Product %s Product ID = %s\n'%(productName,str(id_prod))
				print('\tSelected product Id from T_PROD for %s : %s'%(productName,str(id_prod)))
				return id_prod
			except Exception as eee:
				print('ERROR Getting Product ID from T_PROD')
				print(str(eee))
				return None
	
		def get_scope_id(scopeName):
			""" get scope id from KATE DB
			:params:
				scopeName:str scope name identification (i.e. DATA)
			
			:return: None|int
			"""
			global testReport
			try:
				#------------------------Checking Scope ID---------------------------------
				myRecordSet.execute("SELECT count(id_scope) as myCount from T_SCOPE WHERE description='"+scopeName+"'")
				row=myRecordSet.fetchone()
				if row[0]==0:
					testReport+='***ERROR*** SCOPE '+scopeName+' not found in DB!!!\n'
					testReport+='Rolling Back...\n'
					print('\t***ERROR*** SCOPE %s not found in DB!!!. Rolling back...'%scopeName)
					return None
				myRecordSet.execute("SELECT id_scope from T_SCOPE where description='"+tempFields[2]+"'")
				row=myRecordSet.fetchone()
				id_scope = row[0]
				testReport+='Scope %s Scope ID = %s\n'%(scopeName,str(id_scope))
				print('\tSelected scope Id from T_SCOPE for %s : %s'%(scopeName,str(id_scope)))
				return id_scope
			except Exception as eee:
				print('ERROR Getting Scope ID from T_SCOPE')
				print(str(eee))
				return None

		def get_area_id(areaName):
			""" get area id from KATE DB
			:params:
				scopeName:str area name identification (i.e. EOAM)
			
			:return: None|int
			"""
			global testReport
			try:
				#------------------------Checking Area ID---------------------------------
				myRecordSet.execute("SELECT count(id_area) as myCount from T_AREA WHERE area_name='"+areaName+"'")
				row=myRecordSet.fetchone()
				if row[0]==0:
					testReport+='***ERROR*** AREA '+areaName+' not found in DB!!!\n'
					testReport+='Rolling Back...\n'
					print('\t***ERROR*** AREA %s not found in DB!!!. Rolling back...'%areaName)
					return None
				myRecordSet.execute("SELECT id_area from T_AREA where area_name='"+areaName+"'")
				row=myRecordSet.fetchone()
				id_area = row[0]
				testReport+='Area %s Area ID = %s\n'%(areaName,str(id_area))
				print('\tSelected Area Id from T_AREA for %s : %s'%(areaName,str(id_area)))
				return id_area
			except Exception as eee:
				print('ERROR Getting Area ID from T_AREA')
				print(str(eee))
				return None

		def get_sw_rel_id(releaseName):
			""" get software release id from KATE DB
			:params:
				releaseName:str sw release identification (i.e. 7.10.10)
			
			:return: None|int
			"""
			global testReport
			try:
				#------------------------Checking SW Release ID---------------------------------
				myRecordSet.execute("SELECT count(id_sw_rel) as myCount from T_SW_REL WHERE sw_rel_name='"+releaseName+"'")
				row=myRecordSet.fetchone()
				if row[0]==0:
					testReport+='***ERROR*** RELEASE '+releaseName+' not found in DB!!!\n'
					testReport+='Rolling Back...\n'
					print('\t***ERROR*** RELEASE %s not found in DB!!!. Rolling back...'%releaseName)
					return None
				myRecordSet.execute("SELECT id_sw_rel from T_SW_REL where sw_rel_name='"+releaseName+"'")
				row=myRecordSet.fetchone()
				id_sw_rel=row[0]
				testReport+='Release %s Release ID = %s\n'%(releaseName,str(id_sw_rel))
				print('\tSelected Release Id from T_SW_REL for %s : %s'%(releaseName,str(id_sw_rel)))
				return id_sw_rel
			except Exception as eee:
				print('ERROR Getting Release ID from T_SW_REL')
				print(str(eee))
				return None

		def get_domain_id(prodId,scopeId,areaId,domainName,swRelId):
			""" get domain id from KATE DB
			:params:
				prodId: 	id_prod identfication from T_PROD DB Table
				scopeId:	id_scope identification from T_SCOPE DB Table
				areaId:		id_area identification from T_AREA DB Table
				domainName:	str domain name identificatio (i.e. EOAM)
				swRelId:	id_sw_rel dentification fro T_SW_REL DB Table
			
			:return: None|int
			"""
			global testReport
			try:
				#------------------------Getting Domain ID---------------------------------
				myRecordSet.execute("SELECT count(id_domain) as myCount from T_DOMAIN WHERE T_SW_REL_id_sw_rel="+str(swRelId)+" and T_PROD_id_prod="+str(prodId)+" and T_AREA_id_area="+str(areaId)+" and T_SCOPE_id_scope="+str(scopeId))
				row=myRecordSet.fetchone()
				if row[0]==0:
					testReport+='***ERROR*** DOMAIN '+domainName+' not found in DB!!!\n'
					testReport+='Rolling Back...\n'
					print('\t***ERROR*** DOMAIN %s not found in DB!!!. Rolling back...'%domainName)
					return None
				myRecordSet.execute("SELECT id_domain from T_DOMAIN WHERE T_SW_REL_id_sw_rel="+str(swRelId)+" and T_PROD_id_prod="+str(prodId)+" and T_AREA_id_area="+str(areaId)+" and T_SCOPE_id_scope="+str(scopeId))
				row=myRecordSet.fetchone()
				id_domain=row[0]
				testReport+='ReleaseId %s Domain %s .Domain ID = %s\n'%(str(swRelId),domainName,str(id_domain))
				print('\tSelected Domain Id from T_DOMAIN for Domain %s in SW_REL ID %s : %s'%(domainName,str(swRelId),str(id_domain)))
				return id_domain
			except Exception as eee:
				print('ERROR Getting Domain ID from T_DOMAIN')
				print(str(eee))
				return None
			
			
			
		tempFields=testDict['fullPath'].split('/')
		#fullPath format : ./TestCases/ProductName/ScopeName/AreaName/TestName.py
		
		#getting all required values from DB, exiting in case of trouble...
		id_prod=get_product_id(tempFields[1])
		if id_prod is None: return testReport
		id_scope=get_scope_id(tempFields[2])
		if id_scope is None: return testReport
		id_area=get_area_id(tempFields[3])
		if id_area is None: return testReport
		
		tempRelease=testDict['tag'].split(settings.TAG_SPLIT)[0]
		
		id_sw_rel=get_sw_rel_id(tempRelease)
		if id_sw_rel is None:return testReport
		
		revision=testDict['tag'].strip()
		
		id_domain = get_domain_id(id_prod,id_scope,id_area,tempFields[3],id_sw_rel)
		if id_domain is None:return testReport
		
		#at this point all required fields are correctly collected from DB
		#trying to push test case into DB
		# 3 tables must be updated: T_TEST, T_TEST_REVS, T_TPS
		
		#add test to T_TEST Table
		test_id=add_testCase(testDict['fullPath'])
		if test_id is None:return testReport
		
		#add test to T_TEST_REVS Table
		id_testRev =add_testCase_revision(test_id,testDict['tag'],testDict['dependency'],testDict['author'].strip(),testDict['lab'].strip(),testDict['description'],testDict['topology'].strip(),testDict['run_section'].strip())
		if id_testRev is None:return testReport
		
		#adding TPS references to T_TPS
		testReport+=('\nTPS References:\n')
		for myTps in testDict['tps'].split('*'):
			myTps=myTps.strip()
			if myTps != "":
				tpslist=myTps.split(settings.TPS_SPLIT)
				#tpslist[0] contains the Area reference
				#tpslist[1] contains the tps id
				#getting areaid for tps area reference
				tpsAreaId=get_area_id(tpslist[0])
				if tpsAreaId is None:
					rollback_test_tps(id_testRev)
					rollback_test_revision(id_testRev)
					rollback_test(test_id)
					return testReport
				tpsDomainId=get_domain_id(id_prod,id_scope,tpsAreaId,tpslist[0],id_sw_rel)
				
				if tpsDomainId is None:
					rollback_test_tps(id_testRev)
					rollback_test_revision(id_testRev)
					rollback_test(test_id)
					return testReport
				
				print('\tAdding TPS %s %s area %s domain %s to T_TPS table'%(tpslist[0],tpslist[1],tpsAreaId,tpsDomainId))
				
				try:
					myRecordSet.execute("INSERT INTO T_TPS (tps_reference,T_DOMAIN_id_domain,T_TEST_REVS_id_TestRev) VALUES('"+str(tpslist[1])+"',"+str(tpsDomainId)+","+str(id_testRev)+")")
					connection.commit()
					
				except Exception as err:
					
					testReport+='***ERROR*** Unable to add T_TPS entry!!!\n'
					testReport+=str(err.args)
					testReport+='Rolling Back...\n'
					print('\t***ERROR*** Unable to add T_TPS entry!!\n%s\n%s!'%(str(err),str(err.args)))
					
					rollback_test_tps(id_testRev)
					rollback_test_revision(id_testRev)
					rollback_test(test_id)
					return testReport
				
		print('\nEverithing OK\n')
		return testReport
	
	except Exception as xxx:
			print('ERROR on addTestToDB')
			print(str(xxx))
			return None
	
