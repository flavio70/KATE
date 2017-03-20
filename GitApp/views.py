from django.shortcuts import render
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from django.contrib import auth
from django.views.decorators.csrf import requires_csrf_token
from django.http import JsonResponse
from django.conf import settings

from GitApp.models import *
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import re

import logging,subprocess

logger = logging.getLogger(__name__)

# Create your views here.


def get_testinfo(testpath):
	""" 
		get metadata from testcase
		:param testpath: Full testcase path
		
		:return: Dictionary containing availables info fields
		
		Description,Topology,Dependency,Lab,TPS,RUnSections,Author
	"""
	import ast,re
	res=None
	#testFullName = os.path.abspath(testpath).decode('ascii')
	#logger.debug('TestFullPath: %s'% testpath)
	try:
		M = ast.parse(testpath)
		doc=ast.get_docstring(M)
			
		if doc is not None:
			docre = re.findall(':field (.*)?',doc,re.MULTILINE)
			docre=[i.split(':') for i in docre]
			res={}
			res['Description']=''
			res['TPS']=''
			for elem in docre:
				if (elem[0] == "Description"):
					#logger.debug('Description %s'%elem[1])
					res['Description'] =  res['Description']  + re.sub('["\']+','',elem[1]) + '\n'
				elif (elem[0] == "TPS"):
					res['TPS'] =  res['TPS']  + re.sub('["\']+','',elem[1]) + '*'
				else:
					res[elem[0]]=re.sub('["\']+','',elem[1])
					#logger.debug( '%s %s' %(elem[0],elem[1]))
	except Exception as xxx:
		logger.debug('ERROR on get_testinfo')
		logger.debug(str(xxx))
	
	return res

def addTestListToDB(testList):
	"""
	#testAry=[{'fullPath':'TestCases/1850TSS320/DATA/DATAQOS/pippo.py','tag':'7.2@01','diff':'A','dependency':'dep1','author':'COLOMX','lab':'SVT','description':'descr1','topology':'topo1','run_section':'11111','tps':'1.2.3*4.5.6'}]
"""
	listReport=''
	liststatus = True
	try:
		for myTest in testList:
			if myTest['diff']=='A'or myTest['diff']=='M':
				res=addTestToDB(myTest)
				listReport+=res['data']
				if not res['status']:liststatus = False
			#logger.debug(testList)
		return {'status':liststatus,'data':listReport}
	except Exception as xxx:
		logger.debug('ERROR on addTestListToDB')
		logger.debug(str(xxx))


def push_hook(data):
	from git import Repo, RemoteProgress
	import os

	class MyProgressPrinter(RemoteProgress):
		
		def update(self, op_code, cur_count, max_count=None, message=''):
			logger.debug('%s , %s, %s, %s, %s'%(op_code, cur_count, max_count, cur_count / (max_count or 100.0), message or "NO MESSAGE"))

	logger.debug('Calling push event management...')
	logger.debug(data)
	repository = data.get('repository')
	repository_name = repository.get('name')
	
	logger.debug('\nEvent triggered by pushing on repository %s\n'%repository_name)
	if repository_name == settings.GIT['USERLIBS_REPO_NAME']:
		repository_path = settings.GIT['USERLIBS_REPO_NAME_PATH']
		logger.debug('\nUpdating %s%s GIT repository...'%(repository_path,repository_name))
		local_repo_path = '%s%s'%(repository_path,repository_name)

		#creating Repo object instance
		myRepo=Repo(local_repo_path)
		git=myRepo.git


		#getting origin
		origin = myRepo.remotes.origin
		if not origin.exists(): return {'status':False,'data': "remote origin not found for GIT repository " + local_repo_path + " Please check your GIT Repository configuration"}
		# checkout on master
		myRepo.head.ref=myRepo.heads.master
		# try to fetch from origin
		logger.debug('Fetching from remote origin...\n')
	
		try:
			for pull_info in origin.pull(progress=MyProgressPrinter()):
				logger.debug("Updated %s to %s " % (pull_info.ref, pull_info.commit))

			logger.debug('\nRepository Updated\n')
		
		except Exception as ex:
			template = "An exception of type {0} occured. Arguments:\n{1!r}"
			message = template.format(type(ex).__name__, ex.args)
			logger.debug(message)
			logger.debug('\n Ops! fetching problems. Going haead...\n')
			return {'status':False,'data':'Git Fetching problems'}



		return {'status':True,'data':'NoData'}
	else:
		return {'status':False,'data':'2B Implemented'}

def tag_push_hook(data):
	from git import Repo, RemoteProgress
	import os

	class MyProgressPrinter(RemoteProgress):
		def update(self, op_code, cur_count, max_count=None, message=''):
			logger.debug('%s , %s, %s, %s, %s'%(op_code, cur_count, max_count, cur_count / (max_count or 100.0), message or "NO MESSAGE"))
	# end
	
	logger.debug('Calling Tag push event management...\n')
	logger.debug(data)
	repository = data.get('repository')
	repository_name = repository.get('name')
	repository_url = repository.get('url')
	after = data.get('after')
	before = data.get('before')
	checkout_sha = data.get('checkout_sha')
	ref = data.get('ref')
	reflist = ref.split('/')
	currentTag = reflist[len(reflist)-1]
	result=[]

	logger.debug('\ncheckout sha: %s\n' % checkout_sha)
	logger.debug('Current TAG value: %s \n' % currentTag)

	if not checkout_sha:return {'status':False,'data':"Are we deleting tag?... Nothing to do. Stopping execution..."}

	logger.debug('\nchecking current TAG: %s Format...' % currentTag)
	'''
	TAG FORMAT Expected coming from branch xxxxx: XXXXX@abcd
	'''
	tagSplit = currentTag.split(settings.TAG_SPLIT)
	if (len(tagSplit) != 2): return {'status':False,'data':"current TAG " + currentTag + " is Not in the right format, exiting ..."}
	
	tagBranchu=tagSplit[0]
	tagBranchl=tagBranchu.lower()
	tagVal=tagSplit[1]
	logger.debug('\nOK TAG is in the correct format: branch %s Tag Separator %s  tag version %s \n' % (tagBranchl,settings.TAG_SPLIT,tagVal))
	
	
	local_repo_dir=settings.BASE_DIR + settings.GIT_REPO_PATH
	local_repo_path= settings.BASE_DIR + settings.GIT_REPO_PATH + '/' + repository_name
	
	
	if not os.path.isdir(local_repo_dir):os.mkdir(local_repo_dir)
	
	if not os.path.isdir(local_repo_path):
		#in this case we assume we have to clone the repository from remote url
		logger.debug('Cloning remote repo %s from: %s to %s \n' % (repository_name, repository_url, local_repo_dir) )
		Repo.clone_from(repository_url, local_repo_path)
	#crating Repo object instance
	myRepo=Repo(local_repo_path)
	git=myRepo.git
	
	#getting origin
	origin = myRepo.remotes.origin
	if not origin.exists(): return {'status':False,'data': "remote origin not found for GIT repository " + local_repo_path + " Please check your GIT Repository configuration"}
	# checkout on master
	myRepo.head.ref=myRepo.heads.master
	# try to fetch from origin
	logger.debug('Fetching from remote origin...\n')
	
	try:
		for fetch_info in origin.fetch(progress=MyProgressPrinter()):
			logger.debug("Updated %s to %s " % (fetch_info.ref, fetch_info.commit))

		logger.debug('\nRepository Updated\n')
		
	except Exception as ex:
		template = "An exception of type {0} occured. Arguments:\n{1!r}"
		message = template.format(type(ex).__name__, ex.args)
		logger.debug(message)
		logger.debug('\n Ops! fetching problems. Going haead...\n')
		
	#trying to checkout the tag release branch
	try:
		myRepo.head.ref = myRepo.remotes.origin.refs[tagBranchl]
		logger.debug("Repo head set to %s" % tagBranchl)
	except:
		return {'status':False,'data':"Failed to chekout to branch " + tagBranchl + " exiting..."}

	logger.debug('Getting commits and tags...')
	commitList=list(myRepo.iter_commits())
	tagList=sorted(myRepo.tags, key=lambda t: t.commit.committed_date)
	
	logger.debug("\nRepo Tags(%s):\n %s \n" % (len(tagList),tagList))
	
	tagListf=[elem for elem in tagList if tagBranchu + settings.TAG_SPLIT in elem.name]
	
	logger.debug("\nRepo Tags filterd by branch %s (%s): \n %s" % (tagBranchu,len(tagListf),tagListf))
	
	firstCommit = commitList[len(commitList)-1].hexsha
	logger.debug("\nFirst GIT Commit hexsha for branch %s : %s \n" % (tagBranchl,firstCommit))
	
	
	#getting the commit related to the previous tag for selected branch
	if (len(tagListf) ==1):
		#is the first tag for the branch
		before = firstCommit
		logger.debug("Setting before commit value to first commit: %s" % before)
	else:
		before=tagListf[len(tagListf)-2].tag.hexsha
		logger.debug("Setting before commit value to commit: %s" % before)
	
	
	beforeCommit = myRepo.commit(before)
	#logger.debug("\nBefore commit: %s, TAG commit: %s \n" % (beforeCommit.hexsha,checkout_sha))
	
	tagdiff=beforeCommit.diff(checkout_sha)
	logger.debug("\nTAG Differences...\n")
	
	try:
		for litem in tagdiff:
			#logger.debug('\n' + litem)
			if litem.new_file:
				#new file
				#getting file content "litem.b_blob.data_stream.read()" and parsing the doc_string content
				if not re.match('.*__.+__\.py',litem.b_path):
					if re.match('.*.py',litem.b_path):
						logger.debug('TestCase %s Added. Getting metadata ...'%litem.b_path)
						tinfo=get_testinfo(litem.b_blob.data_stream.read())
						logger.debug('\n TestCase Metadata:\n %s \n'%tinfo)
						res={'fullPath': litem.b_path,'tag': currentTag, 'diff': 'A', 'dependency':tinfo['Dependency'], 'author':tinfo['Author'], 'lab':tinfo['Lab'], 'description':tinfo['Description'], 'topology':tinfo['Topology'], 'run_section':tinfo['RunSections'], 'tps':tinfo['TPS']}
						result.append(res)
			elif litem.deleted_file:
				logger.debug('Deleted file %s . Not yet managed in DB Export')
				#deleted file
				#res={'fullPath': litem.a_path,'tag': currentTag, 'diff': 'D', 'dependency':tinfo['Dependency'], 'author':tinfo['Author'], 'lab':tinfo['Lab'], 'description':tinfo['Description'], 'topology':tinfo['Topology'], 'run_section':tinfo['RunSections'], 'tps':tinfo['TPS']}
			elif litem.renamed:
				logger.debug('Renamed file %s . Not yet managed in DB Export')
				#renamed file
				#res={'fullPath': litem.b_path,'tag': currentTag, 'diff': 'R', 'dependency':tinfo['Dependency'], 'author':tinfo['Author'], 'lab':tinfo['Lab'], 'description':tinfo['Description'], 'topology':tinfo['Topology'], 'run_section':tinfo['RunSections'], 'tps':tinfo['TPS']}
			else:
				#modified file
				#getting file content "litem.b_blob.data_stream.read()" and parsing the doc_string content
				if not re.match('.*__.+__\.py',litem.b_path):
					if re.match('.*.py',litem.b_path):
						logger.debug('TestCase %s Modified. Getting metadata'%litem.b_path)
						tinfo=get_testinfo(litem.b_blob.data_stream.read())
						logger.debug('\n TestCase Metadata:\n %s \n'%tinfo)
						res={'fullPath': litem.b_path,'tag': currentTag, 'diff': 'M', 'dependency':tinfo['Dependency'], 'author':tinfo['Author'], 'lab':tinfo['Lab'], 'description':tinfo['Description'], 'topology':tinfo['Topology'], 'run_section':tinfo['RunSections'], 'tps':tinfo['TPS']}
						result.append(res)
	except Exception as eee:
		logger.debug(str(eee))
		return {'status':False,'data':str(eee)}
	
	try:
		#logger.debug(result)
		logger.debug('\nAdding testcases to K@TE MySQL DB...\n')
		finalres=addTestListToDB(result)
		
		swrel=TSwRel.objects.get(sw_rel_name=tagBranchu)
		#adding the result to KATE DB
		#newitem = TGitActivity(status='ppp',data='xxx',tag=currentTag,t_sw_rel_id_sw_rel=swrel)
		newitem = TGitActivity(status=finalres['status'],data=finalres['data'],tag=currentTag,t_sw_rel_id_sw_rel=swrel)
		newitem.save()
		#updating Users git flag
		AuthUser.objects.filter(is_active=1).update(git_usershow=1)
		#return{'status':'ppp','data':'xxx'}
		return {'status':finalres['status'],'data':finalres['data']}
	except Exception as eee:
		logger.debug(str(eee))
		return {'status':False,'data':str(eee)}

def issue_hook(data):
	logger.debug('Calling Issue event management...')
	logger.debug(data)
	return '2B Implemented'

def note_hook(data):
	logger.debug('Calling note event management...')
	logger.debug(data)
	return '2B Implemented'

def merge_request_hook(data):
	logger.debug('Calling merge request event management...')
	logger.debug(data)
	return '2B Implemented'





@csrf_exempt
def gitlab_webhook(request):
	if request.method == 'POST' and request.body:
		http_x_gitlab_event = request.META.get('HTTP_X_GITLAB_EVENT', '')
		logger.debug('x_gitlab_event: %s' % http_x_gitlab_event)
		req_decoded=request.body.decode('ascii')
		json_data = json.loads(req_decoded)
		#logger.debug('json data: %s ' % json_data)
		object_kind = json_data.get('object_kind', '')
		project_id = json_data.get('project_id', '')
		repo_data = json_data.get('repository', '')
		user_id = json_data.get('user_id', '')
		user_name = json_data.get('user_name', '')
		user_email = json_data.get('user_email', '')
		
		logger.debug('Object Kind: %s' % object_kind)
		logger.debug('Project Id: %s' % project_id)
		logger.debug('Repo Data: %s' % repo_data)
		logger.debug('User Id: %s' % user_id)
		logger.debug('User Name: %s' % user_name)
		logger.debug('User email: %s' % user_email)
		
		
		if repo_data:
			repo_name = repo_data.get('name', '')
			repo_url = repo_data.get('url', '')
			logger.debug('	Repository Name: %s' % repo_name)
			logger.debug('	Repository URL: %s' % repo_url)
			
			
			runPhase = {'Push Hook': push_hook, 'Tag Push Hook' : tag_push_hook, 'Issue Hook' : issue_hook, 'Note Hook' : note_hook, 'Merge Request Hook' : merge_request_hook}
			queryRes=runPhase[http_x_gitlab_event](json_data)
			
			logger.debug('\n\n %s Results: %s\n\n%s\n\n'%(http_x_gitlab_event,queryRes['status'],queryRes['data']))
			
			
			return HttpResponse(queryRes)

	return HttpResponse('Hehe! No POST or not request.body')



def getgittag(request):
	

	context = RequestContext(request)
	if 'login' not in request.session:
		context_dict={'fromPage':'index'}
		return render_to_response('taws/login.html',context_dict,context)

	username=request.session['login']
	#phase=request.POST.get('phase','')
	
	res=get_DB_git_show(username)
	last = TGitActivity.objects.last()
	if last:
		ctag=last.tag
		cstatus=last.status
		cdata=last.data
		
	context_dict={'login':request.session['login'], 
							'tag':ctag,
							'status':cstatus,
							'content':cdata,
							'showgit':res}


	#return render(request,'taws/createNewTest.html',context_dict)
	return HttpResponse(json.dumps(context_dict),content_type="application/json")


def setGitFlag(request):


	context = RequestContext(request)
	if 'login' not in request.session:
		context_dict={'fromPage':'index'}
		return render_to_response('taws/login.html',context_dict,context)

	username=request.session['login']
	flag=request.POST.get('flag','0')
	res=set_DB_git_flag(username,flag.strip())
	context_dict={'login':request.session['login'], 
							'res':res}


	#return render(request,'taws/createNewTest.html',context_dict)
	return HttpResponse(json.dumps(context_dict),content_type="application/json")


def gitTagShow(request):
	import re
	from django.utils.safestring import mark_safe
	
	context = RequestContext(request)
	if 'login' not in request.session:
		context_dict={'fromPage':'index'}
		return render_to_response('taws/login.html',context_dict,context)

	curruser=request.session['login']
	treeView=''
	AuthUser.objects.filter(username=curruser).update(git_usershow=0)
	alltags = TGitActivity.objects.all()
	for tag in reversed(alltags):
		logger.debug('tag %s'%tag.tag)
		logger.debug('tag Status:%s'%tag.status)
		
		treeView+="{text: '"+tag.tag+"',"
		treeView+="href: '#"+tag.tag+"',"
		
		if tag.status=='True':
			logger.debug('Tag OK')
			treeView+="tags: [],"
		else:
			logger.debug('Tag KO')
			treeView+="tags: ['1'],"
		
		res=re.findall('TestCases(.*)?',tag.data,re.MULTILINE)	
		logger.debug('%s items in current tag'%len(res))
		if len(res)>0:
			treeView+="nodes:["
			for mytest in res:
				logger.debug(mytest)
				treeView+="{text: '"+mytest+"',"
				treeView+="href: '#"+mytest+"',"
				treeView+="tags: [],},"
			
			treeView+="]"
		treeView+="},"		
	
	context_dict={'login':request.session['login'],
		'treeView':mark_safe(treeView)}
	return render(request,'GitApp/gitTagShow.html',context_dict)

def setDevGIT(request):
	from taws.views import getUserRepoBranch,setUserRepo
	context = RequestContext(request)
	context_dict={'nothing':'nothing'}
	branch=request.POST.get('branch','')
	if 'login' not in request.session:
		context_dict={'fromPage':'test_development'}
		return render_to_response('taws/login.html',context_dict,context)
	username=request.session['login']
	gitRes =setUserRepo(username,branch)
	if (gitRes == "OK"):
		creationReport='<h4>Your GIT Repository is set on <span class="label label-default">'+branch+'</span> Release Branch.</h4>'			
		creationReportType='alert-success'
		creationReportTitle='Set GIT Branch Done!!'
		creationReportFooter='<p>Your local test browsing is referred to selected branch content!</p>'
	else:
		creationReport=gitRes
		creationReportType='alert-danger'
		creationReportTitle='Your GIT TestCase Repository must be manually Updated!!'
		creationReportFooter=''
		
	userBranch=getUserRepoBranch(username)
	
	
	return  JsonResponse({'creationReportTitle':creationReportTitle,'creationReport':creationReport,'creationReportType':creationReportType,'creationReportFooter':creationReportFooter,'userBranch':userBranch['current'],'userBranchList':userBranch['list']}, safe=False)




