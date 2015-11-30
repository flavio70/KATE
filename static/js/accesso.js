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
	};
	var queryDB = function(sersverResponse_data, textStatus_ignored,jqXHR_ignored)  {
		//alert(sersverResponse_data, textStatus_ignored,jqXHR_ignored);
		//prompt('',sersverResponse_data['myStr']);
		testListString=String(sersverResponse_data['testString']).split('$');
		//updateTestTable('testTable',testListString);
		updateTestTable('testTable',testListString);
		//alert(sersverResponse_data['testString']);
		//    if(myAction=='localBrowsing'){
		//      //alert(sersverResponse_data['localString']);
		//  		testBundleString=String(sersverResponse_data['localString']).split('$');
		//    		  updateTestTable('testBundleTable',testBundleString);
   		 //}
	};
	var saveSuite = function(sersverResponse_data, textStatus_ignored,jqXHR_ignored)  {
		myUserSuite='';
		mySharedSuite='';
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
		//for(i=0;sersverResponse_data['sharedSuiteAry'];i++){myUserSuite+='<li><a onclick="suiteID={{ myItem.suiteID }};document.getElementById(\'userSuites\').innerHTML=\'{{ myItem.suiteName }} <span class=caret></span>\' ">{{ myItem.suiteName }}</a></li>';}
		//document.getElementById('serverPersonalSuite').innerHTML=myUserSuite;
		//fillSelect(sersverResponse_data['userSuiteAry'],document.getElementById('serverPersonalSuite'),'Select Here',sersverResponse_data['suiteID']);
		//fillSelect(sersverResponse_data['sharedSuiteAry'],document.getElementById('serverSharedSuite'),'Select Here',sersverResponse_data['suiteID']);
		testListString=String(sersverResponse_data['testString']).split('$');
		updateTestTable('testBundleTable',testListString);
		//alert(sersverResponse_data['testString']);
		suiteChanged=false;
		showalert("Suite correctly saved","alert-success")
	};
	var deleteSuite = function(sersverResponse_data, textStatus_ignored,jqXHR_ignored)  {
		userSuiteID='';
		sharedSuiteID='';
		myUserSuite='';
		mySharedSuite='';
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
		showalert("Suite correctly deleted","alert-success")
	};
	var queryIteration = function(sersverResponse_data, textStatus_ignored,jqXHR_ignored)  {
		//updateTableRow(sersverResponse_data['testString'],lineNumber,currentTable);
		modRecordToTable(sersverResponse_data['testString'],lineNumber,currentTable);
	};
	var savePreset = function(sersverResponse_data, textStatus_ignored,jqXHR_ignored)  {
		//alert('Preset '+sersverResponse_data['fileName']+' Saved!');
		//alert(sersverResponse_data['userPreset'],sersverResponse_data['fileName']);
		updatePresetList(sersverResponse_data['userPreset'],'personalPreset',sersverResponse_data['fileName'])
		loadPreset(sersverResponse_data['username'],sersverResponse_data['presetAry']);
		//tempPresetAry=sersverResponse_data['presetAry'].split('$');
		//var preset=new Array();
		//for(zq_i=0;zq_1<tempPresetAry.length();zq_i++){
		//	preset.push(tempPresetAry[i]);
		//}
		//fillSelect(preset,document.getElementById('personalPreset'),'Select Here','<%=fileName%>');
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

	var createTest = function(sersverResponse_data, textStatus_ignored,jqXHR_ignored)  {
		//prompt('',sersverResponse_data['templatePreset'].replace('%0A','%0D%0A'));
		alert(sersverResponse_data['creationReport']);
    window.opener.doAccess('localBrowsing');
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
	if(myAction=='saveSuite'){
		alert(savingString);
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
		$.ajax({
			type: "POST",
			dataType: 'json',
			url: myURL,
			data: {
				action: myAction,
				presetBody: changeScript.presetBody.value,
				presetName: changeScript.presets.value,
				newPreset: changeScript.newPreset.value
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
				presetID: document.getElementById('personalPreset').value
				},
			success: getPreset,
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
        topoID: document.getElementById('selectTopo').options[document.getElementById('selectTopo').selectedIndex].value,
        presetID: document.getElementById('selectPreset').options[document.getElementById('selectPreset').selectedIndex].value
				},
			success: getPresetTemplate,
			error: function(xhr, textStatus, errorThrown) {
					alert("Please report this error: "+errorThrown+xhr.status+xhr.responseText);
				}
		});
	}

	if(myAction=='createTest'){
		$.ajax({
			type: "POST",
			dataType: 'json',
			url: myURL,
			data: {
				action: myAction,
        			testName:document.getElementById('testName').value,
        			presetBody:document.getElementById('preview').value,
				product:document.getElementById('product').options[document.getElementById('product').selectedIndex].text,
				domain:document.getElementById('domain').options[document.getElementById('domain').selectedIndex].text,
				area:document.getElementById('area').options[document.getElementById('area').selectedIndex].text
				},
			success: createTest,
			error: function(xhr, textStatus, errorThrown) {
					alert("Please report this error: "+errorThrown+xhr.status+xhr.responseText);
				}
		});
	}

	if(myAction=='deleteTest'){
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
