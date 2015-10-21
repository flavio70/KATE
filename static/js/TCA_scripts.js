var releaseAry = new Array();
var areaAry = new Array();
var productAry = new Array();
var tunedAry = new Array();
var notTunedAry = new Array();
var tunedFolderAry = new Array();
var checkedFolderAry = new Array();
var reportAry = new Array();
var reportAryRT = new Array();
var orphanedTunedAry = new Array();
var orphanedTunedFolderAry = new Array();
var releasedAry = new Array();
var tunedTCary = new Array();
var tunedListAry = new Array();
var benches = new Array();
var availableAreas = new Array();
var localTestingAry = new Array();
var personalSuite = new Array();
var sharedSuite = new Array();
var testListString = new Array();
var tempBundleListString = new Array();
var bundleListString = new Array();
var filterAry = new Array(5);
var hiddenColumnAry = new Array();
var express = "";
var patternFilter = "";
var topologyFilter = "";
var facilityFilter = "";
var owner = "";
var checked = new Array();
checked[0] = new Array();
checked[1] = new Array();
checked[2] = new Array();
checked[3] = new Array();
checked[4] = new Array();
TSRTReport = new Array();
var totTPS = 0;
var totTime = 0;
var totMetric = 0;
var scrollReport;
var startingUp = false;
var checkRunning;
var semaforo=false;
var lstTemp,prmTemp,drcTemp,modifyTemp;
var totalSize,fileManReport,FileManIter; //for Menu Frame Settings
var highlighted;
var fileList = "";
var tsrtValues;
var resultCollectorValues;
var resultNotes = new Array();
var tsrtReport;
var tuningFile;
var tuneList;
var tuneBundle;
var commitment;
var personalPreset = new Array();
var sharedPreset = new Array();
var TAWSVersion = '2.2.4';


function insertBundleList(numAdd,position){
	myTable=top.principale.document.getElementById('testTable');
	if(position==''){addPosition='';}
		else{addPosition=position;}
	for(q=0;q<parseInt(numAdd);q++){
		for(i=1;i<myTable.rows.length;i++){
			if(myTable.rows[i].style.background=='red'){
				addRecordToTable(myTable.rows[i].name,'testBundleTable',addPosition);
				if(position!=''){addPosition++;}
			}
		}
	}
	if(position!=''){
		myTable2=top.principale.document.getElementById('testBundleTable');
		for(i=1;i<myTable2.rows.length;i++){
			myTable2.rows[i].cells[0].innerHTML=i;
		}
	}
	colorTable('testBundleTable');
	colorTable('testTable');
	updateStats('testBundleTable')
	updateStats('testTable')
	top.principale.document.getElementById('tuneBtn').disabled=true;
	//top.principale.document.getElementById('execBtn').disabled=true;
}

function deleteRequest(){
	deleteRequest2='';
	myTable=top.principale.document.getElementById('testTable');
	if((owner!='LOCAL')&&(myTable.rows.length>1)){
		for(i=1;i<myTable.rows.length;i++){
			if(myTable.rows[i].style.background=='red'){
				tempDelete=myTable.rows[i].name.split('#');
				deleteRequest2+=tempDelete[0]+'#['+tempDelete[1]+']-['+tempDelete[2]+']-['+tempDelete[4]+']'+tempDelete[6]+'$';
			}
		}
		top.accesso.pivot.action='accesso.asp?azione=deleteRequest';
		top.accesso.pivot.string1.value=deleteRequest2;
		top.accesso.pivot.submit();
	}
}

function insertAllBundleList(){
	document.getElementById('transparency').style.zIndex=10;
	document.getElementById('transparencyImg').style.visibility='visible';
	myTable=top.principale.document.getElementById('testTable');
	for(i=1;i<myTable.rows.length;i++){
		addRecordToTable(myTable.rows[i].name,'testBundleTable','');
	}
	colorTable('testBundleTable');
	updateStats('testBundleTable')
	top.principale.document.getElementById('tuneBtn').disabled=true;
	document.getElementById('transparency').style.zIndex=-1;
	document.getElementById('transparencyImg').style.visibility='hidden';
}

function removeBundleList(){
	myTable=top.principale.document.getElementById('testBundleTable');
	for(i=1;i<myTable.rows.length;i++){
		if(myTable.rows[i].style.background=='red'){
			myTable.deleteRow(i);
			i--
		}
	}
	updateStats('testBundleTable')
	colorTable('testBundleTable');
	top.principale.document.getElementById('tuneBtn').disabled=true;
	//top.principale.document.getElementById('execBtn').disabled=true;
}

function removeAllBundleList(){
	emptyTable('testBundleTable');
	updateStats('testBundleTable')
	top.principale.document.getElementById('tuneBtn').disabled=true;
	//top.principale.document.getElementById('execBtn').disabled=true;
}

function updateTestTable(tableName,testAry){
	//processing(true);
	emptyTable(tableName);
	for (i = 0;i < testAry.length; i++) {
		if(testAry[i]!=''){addRecordToTable(testAry[i],tableName,'');}
	}
	if(tableName=='testBundleTable'){updateStats(tableName);}
	colorTable(tableName);
	if(document.getElementById('reportTable')){createReportHistory();}
}

function addRecordToTable(testString,tableName,position){
	var myTable = document.getElementById(tableName);
	numCol=myTable.getElementsByTagName('th').length;
	if(tableName=='testTable'){checkedAry=0;}
	if(tableName=='testBundleTable'){checkedAry=1;}
	testCellAry=testString.split('#');
	if (position!=''){var row = myTable.insertRow(position);}
		else{var row = myTable.insertRow();}
	row.onmouseover = function(){Color(this,checkedAry);}
	row.onmouseout = function(){Decolor(this,checkedAry);}
	row.name = testString;
	row.id=testCellAry[0];
	row.onclick = function(){Check(this,checkedAry);}
	row.ondblclick = function(){if(owner!='LOCAL'){window.open('modifyList.asp?targetID='+this.id+'&action=show','name','height=700,width=1000,resizable=1');}}
	styleIndex=0;
	for(j = 0;j < numCol; j++) {
		if (document.all){var tempCell = row.insertCell();}
		if (dom){var tempCell = row.insertCell(j);}
		tempCell.style.textAlign = 'center';
		if((parseInt(myTable.rows[0].cells[j].name)==5)&&(testCellAry[5]!='-')){
			tps=testCellAry[5].split(',');
			for(tpsIndex=0;tpsIndex<tps.length-1;tpsIndex++){
				var textNode = top.principale.document.createTextNode(tps[tpsIndex]);
				tempCell.style.textAlign = 'center';
				tempCell.appendChild(textNode);
				var acccapo = top.principale.document.createElement("br");
				tempCell.style.textAlign = 'center';
				tempCell.appendChild(acccapo);
			}
			var textNode = top.principale.document.createTextNode(tps[tpsIndex]);
			tempCell.style.textAlign = 'center';
			tempCell.appendChild(textNode);
		}else{
			var textNode = document.createTextNode(testCellAry[myTable.rows[0].cells[j].name]);
		}
		if(parseInt(myTable.rows[0].cells[j].name)==6){
			tempCell.style.textAlign = 'left';
			textNode = document.createElement ('A');
			toolTipText='TEST ID : '+testCellAry[0];
			toolTipText+='\nMAX ITERATION : '+testCellAry[13];
			toolTipText+='\nFull Path : '+testCellAry[20];
			toolTipText+='\nPRODUCT : '+testCellAry[1];
			toolTipText+='\nSW Release : '+testCellAry[2];
			toolTipText+='\nDependency : '+testCellAry[12];
			toolTipText+='\nExecution Assignment : '+testCellAry[10];
			toolTipText+='\nAuthor : '+testCellAry[14];
			toolTipText+='\nLast Update : '+testCellAry[16];
			if(testCellAry[17]=='A'){toolTipText+='\nTest Status : OK';}
				else{toolTipText+='\nTest Status : TO BE CHECKED';}
			toolTipText+='\nDescription : '+testCellAry[15];
			textNode.setAttribute("title",toolTipText)
			textone=testCellAry[6];
			textNode.appendChild (document.createTextNode (textone));
			tempCell.style.textAlign = 'left';
		}
		if(parseInt(myTable.rows[0].cells[j].name)==0){var textNode = document.createTextNode(myTable.rows.length-1);}
		if(parseInt(myTable.rows[0].cells[j].name)==7){var textNode = document.createTextNode(seconds2Time(testCellAry[7]));}
		if(parseInt(myTable.rows[0].cells[j].name)==9){tempCell.onclick = function(){window.open('topologyViewer.asp?myTopology='+this.innerText,'name','height=600,width=800,resizable=1');}}
		switch(true){
			case ((parseInt(myTable.rows[0].cells[j].name)==10)||(parseInt(myTable.rows[0].cells[j].name)==12)||(parseInt(myTable.rows[0].cells[j].name)==17)):
				var cellImage = document.createElement("IMG");
				if((testCellAry[myTable.rows[0].cells[j].name]=='NOT ASSIGNED')||((testCellAry[myTable.rows[0].cells[j].name]!='NA')&&(parseInt(myTable.rows[0].cells[j].name)==12))||(testCellAry[myTable.rows[0].cells[j].name]=='C')){
					cellImage.setAttribute('src','/images/KO.gif');
				}else{
					cellImage.setAttribute('src','/images/OK.gif');
				}
				tempCell.appendChild(cellImage);
				break;
			case ((parseInt(myTable.rows[0].cells[j].name)==18)&&(tableName=='testTable')):
				livArray=testCellAry[18].split('!');
				var livraison = document.createElement("select");
				for(q=0;q<livArray.length;q++){
					livraison.options[q] = new Option(livArray[q],livArray[q]);
				}
				//livraison.style.width="90%";
				//result.style.height="100%";
				//result.style.padding="3px";
				livraison.style.fontSize="7pt";
				livraison.onchange=function(){
												tempArray=this.parentElement.parentElement.name.split('#');
												tempArray[18]=this.value;
												this.parentElement.parentElement.name=tempArray.join('#');
											}
				tempArray=row.name.split('#');
				tempArray[18]=livArray[0];
				row.name=tempArray.join('#');
				tempCell.appendChild(livraison);
				break;
			default:
				tempCell.appendChild(textNode);
		}
		if(myTable.rows[0].cells[tempCell.cellIndex+styleIndex].style.display=='none'){tempCell.style.display='none';styleIndex++;}
	}
	if(row.clientHeight<18&&myTable.id=='testBundleTable'){row.style.height=18;}
}


function openDoc(docString){
 newwindow = window.open(docString);
}

function updateStats(totalTable){
	var myTable = document.getElementById(totalTable);
	tot1 = 0
	tot2 = 0
	tot3 = 0
	tot4 = 0
	for(i=1;i<myTable.rows.length;i++){
		tempAry=myTable.rows[i].name.split('#');
		tempTPS=tempAry[5].split(',');
		if(((totalTable=='testTable')&&(myTable.rows[i].style.background=='red'))||(totalTable=='testBundleTable')){
			tot1=tot1+1;
			tot2=tot2+parseInt(tempTPS.length);
			tot3=tot3+parseInt(tempAry[7]);
			tot4=tot4+parseInt(tempAry[8]);
		}
	}
	if(totalTable=='testTable'){tableName='selected';}
	if(totalTable=='testBundleTable'){tableName='bundle';}
	tot3=seconds2Time(tot3);
	document.getElementById(tableName + "Number").innerHTML  = tot1;
	document.getElementById(tableName + "TPS").innerHTML  = tot2;
	document.getElementById(tableName + "Time").innerHTML  = tot3;
	document.getElementById(tableName + "Metric").innerHTML  = tot4;
}

function Color(t,io){
	if(t.style.background!='red'){
		t.style.background='orange';
	}
}

function Decolor(t,io){
	if(t.style.background!='red'){
		if(t.rowIndex%2){
			t.style.background='white';
		}else{
			t.style.background='#eeeeee';
		}
	}
}

function Check(t,io){
	if(t.style.background!='red'){t.style.background='red';}
		else{
			if(t.rowIndex%2){
				t.style.background='white';
			}else{
				t.style.background='#eeeeee';
			}
		}
	updateStats(t.parentNode.parentNode.id);
}

function updateSelectList(bundleString2,listName){
	var myBundle2 = document.getElementById(listName);
	myBundle2.options.length=0;
	bundleListString2 = bundleString2.split("$");
	if((listName != "selectReport") && (listName != "reportSummary") && (listName != "runningList")){
		var addTest = document.createElement('option');
		addTest.text = "Select File...";
		addTest.value = "";
		try {
		   myBundle2.add(addTest, null); // standards compliant; doesn't work in IE
		  }
		 catch(ex) {
		   myBundle2.add(addTest); // IE only
		}
	}
	for (i = 0;i < bundleListString2.length-1; i++) {
		if(listName=='selectBundle' || listName=='loadBundle'){
			if(bundleListString2[i].match('TUNED')==null && listName=='loadBundle'){
				var addTest = document.createElement('option');
				addTest.text = bundleListString2[i];
				addTest.value = bundleListString2[i];
				myBundle2.add(addTest); // IE only
			}
			if(bundleListString2[i].match('TUNED')!=null && listName=='selectBundle'){
				var addTest = document.createElement('option');
				addTest.text = bundleListString2[i];
				addTest.value = bundleListString2[i];
				myBundle2.add(addTest); // IE only
			}
		}else{
			var addTest = document.createElement('option');
			tempElement = bundleListString2[i].split('#');
			addTest.text = tempElement[0];
			addTest.value = tempElement[0];
			myBundle2.add(addTest); // IE only
		}
	}
	if(startingUp){
		startingUp = false;
		parent.accesso.location.href = 'accesso.asp';
	}
}


function browseLocal(){
	if(owner!='LOCAL'){
		emptyTable('testBundleTable');
		owner='LOCAL';
	}
	document.getElementById('saveLocal').disabled=false;
	document.getElementById('savePersonal').disabled=true;
	document.getElementById('saveShared').disabled=true;
	document.getElementById('topoA').disabled=true;
	document.getElementById('topoB').disabled=true;
	document.getElementById('topoC').disabled=true;
	document.getElementById('topoD').disabled=true;
	document.getElementById('facility').disabled=true;
	document.getElementById('pattern').disabled=true;
	document.getElementById('filterString').disabled=true;
	document.getElementById('clearBtn').disabled=true;
	document.getElementById('serverPersonalSuite').selectedIndex=0;
	document.getElementById('serverSharedSuite').selectedIndex=0;
	document.getElementById('product').selectedIndex=0;
	document.getElementById('SWrelease').selectedIndex=0;
	document.getElementById('area').selectedIndex=0;
	updateTestTable('testTable',localTestingAry);
	//for(i=0;i<29;i++){document.getElementById(i).disabled=true;}
	owner='LOCAL';
	//document.getElementById('assign').disabled=true;
}

function deleteFile(deleteName){
	if(deleteName.value!=''){
		selectTest.action = 'accesso.asp?azione=deletesuite';
		selectTest.target = "connection";
		selectTest.savingStringValue.value = deleteName.value;
		if(confirm("Are you sure you want to delete " + deleteName.options[deleteName.selectedIndex].text +"?")){selectTest.submit();}
	}
}

function deleteFileLocal(deleteName){
	if(deleteName.value!=''){
		selectTest.action = 'pythonAccess.asp?azione=deletesuite';
		selectTest.target = "connection";
		selectTest.targetFile.value = deleteName.value;
		if(confirm("Are you sure you want to delete " + deleteName.options[deleteName.selectedIndex].text +"?")){selectTest.submit();}
	}
}

function filter(t){
	topoFilter='';
	topologyFilter='';
	facilityFilter='';
	patternFilter=document.getElementById('pattern').value;
	//assignFilter=document.getElementById('assign').checked;
	assignFilter=false;
	for(i=0;i<20;i++){
		if(document.getElementById(i).checked){topologyFilter+=document.getElementById(i).name+'|';}
	}
	if(topologyFilter.charAt(topologyFilter.length-1)=='|'){topologyFilter=topologyFilter.slice(0,topologyFilter.length-1);}
	for(i=20;i<29;i++){
		if(document.getElementById(i).checked){facilityFilter+=document.getElementById(i).name+'|';}
	}
	if(facilityFilter.charAt(facilityFilter.length-1)=='|'){facilityFilter=facilityFilter.slice(0,facilityFilter.length-1);}
	parent.accesso.location.href='accesso.asp?azione=getTestCasesFromDB&product='+document.getElementById('product').value+'&SWrelease='+document.getElementById('SWrelease').value+'&area='+document.getElementById('area').value+'&topologyFilter='+topologyFilter+'&facilityFilter='+facilityFilter+'&patternFilter='+patternFilter+'&assignFilter='+assignFilter;
}

function seconds2Time(seconds){
	mySeconds = 0;
	myMinutes = '';
	myHours = '';
	myDays = '';
	if(seconds > 0){
		mySeconds = seconds % 60;
			if(seconds >= 60){
				myMinutes = (seconds - mySeconds)/60;
				if(mySeconds < 10){mySeconds = '0' + mySeconds;}
				if(myMinutes >= 60){
					myHours = (myMinutes - (myMinutes % 60))/60;
					myMinutes = myMinutes % 60;
					if(myMinutes < 10){myMinutes = '0' + myMinutes;}
					myMinutes = myMinutes + ':';
					if(myHours >= 24){
						myDays = (myHours - (myHours % 24))/24;
						myHours = myHours % 24;
						if(myHours < 10){myHours = '0' + myHours;}
						myHours = myHours + ':';
						myDays = myDays + ':';
					}else{myHours = myHours + ':';}
				}else{myMinutes = myMinutes + ':';}
			}
		}
	return myDays+myHours+myMinutes+mySeconds;
}

function time2Seconds(myTime){
	timeAry = myTime.split(":");
	if(timeAry.length > 0){
		if(timeAry.length > 1){myTime = parseInt(timeAry[timeAry.length-1]) + (parseInt(timeAry[timeAry.length-2])*60);}
		if(timeAry.length > 2){myTime = myTime + (parseInt(timeAry[timeAry.length-3])*60);}
		if(timeAry.length > 3){myTime = myTime + (parseInt(timeAry[timeAry.length-4])*24);}
	}
	return myTime;
}

function emptyTable(tbl){
	var myTable = document.getElementById(tbl);
	if(myTable){
		var numRow = myTable.rows;
		iterations = numRow.length;
		if(iterations > 1){
			for(i=0;i<iterations-1;i++){
				myTable.deleteRow(1);
			}
		}
	}
}

function popitup(url) {
	if(rightclicked != ''){
		if(url == 'details.asp'){
			newwindow=window.open(url,'name','height=500,width=600,resizable=1');
			if (window.focus) {newwindow.focus()}
			return false;
		}else{
			tempChecked = rightclicked.split("#");
			parent.accesso.location.href = 'accesso.asp?azione=scriptModify&scriptTarget=' + escape(tempChecked[6].replace(/\\/g,"/") + tempChecked[1]);
		}
	}
}

function saveFile(selectId,ownership){
	owner=ownership;
	saveID=selectId.value;
	saveText=selectId.options[selectId.selectedIndex].text;
	path=selectId.id;
	savingString='';
	if(saveText!='Select Here'){
		saveText = prompt('Insert Suite Name!',saveText)
	}else{
		saveText = prompt('Insert Suite Name!','newSuite.mlt');
	}
	if(saveText!=null){
		if(saveText.substr((saveText.length - 4),(saveText.length - 1))!='.mlt'){saveText+='.mlt';}
		foundSuite=false;
		parent.accesso.document.pivot.string3.value=ownership;
		for(i=1;i<selectId.options.length;i++){
			if(selectId.options[i].text==saveText){
				foundSuite=true;
				if(owner!='LOCAL'){saveID=selectId.options[i].value;}
				break;
			}
		}
		if(foundSuite==false){saveID=saveText;}
		myTable=top.principale.document.getElementById('testBundleTable');
		for(i=1;i<myTable.rows.length;i++){
			tempAry = myTable.rows[i].name.split("#");
			savingString +=tempAry[0] + "$";
		}
		parent.accesso.document.pivot.string1.value = savingString;
		parent.accesso.document.pivot.string2.value = saveID.replace(/'/g,"");
		parent.accesso.document.pivot.action = "accesso.asp?azione=savesuite";
		if((foundSuite==true&&confirm("Overwrite " + saveText +"?"))||foundSuite==false){
			parent.accesso.document.pivot.submit();
		}
	}
}

function jsaveFile(selectId,ownership){
	owner=ownership;
	saveID=selectId.value;
	saveText=selectId.options[selectId.selectedIndex].text;
	path=selectId.id;
	savingString='';
	if(saveText!='Select Here'){
		saveText = prompt('Insert Suite Name!',saveText)
	}else{
		saveText = prompt('Insert Suite Name!','newSuite');
	}
	if(saveText!=null){
		//if(saveText.substr((saveText.length - 4),(saveText.length - 1))!='.mlt'){saveText+='.mlt';}
		foundSuite=false;
		parent.accesso.document.pivot.string3.value=ownership;
		for(i=1;i<selectId.options.length;i++){
			if(selectId.options[i].text==saveText){
				foundSuite=true;
				if(owner!='LOCAL'){saveID=selectId.options[i].value;}
				break;
			}
		}
		if(foundSuite==false){saveID=saveText;}
		myTable=top.principale.document.getElementById('testBundleTable');
		for(i=1;i<myTable.rows.length;i++){
			tempAry = myTable.rows[i].name.split("#");
			savingString +=tempAry[0] + "#" + tempAry[18] + "$";
		}
		parent.accesso.document.pivot.string1.value = savingString;
		parent.accesso.document.pivot.string2.value = saveID.replace(/'/g,"");
		parent.accesso.document.pivot.action = "accesso.asp?azione=jsavesuite";
		if((foundSuite==true&&confirm("Overwrite " + saveText +"?"))||foundSuite==false){
			parent.accesso.document.pivot.submit();
		}
	}
}

function saveFileLocal(selectId,ownership){
	owner=ownership;
	saveID=selectId.value;
	saveText=selectId.options[selectId.selectedIndex].text;
	savingString='';
	if(saveText!='Select Here'){
		saveText = prompt('Insert Suite Name!',saveText)
	}else{
		saveText = prompt('Insert Suite Name!','newSuite.mlt');
	}
	if(saveText!=null){
		if(saveText.substr((saveText.length - 4),(saveText.length - 1))!='.mlt'){saveText+='.mlt';}
		foundSuite=false;
		//parent.accesso.document.pivot.string3.value=ownership;
		for(i=1;i<selectId.options.length;i++){
			if(selectId.options[i].text==saveText){
				foundSuite=true;
				if(owner!='LOCAL'){saveID=selectId.options[i].value;}
				break;
			}
		}
		if(foundSuite==false){saveID=saveText;}
		myTable=top.principale.document.getElementById('testBundleTable');
		for(i=1;i<myTable.rows.length;i++){
			tempAry = myTable.rows[i].name.split("#");
			savingString +=tempAry[0] + "\n";
		}
		selectTest.saveBody.value = savingString;
		selectTest.targetFile.value = saveID.replace(/'/g,"");
		//parent.accesso.document.pivot.action = "accesso.asp?azione=savesuite";
		selectTest.action='pythonAccess.asp?azione=savesuite';
		selectTest.target='connection';
		if((foundSuite==true&&confirm("Overwrite " + saveText +"?"))||foundSuite==false){
			selectTest.submit();
		}
	}
}

function confirmSaving(file,alreadyPresent,action){
	if(action == "save"){
		savingString = "";
		myTable=top.principale.document.getElementById('testBundleTable');
		for(i=1;i<myTable.rows.length;i++){
			tempAry = myTable.rows[i].name.split("#");
			savingString +=tempAry[0] + "$";
		}
		parent.accesso.document.pivot.string1.value = savingString;
		parent.accesso.document.pivot.string2.value = file;
		parent.accesso.document.pivot.string3.value = 'reload';
		parent.accesso.document.pivot.action = "accesso.asp?azione=save";
		if(alreadyPresent == "True"){
			if(confirm("Overwrite " + file +"?")){
				parent.accesso.document.pivot.submit();}
		}else{
			parent.accesso.document.pivot.string3.value = 'nuovo';
			parent.accesso.document.pivot.submit();
			var myBundle2 = top.principale.document.getElementById('loadBundle');
			var newTestSuite = document.createElement('option');
			try {
			   myBundle2.add(newTestSuite, null); // standards compliant; doesn't work in IE
			  }
			 catch(ex) {
			   myBundle2.add(newTestSuite); // IE only
			}
			for(k=0;k<=myBundle2.length-1;k++){
				if(myBundle2.options[k].value == tempName[tempName.length-1]){
					myBundle2.selectedIndex = k;
				}
			}
			myBundle2.value=tempName[tempName.length-1];
		}
	}else{
	}
}

function emptyChecked(io){
	iterations = checked[io].length;
	for(k=0;k<iterations;k++){
		res = checked[io].pop();
	}
}

function checkRun(){
	checkDescription = document.changeScript.changeDescription.value.replace(/'/g,"");
	checkDescription = checkDescription.replace(/$/g,"");
	checkDescription = checkDescription.replace(/#/g,"");
	checkDescription = checkDescription.replace(/\\/g,"");
	checkDescription = checkDescription.replace(/\n/g,"Description:");
	document.changeScript.changeValues.value = "#" + testName.innerHTML + "#" + time2Seconds(document.changeScript.changeDuration.value) + "#" + document.changeScript.changeMetric.value + "#" + document.changeScript.changeNode.value + "#" + checkDescription;
	if(confirm("Change Values for " + document.changeScript.scriptPath.value + "?\n   Duration = " + document.changeScript.changeDuration.value + "\n   Metric = " + document.changeScript.changeMetric.value + "\n   Target Node = " + document.changeScript.changeNode.value  + "\n   Description = " + checkDescription))
	{document.changeScript.submit();}
}

if (document.getElementById){
document.write('<style type="text/css">\n')
document.write('.menu_int{display: none;}\n')
document.write('</style>\n')
}

function setMenuSize(){
	totalSize = 14
	for(i=0;i<document.getElementById('menu').getElementsByTagName("div").length;i++){
		totalSize = totalSize + document.getElementById('linkMenu(' + i + ')').clientHeight;
	}
	if(document.getElementById('sub1').style.display == "block"){
		totalSize = totalSize + document.getElementById('sub1').clientHeight + 8;
	}
	if(parent.principale.checked[0].length != 0){
		totalSize += 20;
	}
	parent.document.getElementById('frameLeft').rows='135,' + totalSize + ',*';
}

function SwitchMenu(obj){
	oldSize = parent.parent.document.getElementById('frameLeft').rows.split(",");
	if(document.getElementById(obj)){
	var el = document.getElementById(obj);
	var ar = document.getElementById("menu").getElementsByTagName("span");
		if(el.style.display != "block"){
			for (var i=0; i<ar.length; i++){
				if (ar[i].className=="menu_int")
				ar[i].style.display = "none";
			}
			el.style.display = "block";
		}else{
			el.style.display = "none";
		}
		//setMenuSize();
	}else{
		var ar = document.getElementById("menu").getElementsByTagName("span");
		for (var i=0; i<ar.length; i++){
				if (ar[i].className=="menu_int")
				ar[i].style.display = "none";
				//setMenuSize();
				//parent.document.getElementById('frameLeft').rows='135,' + totalSize + ',*';
				//var myTable = parent.parent.descriptionFrame.document.getElementById("descriptionTable");
				//myTable.document.getElementById("descriptionCell").innerHTML = "";
			}
	}
}

var x1 = 11;   // change the # on the left to adjust the X co-ordinate
var y1 = 250;  // change the # on the left to adjust the Y co-ordinate

(document.getElementById && !document.all) ? dom = true : dom = false;

function typeStart() {
  if (dom) {
	document.write('<div id="logoBox" style="position:absolute; z-index:1; left:' + ((document.getElementById("slidingButtons").offsetLeft+(document.getElementById("slidingButtons").clientWidth/2))-22) + 'px; top:' + (document.getElementById("slidingButtons").offsetTop) + 'px; visibility:visible">');
	}
  if (document.all) {
   document.write('<div id="logoBox" style="position:absolute; z-index:1; left:' + ((document.getElementById("slidingButtons").offsetLeft+(document.getElementById("slidingButtons").clientWidth/2))-15) + 'px; top:' + (document.getElementById("slidingButtons").offsetTop) + 'px; visibility:visible">');
   }
 }

function typeEnd() {
  if (document.all || dom) { document.write('</div>') }
 }

function placeIt() {
  if (dom) {document.getElementById("logoBox").style.top = document.body.scrollTop + y1 + "px"; document.getElementById("logoBox").style.left = document.body.scrollLeft + ((document.getElementById("slidingButtons").offsetLeft+(document.getElementById("slidingButtons").clientWidth/2))-25) + x1 + "px";}
  if (document.all) {document.all["logoBox"].style.top = document.body.scrollTop + y1 + "px"; document.all["logoBox"].style.left = document.body.scrollLeft + ((document.getElementById("slidingButtons").offsetLeft+(document.getElementById("slidingButtons").clientWidth/2))-15) + "px";}
  window.setTimeout("placeIt()", 10);
 }

// Multiple onload function created by: Simon Willison
// http://simonwillison.net/2004/May/26/addLoadEvent/
function addLoadEvent(func) {
  var oldonload = window.onload;
  if (typeof window.onload != 'function') {
    window.onload = func;
  } else {
    window.onload = function() {
      if (oldonload) {
        oldonload();
      }
      func();
    }
  }
}

function retrieveValues2(){
	var stringa = "";
	for(i=0;i<document.myForm.checks.length;i++){
		if(document.myForm.checks[i].checked){
			ext1 = document.myForm.checks[i].id.substr((document.myForm.checks[i].id.length - 4),(document.myForm.checks[i].id.length - 1));
			pref = document.myForm.checks[i].id.substr(0,(document.myForm.checks[i].id.length - 4));
			if((ext1 == ".lst") || (ext1 == ".prm") || (ext1 == ".drc")){
				var found = 0,foundChk = 0;
				for(j=0;j<document.myForm.checks.length;j++){
					if(document.myForm.checks[j].id == pref + ".lst"){found += 1;if(document.myForm.checks[j].checked){foundChk += 1;}}
					if(document.myForm.checks[j].id == pref + ".prm"){found += 1;if(document.myForm.checks[j].checked){foundChk += 1;}}
					if(document.myForm.checks[j].id == pref + ".drc"){found += 1;if(document.myForm.checks[j].checked){foundChk += 1;}}
				}
				if(found != foundChk){
					if(confirm("Prevent orphaned scripts for " + document.myForm.checks[i].id + "?")){
						stringa += pref + ".lst#" + pref + ".prm#" + pref + ".drc#";
					}else{
						stringa += document.myForm.checks[i].id + "#";
					}
				}else{
					stringa += document.myForm.checks[i].id + "#";
				}
			}else{
				stringa += document.myForm.checks[i].id + "#";
			}
		}
	}
	document.myForm.names.value = stringa;
}

function fileMan2(){
	fileManReport = "";
	FileManIter = 0;
	if(confirm("Are you sure you want to delete?")){
		setTimeout(waitFileManager(),5000);
	}
}

function waitFileManager2(){
	if(FileManIter == 0){
		document.myForm.action = 'http://151.98.47.103/frames/accesso.asp?azione=fileManager';
		document.myForm.submit();
		FileManIter += 1;
	}
	if(FileManIter == 1){
		document.myForm.action = 'http://151.98.152.147/frames/accesso.asp?azione=fileManager';
		document.myForm.submit();
		FileManIter += 1;
	}
	if(FileManIter == 2){
		document.myForm.action = 'http://151.98.152.162/frames/accesso.asp?azione=fileManager';
		document.myForm.submit();
		self.location.reload();
	}
}

function colorTable(tableName){
	var myRows = document.getElementById(tableName).rows;
	for(k = 0;k < myRows.length-1;k++){
		if (k%2){myRows[k+1].style.background='#eeeeee';}
			else{myRows[k+1].style.background='white';}
	}
}

function getNodeIP2(node){
	switch(node){
		case "A":
			nodeIP = "151.98.153.130";
			break;
		case "B":
			nodeIP = "151.98.153.131";
			break;
		case "C":
			nodeIP = "151.98.153.132";
			break;
		case "C":
			nodeIP = "151.98.152.103";
			break;
		default:
			nodeIP = "???";
	}
	return nodeIP;
}

function getFrameRunATM2(pc){
	switch(pc){
		case "151.98.47.103":
			myFrame = top.principale.frames['dario'];
			break;
		case "151.98.40.140":
			myFrame = top.principale.frames['mario'];
			break;
		case "151.98.152.162":
			myFrame = top.principale.frames['ipa162'];
			break;
		case "151.98.152.147":
			myFrame = top.principale.frames['pclag2'];
			break;
		default:
			myFrame = top.principale;
	}
	return myFrame;
}

function fillLocalRunTable2(report,testString,runningName,counter){
	top.principale.document.all.c.innerHTML = report;
	top.principale.document.all.c.style.color = 'green';
	if(report == 'STOPPED'){
		top.principale.document.all.c.style.color = 'red';
		top.principale.checkATMStatus(false);
		top.principale.document.getElementById('pollingTime').selectedIndex = 0;
		top.principale.document.getElementById('followOutput').checked = false;
		top.principale.changePolling("");
		top.principale.document.getElementById('RUNbtn').disabled = false;
		top.principale.document.getElementById('KILLbtn').disabled = true;
		top.principale.document.getElementById('selectBundle').disabled = false;
		top.principale.updateSelectList(testString,'runningList');
	}else{
		var mySelect = top.principale.document.getElementById('selectBundle');
		if(top.principale.document.getElementById('RUNbtn').disabled == false){
			for(i=0;i<=mySelect.length-1;i++){
				if(mySelect.options[i].value == runningName){
					mySelect.selectedIndex = i;
				}
			}
			top.principale.document.getElementById('RUNbtn').disabled = true;
			top.principale.document.getElementById('KILLbtn').disabled = false;
			top.principale.updateSelectList(testString,'runningList');		
			mySelect.disabled = true;
			top.principale.document.getElementById('runningList').selectedIndex = parseInt(counter);
			if(testString != 'Launched manually$'){top.principale.checkATMStatus(true);}
		}else{
			top.principale.document.getElementById('runningList').selectedIndex = parseInt(counter);
		}
	}
}

function fillRunTable(report,runningName,testString,suiteOwner,startingDate,testSummary,targetBench,SWP,timeAry,totTime,elapsedTime,remainingTime,exstimatedTime,tableName,reportButton,storedDur,realDur,tawsdb){
	myTable=top.principale.document.getElementById(tableName);
	TCEntry=testString.split("$");
	TCResult=testSummary.split("$");
	timeList=timeAry.split("$");
	storedDurList=storedDur.split("$");
	realDurList=realDur.split("$");
	if(top.principale.document.getElementById('ATMStatus').childNodes.length!=0){
		top.principale.document.getElementById('ATMStatus').removeChild(top.principale.document.getElementById('ATMStatus').childNodes[0]);
		top.principale.document.getElementById('suite').removeChild(top.principale.document.getElementById('suite').childNodes[0]);
		top.principale.document.getElementById('owner').removeChild(top.principale.document.getElementById('owner').childNodes[0]);
		while(top.principale.document.getElementById('targetBench').hasChildNodes()){
			top.principale.document.getElementById('targetBench').removeChild(top.principale.document.getElementById('targetBench').lastChild);
		}
		//top.principale.document.getElementById('targetBench').removeChild(top.principale.document.getElementById('targetBench').childNodes[0]);
		top.principale.document.getElementById('SWP').removeChild(top.principale.document.getElementById('SWP').childNodes[0]);
		top.principale.document.getElementById('start').removeChild(top.principale.document.getElementById('start').childNodes[0]);
		if(tableName!='runListTable'){top.principale.document.getElementById('tawsdb').removeChild(top.principale.document.getElementById('tawsdb').childNodes[0]);}
		if(tableName=='runListTable'){
			top.principale.document.getElementById('totTime').removeChild(top.principale.document.getElementById('totTime').childNodes[0]);
			top.principale.document.getElementById('elapsedTime').removeChild(top.principale.document.getElementById('elapsedTime').childNodes[0]);
			top.principale.document.getElementById('remainingTime').removeChild(top.principale.document.getElementById('remainingTime').childNodes[0]);
			top.principale.document.getElementById('exstimatedTime').removeChild(top.principale.document.getElementById('exstimatedTime').childNodes[0]);
		}
	}
	var textNode = top.principale.document.createTextNode(report);
	top.principale.document.getElementById('ATMStatus').appendChild(textNode);
	var textNode = top.principale.document.createTextNode(runningName);
	top.principale.document.getElementById('suite').appendChild(textNode);
	var textNode = top.principale.document.createTextNode(suiteOwner);
	top.principale.document.getElementById('owner').appendChild(textNode);
	tempTarget=targetBench.split('#');
	for(i=0;i<tempTarget.length;i++){
		if(i>0){
			var acccapo = top.principale.document.createElement("br");
			top.principale.document.getElementById('targetBench').appendChild(acccapo);
		}
		if(isNaN(tempTarget[i])==false){tempTarget[i]='AUTO-'+tempTarget[i];}
		var textNode = top.principale.document.createTextNode(tempTarget[i]);
		top.principale.document.getElementById('targetBench').appendChild(textNode);
	}
	var textNode = top.principale.document.createTextNode(SWP);
	top.principale.document.getElementById('SWP').appendChild(textNode);
	var textNode = top.principale.document.createTextNode(startingDate);
	top.principale.document.getElementById('start').appendChild(textNode);
	var textNode = top.principale.document.createTextNode(seconds2Time(totTime));
	if(tableName=='runListTable'){
		top.principale.document.getElementById('totTime').appendChild(textNode);
		var textNode = top.principale.document.createTextNode(seconds2Time(elapsedTime));
		top.principale.document.getElementById('elapsedTime').appendChild(textNode);
		var textNode = top.principale.document.createTextNode(seconds2Time(remainingTime));
		top.principale.document.getElementById('remainingTime').appendChild(textNode);
		var textNode = top.principale.document.createTextNode(exstimatedTime);
		top.principale.document.getElementById('exstimatedTime').appendChild(textNode);
		var mySelect = top.principale.document.getElementById('selectBundle');
	}
	if(tableName!='runListTable'){
		var textNode = top.principale.document.createTextNode(tawsdb);
		top.principale.document.getElementById('tawsdb').appendChild(textNode);
	}
	if(report != 'STOPPED'||report == 'READY'){
		if(tableName=='runListTable'){
			//top.principale.document.getElementById('RUNbtn').disabled = true;
			top.principale.document.getElementById('KILLbtn').disabled = false;
			top.principale.document.getElementById('createRunBtn').disabled = true;
			//top.principale.runTest.target.disabled = true;
			//top.principale.runTest.SWRelease.disabled = true;
			//top.principale.runTest.selectBench.disabled = true;
			mySelect.disabled = true;
		}
		while(myTable.rows.length>1){myTable.deleteRow(myTable.rows.length-1);}
		for(i=1;i<TCEntry.length-1;i++){
			testName=TCEntry[i-1].split("\\");
			if(i<TCResult.length){tempResult=TCResult[i-1].split("#");}
				else{tempResult='#'.split("#");}
			if (document.all){var row = myTable.insertRow();}
			if (dom){var row = myTable.insertRow(i+1);}
			if (document.all){var tempCell = row.insertCell();}
			if (dom){var tempCell = row.insertCell(i);}
			var textNode = top.principale.document.createTextNode(i);
			tempCell.style.borderBottom = "inset #999999 1px";
			tempCell.appendChild(textNode);
			if(tempResult.length>2){tempCell.rowSpan=tempResult.length-2;}
			if (document.all){var tempCell = row.insertCell();}
			if (dom){var tempCell = row.insertCell(i);}
			row.style.color='#000000';
			if(testName.length>1){
				var textNode = top.principale.document.createTextNode(testName[testName.length-2]+'\\'+testName[testName.length-1]);
			}else{
				if(testName[testName.length-1].match("%")!=null){
					tempTitle=testName[testName.length-1].split("%");
					var textNode = top.principale.document.createTextNode(tempTitle[2]);
					tempCell.title=tempTitle[1];
				}else{
					var textNode = top.principale.document.createTextNode(testName[testName.length-1]);
				}
			}
			tempCell.style.borderBottom = "inset #999999 1px";
			tempCell.appendChild(textNode);
			if(tempResult.length>2){tempCell.rowSpan=tempResult.length-2;}
			if(tableName=='runListTable'){
				if (document.all){var tempCell = row.insertCell();}
				if (dom){var tempCell = row.insertCell(i);}
				var textNode = top.principale.document.createTextNode(seconds2Time(timeList[i-1]));
				tempCell.style.borderBottom = "inset #999999 1px";
				tempCell.appendChild(textNode);
				if(tempResult.length>2){tempCell.rowSpan=tempResult.length-2;}
				tempCell.style.textAlign = 'center';
			}
			if (i%2){row.style.background='#eeeeee';}
				else{row.style.background='white';}
			if(tableName!='runListTable'){
				tempCell = row.insertCell();
				var reportBtn = top.principale.document.createElement("input");
				reportBtn.disabled=true;
				reportBtn.type="button";
				reportBtn.value="View";
				if(reportButton=='viewReport'){
					reportBtn.id=[i-1];
					//reportBtn.onclick=function(){top.accesso.location.href="accesso.asp?azione=getReportTrunk&reportName=" + runningName + "&reportTrunk=" + this.id;}
					reportBtn.onclick=function(){newwindow=window.open('viewReportTrunk.asp?reportName=' + runningName + '&reportTrunk=' + this.id,'viewReportTrunk','height=600,width=1000,resizable=1');}
					reportBtn.disabled=false;
				}
				reportBtn.style.fontSize="6pt";
				tempCell.style.textAlign = 'center';
				tempCell.style.borderBottom = "inset #999999 1px";
				reportBtn.disabled=false;
				tempCell.appendChild(reportBtn);
			}
			if(tableName!='runListTable'){
				if(tempResult.length>2){tempCell.rowSpan=tempResult.length-2;}
				if (document.all){var tempCell = row.insertCell();}
				if (dom){var tempCell = row.insertCell(i);}
				var textNode = top.principale.document.createTextNode('Exp:');
				tempCell.style.textAlign = 'left';
				tempCell.appendChild(textNode);
				var acccapo = top.principale.document.createElement("br");
				tempCell.style.textAlign = 'left';
				tempCell.appendChild(acccapo);
				var textNode = top.principale.document.createTextNode('Act:');
				tempCell.style.textAlign = 'left';
				tempCell.style.borderBottom = "inset #999999 1px";
				tempCell.appendChild(textNode);
				if(tempResult.length>2){tempCell.rowSpan=tempResult.length-2;}
				if (document.all){var tempCell = row.insertCell();}
				if (dom){var tempCell = row.insertCell(i);}
				var textNode = top.principale.document.createTextNode(seconds2Time(storedDurList[i-1]));
				tempCell.style.textAlign = 'right';
				tempCell.appendChild(textNode);
				var acccapo = top.principale.document.createElement("br");
				tempCell.style.textAlign = 'left';
				tempCell.appendChild(acccapo);
				if(realDurList.length>=i){
					tempDur = realDurList[i-1].split("#");
					var textNode = top.principale.document.createTextNode(seconds2Time(tempDur[1]));
					tempCell.style.textAlign = 'right';
					tempCell.style.borderBottom = "inset #999999 1px";
					tempCell.appendChild(textNode);
					if(tempResult.length>2){tempCell.rowSpan=tempResult.length-2;}
					if (document.all){var tempCell = row.insertCell();}
					if (dom){var tempCell = row.insertCell(i);}
					var sendTimeUpd = top.principale.document.createElement("input");
					sendTimeUpd.type="checkbox";
					//if((tempDur[1]>30)&&((tempDur[1]<storedDurList[i-1]-30)||(tempDur[1]>storedDurList[i-1]+30))){
					if(Math.abs(tempDur[1]-storedDurList[i-1])>30){
						sendTimeUpd.defaultChecked=true;
						sendTimeUpd.disabled=false;
					}else{
						sendTimeUpd.disabled=true;
						sendTimeUpd.defaultChecked=false;
					}
					sendTimeUpd.id=realDurList[i-1];
					tempCell.style.borderBottom = "inset #999999 1px";
					tempCell.appendChild(sendTimeUpd);
				}else{
					var textNode = top.principale.document.createTextNode('NA');
					tempCell.style.textAlign = 'right';
					tempCell.style.borderBottom = "inset #999999 1px";
					tempCell.appendChild(textNode);
					if(tempResult.length>2){tempCell.rowSpan=tempResult.length-2;}
					if (document.all){var tempCell = row.insertCell();}
					if (dom){var tempCell = row.insertCell(i);}
					var sendTimeUpd = top.principale.document.createElement("input");
					sendTimeUpd.type="checkbox";
					sendTimeUpd.disabled=false;
				}
			}
			if(tempResult.length>2){tempCell.rowSpan=tempResult.length-2;}
			if(i==TCResult.length&&report != 'READY'){
				row.style.background='yellow';
				if (document.all){var tempCell = row.insertCell();}
				if (dom){var tempCell = row.insertCell(i);}
				tempCell.colSpan='2';
				if(tableName=='runListTable'){var textNode = top.principale.document.createTextNode('ON GOING');}
					else{var textNode = top.principale.document.createTextNode('CRASH');}
				tempCell.appendChild(textNode);
				tempCell.style.textAlign = 'center';
			}
			if(i<TCResult.length){
				tempResult1=tempResult[1].split(',');
				switch(true){
					case tempResult[0].match("OK")!=null:row.style.background='palegreen';row.style.color='#000000';break;
					case tempResult[0].match("KO")!=null:row.style.background='red';row.style.color='#eeeeee';break;
					default :row.style.background='yellow';row.style.color='#999999';break;
				}
				if(tempResult.length>2){tempCell.rowSpan=tempResult.length-2;}
				if (document.all){var tempCell = row.insertCell();}
				if (dom){var tempCell = row.insertCell(i);}
				if(tempResult1.length>1){var textNode = top.principale.document.createTextNode(tempResult1[0].replace("Test Area: ","").replace(/^\s*|\s*$/g,''));}
					else{var textNode = top.principale.document.createTextNode('NA');}
				switch(true){
					case tempResult[1].match("Passed")!=null:tempCell.style.background='palegreen';tempCell.style.color='#000000';break;
					case tempResult[1].match("Failed")!=null:tempCell.style.background='red';tempCell.style.color='#eeeeee';break;
					default :tempCell.style.background='yellow';break;
				}
				if(tempResult.length<=3){tempCell.style.borderBottom = "inset #999999 1px";}
				tempCell.appendChild(textNode);
				tempCell.style.textAlign = 'center';
				if (document.all){var tempCell = row.insertCell();}
				if (dom){var tempCell = row.insertCell(i);}
				if(tempResult1.length>1){var textNode = top.principale.document.createTextNode(tempResult1[1].replace("TPSId: ","").replace(/^\s*|\s*$/g,''));}
					else{var textNode = top.principale.document.createTextNode('NA');}
				switch(true){
					case tempResult[1].match("Passed")!=null:tempCell.style.background='palegreen';tempCell.style.color='#000000';break;
					case tempResult[1].match("Failed")!=null:tempCell.style.background='red';tempCell.style.color='#eeeeee';break;
					default :tempCell.style.background='yellow';tempCell.style.color='#000000';break;
				}
				if(tempResult.length<=3){tempCell.style.borderBottom = "inset #999999 1px";}
				tempCell.appendChild(textNode);
				tempCell.style.textAlign = 'center';
				for(j=2;j<tempResult.length-1;j++){
					tempResult1=tempResult[j].split(',');
					if (document.all){var row = myTable.insertRow();}
					if (dom){var row = myTable.insertRow(i+1);}
					if (document.all){var tempCell = row.insertCell();}
					if (dom){var tempCell = row.insertCell(i);}
					switch(true){
						case tempResult[j].match("Passed")!=null:row.style.background='palegreen';row.style.color='#000000';break;
						case tempResult[j].match("Failed")!=null:row.style.background='red';row.style.color='#ffffff';break;
						default :row.style.background='yellow';row.style.color='#000000';break;
					}
					tempCell.style.textAlign = 'center';
					if(tempResult1.length>1){var textNode = top.principale.document.createTextNode(tempResult1[0].replace("Test Area: ","").replace(/^\s*|\s*$/g,''));}
					else{var textNode = top.principale.document.createTextNode('NA');}
					if(j==tempResult.length-2){tempCell.style.borderBottom = "inset #999999 1px";}
					tempCell.appendChild(textNode);
					if (document.all){var tempCell = row.insertCell();}
					if (dom){var tempCell = row.insertCell(i);}
					tempCell.style.textAlign = 'center';
					if(tempResult1.length>1){var textNode = top.principale.document.createTextNode(tempResult1[1].replace("TPSId: ","").replace(/^\s*|\s*$/g,''));}
					else{var textNode = top.principale.document.createTextNode('NA');}
					if(j==tempResult.length-2){tempCell.style.borderBottom = "inset #999999 1px";}
					tempCell.appendChild(textNode);
				}
			}
		}
	}
	if(report == 'STOPPED'||report == 'READY'){
		//top.principale.document.getElementById('RUNbtn').disabled = false;
		//top.principale.runTest.target.disabled = false;
		//top.principale.runTest.SWRelease.disabled = false;
		top.principale.document.getElementById('KILLbtn').disabled = true;
		top.principale.document.getElementById('selectBundle').disabled = false;
		top.principale.document.getElementById('createRunBtn').disabled = false;
		//top.principale.runTest.selectBench.disabled = false;
	}
	top.principale.document.getElementById('transparency').style.zIndex=-1;
	top.principale.document.getElementById('transparencyImg').style.visibility='hidden';
	top.accesso.location.href='accesso.asp';
	top.topPage.top1.location.href='topMain.asp';
}

function fillScriptPortingTable2(scriptString){
	var myTable = document.getElementById('portingTable');
	var myRows = myTable.rows;
	iterations = myRows.length;
	if(iterations > 1){
		for(i=0;i<iterations-1;i++){
			myTable.deleteRow(1);
		}
	}
	scriptAry = scriptString.split("#");
	for (i = 0;i < scriptAry.length - 1; i++) {
		if (document.all){var row = myTable.insertRow();}
		if (dom){var row = myTable.insertRow(i+1);}
		row.onmouseover = function(){Color(this,2);}
		row.onmouseout = function(){Decolor(this,2);}
		row.name = scriptAry[i];
		row.onclick = function(){Check(this,2);}
		for(p=checked[2].length-1;p>=0;p--){
			if(scriptAry[i] == checked[2][p]){
				row.style.background='red';
			}
		}
		if (document.all){var tempCell = row.insertCell();}
		if (dom){var tempCell = row.insertCell(j);}
		tempAry = scriptAry[i].split("\\");
		inputText = tempAry[tempAry.length-1];
		var textNode = document.createTextNode(inputText.substring(0,inputText.length-4));
		tempCell.appendChild(textNode);
		tempCell.style.textAlign = 'left';
		tempCell.noWrap = true;
	}
	colorTable('portingTable');
}

function fillTunedSuiteTable2(scriptString){
	var myTable = document.getElementById('availableSuite');
	var myRows = myTable.rows;
	iterations = myRows.length;
	if(iterations > 1){
		for(i=0;i<iterations-1;i++){
			myTable.deleteRow(1);
		}
	}
	scriptAry = scriptString.split("#");
	for (i = 0;i < scriptAry.length - 1; i++) {
		if (document.all){var row = myTable.insertRow();}
		if (dom){var row = myTable.insertRow(i+1);}
		row.onmouseover = function(){Color(this,3);}
		row.onmouseout = function(){Decolor(this,3);}
		row.name = scriptAry[i].substring(0,scriptAry[i].length-4);
		row.onclick = function(){Check(this,3);}
		for(p=checked[3].length-1;p>=0;p--){
			if(scriptAry[i] == checked[3][p]){
				row.style.background='red';
			}
		}
		if (document.all){var tempCell = row.insertCell();}
		if (dom){var tempCell = row.insertCell(j);}
		tempAry = scriptAry[i].split("\\");
		inputText = tempAry[tempAry.length-1];
		var textNode = document.createTextNode(inputText.substring(0,inputText.length-4));
		tempCell.appendChild(textNode);
		tempCell.style.textAlign = 'left';
		tempCell.noWrap = true;
	}
	colorTable('availableSuite');
}

function fillFlagsTable2(scriptString){
	var myTable = document.getElementById('flagsTable');
	var myRows = myTable.rows;
	iterations = myRows.length;
	if(iterations > 1){
		for(i=0;i<iterations-1;i++){
			myTable.deleteRow(1);
		}
	}
	if(scriptString.length>1){
		scriptAry = scriptString.split("ô");
		scriptAry.sort();
		for (i = 0;i < scriptAry.length; i++) {
			if (document.all){var row = myTable.insertRow();}
			if (dom){var row = myTable.insertRow(i+1);}
			tempAry = scriptAry[i].split("\\");
			if (document.all){var tempCell = row.insertCell();}
			if (dom){var tempCell = row.insertCell(j);}
			var flagsInput = document.createElement("input");
			flagsInput.setAttribute("type","text");
			flagsInput.setAttribute("name",tempAry[tempAry.length-1]);
			flagsInput.value=tempAry[tempAry.length-1];
			flagsInput.id=i;
			flagsInput.style.fontSize="7pt";
			flagsInput.style.width="90%";
			flagsInput.style.height="100%";
			flagsInput.style.padding="3px";
			flagsInput.onchange=function(){
				if(this.value != this.name){
					this.style.background='papayawhip';
				}else{
					this.style.background='white';
				}
			}
			tempCell.style.textAlign = 'center';
			tempCell.appendChild(flagsInput);
		}
		colorTable('flagsTable');
	}
}

function fillChangingTable2(){
	var myTable = document.getElementById('changingTable');
	var myRows = myTable.rows;
	iterations = myRows.length;
	if(iterations > 1){
		for(i=0;i<iterations-1;i++){
			myTable.deleteRow(1);
		}
	}
	checked[2].sort();
	checked[2].reverse();
	for(p=checked[2].length-1;p>=0;p--){
		if (document.all){var row = myTable.insertRow();}
		if (dom){var row = myTable.insertRow(i+1);}
		if (document.all){var tempCell = row.insertCell();}
		if (dom){var tempCell = row.insertCell(j);}
		tempAry = checked[2][p].split("\\");
		inputText = tempAry[tempAry.length-1];
		var textNode = document.createTextNode(inputText.substring(0,inputText.length-4));
		tempCell.appendChild(textNode);
		tempCell.style.textAlign = 'left';
		tempCell.noWrap = true;
	}
	colorTable('changingTable');
	
}

function saveTuning2(flagsTable,sameFolder){
	if(checked[2].length!=0){
		if(sameFolder){
			if(confirm('Are you sure to overwrite old files?')){
				flagChange(flagsTable);
			}
		}else{
			newFolderName = prompt('Insert New Script Folder Name...','New Folder');
			if(newFolderName != null){
				document.portingForm.newTunedFolder.value=newFolderName;
				document.portingForm.newTunedFile.value=document.portingForm.loadBundlePorting.value;
				flagChange(flagsTable);
			}else{
				alert('You must insert new script folder name!');
			}
		}
	}
}

function flagChange2(flagsTable){
	changedFlags = "";
	changedFiles = "";
	for(i=0;i<flagsTable.rows.length-1;i++){
		var myInput = flagsTable.rows[i].cells[0].document.getElementById(i);
		if(myInput.value != myInput.name){
			changedFlags += myInput.value + "ñ" + myInput.name + "Ñ";
		}
	}
	for(i=0;i<checked[2].length;i++){
		changedFiles += checked[2][i] + "*";
	}
	document.portingForm.flagsChanges.value=changedFlags;
	document.portingForm.flagsFiles.value=changedFiles;
	if(document.portingForm.flagsChanges.value!=""){document.portingForm.submit();}
}

function reloadFlags2(filelist){
	top.accesso.location="accesso.asp?azione=findFlags&fileList=" + filelist;
}

function flagAll2(portingTable){
	//checked[2].pop();
	for(i=1;i<portingTable.rows.length;i++){
		found = false;
		for(k=0;k<checked[2].length;k++){
			if(portingTable.rows[i].name == checked[2][k]){
				found=true;
			}
		}
		if(found==false){
			checked[2].push(portingTable.rows[i].name);
		}
		portingTable.rows[i].style.background='red';
	}
	fileList = "";
	for(p=0;p<checked[2].length-1;p++){
		fileList += checked[2][p] + "*";
	}
	fillChangingTable();
	top.accesso.location="accesso.asp?azione=findFlags&fileList=" + fileList;
}

function flagNone2(){
	checked[2].length = 0;
	fillChangingTable();
	var myTable = document.getElementById('flagsTable');
	var myRows = myTable.rows;
	myRows.length=0;
}

function fillTSRTTable(){
	scriptString=top.tsrtValues;
	TSRTReport = scriptString.split("$");
	if(scriptString.length>1){
		for(p=0;p<TSRTReport.length-1;p++){
			tempTSRT=TSRTReport[p].split("#");
			for(k=2;k<tempTSRT.length;k=k+3){
				insertTSRTRow(tempTSRT[k],tempTSRT[k+1],tempTSRT[k+2]);
			}
		}
		colorTable('tsrtTable');
	}
}

function insertTSRTRow(area,TPS,OKKO){
	var myTable = top.principale.document.getElementById('tsrtTable');
	var totRows = myTable.rows.length;
	if (document.all){var row = myTable.insertRow();}
	if (dom){var row = myTable.insertRow(totRows+1);}		
	if (document.all){var tempCell = row.insertCell();}
	if (dom){var tempCell = row.insertCell(0);}
	var textNode = document.createTextNode(area);
	tempCell.appendChild(textNode);
	tempCell.style.textAlign = 'center';
	if (document.all){var tempCell = row.insertCell();}
	if (dom){var tempCell = row.insertCell(1);}
	var textNode = document.createTextNode(TPS);
	tempCell.appendChild(textNode);
	tempCell.style.textAlign = 'center';
	if (document.all){var tempCell = row.insertCell();}
	if (dom){var tempCell = row.insertCell(2);}
	var result = document.createElement("select");
	result.options[0] = new Option("Passed","Passed");
	result.options[1] = new Option("Failed","Failed");
	result.options[2] = new Option("Feature N.A.","Feature N.A.");
	result.options[3] = new Option("Blocked","Blocked");
	if(OKKO=="Passed"){result.selectedIndex=0;}
	if(OKKO=="Failed"){result.selectedIndex=1;}
	result.onchange=function(){
		if((this.selectedIndex==0)||(this.selectedIndex==2)){
			document.getElementById(parseInt(this.id)+1).value='';
			document.getElementById(parseInt(this.id)+1).disabled=true;
			document.getElementById(parseInt(this.id)+3).checked=true;
		}else{
			document.getElementById(parseInt(this.id)+1).value='TSDrd99999';
			document.getElementById(parseInt(this.id)+1).disabled=false;
			document.getElementById(parseInt(this.id)+3).checked=false;
		}
	}
	result.id='' + ((5*totRows)+1);
	result.style.width="90%";
	result.style.height="100%";
	result.style.padding="3px";
	result.style.fontSize="7pt";
	tempCell.appendChild(result);
	if (document.all){var tempCell = row.insertCell();}
	if (dom){var tempCell = row.insertCell(3);}
	var DDTS = document.createElement("input");
	DDTS.type="text";
	if(OKKO=="Failed"){DDTS.value="TSDrd99999";}
		else{DDTS.disabled=true;}
	DDTS.id='' + ((5*totRows)+2);
	DDTS.style.width="90%";
	DDTS.style.height="100%";
	tempCell.appendChild(DDTS);
	if (document.all){var tempCell = row.insertCell();}
	if (dom){var tempCell = row.insertCell(4);}
	var remarks = document.createElement("input");
	remarks.type="text";
	remarks.id='' + ((5*totRows)+3);
	remarks.style.width="90%";
	remarks.style.height="100%";
	tempCell.appendChild(remarks);
	if (document.all){var tempCell = row.insertCell();}
	if (dom){var tempCell = row.insertCell(5);}
	var sendTSRT = document.createElement("input");
	sendTSRT.type="checkbox";
	if(OKKO=="Passed"){sendTSRT.defaultChecked=true;}
		else{sendTSRT.defaultChecked=false;}
	sendTSRT.id='' + ((5*totRows)+4);
	tempCell.appendChild(sendTSRT);
}
		
function createTSRTReport(tsrtTable){
	document.TSRTForm.tsrtString.value = '';
	document.TSRTForm.tsrtName.value = top.tsrtReport;
	for(i=1;i<tsrtTable.rows.length;i++){
		if(tsrtTable.document.getElementById((i*5)+4).checked==true){
			document.TSRTForm.tsrtString.value +=tsrtTable.rows[i].cells[0].innerHTML + ',';
			document.TSRTForm.tsrtString.value +=tsrtTable.rows[i].cells[1].innerHTML + ',';
			document.TSRTForm.tsrtString.value +=document.getElementById((i*5)+1).value + ',';
			document.TSRTForm.tsrtString.value +=document.TSRTForm.release.value + ',';
			if((document.getElementById((i*5)+1).value!='Passed')||(document.getElementById((i*5)+1).value!='Feature N.A.')){
				document.TSRTForm.tsrtString.value +=document.getElementById((i*5)+2).value + ',';}
			document.TSRTForm.tsrtString.value +='0,' + document.TSRTForm.author.value + ',';
			document.TSRTForm.tsrtString.value +=document.getElementById((i*5)+3).value + '$';
		}
	}
	document.TSRTForm.submit();
}

function bundlePortingLoad2(portingList){
	tempList = portingList.split("$");
	bundlePortingList = '';
	checked[2].length=0;
	for(k=0;k<tempList.length-1;k++){
		tempBundle = tempList[k].split("#");
		matchString = tempBundle[6] + tempBundle[1];
		found=false;
		for(i=0;i<checked[2].length;i++){
			if(checked[2][i] == matchString){found=true;}
		}
		if(found==false){
			checked[2].push(matchString + ".lst");
			bundlePortingList += matchString + ".lst*";
		}
	}
	fillChangingTable();
	top.accesso.pivot.action='accesso.asp?azione=findFlags';
	top.accesso.pivot.string1.value=bundlePortingList;
	top.accesso.pivot.submit();
}


function tuneSuite(userName){
	switch(true){
		case selectTest.loadBundle.selectedIndex!=0:
			tuneName=selectTest.loadBundle.value.replace(/&/g,'%26');
			break;
		case selectTest.serverSharedSuite.selectedIndex!=0:
			tuneName=selectTest.serverSharedSuite.value.replace(/&/g,'%26');
			break;
		case selectTest.serverPersonalSuite.selectedIndex!=0:
			tuneName=selectTest.serverPersonalSuite.value.replace(/&/g,'%26');
			break;
		default:
			alert('No suites selected!');
	}
	if((tempBundleListString.length!=0)&&(bundleListString.length!=0)){
		if(tempBundleListString.length-1!=bundleListString.length){
			if(confirm('File seems to be changed since loaded,\nwanna save it now for tuning?')){saveFile('TestBundle',tuneName);}
		}else{
			selectTest.savingName.value=tuneName;
			selectTest.action='tuning.asp';
			selectTest.target='principale';
			selectTest.submit();
		}
	}else{
		selectTest.savingName.value=tuneName;
		selectTest.action='tuning.asp';
		selectTest.target='principale';
		selectTest.submit();
	}
}

function jtuneSuite(userName){
	switch(true){
		case selectTest.loadBundle.selectedIndex!=0:
			tuneName=selectTest.loadBundle.value.replace(/&/g,'%26');
			break;
		case selectTest.serverSharedSuite.selectedIndex!=0:
			tuneName=selectTest.serverSharedSuite.value.replace(/&/g,'%26');
			break;
		case selectTest.serverPersonalSuite.selectedIndex!=0:
			tuneName=selectTest.serverPersonalSuite.value.replace(/&/g,'%26');
			break;
		default:
			alert('No suites selected!');
	}
	if((tempBundleListString.length!=0)&&(bundleListString.length!=0)){
		if(tempBundleListString.length-1!=bundleListString.length){
			if(confirm('File seems to be changed since loaded,\nwanna save it now for tuning?')){saveFile('TestBundle',tuneName);}
		}else{
			selectTest.savingName.value=tuneName;
			selectTest.action='jtuning.asp';
			selectTest.target='principale';
			selectTest.submit();
		}
	}else{
		selectTest.savingName.value=tuneName;
		selectTest.action='jtuning.asp';
		selectTest.target='principale';
		selectTest.submit();
	}
}

function fillTable(tableList,tableName){
	var myTable = document.getElementById(tableName);
	if(tableList.length==1){
		tableString = '';
		for(i=0;i<checked[tableList].length;i++){
			tableString += '#'+checked[tableList][i]+'$';
		}
		tableList=tableString;
	}
	scriptAry = tableList.split("$");
	for (i = 0;i < scriptAry.length - 1; i++) {
		tempAry = scriptAry[i].split("#");
		if (document.all){var row = myTable.insertRow();}
		if (dom){var row = myTable.insertRow(i+1);}
		if (document.all){var tempCell = row.insertCell();}
		if (dom){var tempCell = row.insertCell(i);}
		var textNode = document.createTextNode(i+1);
		tempCell.appendChild(textNode);
		if (document.all){var tempCell = row.insertCell();}
		if (dom){var tempCell = row.insertCell(i);}
		var textNode = document.createTextNode(tempAry[1]);
		tempCell.appendChild(textNode);
		tempCell.style.textAlign = 'left';
	}
	colorTable(tableName);
}

function emptySelect(selectName){
	//svuota una select
	var mySelect = document.getElementById(selectName);
	if(mySelect.options.length>0){
		numOptions = mySelect.options.length;
		for(i=numOptions;i>=0;i--){mySelect.options[i]=null;}
	}
}

function colorTableRow(elementText,tableName,color,checkAry){
	myTable = top.principale.document.getElementById(tableName);
	totRows = myTable.rows.length;
	tempString = elementText.split("$");
	for(i=1;i<totRows;i++){
		for(k=0;k<tempString.length-1;k++){
			tempName = tempString[k].split("\\");
			if(myTable.rows[i].innerHTML.match(tempName[tempName.length-1])!=null){
				myTable.rows[i].style.background=color;
				checked[checkAry].push(tempString[k]+'.lst');
			}
		}
	}
}

function checkTable2(arrayFlag,tableName){
	myTable=document.getElementById(tableName);
	totRows=myTable.rows;
	for(i=0;i<totRows.length;i++){
		myTable.rows[i].onmouseover = function(){Color(this,arrayFlag);}
		myTable.rows[i].onmouseout = function(){Decolor(this,arrayFlag);}
		myTable.rows[i].onclick = function(){Check(this,arrayFlag);}
	}
}

function changeView2(tableName){
	emptyTable(tableName);
	switch(tableName){
		case "testTable":
			updateTestTable();
			break;
		case "testBundleTable":
			updateBundleTable();
			break;
		default:
			alert('Table not defined...');
	}
}

function getIPList2(tableList){
	emptyTable('IPTable');
	var myTable = document.getElementById('IPTable');
	scriptAry = tableList.split("$");
	for (i=0;i<scriptAry.length-1;i++) {
		tempAry = scriptAry[i].split("#");
		if (document.all){var row = myTable.insertRow();}
		if (dom){var row = myTable.insertRow(i);}
		if (document.all){var tempCell = row.insertCell();}
		if (dom){var tempCell = row.insertCell(j);}
		var checkIP = document.createElement("input");
		checkIP.type="checkbox";
		checkIP.id=''+i*1000;
		checkIP.onclick=function(){top.accesso.location='accesso.asp?azione=changeIPStatus&row='+this.id+'&check='+this.checked;}
		if(tempAry[0].match("NOP")){
			checkIP.defaultChecked=false;
			tempAry[0]=tempAry[0].replace("NOP","")
		}else{checkIP.defaultChecked=true;}
		tempCell.appendChild(checkIP);
		for (j = 0;j < tempAry.length; j++) {
			if (document.all){var tempCell = row.insertCell();}
			if (dom){var tempCell = row.insertCell(j);}
			var textNode = document.createTextNode(tempAry[j]);
			tempCell.appendChild(textNode);
		}
		if (document.all){var tempCell = row.insertCell();}
		if (dom){var tempCell = row.insertCell(j+1);}
		var deleteRow = document.createElement("input");
		deleteRow.type="button";
		deleteRow.value="REMOVE";
		deleteRow.style.fontSize="6pt";
		deleteRow.name=i;
		deleteRow.onclick=function(){top.accesso.location='accesso.asp?azione=deleteIP&row='+this.name;}
		tempCell.appendChild(deleteRow);
	}
	colorTable('IPTable');
}

function fillTableEqpt2(tableList,tableName){
	emptyTable(tableName);
	var myTable = document.getElementById(tableName);
	scriptAry = tableList.split("$");
	for (i = 0;i < scriptAry.length - 1; i++) {
		tempAry = scriptAry[i].split("#");
		if (document.all){var row = myTable.insertRow();}
		if (dom){var row = myTable.insertRow(i+1);}
		for(j=0;j<tempAry.length;j++){
			if (document.all){var tempCell = row.insertCell();}
			if (dom){var tempCell = row.insertCell(i);}
			var textNode = document.createTextNode(tempAry[j]);
			tempCell.appendChild(textNode);
			tempCell.style.textAlign = 'left';
		}
	}
	colorTable(tableName);
}

function fillSelect(ary,targetSelect,header,defaultSelection){
	if(targetSelect.options.length>0){targetSelect.options.length=0;}
	targetSelect.disabled=false;
	selectIndex=0;
	if(header!=''){
		var addArea = document.createElement('option');
		addArea.text = header;
		addArea.value = '';
		targetSelect.add(addArea);
	}
	for (i = 0;i < ary.length; i++) {
		var addArea = document.createElement('option');
		tempAry = ary[i].split("#");
		if(ary[i].match('#')){
			addArea.text = tempAry[0];
			addArea.value = tempAry[1];
		}else{
			addArea.text = tempAry[0];
			addArea.value = tempAry[0];
		}
		addArea.title=tempAry[0];
		if(tempAry[1]==defaultSelection){selectIndex=i+1;}
		targetSelect.add(addArea);
	}
	targetSelect.selectedIndex=selectIndex;
}

function extractTCFromExcelValues(resultAry,productList){
	if(this.location.pathname.match('runATM.asp')!=null){myForm=top.principale.runTest;}
		else{myForm=top.principale.report;}
	tempResult1=resultAry.split("$");
	top.resultCollectorValues="";
	top.principale.document.getElementById('excelValues').value="";
	for(i=0;i<tempResult1.length-1;i++){
		tempResult2=tempResult1[i].split("#");
		testName=tempResult2[0];
		//tempResult3=tempResult2[0].split(" ");
		switch(true){
			case tempResult1[i].match("Passed")!=null&&tempResult1[i].match("Failed")==null:testResult="OK";break;
			case tempResult1[i].match("Failed")!=null:testResult="KO";break;
			default :testResult="NA";break;
		}
		testDate=tempResult2[1];
		//if(testName.match("COMMON")==null){
			top.resultCollectorValues+=testResult+"#"+testDate+"$";
			top.principale.document.getElementById('excelValues').value+=testName+"$";
		//}
	}
	myForm.action='accesso.asp?azione=getTestCasesFromDBbyList&product='+productList;
	myForm.target='connection';
	myForm.submit();
}

function addCurrentReportColumn2(resultFromDB){
	numRows = resultFromDB.split("$");
	var myTable=document.getElementById('testTable');
	if(myTable.rows.length>1){
		cells=myTable.rows[0].getElementsByTagName("TH");
		var tempCell = myTable.rows[0].insertCell(cells.length);
		tempCell.style.color='white';
		var textNode = document.createTextNode('Today');
		tempCell.appendChild(textNode);
		var tempCell = myTable.rows[0].insertCell(cells.length+1);
		tempCell.style.color='white';
		var textNode = document.createTextNode('Notes');
		tempCell.appendChild(textNode);
		for (var h=0; h<numRows.length-1; h++) {
			//var row = myTable.insertRow(h+1);
			resultNotes.push("NA");
			var tempCell = myTable.rows[h+1].insertCell(cells.length);
			tempStr=numRows[h].split(' ');
			var textNode = document.createTextNode(tempStr[0].replace(/#/g," "));
			tempCell.style.width="10px";
			tempCell.style.textAlign = 'center';
			tempCell.appendChild(textNode);
			switch(true){
				case numRows[h].match("OK")!=null:tempCell.style.background='palegreen';break;
				case numRows[h].match("KO")!=null:tempCell.style.background='red';break;
				default :tempCell.style.background='yellow';break;
			}
			var tempCell = myTable.rows[h+1].insertCell(cells.length+1);
			var remarks = document.createElement("input");
			remarks.name=h;
			if((numRows[h].match("OK")==null)&&(numRows[h].match("KO")==null)){remarks.disabled=true;}
			remarks.onchange = function(){resultNotes[this.name]=this.value;}
			remarks.type="text";
			remarks.style.width="100%";
			tempCell.style.width="200px";
			tempCell.appendChild(remarks);
		}
	}
	//filterCell.width=parseInt(filterCell.clientWidth)+220;
}

function createReportHistory(){
	var myTable=top.principale.document.getElementById('testTable');
	testList='';
	for (var h=1; h<myTable.rows.length; h++) {
		tempName=myTable.rows[h].name.split("#");
		testList+=tempName[0]+"$";
	}
	top.principale.document.sendTAWSDBReport.DBNames.value=testList;
	top.principale.document.sendTAWSDBReport.action='accesso.asp?azione=getDBReports';
	top.principale.document.sendTAWSDBReport.target='connection';
	top.principale.document.sendTAWSDBReport.submit();
}

function createReportHistoryTable(testList){
	reportAry = testList.split("*");
	var myTable=document.getElementById('reportTable');
	for(var i=myTable.rows.length;i>0;i--){
		myTable.deleteRow(i-1);
	}
	var rowHead = myTable.insertRow(0);
	rowHead.style.background='#660099';
	rowHead.style.color='#eeeeee';
	rowHead.style.fontFamily='verdana';
	rowHead.style.fontWeight='bold';
	var alterTable=document.getElementById('testTable');
	maxCells=0;
	for (var h=0; h<reportAry.length-1; h++) {
		var row = myTable.insertRow();
		if(reportAry[h]!=''){
			numResults=reportAry[h].split("$");
			for (var j=0; j<numResults.length-1; j++) {
				if(j>=maxCells){
					var tempCell = rowHead.insertCell();
					tempCell.style.color='white';
					var textNode = document.createTextNode('Run'+(parseInt(j)+1));
					tempCell.appendChild(textNode);
					maxCells++;
				}
				results=numResults[j].split("#");
				var tempCell = row.insertCell();
				textNode = document.createElement ('A');
				textNode.setAttribute("title",results[2])
				textone=results[1];
				textNode.appendChild (document.createTextNode (textone));
				tempCell.style.textAlign = 'center';
				tempCell.appendChild(textNode);
				if(results[0].match("OK")!=null){tempCell.style.background='palegreen';}
					else{tempCell.style.background='red';}
			}
		}else{
			var tempCell = row.insertCell();
			var textNode = document.createTextNode('');
			tempCell.appendChild(textNode);
			row.height=45;
		}
		//alterTable.rows[h+1].height=47;
		alterTable.rows[h+1].onmouseover="";
		alterTable.rows[h+1].onmouseout="";
		alterTable.rows[h+1].onclick="";

	}
	document.sendTAWSDBReport.action='accesso.asp?azione=collectReport';
	alignReportTable();
}

function checkTunedFolder(){
	checkedFolderAry.length=0;
	orphanedTunedAry.length=0;
	orphanedTunedFolderAry.length=0;
	for(i=0;i<tunedAry.length;i++){
		tempTunedAry=tunedAry[i].split('#');
		foundOrphan=false;
		for(j=0;j<tunedFolderAry.length;j++){
			tempTunedFolderAry=tunedFolderAry[j].split("#");
			if(tempTunedAry[1].substring(0,tempTunedAry[1].length-4).toUpperCase().replace(/RECOVERY/,'TUNED')==tempTunedFolderAry[0].toUpperCase()){foundOrphan=true;checkedFolderAry.push(tunedAry[i].replace(/.mlt/,'').replace(/.mlt/,''));}
		}
		if(tempTunedAry[1].match("BATCH")!=null){foundOrphan=true;checkedFolderAry.push(tunedAry[i].replace(/.mlt/,'').replace(/.mlt/,''));}
		if(foundOrphan==false){orphanedTunedAry.push(tunedAry[i]);}
	}
	for(j=0;j<tunedFolderAry.length;j++){
		tempTunedFolderAry=tunedFolderAry[j].split("#");
		foundOrphan=false;
		for(i=0;i<tunedAry.length;i++){
			tempTunedAry=tunedAry[i].split('#');
			if(tempTunedAry[1].substring(0,tempTunedAry[1].length-4).toUpperCase()==tempTunedFolderAry[0].toUpperCase()){foundOrphan=true;}
		}
		if(foundOrphan==false){
			orphanedTunedFolderAry.push(tunedFolderAry[j]);
			}

	}
}

function createSuiteTable(){
	checkTunedFolder();
	var myTable=document.getElementById('suiteTable');
	for(j=0;j<checkedFolderAry.length;j++){
		if(checkedFolderAry[j].match("LOCAL_TESTING")==null){
			tempTunedFolderAry=checkedFolderAry[j].split("#");
			var row = myTable.insertRow();
			row.name=tempTunedFolderAry[1];
			var tempCell = row.insertCell();
			var textNode = document.createTextNode(tempTunedFolderAry[0]);
			tempCell.style.textAlign = 'left';
			tempCell.appendChild(textNode);
			tempCell = row.insertCell();
			var deleteBtn = document.createElement("input");
			deleteBtn.type="button";
			deleteBtn.value="Delete";
			deleteBtn.className="stylishButton";
			deleteBtn.name=tempTunedFolderAry[0];
			deleteBtn.onclick=function(){document.manageSuite.action='accesso.asp?azione=deleteSuite';
										 document.manageSuite.targetSuite.value=this.name;
										 document.manageSuite.submit();}
			tempCell.style.textAlign = 'center';
			tempCell.appendChild(deleteBtn);
			var modifyBtn = document.createElement("input");
			modifyBtn.type="button";
			modifyBtn.value="Modify";
			modifyBtn.className="stylishButton";
			modifyBtn.name=tempTunedFolderAry[0];
			//modifyBtn.disabled=true;
			modifyBtn.onclick=function(){newwindow=window.open('modifyTunedSuite.asp?suiteName='+this.name.replace(/&/g,'%26')+'&action=show','modifyTunedSuite','scrollbars=no,width=900,height=630,left=50,top=30');}
			tempCell.style.textAlign = 'center';
			tempCell.appendChild(modifyBtn);
			var tempCell = row.insertCell();
			var textNode = document.createTextNode('OK');
			tempCell.style.textAlign = 'center';
			tempCell.style.background='palegreen';
			tempCell.appendChild(textNode);
			var tempCell = row.insertCell();
			var textNode = document.createTextNode('OK');
			tempCell.style.textAlign = 'center';
			tempCell.style.background='palegreen';
			tempCell.appendChild(textNode);
		}
	}
	for(j=0;j<orphanedTunedAry.length;j++){
		tempTunedFolderAry=orphanedTunedAry[j].split("#");
		var row = myTable.insertRow();
		row.name=tempTunedFolderAry[1];
		var tempCell = row.insertCell();
		var textNode = document.createTextNode(tempTunedFolderAry[0]);
		tempCell.style.textAlign = 'left';
		tempCell.appendChild(textNode);
		tempCell = row.insertCell();
		var deleteBtn = document.createElement("input");
		deleteBtn.type="button";
		deleteBtn.value="Delete";
		deleteBtn.className="stylishButton";
		deleteBtn.name=tempTunedFolderAry[0].substring(0,tempTunedFolderAry[0].length-4);
		deleteBtn.onclick=function(){document.manageSuite.action='accesso.asp?azione=deleteSuite';
									 document.manageSuite.targetSuite.value=this.name;
									 document.manageSuite.submit();}
		tempCell.style.textAlign = 'center';
		tempCell.appendChild(deleteBtn);
		var tempCell = row.insertCell();
		var textNode = document.createTextNode('OK');
		tempCell.style.textAlign = 'center';
		tempCell.style.background='palegreen';
		tempCell.appendChild(textNode);
		var tempCell = row.insertCell();
		var textNode = document.createTextNode('KO');
		tempCell.style.textAlign = 'center';
		tempCell.style.background='red';
		tempCell.appendChild(textNode);
	}
	for(j=0;j<orphanedTunedFolderAry.length;j++){
		tempTunedFolderAry=orphanedTunedFolderAry[j].split("#");
		var row = myTable.insertRow();
		row.name=tempTunedFolderAry[1];
		var tempCell = row.insertCell();
		var textNode = document.createTextNode(tempTunedFolderAry[0]);
		tempCell.style.textAlign = 'left';
		tempCell.appendChild(textNode);
		tempCell = row.insertCell();
		var deleteBtn = document.createElement("input");
		deleteBtn.type="button";
		deleteBtn.value="Delete";
		deleteBtn.name=tempTunedFolderAry[0];
		deleteBtn.className="stylishButton";
		deleteBtn.onclick=function(){document.manageSuite.action='accesso.asp?azione=deleteSuite';
									 document.manageSuite.targetSuite.value=this.name;
									 document.manageSuite.submit();}
		tempCell.style.textAlign = 'center';
		tempCell.appendChild(deleteBtn);
		var tempCell = row.insertCell();
		var textNode = document.createTextNode('KO');
		tempCell.style.textAlign = 'center';
		tempCell.style.background='red';
		tempCell.appendChild(textNode);
		var tempCell = row.insertCell();
		var textNode = document.createTextNode('OK');
		tempCell.style.textAlign = 'center';
		tempCell.style.background='palegreen';
		tempCell.appendChild(textNode);
	}
	colorTable('suiteTable');
}

function fillReleasingTable(TCarray){
	var myTable=document.getElementById('toBeReleased');
	for(j=0;j<TCarray.length-1;j++){
		tempTCary = TCarray[j].split('\\');
		var row = myTable.insertRow();
		row.id=TCarray[j];
		var tempCell = row.insertCell();
		var textNode = document.createTextNode(j+1);
		tempCell.style.textAlign = 'center';
		tempCell.appendChild(textNode);
		var tempCell = row.insertCell();
		var textNode = document.createTextNode(tempTCary[tempTCary.length-1]);
		tempCell.style.textAlign = 'left';
		tempCell.appendChild(textNode);
		var tempCell = row.insertCell();
		var TBC = document.createElement("input");
		TBC.type="checkbox";
		TBC.id=TCarray[j]+'$TBC';
		tempCell.appendChild(TBC);
		var tempCell = row.insertCell();
		var selectProduct = document.createElement("select");
		selectProduct.id=TCarray[j]+'$Product';
		selectProduct.options[0] = new Option("Product","");
		for(i=0;i<availableAreas.length;i++){
			tempProduct=availableAreas[i].split('$');
			selectProduct.options[i+1] = new Option(tempProduct[0],tempProduct[1]);
		}
		selectProduct.onchange=function(){	tempCheck=this.id.split("$");
											tempRelease=document.getElementById(tempCheck[0]+'$Product').value.split('#');
											document.getElementById(tempCheck[0]+'$Release').options.length=1;
											document.getElementById(tempCheck[0]+'$Release').disabled=false;
											document.getElementById(tempCheck[0]+'$Btn').disabled=true;
											document.getElementById(tempCheck[0]+'$Release').selectedIndex=0;
											for(i=0;i<tempRelease.length;i++){
												document.getElementById(tempCheck[0]+'$Release').options[i+1] = new Option(tempRelease[i],tempRelease[i]);
											}
										  /*if((document.getElementById(tempCheck[0]+'$Product').value!='')&&(document.getElementById(tempCheck[0]+'$Release').value!='')){
												document.getElementById(tempCheck[0]+'$Btn').disabled=false;
											}else{
												document.getElementById(tempCheck[0]+'$Btn').disabled=true;
											}*/
										  }
		selectProduct.style.fontSize="7pt";
		tempCell.appendChild(selectProduct);
		var tempCell = row.insertCell();
		var selectRelease = document.createElement("select");
		selectRelease.id=TCarray[j]+'$Release';
		selectRelease.options[0] = new Option("Rel","");
		selectRelease.onchange=function(){tempCheck=this.id.split("$");
										  if((document.getElementById(tempCheck[0]+'$Product').value!='')&&(document.getElementById(tempCheck[0]+'$Release').value!='')){
												document.getElementById(tempCheck[0]+'$Btn').disabled=false;
											}else{
												document.getElementById(tempCheck[0]+'$Btn').disabled=true;
											}
										  }
		selectRelease.style.fontSize="7pt";
		selectRelease.disabled=true;
		tempCell.appendChild(selectRelease);
		tempCell = row.insertCell();
		var releaseBtn = document.createElement("input");
		releaseBtn.type="button";
		releaseBtn.value="Deliver";
		releaseBtn.className="stylishButton";
		releaseBtn.id=TCarray[j]+'$Btn';
		releaseBtn.onclick=function(){tempCheck=this.id.split("$");
									 document.releaseTestCases.action='pythonAccess.asp?azione=releaseTC';
									 document.releaseTestCases.TC.value=tempCheck[0]+'$';
									 document.releaseTestCases.TCproduct.value=document.getElementById(tempCheck[0]+'$Product').options[document.getElementById(tempCheck[0]+'$Product').selectedIndex].text+'$';
									 document.releaseTestCases.TCrelease.value=document.getElementById(tempCheck[0]+'$Release').value+'$';
									 document.releaseTestCases.TCTBC.value=document.getElementById(tempCheck[0]+'$TBC').checked+'$';
									 document.releaseTestCases.submit();
									 }
		releaseBtn.style.fontSize="7pt";
		releaseBtn.disabled=true;
		tempCell.style.textAlign = 'center';
		tempCell.appendChild(releaseBtn);
	}
	colorTable('toBeReleased');
	var myTable2=document.getElementById('released');
	for(i=1;i<myTable2.rows.length-1;i++){
		if(i<myTable.rows.length-1){
			if(parseInt(myTable.rows[i].clientHeight)>parseInt(myTable2.rows[i].clientHeight)){
				myTable2.rows[i].height=parseInt(myTable.rows[i].clientHeight);
			}else{
				myTable.rows[i].height=parseInt(myTable2.rows[i].clientHeight);
			}
		}
	}
}

function multiRelease(releaseTarget){
	firstRow=document.getElementById('toBeReleased').rows[1].id;
	multiIndex=document.getElementById(firstRow+'$'+releaseTarget).selectedIndex;
	tempCheck=document.getElementById(document.getElementById('toBeReleased').rows[1].id+'$'+releaseTarget).value.split('#');
	for(i=2;i<document.getElementById('toBeReleased').rows.length;i++){
		document.getElementById(document.getElementById('toBeReleased').rows[i].id+'$'+releaseTarget).selectedIndex=multiIndex;
		if(releaseTarget=='Product'){
			document.getElementById(document.getElementById('toBeReleased').rows[i].id+'$Release').disabled=false;
			document.getElementById(document.getElementById('toBeReleased').rows[i].id+'$Btn').disabled=true;
			for(j=0;j<tempCheck.length;j++){
				document.getElementById(document.getElementById('toBeReleased').rows[i].id+'$Release').options[j+1] = new Option(tempCheck[j],tempCheck[j]);
			}
			document.getElementById(document.getElementById('toBeReleased').rows[i].id+'$Release').selectedIndex=0;
		}else{
			if(document.getElementById(firstRow+'$'+releaseTarget).selectedIndex!=0){document.getElementById(document.getElementById('toBeReleased').rows[i].id+'$Btn').disabled=false;}
		}
	}
}

function createReleasedTable(aryOne){
	var myTable=document.getElementById('released');
	if(aryOne.length>0){
		for(j=0;j<aryOne.length;j++){
			nibbleAry = aryOne[j].split('$');
			tempAry=nibbleAry[0].split('_');
			var row = myTable.insertRow();
			row.id=aryOne[j];
			var tempCell = row.insertCell();
			var textNode = document.createTextNode(j+1);
			tempCell.style.textAlign = 'center';
			tempCell.appendChild(textNode);
			var tempCell = row.insertCell();
			var textNode = document.createTextNode(nibbleAry[0]);
			tempCell.style.textAlign = 'left';
			tempCell.appendChild(textNode);
			var tempCell = row.insertCell();
			var cellImage = document.createElement("IMG");
			if(nibbleAry[3]=='C'){
				cellImage.setAttribute('src','/images/KO.gif');
			}else{
				cellImage.setAttribute('src','/images/OK.gif');
			}
			tempCell.appendChild(cellImage);

			var tempCell = row.insertCell();
			var textNode = document.createTextNode(tempAry[0]);
			tempCell.appendChild(textNode);
			var tempCell = row.insertCell();
			var textNode = document.createTextNode(tempAry[1]);
			tempCell.appendChild(textNode);
			var tempCell = row.insertCell();
			var textNode = document.createTextNode(nibbleAry[1]);
			tempCell.appendChild(textNode);
			tempCell = row.insertCell();
			var removeBtn = document.createElement("input");
			removeBtn.type="button";
			removeBtn.value="Remove";
			removeBtn.id=aryOne[j]+'$Btn';
			removeBtn.style.fontSize="7pt";
			removeBtn.className="stylishButton";
			removeBtn.onclick=function(){tempCheck=this.id.split("$");
										 if(confirm("Remove " + tempCheck[0] +" from Released TC?")){
											document.releaseTestCases.action='accesso.asp?azione=deleteTC';
											document.releaseTestCases.TC.value=tempCheck[2];
											document.releaseTestCases.submit();}
										}
			tempCell.style.textAlign = 'center';
			tempCell.appendChild(removeBtn);
		}
		colorTable('released');
	}
}

function show_hide_column(tblName,col_no) {
	hiddenColumnNum=0;
    if(tblName=='all'){var tbl  = document.getElementById('testTable');}
		else{var tbl  = document.getElementById(tblName);}
	for(k=0;k<=col_no;k++){
		if(tbl.rows[0].cells[k].style.display=='none'){hiddenColumnNum++;}
	}
	var rows = tbl.getElementsByTagName('tr');
    for (var row=0; row<rows.length;row++) {
		var cels = rows[row].getElementsByTagName('td')
		if(col_no!='all'){
			tbl.rows[row].cells[col_no+hiddenColumnNum].style.display='none';
			//hiddenColumnAry.push(col_no+hiddenColumnNum);
		}else{
			for (var cel=0; cel<tbl.rows[row].cells.length;cel++) {
				tbl.rows[row].cells[cel].style.display='block';
			}
		}
    }
    if(tblName=='all'){
		var tbl  = document.getElementById('testBundleTable');
		var rows = tbl.getElementsByTagName('tr');
		for (var row=0; row<rows.length;row++) {
			for (var cel=0; cel<tbl.rows[row].cells.length;cel++) {
				tbl.rows[row].cells[cel].style.display='block';
			}
		}
	}
}
 
function addTableRow(cellAry,myTable,coupling,splitColor,linkningText){
	var row = document.getElementById(myTable).insertRow();
	numCell = cellAry.split(",")
	for(j=0;j<numCell.length;j++){
		var tempCell = row.insertCell();
		if(splitColor=='topBottom'){
			row.style.background='#2FA9B7';
			row.style.fontFamily='verdana';
			row.style.fontWeight='bold';
			row.style.color='white';
		}
		if(numCell[j]==''){numCell[j]='0';}
		var textNode = document.createTextNode(numCell[j]);
		tempCell.appendChild(textNode);
		tempCell.name=numCell[j];
		if(linkningText=='link'){tempCell.onclick=function(){tempName=this.name.split('-');self.location.href='resultStatistics.asp?statTarget='+tempName[0];}}
		if(j>0){tempCell.style.textAlign = 'center';}
		if(coupling=='notCoupled'&&j>0){
			tempCell.colSpan='2';
			tempCell.style.width='70px';
		}
		if(cellAry.match('ASSIGNMENT')!=null){tempCell.style.width='100px';}
		if(splitColor=='greenRed'&&j>0){
			if(j%2||myTable=='assignTable'){tempCell.style.background='palegreen';}
				else{tempCell.style.background='red';}
		}
		if(splitColor=='OKKO'&&j>0){
			if(numCell[j]=='OK'){tempCell.style.background='palegreen';}
			if(numCell[j]=='KO'){tempCell.style.background='red';}
			if(numCell[j]=='NA'){tempCell.style.background='yellow';}
		}
	}
}

function assignSuite2(suiteName){
	assignName = prompt('Insert Suite Executor!','NOT ASSIGNED')
	assignRelease = prompt('Insert Release!','NOT ASSIGNED')
	if(assignName!=''&&assignRelease!=''){top.accesso.location.href='accesso.asp?azione=assignSuite&suiteName=' + suiteName + '&assignName=' + assignName + '&assignRelease=' + assignRelease;}
}

function deleteFromLocalFolder(){
	myTable=top.principale.document.getElementById('testTable');
	deletionConfirm='';
	deletionString='';
	for(i=1;i<myTable.rows.length;i++){
		if(myTable.rows[i].style.background=='red'){
			tempStr=myTable.rows[i].name.split('#');
			//deletionString+=tempStr[0]+'#';
			tempConfirm=tempStr[0].split('TESTING\\');
			deletionConfirm+=tempConfirm[1]+'#';
		}
	}
	selectTest.action='pythonAccess.asp?azione=deleteFileByList';
	selectTest.target='connection';
	if(deletionConfirm!=''){
		if(confirm('Are you sure you want to delete:\n\n'+deletionConfirm.replace(/#/g,"\n")+'\nfrom LOCAL TESTING folder?')){
			selectTest.saveBody.value=deletionConfirm;
			emptyTable('testTable');
			selectTest.submit();
		}
	}else{
		if(confirm('No TCs have been selected,do you want to empty the whole LOCAL TESTING folder?')){
			emptyTable('testTable');
			selectTest.saveBody.value='';
			selectTest.submit();
		}
	}
}

function processing2(state){
	if(state){
document.body.style.cursor = 'wait';
  lockElements(document.getElementsByTagName("a"));
  lockElements(document.getElementsByTagName("input"));
  lockElements(document.getElementsByTagName("select"));
  lockElements(document.getElementsByTagName("check"));

  if (typeof TrPage != "undefined")
  {
    TrPage.getInstance().getRequestQueue().addStateChangeListener(unlockPage);
  }
	}else{
		if (typeof TrRequestQueue == "undefined" || state == TrRequestQueue.STATE_READY)
  {
    //alert("unlocking for state: " + state);
    document.body.style.cursor = 'auto';
    unlockElements(document.getElementsByTagName("a"));
    unlockElements(document.getElementsByTagName("input"));
  }
	}
}

function lockElements2(el)
{
  for (var i=0; i<el.length; i++)
  {
    el[i].style.cursor = 'wait';
    if (el[i].onclick)
    {
      var newEvent = 'return false;' + el[i].onclick;
      //alert(el[i].onclick + "\n\nlock -->\n\n" + newEvent);
      el[i].onclick = newEvent;
    }
  }
}

function unlockElements2(el)
{
  for (var i=0; i<el.length; i++)
  {
    el[i].style.cursor = 'auto';
    if (el[i].onclick && el[i].onclick.search(/^return false;/)==0)
    {
      var newEvent = el[i].onclick.substring(13);
      //alert(el[i].onclick + "\n\nunlock -->\n\n" + newEvent);
      el[i].onclick = newEvent;
    }
  }
}

function deleteReport(reportName,reportType){
	document.report.target='connection';
	if(confirm('Are you sure you want to delete selected report?')==true){
		if(reportType=='RT'){
			document.report.action='accesso.asp?azione=deletereport';
			document.report.targetFile.value=reportName;
		}else{
			document.report.action='pythonAccess.asp?azione=deletereport';
			document.report.targetFile.value=reportName;
		}
		document.report.submit();
		self.location.reload();
	}
}

function downloadReport(reportName){
	if(reportName!=''){
		document.report.action='pythonAccess.asp?azione=downloadFile';
		document.report.targetFile.value=reportName;
		document.report.target='connection';
		document.report.submit();
	}
}

function createFilter(filterValue){
	switch(true){
		case(filterValue.parentNode.id.match('topo')!=null):
			if(topologyFilter.match(filterValue.value)==null){
				if(topologyFilter!=''){topologyFilter+='|';}
				if((document.getElementById('negativeCheck').checked)&&(topologyFilter.match('ô')==null)){topologyFilter='ô'+topologyFilter;}
				if(document.getElementById('negativeCheck').checked==false){topologyFilter=topologyFilter.replace('ô',"");}
				topologyFilter+=filterValue.value;
			}
			break;
		case(filterValue.parentNode.id=='facility'):
			if(facilityFilter.match(filterValue.value)==null){
				if(facilityFilter!=''){facilityFilter+='|';}
				if((document.getElementById('negativeCheck').checked)&&(facilityFilter.match('ô')==null)){facilityFilter='ô'+facilityFilter;}
				if(document.getElementById('negativeCheck').checked==false){facilityFilter=facilityFilter.replace('ô',"");}
				facilityFilter+=filterValue.value;
			}
			break;
		default:
			if(patternFilter.match(filterValue.value)==null){
				if(patternFilter!=''){patternFilter+='|';}
				if((document.getElementById('negativeCheck').checked)&&(patternFilter.match('ô')==null)){patternFilter='ô'+patternFilter;}
				if(document.getElementById('negativeCheck').checked==false){patternFilter=patternFilter.replace('ô',"");}
				patternFilter+=filterValue.value;
			}
	}
	filterValue.parentNode.selectedIndex=0;
	document.getElementById('negativeCheck').checked=false;
	document.getElementById('filterStringLabel').value='';
	if(topologyFilter!=''){document.getElementById('filterStringLabel').value+='( '+topologyFilter.replace('ô',"NOT ").replace('|'," OR ").replace('|'," OR ").replace('|'," OR ").replace('|'," OR ").replace('|'," OR ").replace('|'," OR ")+' )';}
	if((topologyFilter!='')&&(facilityFilter!='')){document.getElementById('filterStringLabel').value+=' AND ';}
	if(facilityFilter!=''){document.getElementById('filterStringLabel').value+='( '+facilityFilter.replace('ô',"NOT ").replace('|'," OR ").replace('|'," OR ").replace('|'," OR ").replace('|'," OR ").replace('|'," OR ").replace('|'," OR ")+' )';}
	if(((topologyFilter!='')||(facilityFilter!=''))&&(patternFilter!='')){document.getElementById('filterStringLabel').value+=' AND ';}
	if(patternFilter!=''){document.getElementById('filterStringLabel').value+='( '+patternFilter.replace('ô',"NOT ").replace('|'," OR ").replace('|'," OR ").replace('|'," OR ").replace('|'," OR ").replace('|'," OR ").replace('|'," OR ")+' )';}
	document.getElementById('clearBtn').disabled=false;
}

function resetFilter(){
	patternFilter = "";
	topologyFilter = "";
	facilityFilter = "";
	document.getElementById('filterStringLabel').value='';
	document.getElementById('clearBtn').disabled=true;
	document.getElementById('pattern').value='Pattern';
}

function queryDB(userName){
	//document.getElementById('transparency').style.zIndex=10;
	//document.getElementById('transparencyImg').src='../images/loading.gif';
	//document.getElementById('transparencyImg').visibility='visible';
	if(owner=='LOCAL'){
		emptyTable('testBundleTable');
		owner=userName;
	}
	if(document.selectTest){
		document.getElementById('saveLocal').disabled=true;
		document.getElementById('savePersonal').disabled=false;
		document.getElementById('saveShared').disabled=false;
		document.getElementById('loadBundle').selectedIndex=0;
	}
	assignFilter=false;
	document.getElementById('topoA').disabled=false;
	document.getElementById('topoB').disabled=false;
	document.getElementById('topoC').disabled=false;
	document.getElementById('topoD').disabled=false;
	document.getElementById('facility').disabled=false;
	document.getElementById('pattern').disabled=false;
	document.getElementById('filterString').disabled=false;
	document.getElementById('clearBtn').disabled=false;
	document.getElementById('negativeCheck').disabled=false;
	if(document.getElementById('product').options[document.getElementById('product').selectedIndex].text!=''&&document.getElementById('product').selectedIndex!=0){queryProduct=document.getElementById('product').options[document.getElementById('product').selectedIndex].text;}
	if(document.getElementById('SWRelease').options[document.getElementById('SWRelease').selectedIndex].text!=''&&document.getElementById('SWRelease').selectedIndex!=0){querySWRelease=document.getElementById('SWRelease').options[document.getElementById('SWRelease').selectedIndex].text;}
	if(document.getElementById('area').options[document.getElementById('area').selectedIndex].text!=''&&document.getElementById('area').selectedIndex!=0){
		tempArea=document.getElementById('area').options[document.getElementById('area').selectedIndex].text.split('-');
		queryArea=tempArea[0];
	}
	if(queryProduct==''&&querySWRelease==''&&queryArea==''&&topologyFilter.length==0&&facilityFilter.length==0){
		if(confirm('Query fields are empty...\nThe operation could take long time.\nProceed anyway?')){
			parent.accesso.location.href='accesso.asp?azione=getTestCasesFromDB&product='+queryProduct+'&SWrelease='+querySWRelease+'&area='+queryArea+'&topologyFilter='+topologyFilter+'&facilityFilter='+facilityFilter+'&patternFilter='+patternFilter+'&assignFilter='+assignFilter;
			top.principale.focus();
		}
	}else{
		parent.accesso.location.href='accesso.asp?azione=getTestCasesFromDB&product='+queryProduct+'&SWrelease='+querySWRelease+'&area='+queryArea+'&topologyFilter='+topologyFilter+'&facilityFilter='+facilityFilter+'&patternFilter='+patternFilter+'&assignFilter='+assignFilter;
		top.principale.focus();
	}
}

function jqueryDB(userName){
	debugger;
	if(owner=='LOCAL'){
		emptyTable('testBundleTable');
		owner=userName;
	}
	if(document.selectTest){
		document.getElementById('saveLocal').disabled=true;
		document.getElementById('savePersonal').disabled=false;
		document.getElementById('saveShared').disabled=false;
		document.getElementById('loadBundle').selectedIndex=0;
	}
	assignFilter=false;
	document.getElementById('topoA').disabled=false;
	document.getElementById('topoB').disabled=false;
	document.getElementById('topoC').disabled=false;
	document.getElementById('topoD').disabled=false;
	document.getElementById('facility').disabled=false;
	document.getElementById('pattern').disabled=false;
	document.getElementById('filterString').disabled=false;
	document.getElementById('clearBtn').disabled=false;
	document.getElementById('negativeCheck').disabled=false;
	document.getElementById('lab').disabled=false;
	if(document.getElementById('area').options[document.getElementById('area').selectedIndex].text!=''&&document.getElementById('area').selectedIndex!=0){
		tempArea=document.getElementById('area').options[document.getElementById('area').selectedIndex].text.split(' - ');
		queryArea=tempArea[0];
	}
	if(queryArea==''&&topologyFilter.length==0&&facilityFilter.length==0){
		if(confirm('Query fields are empty...\nThe operation could take long time.\nProceed anyway?')){
			top.accesso.location.href='accesso.asp?azione=jgetTestCasesFromDB&area='+queryArea+'&topologyFilter='+topologyFilter+'&facilityFilter='+facilityFilter+'&patternFilter='+patternFilter+'&assignFilter='+assignFilter+'&lab='+document.getElementById('lab').value;
			top.principale.focus();
		}
	}else{
		top.accesso.location.href='accesso.asp?azione=jgetTestCasesFromDB&area='+queryArea+'&topologyFilter='+topologyFilter+'&facilityFilter='+facilityFilter+'&patternFilter='+patternFilter+'&assignFilter='+assignFilter+'&lab='+document.getElementById('lab').value;
		top.principale.focus();
	}
}

function updateTimes(){
	myTable=document.getElementById('reportSummary');
	timesStr='';
	for(i=1;i<myTable.rows.length;i++){
		if(myTable.rows[i].cells[5].firstChild.checked==true){
			timesStr+=myTable.rows[i].cells[5].firstChild.id+'$';
		}
		i+=myTable.rows[i].cells[0].rowSpan-1;
	}
	report.action='accesso.asp?azione=updateTimes';
	report.timesList.value=timesStr;
	report.target='connection';
	report.submit();
}