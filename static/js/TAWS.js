var tempBundleListString = new Array();
var bundleListString = new Array();
var testListString = new Array();

var x1 = 11;   // change the # on the left to adjust the X co-ordinate
var y1 = 250;  // change the # on the left to adjust the Y co-ordinate

(document.getElementById && !document.all) ? dom = true : dom = false;

//var iteration='';
//var lineNumber='';


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


function resetFilter(){
	patternFilter = "";
	topologyFilter = "";
	facilityFilter = "";
	document.getElementById('filterStringLabel').value='';
	document.getElementById('clearBtn').disabled=true;
	document.getElementById('pattern').value='Pattern';
}


function queryDB(userName){
	if(owner=='LOCAL'){
		emptyTable('testBundleTable');
		owner=userName;
	}
  	emptyTable('testBundleTable');
	if(document.selectTest){
		document.getElementById('savePersonal').disabled=false;
		document.getElementById('saveShared').disabled=false;
		//document.getElementById('loadBundle').selectedIndex=0;
	}
	assignFilter=false;
	document.getElementById('topoA').disabled=false;
	document.getElementById('topoB').disabled=false;
	document.getElementById('topoC').disabled=false;
	document.getElementById('topoD').disabled=false;
	//document.getElementById('facility').disabled=false;
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
		//alert(queryProduct,queryArea);
		//parent.accesso.location.href='accesso.asp?azione=getTestCasesFromDB&product='+queryProduct+'&SWrelease='+querySWRelease+'&area='+queryArea+'&topologyFilter='+topologyFilter+'&facilityFilter='+facilityFilter+'&patternFilter='+patternFilter+'&assignFilter='+assignFilter;
		doAccess('queryDB');
		//top.principale.focus();
	}
}

function jsaveFile(selectId){
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
		foundSuite=false;
		for(i=1;i<selectId.options.length;i++){
			if(selectId.options[i].text==saveText){
				foundSuite=true;
				if(owner!='LOCAL'){saveID=selectId.options[i].value;}
				break;
			}
		}
		if(foundSuite==false){saveID=saveText;}
		myTable=document.getElementById('testBundleTable');
		for(i=1;i<myTable.rows.length;i++){
			tempAry = myTable.rows[i].name.split("#");
			savingString +=tempAry[10]+'#'+tempAry[17]+"$";
			//alert(savingString);
		}
		//parent.topPage.connection.document.pivot.string1.value = savingString;
		//parent.topPage.connection.document.pivot.string2.value = saveID.replace(/'/g,"");
		//parent.topPage.connection.document.pivot.action = "accesso.asp?azione=jsavesuite";
		if((foundSuite==true&&confirm("Overwrite " + saveText +"?"))||foundSuite==false){
			//alert(savingString);
			doAccess('saveSuite');
		}
	}
}

function saveLocalSuite(){
	savingString=''
	myTable=document.getElementById('testBundleTable');
	for(i=1;i<myTable.rows.length;i++){
		tempAry = myTable.rows[i].name.split("#");
		savingString +=tempAry[13]+"#"+tempAry[17]+"$";
	}
	savingString=savingString.slice(0,-1)
	//alert('SAVE'+savingString);
	doAccess('saveLocal');
}

function updateTestTable(tableName,testAry){
	emptyTable(tableName);
	for (i = 0;i < testAry.length; i++) {
		if(testAry[i]!=''){addRecordToTable(testAry[i],tableName,'');}
	}
	if(tableName=='testBundleTable'){
		updateStats(tableName);
		//document.getElementById('tuneBtn').disabled=false;
	}
	colorTable(tableName);
	if(document.getElementById('reportTable')){createReportHistory();}
}

function addRecordToTable(testString,tableName,position){
	//alert('LOAD'+testString);
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
		if((parseInt(myTable.rows[0].cells[j].id)==5)&&(testCellAry[5]!='-')){
			tps=testCellAry[5].split('!');
			for(tpsIndex=0;tpsIndex<tps.length-1;tpsIndex++){
				var textNode = document.createTextNode(tps[tpsIndex]);
				tempCell.style.textAlign = 'center';
				tempCell.appendChild(textNode);
				var acccapo = document.createElement("br");
				tempCell.style.textAlign = 'center';
				tempCell.appendChild(acccapo);
			}
			var textNode = document.createTextNode(tps[tpsIndex]);
			tempCell.style.textAlign = 'center';
			tempCell.appendChild(textNode);
		}else{
			var textNode = document.createTextNode(testCellAry[myTable.rows[0].cells[j].id]);
		}
		if(parseInt(myTable.rows[0].cells[j].id)==6){
			tempCell.style.textAlign = 'left';
			textNode = document.createElement ('p');
			toolTipText='TEST ID : '+testCellAry[0];
			toolTipText+='\nPRODUCT : '+testCellAry[1];
			toolTipText+='\nSW Release : '+testCellAry[2];
			toolTipText+='\nDependency : '+testCellAry[12];
			toolTipText+='\nFull Path : '+testCellAry[13];
			toolTipText+='\nExecution Release : '+testCellAry[11];
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
		if(parseInt(myTable.rows[0].cells[j].id)==0){var textNode = document.createTextNode(myTable.rows.length-1);}
		if(parseInt(myTable.rows[0].cells[j].id)==7){var textNode = document.createTextNode(seconds2Time(testCellAry[7]));}
		if(parseInt(myTable.rows[0].cells[j].id)==9){tempCell.onclick = function(){window.open('topologyViewer.asp?myTopology='+this.innerText,'name','height=600,width=800,resizable=1');}}
		switch(true){
			case ((parseInt(myTable.rows[0].cells[j].id)==10)||(parseInt(myTable.rows[0].cells[j].id)==12)||(parseInt(myTable.rows[0].cells[j].id)==24)):
				var cellImage = document.createElement("IMG");
				if((testCellAry[myTable.rows[0].cells[j].id]=='NOT ASSIGNED')||((testCellAry[myTable.rows[0].cells[j].id]!='NA')&&(parseInt(myTable.rows[0].cells[j].id)==12))||(testCellAry[myTable.rows[0].cells[j].id]=='C')){
					cellImage.setAttribute('src','/images/KO.gif');
				}else{
					cellImage.setAttribute('src','/images/OK.gif');
				}
				tempCell.appendChild(cellImage);
				break;
			case (parseInt(myTable.rows[0].cells[j].id)==18):
				livArray=testCellAry[18].split('!');
				var livraison = document.createElement("select");
				for(q=0;q<livArray.length;q++){
					tempLiv=livArray[q].split('|');
					livraison.options[q] = new Option(tempLiv[0],tempLiv[1]);
				}
				//livraison.style.width="90%";
				//result.style.height="100%";
				//result.style.padding="3px";
				livraison.style.fontSize="7pt";
				livraison.onchange=function(){
								iteration=this.value;
								lineNumber=this.parentElement.parentElement.rowIndex;
								currentTable=this.parentElement.parentElement.parentElement.parentElement;
								doAccess('queryIteration');
								//tempArray=this.parentElement.parentElement.id.split('#');
								//tempArray[18]=this.value;
								//this.parentElement.parentElement.id=tempArray.join('#');
							}
				//tempArray=row.name.split('#');
				//tempArray[18]=livArray[0];
				//row.name=tempArray.join('#');
				tempCell.appendChild(livraison);
				break;
			case ((parseInt(myTable.rows[0].cells[j].id)==17)&&(tableName=='testTable')):
				var cellImage = document.createElement("IMG");
				if(testCellAry[17].charAt(0)=='0'){cellImage.setAttribute('src',KO_GIF);}
					else{cellImage.setAttribute('src',OK_GIF);}
				tempCell.appendChild(cellImage);
				for(zq_i=1;zq_i<5;zq_i++){
					if (document.all){var tempCell = row.insertCell();}
					if (dom){var tempCell = row.insertCell();}
					var cellImage = document.createElement("IMG");
					if(testCellAry[17].charAt(zq_i)=='0'){cellImage.setAttribute('src',KO_GIF);}
						else{cellImage.setAttribute('src',OK_GIF);}
					tempCell.appendChild(cellImage);
				}
				break;
			case ((parseInt(myTable.rows[0].cells[j].id)==17)&&(tableName=='testBundleTable')):
				//testCellAry[17]=testCellAry[17].replace(/1/g,'2');
				row.name=testCellAry.join('#');
				var runSection = document.createElement("input");
				runSection.type="checkbox";
				runSection.onclick=function(){
								tempAry=this.parentElement.parentElement.name.split('#');
								newSection=['1','1','1','1','1'];
								for(zq_k=0;zq_k<5;zq_k++){
									switch(true){
										case(this.parentElement.parentElement.cells[8+zq_k].firstChild.checked):
											newSection[0+zq_k]='2';
											break;
										case(!(this.parentElement.parentElement.cells[8+zq_k].firstChild.checked)&&!(this.parentElement.parentElement.cells[8].firstChild.disabled)):
											newSection[0+zq_k]='1';
											break;
										case(this.parentElement.parentElement.cells[8+zq_k].firstChild.disabled):
											newSection[0+zq_k]='0';
											break;
										default:
									}
								}
								tempAry[17]=newSection.join('');
								this.parentElement.parentElement.name=tempAry.join('#');
								}
				switch(testCellAry[17].charAt(0)){
					case '0':
						runSection.disabled=true;
						break;
					case '1':
						runSection.disabled=false;
						runSection.defaultChecked=false;
						break;
					case '2':
						runSection.disabled=false;
						runSection.defaultChecked=true;
						break;
					default:
				}
				tempCell.appendChild(runSection);
				for(zq_i=1;zq_i<5;zq_i++){
					if (document.all){var tempCell = row.insertCell();}
					if (dom){var tempCell = row.insertCell();}
					var runSection = document.createElement("input");
					runSection.type="checkbox";
					runSection.onclick=function(){tempAry=this.parentElement.parentElement.name.split('#');
								newSection=['1','1','1','1','1'];
								for(zq_k=0;zq_k<5;zq_k++){
									switch(true){
										case(this.parentElement.parentElement.cells[8+zq_k].firstChild.checked):
											newSection[0+zq_k]='2';
											break;
										case(!(this.parentElement.parentElement.cells[8+zq_k].firstChild.checked)&&!(this.parentElement.parentElement.cells[8].firstChild.disabled)):
											newSection[0+zq_k]='1';
											break;
										case(this.parentElement.parentElement.cells[8+zq_k].firstChild.disabled):
											newSection[0+zq_k]='0';
											break;
										default:
									}
								}
								tempAry[17]=newSection.join('');
								this.parentElement.parentElement.name=tempAry.join('#');}
					switch(testCellAry[17].charAt(zq_i)){
						case '0':
							runSection.disabled=true;
							break;
						case '1':
							runSection.disabled=false;
							runSection.defaultChecked=false;
							break;
						case '2':
							runSection.disabled=false;
							runSection.defaultChecked=true;
							break;
						default:
					}
					tempCell.appendChild(runSection);
				}
				break;
			default:
				tempCell.appendChild(textNode);
		}
		//if(myTable.rows[0].cells[tempCell.cellIndex+styleIndex].style.display=='none'){tempCell.style.display='none';styleIndex++;}
	}
	if(row.clientHeight<18&&myTable.id=='testBundleTable'){row.style.height=18;}
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

function colorTable(tableName){
	var myRows = document.getElementById(tableName).rows;
	for(k = 0;k < myRows.length-1;k++){
		if (k%2){myRows[k+1].style.background='#eeeeee';}
			else{myRows[k+1].style.background='white';}
	}
}

function Color(t,io){
	if(t.style.background.indexOf('red')<0){
		t.style.background='orange';
	}
}

function Decolor(t,io){
	if(t.style.background.indexOf('red')<0){
		if(t.rowIndex%2){
			t.style.background='white';
		}else{
			t.style.background='#eeeeee';
		}
	}
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

function Check(t,io){
	if(t.style.background.indexOf('red')<0){t.style.background='red';}
		else{
			if(t.rowIndex%2){
				t.style.background='white';
			}else{
				t.style.background='#eeeeee';
			}
		}
	updateStats(t.parentNode.parentNode.id);
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
		if(((totalTable=='testTable')&&(myTable.rows[i].style.background.indexOf('red')>=0))||(totalTable=='testBundleTable')){
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

function insertBundleList(numAdd,position){
	myTable=document.getElementById('testTable');
	if(position==''){addPosition='';}
		else{addPosition=position;}
	for(t=0;t<parseInt(numAdd);t++){
		for(i=1;i<myTable.rows.length;i++){
			if(myTable.rows[i].style.background.indexOf('red')>=0){
				testCellAry=myTable.rows[i].name.split('#');
				testCellAry[17]=testCellAry[17].replace(/1/g,'2');
				testString=testCellAry.join('#');
				addRecordToTable(testString,'testBundleTable',addPosition);
				if(position!=''){addPosition++;}
			}
		}
	}
	if(position!=''){
		myTable2=document.getElementById('testBundleTable');
		for(i=1;i<myTable2.rows.length;i++){
			myTable2.rows[i].cells[0].innerHTML=i;
		}
	}
	colorTable('testBundleTable');
	colorTable('testTable');
	updateStats('testBundleTable')
	updateStats('testTable')
	//document.getElementById('tuneBtn').disabled=true;
	//top.principale.document.getElementById('execBtn').disabled=true;
}

function insertAllBundleList(){
	//document.getElementById('transparency').style.zIndex=10;
	//document.getElementById('transparencyImg').style.visibility='visible';
	myTable=document.getElementById('testTable');
	for(i=1;i<myTable.rows.length;i++){
		testCellAry=myTable.rows[i].name.split('#');
		testCellAry[17]=testCellAry[17].replace(/1/g,'2');
		testString=testCellAry.join('#');
		addRecordToTable(testString,'testBundleTable','');
	}
	colorTable('testBundleTable');
	updateStats('testBundleTable')
	//document.getElementById('tuneBtn').disabled=true;
	//document.getElementById('transparency').style.zIndex=-1;
	//document.getElementById('transparencyImg').style.visibility='hidden';
}

function removeBundleList(){
	myTable=document.getElementById('testBundleTable');
	for(i=1;i<myTable.rows.length;i++){
		if(myTable.rows[i].style.background.indexOf('red')>=0){
			myTable.deleteRow(i);
			i--
		}
	}
	updateStats('testBundleTable')
	colorTable('testBundleTable');
	//document.getElementById('tuneBtn').disabled=true;
	//top.principale.document.getElementById('execBtn').disabled=true;
}

function removeAllBundleList(){
	emptyTable('testBundleTable');
	updateStats('testBundleTable')
	//document.getElementById('tuneBtn').disabled=true;
	//top.principale.document.getElementById('execBtn').disabled=true;
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
		//tempAry = ary[i].split("#");
		//if(ary[i].match('#')){
			addArea.text = ary[i]['suiteName'];
			addArea.value = ary[i]['suiteID'];
		//}else{
		//	addArea.text = tempAry[0];
		//	addArea.value = tempAry[0];
		//}
		addArea.title=ary[i]['suiteName'];
		if(ary[i]['suiteID']==defaultSelection){selectIndex=i+1;}
		targetSelect.add(addArea);
	}
	targetSelect.selectedIndex=selectIndex;
}

function deleteTest(){
	myTable=document.getElementById('testTable');
  deleteList=''
	for(i=1;i<myTable.rows.length;i++){
		if(myTable.rows[i].style.background.indexOf('red')>=0){
      tempStr=myTable.rows[i].name.split('#');
      deleteList+=tempStr[13]+'#';
			myTable.deleteRow(i);
			i--
		}
	}
  deleteList=deleteList.slice(0,-1);
  doAccess('deleteTest');
	updateStats('testBundleTable')
	colorTable('testBundleTable');
	//document.getElementById('tuneBtn').disabled=true;
	//top.principale.document.getElementById('execBtn').disabled=true;
}

function updateTableRow(testString,lineNumber,myTable){
	//alert(testString);
	//myTable=document.getElementById(tableName);
	numCol=myTable.getElementsByTagName('th').length;
	testCellAry=testString.split('#');
	for(j = 0;j < numCol; j++) {
		var tempCell = myTable.rows[lineNumber].cells[j];
		if((parseInt(myTable.rows[0].cells[j].id)!=18)&&(parseInt(myTable.rows[0].cells[j].id)!=0)&&(parseInt(myTable.rows[0].cells[j].id)!=17)){
			while(tempCell.hasChildNodes()){
				tempCell.removeChild(tempCell.lastChild);
			}
		}
		if((parseInt(myTable.rows[0].cells[j].id)==5)&&(testCellAry[5]!='-')){
			tps=testCellAry[5].split('!');
			for(tpsIndex=0;tpsIndex<tps.length-1;tpsIndex++){
				var textNode = document.createTextNode(tps[tpsIndex]);
				tempCell.style.textAlign = 'center';
				tempCell.appendChild(textNode);
				var acccapo = document.createElement("br");
				tempCell.style.textAlign = 'center';
				tempCell.appendChild(acccapo);
			}
			var textNode = document.createTextNode(tps[tpsIndex]);
			tempCell.style.textAlign = 'center';
			tempCell.appendChild(textNode);
		}else{
			if(parseInt(myTable.rows[0].cells[j].id)!=17){var textNode = document.createTextNode(testCellAry[myTable.rows[0].cells[j].id]);}
		}
		if(parseInt(myTable.rows[0].cells[j].id)==6){
			tempCell.style.textAlign = 'left';
			textNode = document.createElement ('A');
			toolTipText='TEST ID : '+testCellAry[0];
			toolTipText+='\nPRODUCT : '+testCellAry[1];
			toolTipText+='\nSW Release : '+testCellAry[2];
			toolTipText+='\nDependency : '+testCellAry[12];
			toolTipText+='\nFull Path : '+testCellAry[13];
			toolTipText+='\nExecution Release : '+testCellAry[11];
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
		if(parseInt(myTable.rows[0].cells[j].id)==7){var textNode = document.createTextNode(seconds2Time(testCellAry[7]));}
		if(parseInt(myTable.rows[0].cells[j].id)==9){tempCell.onclick = function(){window.open('topologyViewer.asp?myTopology='+this.innerText,'name','height=600,width=800,resizable=1');}}
		if((parseInt(myTable.rows[0].cells[j].id)!=18)&&(parseInt(myTable.rows[0].cells[j].id)!=0)&&(parseInt(myTable.rows[0].cells[j].id)!=17)){tempCell.appendChild(textNode);}
		if(parseInt(myTable.rows[0].cells[j].id)==17){
			//if(testCellAry[17].charAt(0)=='0'){tempCell.style.backgroundColor='red';}
				//else{tempCell.style.backgroundColor='green';}
			for(zq_i=0;zq_i<5;zq_i++){
				//if (document.all){var tempCell = row.insertCell();}
				//if (dom){var tempCell = row.insertCell();}
				if(testCellAry[17].charAt(zq_i)==0){myTable.rows[lineNumber].cells[j+zq_i].firstChild.src=KO_GIF;}
					else{myTable.rows[lineNumber].cells[j+zq_i].firstChild.src=OK_GIF;}
			}
		}
	}
	myTable.rows[lineNumber].name=testString;

}

function updateSection(myObj){
	alert(myObj.parent.parent.id);
}


function jtuneSuite(){
	switch(true){
		//case selectTest.loadBundle.selectedIndex!=0:
			//tuneName=selectTest.loadBundle.value.replace(/&/g,'%26');
			//break;
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
			if(confirm('File seems to be changed since loaded,\nwanna save it now for tuning?')){jsaveFile('TestBundle',tuneName);}
		}else{
			//alert('pippone');
			selectTest.savingName.value=tuneName;
			selectTest.action='/taws/tuning/';
			//selectTest.target='principale';
			selectTest.submit();
		}
	}else{
		selectTest.savingName.value=tuneName;
		selectTest.action='/taws/tuning/';
		//selectTest.target='principale';
		selectTest.submit();
	}
}

function fillSelectCreator(valueStr,myselect,selection){
  if(valueStr!=''){myselect.disabled=false;}
    else{myselect.disabled=true;}
  myselect.length=1;
  tempAry1=valueStr.split('@');
  for(i=0;i<tempAry1.length;i++){
    tempAry2=tempAry1[i].split('?');
    var addTest = document.createElement('option');
    addTest.text = tempAry2[0];
    if(tempAry2.length>1){addTest.value = tempAry2[1].replace(/#/g,'?').replace(/%/g,'@').replace(/\|/g,'%');}
    myselect.add(addTest);
    if(tempAry2[1]==selection){myselect.selectedIndex=i+1;}
  }
}

/*function editTest(){
	myTable=document.getElementById('testTable');
  	editList=''
	for(i=1;i<myTable.rows.length;i++){
		if(myTable.rows[i].style.background.indexOf('red')>=0){
      			tempStr=myTable.rows[i].name.split('#');
      			editList+=tempStr[13]+'#';
			myTable.deleteRow(i);
			i--
		}
	}
  editList=editList.slice(0,-1);
  doAccess('editList');
	updateStats('testBundleTable')
	colorTable('testBundleTable');
	document.getElementById('tuneBtn').disabled=true;
	//top.principale.document.getElementById('execBtn').disabled=true;
}*/

