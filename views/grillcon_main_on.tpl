<!DOCTYPE html>
<html lang="en">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<link rel="shortcut icon" href="{{ get_url('static', path='favicon.ico') }}">
<link rel="stylesheet" href="{{ get_url('static', path='style.css') }}">

<title>Grill Controller</title>

<script type="text/javascript"
    src="http://code.jquery.com/jquery-1.10.1.min.js"></script>
<script>
    $(document).ready(
            function() {
                setInterval(function() {
                    xmlhttp.open("GET", "/getupdate.json", true);
                    xmlhttp.send();
                    //alert("test")
                }, 10000);
            });
</script>


<script type="text/javascript">
var xmlhttp;

xmlhttp=new XMLHttpRequest();



// This will render the two output which substitute the
// elements id="raw" and id="forin"
function GetItems()
{
    
  if (xmlhttp.readyState==4 && xmlhttp.status==200) {
    // var jsonobj = eval ("(" + xmlhttp.responseText + ")"); 
    var jsonobj = JSON.parse(xmlhttp.responseText); 

    // var output = xmlhttp.responseText;
    // document.getElementById("raw").innerHTML = output;

    // logic to display data if offline
    if (navigator.onLine) {
            output = "";
            output += jsonobj[3]
            document.getElementById("timestamp").innerHTML = output;
    } else{
            output = "Grill: ";
            output += jsonobj[0]
            output += " Meat: "
            output += jsonobj[1]
            output += " Fan: "
            output += jsonobj[2]
            output += " Timestamp: "
            output += jsonobj[3]
            document.getElementById("timestamp").innerHTML = output;
    }

    
    //var json_array = JSON.parse(json_string);
    // for (i in jsonobj) {
        // jsonobj[i] = JSON.parse(jsonobj[i]);
    // }
    
    for (var i = 0; i < 3; i++) {
    jsonobj[i] = JSON.parse(jsonobj[i]);
    }

    drawChart2(jsonobj[0], jsonobj[1], jsonobj[2]);

  } else {
    alert("data not available");
  }
}

// xmlhttp.onreadystatechange = GetArticles;
// the GetItems function will be triggered once the ajax
// request is terminated.
xmlhttp.onload = GetItems;

// send the request in an async way
function start()
{
    createFormNotes();
    xmlhttp.open("GET", "/getupdate.json", true);
    xmlhttp.send();
}
</script>


<script type="text/javascript" src="https://www.google.com/jsapi"></script>    
        <script type="text/javascript">
        google.load("visualization", "1", {packages:["gauge"]});      
        google.setOnLoadCallback(drawChart);      
    function drawChart() 
    {        
       var data = google.visualization.arrayToDataTable([
        ['Label', 'Value'],
        ['Grill', {{dict_temps_row['grill_temp']}}],
        ['Meat', {{dict_temps_row['meat_temp']}}],
        ['Fan', {{dict_temps_row['fan']}}]
        ]);

        var options = {
        width: 400, height: 120,
        max: 300, min: 0,
        redFrom: 275, redTo: 300,
        yellowFrom:250, yellowTo: 275,
        minorTicks: 20
        };
        var chart = new google.visualization.Gauge(document.getElementById('guages_div'));
        chart.draw(data, options);
    };    
    function drawChart2(grill, meat, fan) 
    {        
       var data = google.visualization.arrayToDataTable([
        ['Label', 'Value'],
        ['Grill', grill],
        ['Meat', meat],
        ['Fan', fan]
        ]);
        
        var options = {
        width: 400, height: 120,
        max: 300, min: 0,
        redFrom: 275, redTo: 300,
        yellowFrom:250, yellowTo: 275,
        minorTicks: 20
        };
        var chart = new google.visualization.Gauge(document.getElementById('guages_div'));
        chart.draw(data, options);
    };

</script>

<script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
    google.load("visualization", "1", {packages:["corechart"]});
    google.setOnLoadCallback(drawChart);
    function drawChart() {
        var data = google.visualization.arrayToDataTable([
        ['Time', 'Grill Temp', 'Meat Temp'],
        {{!rows}}
        ]);
        var options = {
            title: 'Temperature'
        };
        var chart = new google.visualization.LineChart(document.getElementById('table_div'));
        chart.draw(data, options);
    }
</script>
 
 <script>
    function showStatus() {
    var div = document.getElementById("status");
                div.textContent = "The grill is On, target temp is " + {{dict_variables_row['target']}} + ", finish temp is " + {{dict_variables_row['finish']}};
                var text = div.textContent;
        };
        
    // jQuery(document).ready(function() {
    // jQuery('.tabs .tab-links a').on('click', function(e)  {
        // var currentAttrValue = jQuery(this).attr('href');

        // // Show/Hide Tabs
        // //jQuery('.tabs ' + currentAttrValue).show().siblings().hide();
        // window.location.href = currentAttrValue;
        // //alert(currentAttrValue);

        // // Change/remove current tab to active
        // jQuery(this).parent('li').addClass('active').siblings().removeClass('active');

        // e.preventDefault();
    // });
// });

function createFormNotes(){

    var userDiv = document.getElementById("notesDiv");

    var createFormUser = document.createElement('form'); // Create New Element Form
    createFormUser.setAttribute("action", "/main"); // Setting Action Attribute on Form
    createFormUser.setAttribute("method", "post"); // Setting Method Attribute on Form
    userDiv.appendChild(createFormUser);

    var textboxNotes = document.createElement("input");
    createFormUser.appendChild(document.createTextNode("Notes "));
    textboxNotes.type = "text";
    textboxNotes.name = "notes";
    textboxNotes.placeholder = "{{!cook_notes}}";
    textboxNotes.style.width = '40%';   // CSS property
    createFormUser.appendChild(textboxNotes);
    createFormUser.appendChild(document.createElement('br'));
    
    var submitelement = document.createElement('input'); // Append Submit Button
    submitelement.setAttribute("type", "submit");
    submitelement.setAttribute("name", "notesSubmit");
    submitelement.setAttribute("value", "Submit");
    createFormUser.appendChild(submitelement);
}

 </script>

</head>

<body onload="start()">

<div class="tabs">
    <ul class="tab-links">
        <li class="active"><a href="/main">Main</a></li>
        <li><a href="/history">History</a></li>
        <li><a href="/admin">Admin</a></li>
    </ul>

</div>

<div id="guages_div" style="width: 400px; height: 120px;"></div>


<p>
<div id="status"></div>
<script type="text/javascript">
    showStatus()
</script>
</p>

<p>The latest update is:</p>
<div id="timestamp"></div>
<br>

<!--form to modify cook if grill is on-->
<div id="modify_form">
<br>
<p>Modify cook settings below:</p>

<form action="/main" method="POST">
    Cook Name
    <select name="option_cook_name">
    <option value="name">{{dict_variables_row['name']}}</option>
    </select>
    Target Grill Temp
    <input type="text" size="10" name="option_target_temp" value="">
    
    Meat Finish Temp
    <input type="text" size="10" name="option_finish_temp" value="">

    <input type="submit" name="Modify Current Cook" value="Modify Current Cook">
</form>

<form action="/main" method="POST">
    <input type="radio" name="option_off" value="Off">Off
    <input type="submit" value="Turn Off">
</form>

 
<div id="table_div" style="width: 900px; height: 500px;"></div>
<br>
<div id="notesDiv"> </div>




</body>
</html>



