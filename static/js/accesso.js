/*
  This file must be imported immediately-before the close-</body> tag,
  and after JQuery and Underscore.js are imported.
*/
/**
  The number of milliseconds to ignore clicks on the *same* like
  button, after a button *that was not ignored* was clicked. Used by
  `$(document).ready()`.
 
  Equal to <code>500</code>.
 */
var MILLS_TO_IGNORE_LIKES = 500;
/**
   Executes a like click. Triggered by clicks on the various yes/no links.
 */
/*var processLike = function(myAction)  {
   var processServerResponse = function(sersverResponse_data, textStatus_ignored,
                            jqXHR_ignored)  {
      //alert("sf sersverResponse_data='" + sersverResponse_data + "', textStatus_ignored='" + textStatus_ignored + "', jqXHR_ignored='" + jqXHR_ignored + "', color_id='" + color_id + "'");
	alert(myAction);
      $('#myObj').html(sersverResponse_data);
   }
 
   var config = {
      url: myURL,
      dataType: 'html',
      success: processServerResponse
      //Should also have a "fail" call as well.
   };
   $.ajax(config);
};*/

function doAccess2(myAction){
   var processServerResponse = function(sersverResponse_data, textStatus_ignored,
                            jqXHR_ignored)  {
      //alert("sf sersverResponse_data='" + sersverResponse_data + "', textStatus_ignored='" + textStatus_ignored + "', jqXHR_ignored='" + jqXHR_ignored + "', color_id='" + color_id + "'");
	//alert(myAction);
      $('#myObj').html(sersverResponse_data);
   }
 	//alert(myAction);

   var config = {
      url: myURL,
      dataType: 'html',
	//type: 'POST',
	data: {myChoice:'bbbb'},
      success: processServerResponse,
	error: alert('pirlaaa')
      //Should also have a "fail" call as well.
   };
   $.ajax(config);

}

// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function doAccess(myAction){
//------------------------CALL BACK FUNCTIONS---------------------------------------------------------------------------
	var processServerResponse = function(sersverResponse_data, textStatus_ignored,jqXHR_ignored)  {
		//alert("sf sersverResponse_data='" + sersverResponse_data + "', textStatus_ignored='" + textStatus_ignored + "', jqXHR_ignored='" + jqXHR_ignored);
		//alert(myAction);
		$('#myObj').html(sersverResponse_data);
		//alert(sersverResponse_data);
	};


	var loadSuite = function(sersverResponse_data, textStatus_ignored,jqXHR_ignored)  {
		//alert(sersverResponse_data, textStatus_ignored,jqXHR_ignored);
		//alert(sersverResponse_data['testString']);
		testListString=String(sersverResponse_data['testString']).split('$');
		updateTestTable('testBundleTable',testListString);
		suiteChanged=false;
		showalert("Suite correctly loaded","alert-success");
	};
	var queryDB = function(sersverResponse_data, textStatus_ignored,jqXHR_ignored)  {
		testListString=String(sersverResponse_data['testString']).split('$');
		console.log('call doAccess function, action='+myAction+' ...')
		updateTestTable('testTable',testListString);
		if(myAction=='localBrowsing'||myAction=='job_browsing'){updateTestTable('testBundleTable',sersverResponse_data['localString'].split('$'));}
		/*for(myItem in sersverResponse_data['tagList']){
			tempTagList+='<li><a onclick="document.getElementById(\'tag\').innerHTML=\''+sersverResponse_data['tagList'][myItem].tag
			Name+' <span class=\\\'caret\\\'></span>\';queryDB();">'+sersverResponse_data[myItem].areaName+'</a></li>';
		}
		document.getElementById('area').disabled=false;
		document.getElementById('area-dropdown').innerHTML=tempAreaList;*/
	};
	var saveSuite = function(sersverResponse_data, textStatus_ignored,jqXHR_ignored)  {
		myUserSuite='';
		mySharedSuite='';
		suiteID=sersverResponse_data['suiteID'];
		suiteName=sersverResponse_data['suiteName'];
		userSuiteAry=sersverResponse_data['userSuiteAry'];
		for(i=0;i<userSuiteAry.length;i++){
			myUserSuite+='<li><a onclick="suiteID='+userSuiteAry[i]['suiteID']+';document.getElementById(\'userSuites\').innerHTML=\''+userSuiteAry[i]['suiteName']+' <span class=caret></span>\' ">'+userSuiteAry[i]['suiteName']+'</a></li>';
		}
		document.getElementById('serverPersonalSuite').innerHTML=myUserSuite;
		userSuiteAry=sersverResponse_data['sharedSuiteAry'];
		for(i=0;i<userSuiteAry.length;i++){
			myUserSuite+='<li><a onclick="suiteID='+userSuiteAry[i]['suiteID']+';document.getElementById(\'userSuites\').innerHTML=\''+userSuiteAry[i]['suiteName']+' <span class=caret></span>\' ">'+userSuiteAry[i]['suiteName']+'</a></li>';
		}
		document.getElementById('serverSharedSuite').innerHTML=myUserSuite;
		if(sersverResponse_data['owner']!='SHARED'){document.getElementById('userSuites').innerHTML=suiteName+' <span class=caret></span>';}
			else{document.getElementById('sharedSuites').innerHTML=suiteName+' <span class=caret></span>';}
		testListString=String(sersverResponse_data['testString']).split('$');
		updateTestTable('testBundleTable',testListString);
		//alert(sersverResponse_data['testString']);
		suiteChanged=false;
		showalert("Suite correctly saved","alert-success");
	};
	var deleteSuite = function(sersverResponse_data, textStatus_ignored,jqXHR_ignored)  {
		/*userSuiteID='';
		sharedSuiteID='';*/
		myUserSuite='';
		mySharedSuite='';
		suiteID='';
		suiteName='';
		userSuiteAry=sersverResponse_data['userSuiteAry'];
		for(i=0;i<userSuiteAry.length;i++){
			myUserSuite+='<li><a onclick="suiteID='+userSuiteAry[i]['suiteID']+';document.getElementById(\'userSuites\').innerHTML=\''+userSuiteAry[i]['suiteName']+' <span class=caret></span>\' ">'+userSuiteAry[i]['suiteName']+'</a></li>';
		}
		document.getElementById('serverPersonalSuite').innerHTML=myUserSuite;
		document.getElementById('userSuites').innerHTML='User Suites <span class=caret></span>';
		userSuiteAry=sersverResponse_data['sharedSuiteAry'];
		for(i=0;i<userSuiteAry.length;i++){
			mySharedSuite+='<li><a onclick="suiteID='+userSuiteAry[i]['suiteID']+';document.getElementById(\'userSuites\').innerHTML=\''+userSuiteAry[i]['suiteName']+' <span class=caret></span>\' ">'+userSuiteAry[i]['suiteName']+'</a></li>';
		}
		document.getElementById('serverSharedSuite').innerHTML=myUserSuite;
		document.getElementById('sharedSuites').innerHTML='Shared Suites <span class=caret></span>';
		//fillSelect(sersverResponse_data['userSuiteAry'],document.getElementById('serverPersonalSuite'),'Select Here',sersverResponse_data['suiteID']);
		//fillSelect(sersverResponse_data['sharedSuiteAry'],document.getElementById('serverSharedSuite'),'Select Here',sersverResponse_data['suiteID']);
		emptyTable('testBundleTable');
		showalert("Suite correctly deleted","alert-success");
	};
	var queryIteration = function(sersverResponse_data, textStatus_ignored,jqXHR_ignored)  {
		//updateTableRow(sersverResponse_data['testString'],lineNumber,currentTable);
		modRecordToTable(sersverResponse_data['testString'],lineNumber,currentTable);
	};
	var savePreset = function(sersverResponse_data, textStatus_ignored,jqXHR_ignored)  {
		//alert('Preset '+sersverResponse_data['username']+' Saved!');
		//alert(sersverResponse_data['userPreset'],sersverResponse_data['fileName']);
		presetType='sharedPreset';
		if(sersverResponse_data['owner']!='SHARED'){presetType='userPreset';}
		updatePresetList(sersverResponse_data['userPreset'],presetType,sersverResponse_data['fileName'],sersverResponse_data['fileID'],sersverResponse_data['fileTitle'])
		loadPreset(sersverResponse_data['username'],sersverResponse_data['presetAry']);
		showalert("Preset "+sersverResponse_data['fileName']+" correctly saved","alert-success")
		//tempPresetAry=sersverResponse_data['presetAry'].split('$');
		//var preset=new Array();
		//for(zq_i=0;zq_1<tempPresetAry.length();zq_i++){
		//	preset.push(tempPresetAry[i]);
		//}
		//fillSelect(preset,document.getElementById('personalPreset'),'Select Here','<%=fileName%>');
	};
	var deletePreset = function(sersverResponse_data, textStatus_ignored,jqXHR_ignored)  {
		userSelection='';
		sharedSelection='';
		//if(sersverResponse_data['userPreset']=='SHARED'){sharedSelection=sersverResponse_data['fileName'];}
		//	else{userSelection=sersverResponse_data['fileName'];}
		updatePresetList(sersverResponse_data['userPreset'],'userPreset');
		updatePresetList(sersverResponse_data['sharedPreset'],'sharedPreset');
		//valueTable.clear().draw();
		showalert("Preset "+sersverResponse_data['presetName']+" correctly deleted","alert-success")
	};
	var getPreset = function(sersverResponse_data, textStatus_ignored,jqXHR_ignored)  {
		//prompt('',sersverResponse_data['presetAry']);
		loadPreset(sersverResponse_data['username'],sersverResponse_data['presetAry']);
	};


	var getPresetTemplate = function(sersverResponse_data, textStatus_ignored,jqXHR_ignored)  {
		//prompt('',sersverResponse_data['templatePreset'].replace('%0A','%0D%0A'));
		document.getElementById('preview').value=sersverResponse_data['templatePreset'];
     checkFields();
	};

	var addSmartSuite = function(sersverResponse_data, textStatus_ignored,jqXHR_ignored)  {
		//prompt('',sersverResponse_data['templatePreset'].replace('%0A','%0D%0A'));
		tempTopo=sersverResponse_data['topology'].split(',');
		excludedTopologies=sersverResponse_data['excludedTopologies'].split('#');
		topoStr='';
		for(i=0;i<tempTopo.length;i++){
			checkStr='';
			excludeFound=false;
			for(j=0;j<excludedTopologies.length;j++){if(excludedTopologies[j]==tempTopo[i].replace('#','')){excludeFound=true;}}
			if(tempTopo[i].match('#')!=null&&excludeFound!=true){checkStr=' checked ';}
			if(tempTopo[i].match('#')==null){checkStr=' disabled ';}
			topoStr+=tempTopo[i].replace('#','')+"<input onclick='selectPresetDropDown($(this));' value='"+tempTopo[i].replace('#','')+"' type='checkbox' "+checkStr+">";
			//if(i<tempTopo.length){topoStr+='<br>';}
		}
		/*tempBench=sersverResponse_data['benches'].split('#');
		benchStr='';
		for(i=1;i<tempBench.length;i++){
			benchStr+='<button id="'+tempBench[i].replace('#','')+'" onclick="$(\'#testTable tr td button\').removeClass(\'selected\');$(this).addClass(\'selected\');window.open(\'/taws/selectEqpt/?myVars=$\'+this.id+\'$\',\'viewReportTrunk\',\'height=600,width=1000,resizable=1\');">'+tempBench[i].replace('#','')+'</button>';
			//benchStr+="<input type='button' value="+tempBench[i].replace('#','')+">";
			if(i<tempBench.length){benchStr+='<br>';}
		}*/
		presetDropDown=presetDropDownPre+presetStr+presetDropDownPost;
		if(rowIndex=='NEW'){
			myRow=testTable.row.add({
				"control" : "<img src='/static/images/details_close.png'></img>",
				"prod" : sersverResponse_data['product'],
				"rel" : sersverResponse_data['sw_rel_name'],
				"suite": sersverResponse_data['area_name'],
				"topologies" : topoStr,
				"options" : 'FU',
				"tc": sersverResponse_data['CURRtc']+'/'+sersverResponse_data['TOTtc'],
				"tps": sersverResponse_data['CURRtps']+'/'+sersverResponse_data['TOTtps'],
				"duration": '0',
				"preset": presetDropDown
			}
			).draw( false );
		}else{
			var oTable = $('#testTable').dataTable();
			oTable.fnUpdate(topoStr,rowIndex,4,false);
			oTable.fnUpdate(sersverResponse_data['CURRtc']+'/'+sersverResponse_data['TOTtc'],rowIndex,6,false);
			oTable.fnUpdate(sersverResponse_data['CURRtps']+'/'+sersverResponse_data['TOTtps'],rowIndex,7,false);
		}
		updateStats('smart');
	};

	var createTest = function(sersverResponse_data, textStatus_ignored,jqXHR_ignored)  {
		//prompt('',sersverResponse_data['templatePreset'].replace('%0A','%0D%0A'));
		//alert(sersverResponse_data['creationReport']);
		$("body").removeClass("loading");
		console.log('CreateTest Ajax success')
		console.log(sersverResponse_data)
		console.log("User GIT Branch set to: "+sersverResponse_data['userBranch'])
		console.log("User GIT Branch list: "+sersverResponse_data['userBranchList'])
		
			
		for	(index = 0; index < sersverResponse_data['userBranchList'].length; index++) {
			console.log(" Item: "+sersverResponse_data['userBranchList'][index]);
		} 
		
		//document.getElementById('gituserbranch').innerHTML=sersverResponse_data['userBranch'];
		showmodal(sersverResponse_data['creationReportTitle'],sersverResponse_data['creationReport'],sersverResponse_data['creationReportType'],sersverResponse_data['creationReportFooter']);
		fillGitDropDown(sersverResponse_data['userBranch'],sersverResponse_data['userBranchList']) 
		doAccess('localBrowsing');
	};
	var viewTest = function(sersverResponse_data, textStatus_ignored,jqXHR_ignored)  {
		tempRevision='';
		document.getElementById('modalTitle').innerHTML=sersverResponse_data['testName'];
		if(sersverResponse_data['revision']!="NA"){
			for (myItem in sersverResponse_data['revList']){
				tempRevision+='<li><a id="'+sersverResponse_data['revList'][myItem].revId+'" onclick="document.getElementById(\'idTestRev\').value=this.id;doAccess(\'viewTestCase\');">'+sersverResponse_data['revList'][myItem].rev+'</a></li>';
			}
			tempButton='<button type="button" class="btn btn-default navbar-btn" disabled>Revision</button>\
				<button class="btn btn-default dropdown-toggle navbar-btn" type="button" id="userPreset" data-toggle="dropdown" aria-haspopup="true" aria-expanded="true">'+sersverResponse_data['revision']+'\
				<span class="caret"></span>\
				</button>\
					<ul class="dropdown-menu" id="userPresetDropdown">'+tempRevision+'</ul>';
		}else{
			tempButton='<button type="button" class="btn btn-default navbar-btn">Save File</button>';
		}
		document.getElementById('modalButton').innerHTML=tempButton;
		//document.getElementById('modalInput').value=sersverResponse_data['testName'];
		document.getElementById('comment').innerHTML=sersverResponse_data['myFile'];
		//alert(sersverResponse_data);
   		 //window.opener.doAccess('localBrowsing');
	};
	var getSwRelease = function(sersverResponse_data, textStatus_ignored,jqXHR_ignored)  {
		console.log('Get SW Release');
		console.log(sersverResponse_data);
		tempSWList='';
			
		for(myItem in sersverResponse_data){
			tempSWList+='<li><a onclick="document.getElementById(\'sw-release\').innerHTML=\''+sersverResponse_data[myItem].swName+' <span class=\\\'caret\\\'></span>\';SWRelease='+sersverResponse_data[myItem].swID+';doAccess(\'getDomain\');">'+sersverResponse_data[myItem].swName+'</a></li>';
		} 
		document.getElementById('sw-release').disabled=false;
		document.getElementById('sw-release-dropdown').innerHTML=tempSWList;
		document.getElementById('domain').disabled=true;
		document.getElementById('domain-dropdown').innerHTML='';
		document.getElementById('area').disabled=true;
		document.getElementById('area-dropdown').innerHTML='';
	};

	var getDomain = function(sersverResponse_data, textStatus_ignored,jqXHR_ignored)  {
		console.log('Get Domain');
		console.log(sersverResponse_data);
		tempDomainList='';
			
		for(myItem in sersverResponse_data){
			tempDomainList+='<li><a onclick="document.getElementById(\'domain\').innerHTML=\''+sersverResponse_data[myItem].domainName+' <span class=\\\'caret\\\'></span>\';domainID='+sersverResponse_data[myItem].domainID+';doAccess(\'getArea\');">'+sersverResponse_data[myItem].domainName+'</a></li>';
		} 
		document.getElementById('domain').disabled=false;
		document.getElementById('domain-dropdown').innerHTML=tempDomainList;
		document.getElementById('area').disabled=true;
		document.getElementById('area-dropdown').innerHTML='';
	};

	var getArea = function(sersverResponse_data, textStatus_ignored,jqXHR_ignored)  {
		console.log('Get Area');
		console.log(sersverResponse_data);
		tempAreaList='';
			
		for(myItem in sersverResponse_data){
			tempAreaList+='<li><a onclick="document.getElementById(\'area\').innerHTML=\''+sersverResponse_data[myItem].areaName+' <span class=\\\'caret\\\'></span>\';queryDB();">'+sersverResponse_data[myItem].areaName+'</a></li>';
		}
		document.getElementById('area').disabled=false;
		document.getElementById('area-dropdown').innerHTML=tempAreaList;
	};

//------------------------POST VALUES-----------------------------------------------------------------------------------
	var csrftoken = getCookie('csrftoken');
	$.ajaxSetup({
	    beforeSend: function(xhr, settings) {
		if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
		    xhr.setRequestHeader("X-CSRFToken", csrftoken);
		}
	    }
	});
	//alert(serverPersonalSuite.value);
	if(myAction=='loadSuite'){
		$.ajax({
			type: "POST",
			dataType: 'json',
			url: myURL,
			data: {
				action: myAction,
				owner: owner,
				loadID: suiteID
				},
			success: loadSuite,
			error: function(xhr, textStatus, errorThrown) {
					alert("Please report this error: "+errorThrown+xhr.status+xhr.responseText);
				}
		});
	}
	if(myAction=='queryDB'){
    //document.getElementById('serverPersonalSuite').disabled=false;
    //document.getElementById('serverSharedSuite').disabled=false;
		$.ajax({
			type: "POST",
			dataType: 'json',
			url: myURL,
			data: {
				action: myAction,
				queryProduct:queryProduct,
				querySWRelease:querySWRelease,
				queryArea:queryArea,
				},
			success: queryDB,
			error: function(xhr, textStatus, errorThrown) {
					alert("Please report this error: "+errorThrown+xhr.status+xhr.responseText);
				}
		});
	}
	if(myAction=='addSmartSuite'){
	    //document.getElementById('serverPersonalSuite').disabled=false;
	    //document.getElementById('serverSharedSuite').disabled=false;
			$.ajax({
				type: "POST",
				dataType: 'json',
				url: myURL,
				data: {
					action: myAction,
					queryProduct:queryProduct,
					querySWRelease:querySWRelease,
					queryArea:queryArea,
					presetID:presetID,
					excludedTopologies:excludedTopologies.slice(0,-1)
					},
				success: addSmartSuite,
				error: function(xhr, textStatus, errorThrown) {
						alert("Please report this error: "+errorThrown+xhr.status+xhr.responseText);
					}
			});
		}
	if(myAction=='saveSuite'){
		//alert(savingString);
		$.ajax({
			type: "POST",
			dataType: 'json',
			url: myURL,
			data: {
				action: myAction,
				owner: owner,
				savingString: savingString,
				saveID: saveID
				},
			success: saveSuite,
			error: function(xhr, textStatus, errorThrown) {
					alert("Please report this error: "+errorThrown+xhr.status+xhr.responseText);
				}
		});
	}
	if(myAction=='deleteSuite'){
		$.ajax({
			type: "POST",
			dataType: 'json',
			url: myURL,
			data: {
				action: myAction,
				owner: owner,
				deleteID: suiteID
				},
			success: deleteSuite,
			error: function(xhr, textStatus, errorThrown) {
					alert("Please report this error: "+errorThrown+xhr.status+xhr.responseText);
				}
		});
	}
	if(myAction=='shareSuite'){
		$.ajax({
			type: "POST",
			dataType: 'json',
			url: myURL,
			data: {
				action: myAction,
				owner: owner,
				shareID: suiteID
				},
			success: saveSuite,
			error: function(xhr, textStatus, errorThrown) {
					alert("Please report this error: "+errorThrown+xhr.status+xhr.responseText);
				}
		});
	}
	if(myAction=='queryIteration'){
		$.ajax({
			type: "POST",
			dataType: 'json',
			url: myURL,
			data: {
				action: myAction,
				iteration: iteration
				},
			success: queryIteration,
			error: function(xhr, textStatus, errorThrown) {
					alert("Please report this error: "+errorThrown+xhr.status+xhr.responseText);
				}
		});
	}
	if(myAction=='savePreset'){
		//alert(myAction);
		//alert(myValues);
		//alert(presetID);
		//alert(presetSelection);
		console.log('calling savePreset from accesso.js...');
		console.log('Ajax POST to '+myURL);
		console.log('action: '+myAction);
		console.log('presetBody: ' + myValues);
		console.log('presetName: ' + presetID);
		console.log('presetType: ' + presetSelection);
		$.ajax({
			type: "POST",
			dataType: 'json',
			url: myURL,
			data: {
				action: myAction,
				presetBody: myValues,
				presetName: presetID,
				presetType:presetSelection
				},
			success: savePreset,
			error: function(xhr, textStatus, errorThrown) {
					alert("Please report this error: "+errorThrown+xhr.status+xhr.responseText);
				}
		});
	}
	if(myAction=='loadPreset'){
		$.ajax({
			type: "POST",
			dataType: 'json',
			url: myURL,
			data: {
				action: myAction,
				presetID: presetID
				},
			success: getPreset,
			error: function(xhr, textStatus, errorThrown) {
					alert("Please report this error: "+errorThrown+xhr.status+xhr.responseText);
				}
		});
	}

	if(myAction=='deletePreset'){
		$.ajax({
			type: "POST",
			dataType: 'json',
			url: myURL,
			data: {
				action: myAction,
				presetID: presetID,
				presetName: presetName
				},
			success: deletePreset,
			error: function(xhr, textStatus, errorThrown) {
					alert("Please report this error: "+errorThrown+xhr.status+xhr.responseText);
				}
		});
	}

	if(myAction=='localBrowsing'){
		$.ajax({
			type: "POST",
			dataType: 'json',
			url: myURL,
			data: {
				action: myAction
				},
			success: queryDB,
			error: function(xhr, textStatus, errorThrown) {
					alert("Please report this error: "+errorThrown+xhr.status+xhr.responseText);
				}
		});
	}

	if(myAction=='job_browsing'){
		$.ajax({
			type: "POST",
			dataType: 'json',
			url: myURL,
			data: {
				action: myAction,
        'job_name':job_name,
        'suite_name':suite_name
				},
			success: queryDB,
			error: function(xhr, textStatus, errorThrown) {
					alert("Please report this error: "+errorThrown+xhr.status+xhr.responseText);
				}
		});
	}

	if(myAction=='saveLocal'){
		$.ajax({
			type: "POST",
			dataType: 'json',
			url: myURL,
			data: {
				action: myAction,
        savingString: savingString
				},
			success: loadSuite,
			error: function(xhr, textStatus, errorThrown) {
					alert("Please report this error: "+errorThrown+xhr.status+xhr.responseText);
				}
		});
	}
	if(myAction=='getPresetTemplate'){
		$.ajax({
			type: "POST",
			dataType: 'json',
			url: myURL,
			data: {
				action: myAction,
        presetID: document.getElementById('formpresetID').value,
				topoID: document.getElementById('formtopologyID').value
				 //topoID: document.getElementById('selectTopo').options[document.getElementById('selectTopo').selectedIndex].value,
        //presetID: document.getElementById('selectPreset').options[document.getElementById('selectPreset').selectedIndex].value
				},
			success: getPresetTemplate,
			error: function(xhr, textStatus, errorThrown) {
					alert("Please report this error: "+errorThrown+xhr.status+xhr.responseText);
				}
		});
	}

	
	if(myAction=='getTopoTemplate'){
		$.ajax({
			type: "POST",
			dataType: 'json',
			url: myURL,
			data: {
				action: myAction,
				topoID: document.getElementById('formtopologyID').value
				 //topoID: document.getElementById('selectTopo').options[document.getElementById('selectTopo').selectedIndex].value,
        //presetID: document.getElementById('selectPreset').options[document.getElementById('selectPreset').selectedIndex].value
				},
			success: getPresetTemplate,
			error: function(xhr, textStatus, errorThrown) {
					alert("Please report this error: "+errorThrown+xhr.status+xhr.responseText);
				}
		});
	}
	
	if(myAction=='getSwRelease'){
		$.ajax({
			type: "POST",
			dataType: 'json',
			url: myURL,
			data: {
				action: myAction,
				prod: prod
				 //topoID: document.getElementById('selectTopo').options[document.getElementById('selectTopo').selectedIndex].value,
        //presetID: document.getElementById('selectPreset').options[document.getElementById('selectPreset').selectedIndex].value
				},
			success: getSwRelease,
			error: function(xhr, textStatus, errorThrown) {
					alert("Please report this error: "+errorThrown+xhr.status+xhr.responseText);
				}
		});
	}
	
	if(myAction=='getDomain'){
		$.ajax({
			type: "POST",
			dataType: 'json',
			url: myURL,
			data: {
				action: myAction,
				prod: prod,
				swRel: SWRelease
				 //topoID: document.getElementById('selectTopo').options[document.getElementById('selectTopo').selectedIndex].value,
        //presetID: document.getElementById('selectPreset').options[document.getElementById('selectPreset').selectedIndex].value
				},
			success: getDomain,
			error: function(xhr, textStatus, errorThrown) {
					alert("Please report this error: "+errorThrown+xhr.status+xhr.responseText);
				}
		});
	}

	if(myAction=='getArea'){
		$.ajax({
			type: "POST",
			dataType: 'json',
			url: myURL,
			data: {
				action: myAction,
				prod: prod,
				swRel: SWRelease,
				domain: domainID
				 //topoID: document.getElementById('selectTopo').options[document.getElementById('selectTopo').selectedIndex].value,
        //presetID: document.getElementById('selectPreset').options[document.getElementById('selectPreset').selectedIndex].value
				},
			success: getArea,
			error: function(xhr, textStatus, errorThrown) {
					alert("Please report this error: "+errorThrown+xhr.status+xhr.responseText);
				}
		});
	}

	
	
	
	
	if(myAction=='createTest'){
		$("body").addClass("loading");
		$.ajax({
			type: "POST",
			dataType: 'json',
			url: myURL,
			data: {
				action: myAction,
        testName:document.getElementById('testName').value,
        presetBody:document.getElementById('preview').value,
        topoID:document.getElementById('formtopologyID').value,
				//product:document.getElementById('product').options[document.getElementById('product').selectedIndex].text,
				//domain:document.getElementById('domain').options[document.getElementById('domain').selectedIndex].text,
				//area:document.getElementById('area').options[document.getElementById('area').selectedIndex].text
				product:document.getElementById('createTestProductValue').value,
				domain:document.getElementById('createTestDomainValue').value,
				area:document.getElementById('createTestAreaValue').value,
			  release:document.getElementById('createTestReleaseValue').value,
				},
			success: createTest,
			error: function(xhr, textStatus, errorThrown) {
					$("body").removeClass("loading");
					alert("Please report this error: "+errorThrown+xhr.status+xhr.responseText);
				}
		});
	}

	if(myAction=='deleteTest' && deleteList != ''){
		$.ajax({
			type: "POST",
			dataType: 'json',
			url: myURL,
			data: {
				action: myAction,
        			deleteList:deleteList
				},
			success: createTest,
			error: function(xhr, textStatus, errorThrown) {
					alert("Please report this error: "+errorThrown+xhr.status+xhr.responseText);
					
				}
		});
	}
	if(myAction=='viewTestCase'){
		$.ajax({
			type: "POST",
			dataType: 'json',
			url: myURL,
			data: {
				action: myAction,
				idTestRev:selectTest.idTestRev.value
				},
			success: viewTest,
			error: function(xhr, textStatus, errorThrown) {
					alert("Please report this error: "+errorThrown+xhr.status+xhr.responseText);
				}
		});
	}

/*	if(myAction=='editList'){
		$.ajax({
			type: "POST",
			dataType: 'json',
			url: myURL,
			data: {
				action: myAction,
        			editList:editList
				},
			success: createTest,
			error: function(xhr, textStatus, errorThrown) {
					alert("Please report this error: "+errorThrown+xhr.status+xhr.responseText);
				}
		});
	}
*/
}


/*$(document).ready(function()  {
	 $("#selectTest").submit(function(){
		    $.ajax({
			type: "POST",
			dataType: 'html',
			url: "/taws/accesso/",
			data: {targetFile: 'bbbb'},
			success: processServerResponse,
			error: function(xhr, textStatus, errorThrown) {
			    alert("Please report this error: "+errorThrown+xhr.status+xhr.responseText);
			}
		    })
	})
})*/

/**
   The Ajax "main" function. Attaches the listeners to the elements on
   page load, each of which only take effect every
   <link to MILLS_TO_IGNORE_LIKES> seconds.
 
   This protection is only against a single user pressing buttons as fast
   as they can. This is in no way a protection against a real DDOS attack,
   of which almost 100% bypass the client (browser) (they instead
   directly attack the server). Hence client-side protection is pointless.
 
   - http://stackoverflow.com/questions/28309850/how-much-prevention-of-rapid-fire-form-submissions-should-be-on-the-client-side
 
   The protection is implemented via Underscore.js' debounce function:
  - http://underscorejs.org/#debounce
 
   Using this only requires importing underscore-min.js. underscore-min.map
   is not needed.
 */
//$(document).ready(function()  {
  /*
    There are many buttons having the class
 
      td__toggle_color_like_button
 
    This attaches a listener to *every one*. Calling this again
    would attach a *second* listener to every button, meaning each
    click would be processed twice.
   */
//  $('.td__toggle_color_like_button').click(processLike,
  //    MILLS_TO_IGNORE_LIKES, true);
  /*
    Warning: Placing the true parameter outside of the debounce call:
 
    $('#color_search_text').keyup(_.debounce(processSearch,
        MILLS_TO_IGNORE_SEARCH), true);
 
    results in "TypeError: e.handler.apply is not a function".
   */
//});

