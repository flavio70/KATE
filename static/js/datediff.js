// JScript source code
	var DayName=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
	
	
	
	var oneMinute=1000*60;
	
	var intervalObject=new Object();
	intervalObject["yyyy"]={units:1000*60*60*24*365,measure:"year"};
	intervalObject["m"]={units:1000*60*60*24*30,measure:"month"};
	intervalObject["d"]={units:1000*60*60*24,measure:"day"};
		
	
	function DateDiff(dateAddObj){
		this.interval=dateAddObj.interval;
		this.date1=dateAddObj.date1;
		this.date2=dateAddObj.date2;
		this.calculate=calculate;
		this.calculate();
	}

	Date.prototype.DateDiff=DateDiff;
	
	function calculate(){
		
		var paramDate1=new String(this.date1);
		splitDate1=paramDate1.split("/");
		paramDateYear1=splitDate1[2];
		paramDateMonth1=splitDate1[1]-1;
		paramDateDay1=splitDate1[0];
		
		var paramDate2=new String(this.date2);
		splitDate2=paramDate2.split("/");
		paramDateYear2=splitDate2[2];
		paramDateMonth2=splitDate2[1]-1;
		paramDateDay2=splitDate2[0];
						
		var paramDate1Object=new Date(paramDateYear1,paramDateMonth1,paramDateDay1);
		paramDate1Object.setHours(0);
		paramDate1Object.setMinutes(0);
		paramDate1Object.setSeconds(0);
		var paramDate1ObjectTime=paramDate1Object.getTime();
		
		
		var paramDate2Object=new Date(paramDateYear2,paramDateMonth2,paramDateDay2);
		paramDate2Object.setHours(0);
		paramDate2Object.setMinutes(0);
		paramDate2Object.setSeconds(0);
		var paramDate2ObjectTime=paramDate2Object.getTime();
		
		
			
		var diff= paramDate1ObjectTime-paramDate2ObjectTime;
		var timeDiff=Math.floor(diff/intervalObject[this.interval].units);
			
		this.difference = timeDiff;
		
		
	}

