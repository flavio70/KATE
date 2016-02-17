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
	#print('TestFullPath: %s'% testpath)
	
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
				#print('Description %s'%elem[1])
				res['Description'] =  res['Description']  + re.sub('["\']+','',elem[1]) + '\n'
			elif (elem[0] == "TPS"):
				res['TPS'] =  res['TPS']  + re.sub('["\']+','',elem[1]) + '*'
			else:
				res[elem[0]]=re.sub('["\']+','',elem[1])
				#print( '%s %s' %(elem[0],elem[1]))
	
	return res

def addTestListToDB(testList):
	"""
	#testAry=[{'fullPath':'TestCases/1850TSS320/DATA/DATAQOS/pippo.py','tag':'7.2@01','diff':'A','dependency':'dep1','author':'COLOMX','lab':'SVT','description':'descr1','topology':'topo1','run_section':'11111','tps':'1.2.3*4.5.6'}]
"""
	listReport=''
	for myTest in testList:
		if myTest['diff']=='A':listReport+=addTestToDB(myTest)
		#print(testList)
	return listReport

def push_hook(data):
	print('Calling push event management...')
	print(data)
	return '2B Implemented'

def tag_push_hook(data):
	from git import Repo, RemoteProgress
	import os

	class MyProgressPrinter(RemoteProgress):
		def update(self, op_code, cur_count, max_count=None, message=''):
			print(op_code, cur_count, max_count, cur_count / (max_count or 100.0), message or "NO MESSAGE")
	# end
	
	print('Calling Tag push event management...\n')
	print(data)
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

	print('\ncheckout sha: %s\n' % checkout_sha)
	print('Current TAG value: %s \n' % currentTag)

	if not checkout_sha:return "Are we deleting tag?... Nothing to do. Stopping execution..."

	print('\nchecking current TAG: %s Format...' % currentTag)
	'''
	TAG FORMAT Expected coming from branch xxxxx: XXXXX__abcd
	'''
	tagSplit = currentTag.split(settings.TAG_SPLIT)
	if (len(tagSplit) != 2): return "current TAG " + currentTag + " is Not in the right format, exiting ..."
	
	tagBranchu=tagSplit[0]
	tagBranchl=tagBranchu.lower()
	tagVal=tagSplit[1]
	print('\nOK TAG is in the correct format: branch %s Tag Separator %s  tag version %s \n' % (tagBranchl,settings.TAG_SPLIT,tagVal))
	
	
	local_repo_dir=settings.BASE_DIR + '/wrepos'
	local_repo_path= settings.BASE_DIR + '/wrepos/' + repository_name
	
	
	if not os.path.isdir(local_repo_dir):os.mkdir(local_repo_dir)
	
	if not os.path.isdir(local_repo_path):
		#in this case we assume we have to clone the repository from remote url
		print('Cloning remote repo %s from: %s to %s \n' % (repository_name, repository_url, local_repo_dir) )
		Repo.clone_from(repository_url, local_repo_path)
	#crating Repo object instance
	myRepo=Repo(local_repo_path)
	git=myRepo.git
	
	#getting origin
	origin = myRepo.remotes.origin
	if not origin.exists(): return "remote origin not found for GIT repository " + repoPath + " Please check your GIT Repository configuration"
	# checkout on master
	myRepo.head.ref=myRepo.heads.master
	# try to fetch from origin
	print('Fetching from remote origin...\n')
	
	try:
		for fetch_info in origin.fetch(progress=MyProgressPrinter()):
			print("Updated %s to %s " % (fetch_info.ref, fetch_info.commit))

		print('\nRepository Updated\n')
		
	except Exception as ex:
		template = "An exception of type {0} occured. Arguments:\n{1!r}"
		message = template.format(type(ex).__name__, ex.args)
		print(message)
		print('\n Ops! fetching problems. Going haead...\n')
		
	#trying to checkout the tag release branch
	try:
		 myRepo.head.ref = myRepo.remotes.origin.refs[tagBranchl]
		 print("Repo head set to %s" % tagBranchl)
	except:
		return "Failed to chekout to branch " + tagBranchl + " exiting..."

	print('Getting commits and tags...')
	commitList=list(myRepo.iter_commits())
	tagList=sorted(myRepo.tags, key=lambda t: t.commit.committed_date)
	
	print("\nRepo Tags(%s):\n %s \n" % (len(tagList),tagList))
	
	tagListf=[elem for elem in tagList if tagBranchu + settings.TAG_SPLIT in elem.name]
	
	print("\nRepo Tags filterd by branch %s (%s): \n %s" % (tagBranchu,len(tagListf),tagListf))
	
	firstCommit = commitList[len(commitList)-1].hexsha
	print("\nFirst GIT Commit hexsha for branch %s : %s \n" % (tagBranchl,firstCommit))
	
	
	#getting the commit related to the previous tag for selected branch
	if (len(tagListf) ==1):
		#is the first tag for the branch
		before = firstCommit
		print("Setting before commit value to first commit: %s" % before)
	else:
		before=tagListf[len(tagListf)-2].tag.hexsha
		print("Setting before commit value to commit: %s" % before)
	
	
	beforeCommit = myRepo.commit(before)
	#print("\nBefore commit: %s, TAG commit: %s \n" % (beforeCommit.hexsha,checkout_sha))
	
	tagdiff=beforeCommit.diff(checkout_sha)
	print("\nTAG Differences...\n")
	
	try:
		for litem in tagdiff:
			#print('\n' + litem)
			if litem.new_file:
				#new file
				#getting file content "litem.b_blob.data_stream.read()" and parsing the doc_string content
				if not re.match('.*__.+__\.py',litem.b_path):
					if re.match('.*.py',litem.b_path):
						print('TestCase %s Added. Getting metadata ...'%litem.b_path)
						tinfo=get_testinfo(litem.b_blob.data_stream.read())
						print('\n TestCase Metadata:\n %s \n'%tinfo)
						res={'fullPath': litem.b_path,'tag': currentTag, 'diff': 'A', 'dependency':tinfo['Dependency'], 'author':tinfo['Author'], 'lab':tinfo['Lab'], 'description':tinfo['Description'], 'topology':tinfo['Topology'], 'run_section':tinfo['RunSections'], 'tps':tinfo['TPS']}
						result.append(res)
			elif litem.deleted_file:
				print('Deleted file %s . Not yet managed in DB Export')
				#deleted file
				#res={'fullPath': litem.a_path,'tag': currentTag, 'diff': 'D', 'dependency':tinfo['Dependency'], 'author':tinfo['Author'], 'lab':tinfo['Lab'], 'description':tinfo['Description'], 'topology':tinfo['Topology'], 'run_section':tinfo['RunSections'], 'tps':tinfo['TPS']}
			elif litem.renamed:
				print('Renamed file %s . Not yet managed in DB Export')
				#renamed file
				#res={'fullPath': litem.b_path,'tag': currentTag, 'diff': 'R', 'dependency':tinfo['Dependency'], 'author':tinfo['Author'], 'lab':tinfo['Lab'], 'description':tinfo['Description'], 'topology':tinfo['Topology'], 'run_section':tinfo['RunSections'], 'tps':tinfo['TPS']}
			else:
				#modified file
				#getting file content "litem.b_blob.data_stream.read()" and parsing the doc_string content
				if not re.match('.*__.+__\.py',litem.b_path):
					if re.match('.*.py',litem.b_path):
						print('TestCase %s Modified. Getting metadata'%litem.b_path)
						tinfo=get_testinfo(litem.b_blob.data_stream.read())
						print('\n TestCase Metadata:\n %s \n'%tinfo)
						res={'fullPath': litem.b_path,'tag': currentTag, 'diff': 'M', 'dependency':tinfo['Dependency'], 'author':tinfo['Author'], 'lab':tinfo['Lab'], 'description':tinfo['Description'], 'topology':tinfo['Topology'], 'run_section':tinfo['RunSections'], 'tps':tinfo['TPS']}
						result.append(res)
	except Exception as eee:
		print(str(eee))
		return str(eee)
	
	#print(result)
	print('\nAdding testcases to K@TE MySQL DB...\n')
	finalres=addTestListToDB(result)
	return finalres

def issue_hook(data):
	print('Calling Issue event management...')
	print(data)
	return '2B Implemented'

def note_hook(data):
	print('Calling note event management...')
	print(data)
	return '2B Implemented'

def merge_request_hook(data):
	print('Calling merge request event management...')
	print(data)
	return '2B Implemented'

@csrf_exempt
def gitlab_webhook(request):
	if request.method == 'POST' and request.body:
		http_x_gitlab_event = request.META.get('HTTP_X_GITLAB_EVENT', '')
		print('x_gitlab_event: %s' % http_x_gitlab_event)
		req_decoded=request.body.decode('ascii')
		json_data = json.loads(req_decoded)
		#print('json data: %s ' % json_data)
		object_kind = json_data.get('object_kind', '')
		project_id = json_data.get('project_id', '')
		repo_data = json_data.get('repository', '')
		user_id = json_data.get('user_id', '')
		user_name = json_data.get('user_name', '')
		user_email = json_data.get('user_email', '')
		
		print('Object Kind: %s' % object_kind)
		print('Project Id: %s' % project_id)
		print('Repo Data: %s' % repo_data)
		print('User Id: %s' % user_id)
		print('User Name: %s' % user_name)
		print('User email: %s' % user_email)
		
		
		if repo_data:
			repo_name = repo_data.get('name', '')
			repo_url = repo_data.get('url', '')
			print('	Repository Name: %s' % repo_name)
			print('	Repository URL: %s' % repo_url)
			
			
			runPhase = {'Push Hook': push_hook, 'Tag Push Hook' : tag_push_hook, 'Issue Hook' : issue_hook, 'Note Hook' : note_hook, 'Merge Request Hook' : merge_request_hook}
  
			queryRes=runPhase[http_x_gitlab_event](json_data)
			
			print('\n\n TAG PUSH HOOK Results:\n%s\n\n'%queryRes)
			
			
			return HttpResponse(runPhase)

	return HttpResponse('Hehe! No POST or not request.body')

