<!DOCTYPE html>
<html lang="en">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<link rel="shortcut icon" href="{{ get_url('static', path='favicon.ico') }}">
<link rel="stylesheet" href="{{ get_url('static', path='style.css') }}">

<title>Grill Controller</title>

<script type="text/javascript" src="https://www.google.com/jsapi"></script>    
        <script type="text/javascript">
        google.load("visualization", "1", {packages:["gauge"]});      
        google.setOnLoadCallback(drawChart);      
    function drawChart() 
    {        
       var data = google.visualization.arrayToDataTable([
        ['Label', 'Value'],
        ['Grill', 0],
        ['Meat', 0],
        ['Fan', 0]
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

</head>

<body>

<div class="tabs">
    <ul class="tab-links">
        <li class="active"><a href="/main">Main</a></li>
        <li><a href="/history">History</a></li>
        <li><a href="/admin">Admin</a></li>
    </ul>

</div>

<div id="guages_div" style="width: 400px; height: 120px;"></div>


<!--form to start new cook if grill is off-->
<div id="new_form">
<br>
<p>Enter cook settings below:</p>

<form action="/main" method="POST">
    Meat Type  
    <select name="option_cook_name">
    <option value="" selected disabled></option>
    <option value="Brisket">Brisket</option>
    <option value="Shoulder Roast">Shoulder Roast</option>
    <option value="Ribs">Ribs</option>
    <option value="Other">Other</option>
    </select>
    <br> <br>

    Target Grill Temp
    <input type="text" size="10" name="option_target_temp" value="">
    <br> <br>

    Meat Finish Temp
    <input type="text" size="10" name="option_finish_temp" value="">
    <br> <br>

    <input type="submit" name="Start Grill Controller" value="Start Grill Controller">
</form>
</div>


<div id="show" align="center"></div>
   

</body>
</html>



