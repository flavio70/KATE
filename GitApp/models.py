# coding=utf-8
from django.db import models
from django.db import connection
from django.utils.translation import ugettext as _
from taws.models import *

# Create your models here.

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
	testReport=''
	try:
		#------------------------Adding Test ID---------------------------------
		#print('\nAdding Test ID into T_TEST Table...')
		myRecordSet.execute("SELECT count(test_name) as myCount from T_TEST WHERE test_name='"+testDict['fullPath']+"'")
		row=myRecordSet.fetchone()
		testNotFound=False
		if row[0]==0:
			testNotFound=True
			print('\n\tTest %s Not found into T_TEST table,adding...'%testDict['fullPath'])
			testReport+='Test Name '+testDict['fullPath']+' not found in T_TEST adding...'
			myRecordSet.execute("INSERT INTO T_TEST (test_name,test_description) VALUES('"+testDict['fullPath']+"','')")
			connection.commit()
			testReport+='DONE\n'
		myRecordSet.execute("SELECT test_id from T_TEST where test_name='"+testDict['fullPath']+"'")
		row=myRecordSet.fetchone()
		test_id = row[0]
		print('\n\t%s TestID from T_TEST = %s'% (testDict['fullPath'],str(test_id)))
		testReport+='Test ID = '+str(test_id)+'\n'
		tempFields=testDict['fullPath'].split('/')
		#print('...Done\n')
	except Exception as eee:
		print('\nERROR Adding testID into T_TEST Table')
		print(str(eee))
		return testReport
	
	try:
		#------------------------Checking Product ID---------------------------------
		myRecordSet.execute("SELECT count(id_prod) as myCount from T_PROD WHERE product='"+tempFields[1]+"'")
		row=myRecordSet.fetchone()
		if row[0]==0:
			testReport=+'***ERROR*** product '+tempFields[1]+' not found in DB!!!\n'
			testReport=+'Rolling Back...\n'
			print('\t***ERROR*** Product %s not found in DB!!!. Rolling back...'%tempFields[1])
			if testNotFound==True:
				testReport+='Deleting Test ID '+str(test_id)+'...'
				myRecordSet.execute("DELETE FROM T_TEST WHERE test_id="+str(test_id))
				connection.commit()
				testReport+='DONE\n'
				print('\tDeleting test Id: %s from T_TEST...'%str(test_id))
			return testReport
		myRecordSet.execute("SELECT id_prod from T_PROD where product='"+tempFields[1]+"'")
		row=myRecordSet.fetchone()
		id_prod = row[0]
		testReport+='Product ID = '+str(id_prod)+'\n'
		print('\tSelected product Id from T_PROD for %s : %s'%(tempFields[1],str(id_prod)))
	except Exception as eee:
		print('ERROR Getting Product ID from T_PROD')
		print(str(eee))
		return testReport
	
	try:
		#------------------------Checking Scope ID---------------------------------
		myRecordSet.execute("SELECT count(id_scope) as myCount from T_SCOPE WHERE description='"+tempFields[2]+"'")
		row=myRecordSet.fetchone()
		if row[0]==0:
			testReport+='***ERROR*** SCOPE '+tempFields[2]+' not found in DB!!!\n'
			testReport+='Rolling Back...\n'
			print('\t***ERROR*** SCOPE %s not found in DB!!!. Rolling back...'%tempFields[2])
			if testNotFound==True:
				testReport=+'Deleting Test ID '+str(test_id)+'...'
				myRecordSet.execute("DELETE FROM T_TEST WHERE test_id="+str(test_id))
				connection.commit()
				testReport+='DONE\n'
				print('\tDeleting test Id: %s from T_TEST...'%str(test_id))
			return testReport
		myRecordSet.execute("SELECT id_scope from T_SCOPE where description='"+tempFields[2]+"'")
		row=myRecordSet.fetchone()
		id_scope = row[0]
		testReport+='SCOPE ID = '+str(id_scope)+'\n'
		print('\tSelected scope Id from T_SCOPE for %s : %s'%(tempFields[2],str(id_scope)))
	except Exception as eee:
		print('ERROR Getting Scope ID from T_SCOPE')
		print(str(eee))
		return testReport
	
	try:
		#------------------------Checking Area ID---------------------------------
		myRecordSet.execute("SELECT count(id_area) as myCount from T_AREA WHERE area_name='"+tempFields[3]+"'")
		row=myRecordSet.fetchone()
		if row[0]==0:
			testReport+='***ERROR*** AREA '+tempFields[3]+' not found in DB!!!\n'
			testReport+='Rolling Back...\n'
			print('\t***ERROR*** AREA %s not found in DB!!!. Rolling back...'%tempFields[3])
			if testNotFound==True:
				testReport=+'Deleting Test ID '+str(test_id)+'...'
				myRecordSet.execute("DELETE FROM T_TEST WHERE test_id="+str(test_id))
				connection.commit()
				testReport+='DONE\n'
				print('\tDeleting test Id: %s from T_TEST...'%str(test_id))
			return testReport
		myRecordSet.execute("SELECT id_area from T_AREA where area_name='"+tempFields[3]+"'")
		row=myRecordSet.fetchone()
		id_area = row[0]
		testReport+='Area ID = '+str(id_area)+'\n'
		print('\tSelected Area Id from T_AREA for %s : %s'%(tempFields[3],str(id_area)))
	except Exception as eee:
		print('ERROR Getting Area ID from T_AREA')
		print(str(eee))
		return testReport
	
	
	try:
		#------------------------Checking Release ID---------------------------------
		tempRelease=testDict['tag'].split('@')
		myRecordSet.execute("SELECT count(id_sw_rel) as myCount from T_SW_REL WHERE sw_rel_name='"+tempRelease[0]+"'")
		row=myRecordSet.fetchone()
		if row[0]==0:
			testReport+='***ERROR*** RELEASE '+tempRelease[0]+' not found in DB!!!\n'
			testReport+='Rolling Back...\n'
			print('\t***ERROR*** RELEASE %s not found in DB!!!. Rolling back...'%tempRelease[0])
			if testNotFound==True:
				testReport+='Deleting Test ID '+str(test_id)+'...'
				myRecordSet.execute("DELETE FROM T_TEST WHERE test_id="+str(test_id))
				connection.commit()
				testReport+='DONE\n'
				print('\tDeleting test Id: %s from T_TEST...'%str(test_id))
			return testReport
		myRecordSet.execute("SELECT id_sw_rel from T_SW_REL where sw_rel_name='"+tempRelease[0]+"'")
		row=myRecordSet.fetchone()
		id_sw_rel=row[0]
		revision=testDict['tag'].strip()
		testReport+='Release ID = '+str(id_sw_rel)+'\n'
		print('\tSelected Release Id from T_SW_REL for %s : %s'%(tempRelease[0],str(id_sw_rel)))
	except Exception as eee:
		print('ERROR Getting Release ID from T_SW_REL')
		print(str(eee))
		return testReport
	
	
	
	try:
		#------------------------Getting Domain ID---------------------------------
		myRecordSet.execute("SELECT count(id_domain) as myCount from T_DOMAIN WHERE T_SW_REL_id_sw_rel="+str(id_sw_rel)+" and T_PROD_id_prod="+str(id_prod)+" and T_AREA_id_area="+str(id_area)+" and T_SCOPE_id_scope="+str(id_scope))
		row=myRecordSet.fetchone()
		if row[0]==0:
			testReport+='***ERROR*** DOMAIN '+tempFields[3]+' not found in DB!!!\n'
			testReport+='Rolling Back...\n'
			print('\t***ERROR*** DOMAIN %s not found in DB!!!. Rolling back...'%tempFields[3])
			if testNotFound==True:
				testReport+='Deleting Test ID '+str(test_id)+'...'
				myRecordSet.execute("DELETE FROM T_TEST WHERE test_id="+str(test_id))
				connection.commit()
				testReport+='DONE\n'
				print('\tDeleting test Id: %s from T_TEST...'%str(test_id))
			return testReport
		myRecordSet.execute("SELECT id_domain from T_DOMAIN WHERE T_SW_REL_id_sw_rel="+str(id_sw_rel)+" and T_PROD_id_prod="+str(id_prod)+" and T_AREA_id_area="+str(id_area)+" and T_SCOPE_id_scope="+str(id_scope))
		row=myRecordSet.fetchone()
		id_domain=row[0]
		testReport+='Domain ID = '+str(id_domain)+'\n'
		print('\tSelected Domain Id from T_DOMAIN for %s : %s'%(tempRelease[0],str(id_domain)))
	except Exception as eee:
		print('ERROR Getting Domain ID from T_DOMAIN')
		print(str(eee))
		return testReport
	
	
	
	#------------------------Adding Entry to T_TEST_REVS---------------------------------
	try:
		myRecordSet.execute("INSERT INTO T_TEST_REVS (T_TEST_test_id,revision,duration,metric,assignment,dependency,author,release_date,lab,description,topology,run_section,last_update) VALUES("+str(test_id)+",'"+testDict['tag']+"',0,0,'','"+testDict['dependency']+"','"+testDict['author']+"',CURRENT_TIMESTAMP,'"+testDict['lab']+"','"+testDict['description']+"','"+testDict['topology']+"','"+testDict['run_section']+"',CURRENT_TIMESTAMP)")
		connection.commit()
	except Exception as err:
		testReport+='***ERROR*** Unable to add TEST REVS entry!!!\n'
		testReport+=str(err.args)
		testReport+='Rolling Back...\n'
		print('\t***ERROR*** Unable to add TEST REVS entry!!\n%s\n%s!'%(str(err),str(err.args)))
		if testNotFound==True:
			testReport+='Deleting Test ID '+str(test_id)+'...'
			myRecordSet.execute("DELETE FROM T_TEST WHERE test_id="+str(test_id))
			connection.commit()
			testReport+='DONE\n'
			print('\tDeleting test Id: %s from T_TEST...'%str(test_id))
		return testReport
	myRecordSet.execute("SELECT MAX(id_testRev) as id_testRev from T_TEST_REVS")
	row=myRecordSet.fetchone()
	id_testRev=row[0]
	testReport+='TEST REV ID = '+str(id_testRev)+'\n'
	print('\tTest Id: %s Added to T_TEST_REVS Table with ID: %s'%(str(test_id),str(id_testRev)))
	
	
	#------------------------Adding Entry to T_TPS---------------------------------
	for myTps in testDict['tps'].split('*'):
		myTps=myTps.strip()
		if myTps != "":
			tpslist=myTps.split('__')
			#tpslist[0] contains the domain reference
			#tpslist[1] contains the tps id
			try:
				myRecordSet.execute("INSERT INTO T_TPS (tps_reference,T_DOMAIN_id_domain,T_TEST_REVS_id_TestRev) VALUES('"+myTps+"',"+str(id_domain)+","+str(id_testRev)+")")
				#myRecordSet.execute("INSERT INTO T_TPS (tps_reference,T_DOMAIN_id_domain,T_TEST_REVS_id_TestRev) VALUES('"+str(tpslist[1])+"',"+str(id_domain)+","+str(id_testRev)+")")
				connection.commit()
			except Exception as err:
				testReport+='***ERROR*** Unable to add T_TPS entry!!!\n'
				testReport+='Rolling Back...\n'
				print('\t***ERROR*** Unable to add %s into T_TPS entry!!\n%s\n%s!'%(myTps,str(err),str(err.args)))
				if testNotFound==True:
					testReport+='Deleting TPS for Test Rev ID '+str(id_testRev)+'...'
					myRecordSet.execute("DELETE FROM T_TPS WHERE T_TEST_REVS_id_TestRev="+str(id_testRev))
					connection.commit()
					testReport+='DONE\n'
					print('\tDeleting test revision Id: %s from T_TPS...'%str(id_testRev))
					testReport+='Deleting Test Rev ID '+str(id_testRev)+'...'
					myRecordSet.execute("DELETE FROM T_TEST_REVS WHERE test_id="+str(id_testRev))
					connection.commit()
					testReport+='DONE\n'
					print('\tDeleting test Rev Id: %s from T_TEST_REVS...'%str(id_testRev))
					testReport+='Deleting Test ID '+str(test_id)+'...'
					myRecordSet.execute("DELETE FROM T_TEST WHERE test_id="+str(test_id))
					connection.commit()
					testReport+='DONE\n'
					print('\tDeleting test Id: %s from T_TEST...'%str(test_id))
				return testReport
			myRecordSet.execute("SELECT MAX(id_tps) as id_tps from T_TPS")
			row=myRecordSet.fetchone()
			id_tps=row[0]
			testReport+='TPS ID ADDED = '+str(id_tps)+'\n'
			print('\tTPS %s Added to T_TPS Table with ID: %s'%(myTps,str(id_tps)))
	
	return testReport


