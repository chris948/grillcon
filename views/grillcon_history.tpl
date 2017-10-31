<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />

<link rel="shortcut icon" href="{{ get_url('static', path='favicon.ico') }}">
<link rel="stylesheet" href="{{ get_url('static', path='style.css') }}">

<title>Grill Controller</title>

<script type="text/javascript">
    function start()
    {
        createHistoryForm();
        addText();
        createFormNotes();
    }
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
    };

function createHistoryForm(){
    var selectDiv = document.getElementById("selectHistDiv");

    //Create array of options to be added
    //var array = ["Volvo2","Saab","Mercades","Audi"];
    var array = {{!list}};

    var createform = document.createElement('form'); // Create New Element Form
    createform.setAttribute("action", ""); // Setting Action Attribute on Form
    createform.setAttribute("method", "post"); // Setting Method Attribute on Form
    selectDiv.appendChild(createform);

    //Create and append select list
    var selectList = document.createElement("select");
    selectList.setAttribute("id", "historyID");
    selectList.setAttribute("name", "historyName");
    //selectList.id = "mySelect";

    createform.appendChild(selectList);

    //Create and append the options
    for (var i = 0; i < array.length -1; i++) {
        var option = document.createElement("option");
        option.setAttribute("value", array[i]);
        option.text = array[i];
        if (array[i] == "{{graph_value}}") {
            option.selected = true;
        }
        selectList.appendChild(option);
    }

    

    var submitelement = document.createElement('input'); // Append Submit Button
    submitelement.setAttribute("type", "submit");
    submitelement.setAttribute("name", 'submit');
    submitelement.setAttribute("value", "Submit");
    createform.appendChild(submitelement);
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


</script>

<script type="text/javascript">
function addText(){
    document.getElementById("notesBox").innerHTML = "Notes: " + "{{cook_notes}}";
}
</script>

<script type="text/javascript">
function createFormNotes(){

    var userDiv = document.getElementById("notesDiv");

    var createFormUser = document.createElement('form'); // Create New Element Form
    createFormUser.setAttribute("action", "/history"); // Setting Action Attribute on Form
    createFormUser.setAttribute("method", "post"); // Setting Method Attribute on Form
    userDiv.appendChild(createFormUser);

    var textboxNotes = document.createElement("input");
    createFormUser.appendChild(document.createTextNode("Edit Notes "));
    textboxNotes.type = "text";
    textboxNotes.name = "notes";
    textboxNotes.style.width = '20%';   // CSS property
    textboxNotes.placeholder = "{{cook_notes}}";
    createFormUser.appendChild(textboxNotes);
    createFormUser.appendChild(document.createElement('br'));
    
    var textboxHidden = document.createElement("input");
    //createFormUser.appendChild(document.createTextNode("Notes "));
    textboxHidden.type = "hidden";
    textboxHidden.name = "hidden";
    textboxHidden.value = "{{!graph_value}}";
    createFormUser.appendChild(textboxHidden);
    //createFormUser.appendChild(document.createElement('br'));
    
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
        <li><a href="/main">Main</a></li>
        <li class="active"><a href="/history">History</a></li>
        <li><a href="/admin">Admin</a></li>
    </ul>

</div>

<div id="selectHistDiv"> Change Graph </div>


<div id="table_div" style="width: 900px; height: 500px;"></div>
<br>
<p id ="notesBox"></p>
<br>
<div id="notesDiv"></div>



</body>

</html>
