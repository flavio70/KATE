var tempBundleListString = new Array();
var bundleListString = new Array();
var testListString = new Array();
var testTable;
var suiteChanged=false;
var valueTable;

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
	//patternFilter = "";
	//topologyFilter = "";
	//facilityFilter = "";
	//document.getElementById('filterStringLabel').value='';
	//document.getElementById('clearBtn').disabled=true;
	//document.getElementById('pattern').value='Pattern';
}


function queryDB2(userName){
	/*if(owner=='LOCAL'){
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
	document.getElementById('facility').disabled=false;
	document.getElementById('pattern').disabled=false;
	document.getElementById('filterString').disabled=false;
	document.getElementById('clearBtn').disabled=false;
	document.getElementById('negativeCheck').disabled=false;*/
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

function jsaveFile(suiteType){
	savingString='';
	foundSuite=false;
	saveText='';
	if(suiteName!=''){
		newText = prompt('Insert Suite Name!',suiteName);
		if(newText==suiteName){
			foundSuite=true;saveID=suiteID;
		}else{
			saveID=newText;
		}
	}else{
		newText = prompt('Insert Suite Name!','newSuite');
		if(suiteType=='userSuites'){
			for(j=0;j<serverPersonalSuite.children.length;j++){
				if(newText==serverPersonalSuite.children[j].children[0].name){foundSuite=true;saveID=serverPersonalSuite.children[j].children[0].id;}
			}
		}else{
			for(j=0;j<serverSharedSuite.children.length;j++){
				if(newText==serverSharedSuite.children[j].children[0].name){foundSuite=true;saveID=serverSharedSuite.children[j].children[0].id;}
			}
		}
		if(foundSuite==false){saveID=newText;}
	}
	suiteName = newText;
	for(k=0;k<testBundleTable.rows().data().length;k++){
		savingString+=testBundleTable.row(k).data().testId+'#';
		sect1=0;
		sect2=0;
		sect3=0;
		sect4=0;
		sect5=0;
		if(!(testBundleTable.row(testBundleTable.rows()[k]).data().sect1.match('disabled'))){sect1+=1;}
		if(!(testBundleTable.row(testBundleTable.rows()[k]).data().sect2.match('disabled'))){sect2+=1;}
		if(!(testBundleTable.row(testBundleTable.rows()[k]).data().sect3.match('disabled'))){sect3+=1;}
		if(!(testBundleTable.row(testBundleTable.rows()[k]).data().sect4.match('disabled'))){sect4+=1;}
		if(!(testBundleTable.row(testBundleTable.rows()[k]).data().sect5.match('disabled'))){sect5+=1;}
		if(testBundleTable.row(testBundleTable.rows()[k]).data().sect1.match('checked')){sect1+=1;}
		if(testBundleTable.row(testBundleTable.rows()[k]).data().sect2.match('checked')){sect2+=1;}
		if(testBundleTable.row(testBundleTable.rows()[k]).data().sect3.match('checked')){sect3+=1;}
		if(testBundleTable.row(testBundleTable.rows()[k]).data().sect4.match('checked')){sect4+=1;}
		if(testBundleTable.row(testBundleTable.rows()[k]).data().sect5.match('checked')){sect5+=1;}
		savingString+=String(sect1)+String(sect2)+String(sect3)+String(sect4)+String(sect5)+'$';
	}
	if((((foundSuite==true&&confirm("Overwrite " + newText +"?"))||foundSuite==false))&&(saveID!=''&&saveID!='null')&&(savingString!='')&&(newText!=null)){
		document.getElementById(suiteType).innerHTML=suiteName+' <span class="caret"></span>';
		doAccess('saveSuite');
		//alert(saveID);
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

function updateTestTableOldGen(tableName,testAry){
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

function addRecordToTableOldGen(testString,tableName,position){
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
	if(tbl=='testTable'){myTable=testTable;}
		else{myTable=testBundleTable;}
	myTable.rows().remove().draw( false );
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

function updateStatsOldGen(totalTable){
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
	rowNum=testTable.rows('.info').data().length;
	for(i=0;i<rowNum;i++){
		testCellAry=testTable.rows(i).data()[0].testString.split('#');
		testCellAry[17]=testCellAry[17].replace(/1/g,'2');
		testString=testCellAry.join('#');
		addRecordToTable(testString,'testBundleTable','');
	}
	updateStats('cart');
}

function insertAllBundleList(){
	//document.getElementById('transparency').style.zIndex=10;
	//document.getElementById('transparencyImg').style.visibility='visible';
	rowNum=testTable.rows().data().length;
	for(i=0;i<rowNum;i++){
		testCellAry=testTable.rows(i).data()[0].testString.split('#');
		testCellAry[17]=testCellAry[17].replace(/1/g,'2');
		testString=testCellAry.join('#');
		addRecordToTable(testString,'testBundleTable','');
	}
	updateStats('cart');
	suiteChanged=true;
	/*myTable=document.getElementById('testTable');
	for(i=1;i<myTable.rows.length;i++){
		testCellAry=myTable.rows[i].name.split('#');
		testCellAry[17]=testCellAry[17].replace(/1/g,'2');
		testString=testCellAry.join('#');
		addRecordToTable(testString,'testBundleTable','');
	}*/
	//colorTable('testBundleTable');
	//updateStats('testBundleTable')
	//document.getElementById('tuneBtn').disabled=true;
	//document.getElementById('transparency').style.zIndex=-1;
	//document.getElementById('transparencyImg').style.visibility='hidden';
}

function removeBundleList(){
	rowNum=testBundleTable.rows('.info').data().length;
	for(i=0;i<rowNum;i++){
		testBundleTable.rows(i).remove().draw();
	}
	updateStats('cart');
}

function removeAllBundleList(){
	testBundleTable.clear().draw();
	updateStats('cart')
}

function moveSelectedEdge(direction){
    var arr = jQuery('#testBundleTable tbody tr.info')
     
    for(var i=0; i<arr.length; i++) {           
        var tr = arr[i];           
        var row = jQuery(tr);               // row to move.
	var firstRow = testBundleTable.row(0)
        var prevRow = jQuery(tr).prev();    // row to move should be moved up and replace this.
        var nextRow = jQuery(tr).next();    // row to move should be moved up and replace this.
 
        /* already at the top? */
        if(direction=='up'&&prevRow.length==0){  break; }   
        if(direction=='down'&&nextRow.length==0){  break; }   
        
	if(direction=='up'){
		//moveData(row, firstRow);
		//moveVisualSelection(row, prevRow);
		numStep=row[0].sectionRowIndex;
		for(j=1;j<=numStep-i;j++){
			moveData(row, prevRow);
			moveVisualSelection(row, prevRow);
			row = prevRow;
			prevRow = prevRow.prev();
		}
	}
	if(direction=='down'){
		//moveData(row, firstRow);
		//moveVisualSelection(row, prevRow);
		//$('#testBundleTable').dataTable().fnAddData($('#testBundleTable').dataTable().fnGetData(row[0]));
		numStep=row[0].sectionRowIndex;
		for(j=numStep;j<testBundleTable.rows().data().length-i-1;j++){
			moveData(row, nextRow);
			moveVisualSelection(row, nextRow);
			row = nextRow;
			nextRow = nextRow.next();
		}
	}
    }  
 
    // send new comma-separated list of row order to server with ajax.
    //updateRowOrderOnServer(getAllNodes().toString());
	testBundleTable.column(1, {search:'applied', order:'applied'}).nodes().each( function (cell, i) {
		    cell.innerHTML = i+1;
		} );
}

function moveSelected(direction){
    var arr = jQuery('#testBundleTable tbody tr.info')
     
    for(var i=0; i<arr.length; i++) {           
        var tr = arr[i];           
        var row = jQuery(tr);               // row to move.
        var prevRow = jQuery(tr).prev();    // row to move should be moved up and replace this.
        var nextRow = jQuery(tr).next();    // row to move should be moved up and replace this.
 
        /* already at the top? */
        if(direction=='up'&&prevRow.length==0){  break; }   
        if(direction=='down'&&nextRow.length==0){  break; }   
        
	if(direction=='up'){moveData(row, prevRow);moveVisualSelection(row, prevRow);}
	if(direction=='down'){moveData(row, nextRow);moveVisualSelection(row, nextRow);}
    }  
 
    // send new comma-separated list of row order to server with ajax.
    //updateRowOrderOnServer(getAllNodes().toString());
	testBundleTable.column(1, {search:'applied', order:'applied'}).nodes().each( function (cell, i) {
		    cell.innerHTML = i+1;
		} );
}  
 
/* the visual stuff that show which rows are selected */
function moveVisualSelection(actualRow, futureRow){
    actualRow.removeClass("info");
    futureRow.addClass("info");
}
 
/* move the data in the internal datatable structure */
function moveData(actualRow, futureRow){     
    var movedData = $('#testBundleTable').dataTable().fnGetData(actualRow[0]);    // copy of row to move.
    var prevData = $('#testBundleTable').dataTable().fnGetData(futureRow[0]); // copy of old data to be overwritten by above data.
     
    // switch data around :)
    $('#testBundleTable').dataTable().fnUpdate(prevData , actualRow[0]); 
    $('#testBundleTable').dataTable().fnUpdate(movedData , futureRow[0]);
}      

function moveUpTest(){
	rowNum=testBundleTable.rows('.info').data().length;
	for(i=0;i<rowNum;i++){
		selectedRowNumber=testBundleTable.rows('.info')[i][0];
		oldRowNumber=testBundleTable.rows(selectedRowNumber).data()[0].num;
		$('#testBundleTable').dataTable().fnUpdate(oldRowNumber,oldRowNumber-1,1,false);
		$('#testBundleTable').dataTable().fnUpdate(oldRowNumber-1,oldRowNumber,1,false);
	}
	updateStats('cart');
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
	/*switch(true){
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
	}*/
	selectTest.savingName.value=suiteID;
	selectTest.action='/taws/tuning/';
	if(testBundleTable.rows().data().length!=0){
		if(suiteChanged){
			if(confirm('File seems to be changed since loaded,\nwanna save it now for tuning?')){jsaveFile('TestBundle',suiteName);}
		}else{
			//alert('pippone');
			//selectTest.savingName.value=tuneName;
			//selectTest.action='/taws/tuning/';
			//selectTest.target='principale';
			selectTest.submit();
		}
	}else{
		//selectTest.savingName.value=tuneName;
		//selectTest.action='/taws/tuning/';
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

function updateTestTable(tableName,testAry){
	emptyTable(tableName);
	/*if(tableName=='testTable'){myTable=testTable;}
		else{myTable=testBundleTable;}
	myTable.rows().remove().draw( false );*/
	for (i = 0;i < testAry.length-1; i++) {
		addRecordToTable(testAry[i],tableName,'');
	}
	//if(tableName=='testBundleTable'){
	//	updateStats(testTable);
		//document.getElementById('tuneBtn').disabled=false;
	//}
	//colorTable(tableName);
	//if(document.getElementById('reportTable')){createReportHistory();}
}

function addRecordToTable(testString,tableName,lineNumber){
	if(tableName=='testTable'){
		myTable=testTable;
		myNum='';
	}else{
		myTable=testBundleTable;
		myNum=myTable.rows().data().length+1;
	}
	tempField=testString.split('#');
	tempRev=tempField[18].split('!');
 	//revStr='<select onchange="iteration=this.value;lineNumber=this.parentElement.parentElement.rowIndex;currentTable=\''+tableName+'\';doAccess(\'queryIteration\');">';
 	revStr='<select onchange="iteration=this.value;lineNumber=$(this).rowIndex;currentTable=\''+tableName+'\';doAccess(\'queryIteration\');">';
	for(j=0;j<tempRev.length;j++){
		myRev=tempRev[j].split('|');
		if(j==0){revision=myRev[1];}
		revStr+='<option value="'+myRev[1]+'">'+myRev[0]+'</option>';
	}
	revStr+='</select>';
	sectFunct=' onclick="changeSection(this);"';
	if(tableName=='testBundleTable'){
		if(tempField[17][0]=='2'){sect1='<input type="checkbox" checked'+sectFunct+'>';}
		if(tempField[17][0]=='1'){sect1='<input type="checkbox"'+sectFunct+'>';}
		if(tempField[17][0]=='0'){sect1='<input type="checkbox" disabled'+sectFunct+'>';}
	}else{sect1='<img src="'+SECT[tempField[17][0]]+'"/>';}
	if(tableName=='testBundleTable'){
		if(tempField[17][1]=='2'){sect2='<input type="checkbox" checked'+sectFunct+'>';}
		if(tempField[17][1]=='1'){sect2='<input type="checkbox"'+sectFunct+'>';}
		if(tempField[17][1]=='0'){sect2='<input type="checkbox" disabled'+sectFunct+'>';}
	}else{sect2='<img src="'+SECT[tempField[17][1]]+'"/>';}
	if(tableName=='testBundleTable'){
		if(tempField[17][2]=='2'){sect3='<input type="checkbox" checked'+sectFunct+'>';}
		if(tempField[17][2]=='1'){sect3='<input type="checkbox"'+sectFunct+'>';}
		if(tempField[17][2]=='0'){sect3='<input type="checkbox" disabled'+sectFunct+'>';}
	}else{sect3='<img src="'+SECT[tempField[17][2]]+'"/>';}
	if(tableName=='testBundleTable'){
		if(tempField[17][3]=='2'){sect4='<input type="checkbox" checked'+sectFunct+'>';}
		if(tempField[17][3]=='1'){sect4='<input type="checkbox"'+sectFunct+'>';}
		if(tempField[17][3]=='0'){sect4='<input type="checkbox" disabled'+sectFunct+'>';}
	}else{sect4='<img src="'+SECT[tempField[17][3]]+'"/>';}
	if(tableName=='testBundleTable'){
		if(tempField[17][4]=='2'){sect5='<input type="checkbox" checked'+sectFunct+'>';}
		if(tempField[17][4]=='1'){sect5='<input type="checkbox"'+sectFunct+'>';}
		if(tempField[17][4]=='0'){sect5='<input type="checkbox" disabled'+sectFunct+'>';}
	}else{sect5='<img src="'+SECT[tempField[17][4]]+'"/>';}
	myTable.row.add({
		"control" : '',
		"num" : myNum,
		"tps" : tempField[5],
		"test": tempField[6],
		"lab" : tempField[19],
		"rev" : revStr,
		"time": tempField[7],
		"topo": tempField[9],
		"sect1": sect1,
		"sect2": sect2,
		"sect3": sect3,
		"sect4": sect4,
		"sect5": sect5,
		"testId": tempField[0],
		"dependency": tempField[12],
		"metric": tempField[8],
		"assignment": "",
		"author": tempField[14],
		"description": tempField[15],
		"relDate": "",
		"lastUpdate": tempField[16],
		"testString":testString
	}
	).draw( false );
	/*$('#testTable tfoot th').each( function () {
		var title = $(this).prop('title');
		if (title == 'TPS') {$(this).html( '<input type="text" placeholder="Search '+title+'" />' );}
	});*/
//myTable
}

function modRecordToTable(testString,lineNumber,tableName){
	//if(tableName=='testTable'){myTable=testTable;}
	//	else{myTable=testBundleTable;}
	//var myTable = myRow.closest('table');
	//var row = myTable.row(myRow);
	tempField=testString.split('#');
	//tempRev=tempField[18].split('!');
 	//revStr='<select onchange="iteration=this.value;lineNumber=this.parentElement.parentElement.rowIndex;currentTable=this.parentElement.parentElement.parentElement.parentElement;doAccess(\'queryIteration\');">';
	/*revStr='<select onchange="iteration=this.value;lineNumber=$(this).rowIndex;currentTable=\''+currentTable+'\';doAccess(\'queryIteration\');">';
	for(j=0;j<tempRev.length;j++){
		myRev=tempRev[j].split('|');
		checked='';
		alert(tempField[20]+'###'+myRev[0]);
		if(tempField[20]==myRev[0]){checked='checked';alert('CULO');}
		revStr+='<option value="'+myRev[1]+'" '+checked+'>'+myRev[0]+'</option>';
	}
	alert(revStr);*/
	sectFunct=' onclick="changeSection(this);"';
	if(tableName=='testBundleTable'){
		if(tempField[17][0]=='2'){sect1='<input type="checkbox" checked'+sectFunct+'>';}
		if(tempField[17][0]=='1'){sect1='<input type="checkbox"'+sectFunct+'>';}
		if(tempField[17][0]=='0'){sect1='<input type="checkbox" disabled'+sectFunct+'>';}
	}else{sect1='<img src="'+SECT[tempField[17][0]]+'"/>';}
	if(tableName=='testBundleTable'){
		if(tempField[17][1]=='2'){sect2='<input type="checkbox" checked'+sectFunct+'>';}
		if(tempField[17][1]=='1'){sect2='<input type="checkbox"'+sectFunct+'>';}
		if(tempField[17][1]=='0'){sect2='<input type="checkbox" disabled'+sectFunct+'>';}
	}else{sect2='<img src="'+SECT[tempField[17][1]]+'"/>';}
	if(tableName=='testBundleTable'){
		if(tempField[17][2]=='2'){sect3='<input type="checkbox" checked'+sectFunct+'>';}
		if(tempField[17][2]=='1'){sect3='<input type="checkbox"'+sectFunct+'>';}
		if(tempField[17][2]=='0'){sect3='<input type="checkbox" disabled'+sectFunct+'>';}
	}else{sect3='<img src="'+SECT[tempField[17][2]]+'"/>';}
	if(tableName=='testBundleTable'){
		if(tempField[17][3]=='2'){sect4='<input type="checkbox" checked'+sectFunct+'>';}
		if(tempField[17][3]=='1'){sect4='<input type="checkbox"'+sectFunct+'>';}
		if(tempField[17][3]=='0'){sect4='<input type="checkbox" disabled'+sectFunct+'>';}
	}else{sect4='<img src="'+SECT[tempField[17][3]]+'"/>';}
	if(tableName=='testBundleTable'){
		if(tempField[17][4]=='2'){sect5='<input type="checkbox" checked'+sectFunct+'>';}
		if(tempField[17][4]=='1'){sect5='<input type="checkbox"'+sectFunct+'>';}
		if(tempField[17][4]=='0'){sect5='<input type="checkbox" disabled'+sectFunct+'>';}
	}else{sect5='<img src="'+SECT[tempField[17][4]]+'"/>';}
	//revStr+='</select>';
	var oTable = $('#'+tableName).dataTable();
	//oTable.fnUpdate( ['','1',tempField[5],tempField[6],tempField[19],revStr,tempField[7],tempField[9],sect1,sect2,sect3,sect4,sect5,tempField[0],tempField[12],tempField[8],"",tempField[14],tempField[15],"",tempField[16],testString,revision],0);
	oTable.fnUpdate('',lineNumber,0,false);
	//oTable.fnUpdate(lineNumber,lineNumber,1,false);
	oTable.fnUpdate(tempField[5],lineNumber,2,false);
	oTable.fnUpdate(tempField[6],lineNumber,3,false);
	oTable.fnUpdate(tempField[19],lineNumber,4,false);
	//oTable.fnUpdate(revStr,lineNumber,5,true);
	oTable.fnUpdate(tempField[7],lineNumber,6,false);
	oTable.fnUpdate(tempField[9],lineNumber,7,false);
	oTable.fnUpdate(sect1,lineNumber,8,false);
	oTable.fnUpdate(sect2,lineNumber,9,false);
	oTable.fnUpdate(sect3,lineNumber,10,false);
	oTable.fnUpdate(sect4,lineNumber,11,false);
	oTable.fnUpdate(sect5,lineNumber,12,false);
	oTable.fnUpdate(tempField[0],lineNumber,13,false);
	oTable.fnUpdate(tempField[12],lineNumber,14,false);
	oTable.fnUpdate(tempField[8],lineNumber,15,false);
	oTable.fnUpdate('',lineNumber,16,false);
	oTable.fnUpdate(tempField[14],lineNumber,17,false);
	oTable.fnUpdate(tempField[15],lineNumber,18,false);
	oTable.fnUpdate('',lineNumber,19,false);
	oTable.fnUpdate(tempField[16],lineNumber,20,false);
	oTable.fnUpdate(testString,lineNumber,21,false);
	//oTable.fnUpdate(revision,lineNumber,22,false);
	/*testTable.row(myRow).data().tps=tempField[5];
	testTable.row(myRow).data().test=tempField[6];
	testTable.row(myRow).data().lab=tempField[19];
	testTable.row(myRow).data().rev=revStr;
	testTable.row(myRow).data().time=tempField[7];
	testTable.row(myRow).data().topo=tempField[9];
	testTable.row(myRow).data().sect1=sect1;
	testTable.row(myRow).data().sect2=sect2;
	testTable.row(myRow).data().sect3=sect3;
	testTable.row(myRow).data().sect4=sect4;
	testTable.row(myRow).data().sect5=sect5;
	testTable.row(myRow).data().testId=tempField[0];
	testTable.row(myRow).data().dependency=tempField[12];
	testTable.row(myRow).data().metric=tempField[8];
	testTable.row(myRow).data().assignment="";
	testTable.row(myRow).data().author=tempField[14];
	testTable.row(myRow).data().description=tempField[15];
	testTable.row(myRow).data().relDate="";
	testTable.row(myRow).data().lastUpdate=tempField[16];
	testTable.row(myRow).data().testString=testString;
	testTable.row(myRow).data().revision=revision;
	testTable.row(myRow).data().draw(false);*/
	/*$('#testTable tfoot th').each( function () {
		var title = $(this).prop('title');
		if (title == 'TPS') {$(this).html( '<input type="text" placeholder="Search '+title+'" />' );}
	});*/

}
function fillButtons(values,nextItem,selection,currButton){
	if(nextItem=='sw-release'){
		document.getElementById('sw-release').innerHTML='SW Version <span class="caret"></span>';
		document.getElementById('domain-dropdown').innerHTML='';
		document.getElementById('domain').innerHTML='Domain <span class="caret"></span>';
		document.getElementById('area-dropdown').innerHTML='';
		document.getElementById('area').innerHTML='Area <span class="caret"></span>';
		nextSelection='domain';
		document.getElementById('domain').disabled=true;
		document.getElementById('area').disabled=true;
	}
	if(nextItem=='domain'){
		document.getElementById('domain').innerHTML='Domain <span class="caret"></span>';
		document.getElementById('area-dropdown').innerHTML='';
		document.getElementById('area').innerHTML='Area <span class="caret"></span>';
		nextSelection='area';
		document.getElementById('area').disabled=true;
	}
	if(nextItem=='area'){document.getElementById('area').innerHTML='Area <span class="caret"></span>';}
	document.getElementById(currButton).innerHTML=selection+' <span class="caret"></span>';
	document.getElementById(nextItem).disabled=false;
	tempAry1=values.split('@');
	newDropDown='';
	for(i=0;i<tempAry1.length;i++){
		tempAry2=tempAry1[i].split('?');
		nextValues='';
		if(tempAry2.length>1){nextValues=tempAry2[1].replace(/#/g,'?').replace(/%/g,'@').replace(/\|/g,'%')}
		newDropDown+='<li><a onclick="fillButtons(\''+nextValues+'\',\''+nextSelection+'\',\''+tempAry2[0]+'\',\''+nextItem+'\');">'+tempAry2[0]+'</a></li>';
	}
	if(currButton=='area'){queryDB();}
		else{document.getElementById(nextItem+'-dropdown').innerHTML=newDropDown;}
}

function queryDB(userName){
	queryProduct=document.getElementById('product').innerHTML.replace(' <span class="caret"></span>','');
	querySWRelease=document.getElementById('sw-release').innerHTML.replace(' <span class="caret"></span>','');
	queryArea=document.getElementById('area').innerHTML.replace(' <span class="caret"></span>','');
	doAccess('queryDB');
}

function updateStats(perspective){
	if(perspective=='selection'){
		totTime=0;
		totMetric=0;
		totTPS=0;
		for(k=0;k<testTable.rows('.info').data().length;k++){
			totTime+=parseInt(testTable.row(testTable.rows('.info')[k]).data().time);
			totMetric+=parseInt(testTable.row(testTable.rows('.info')[k]).data().metric);
			tempTPS=testTable.row(testTable.rows('.info')[k]).data().tps
			totTPS+=(tempTPS.length-tempTPS.replace('<br>','').length)/4+1
		}
		document.getElementById('badge-sel-test').innerHTML=testTable.rows('.info').data().length;
		document.getElementById('badge-sel-tps').innerHTML=totTPS;
		document.getElementById('badge-sel-time').innerHTML=String(totTime).toHHMMSS();
		document.getElementById('badge-sel-metric').innerHTML=totMetric;
	}
	if(perspective=='cart'){
		totTime=0;
		totMetric=0;
		totTPS=0;
		for(k=0;k<testBundleTable.rows().data().length;k++){
			totTime+=parseInt(testBundleTable.row(testBundleTable.rows()[k]).data().time);
			totMetric+=parseInt(testBundleTable.row(testBundleTable.rows()[k]).data().metric);
			tempTPS=testBundleTable.row(testBundleTable.rows()[k]).data().tps;
			totTPS+=(tempTPS.length-tempTPS.replace('<br>','').length)/4+1;
		}
		document.getElementById('badge-cart-test').innerHTML=testBundleTable.rows().data().length;
		document.getElementById('badge-cart-tps').innerHTML=totTPS;
		document.getElementById('badge-cart-time').innerHTML=String(totTime).toHHMMSS();
		document.getElementById('badge-cart-metric').innerHTML=totMetric;
		showalert("Test Cases Adde Succesfully.&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Total Test:"+testBundleTable.rows().data().length+"\
							  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Tot Time:"+String(totTime).toHHMMSS()+"\
							  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Total TPS:"+totTPS+"\
							  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Total Metric:"+totMetric,"alert-success")
	}
	/*var myTable = document.getElementById(totalTable);
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
	document.getElementById(tableName + "Metric").innerHTML  = tot4;*/
}

String.prototype.toHHMMSS = function () {
    var sec_num = parseInt(this, 10); // don't forget the second param
    var hours   = Math.floor(sec_num / 3600);
    var minutes = Math.floor((sec_num - (hours * 3600)) / 60);
    var seconds = sec_num - (hours * 3600) - (minutes * 60);

    if (hours   < 10) {hours   = "0"+hours;}
    if (minutes < 10) {minutes = "0"+minutes;}
    if (seconds < 10) {seconds = "0"+seconds;}
    var time    = hours+':'+minutes+':'+seconds;
    return time;
}

function changeSection(myObj){
	var oTable = $('#testBundleTable').dataTable();
	lineNumber=myObj.closest('tr').sectionRowIndex;
	cellNumber=myObj.parentElement.cellIndex;
	if(myObj.checked==true){
		oTable.fnUpdate('<input type="checkbox" checked'+sectFunct+'>',lineNumber,cellNumber,false);
	}else{
		oTable.fnUpdate('<input type="checkbox"'+sectFunct+'>',lineNumber,cellNumber,false);
	}
}
