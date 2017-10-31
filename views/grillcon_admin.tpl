<!DOCTYPE html>
<html lang="en">
<head>

<link rel="shortcut icon" href="{{ get_url('static', path='favicon.ico') }}">
<link rel="stylesheet" href="{{ get_url('static', path='style.css') }}">

<title>Grill Controller Admin</title>

<script type="text/javascript">

function start(){
    createFormBackup();
    createFormSettings();
    createFormUser();
    createHistoryForm();
    
}

function createFormBackup(){
    
    var backupDiv = document.getElementById("backupDiv");

    var createFormBackup = document.createElement('form'); // Create New Element Form
    createFormBackup.setAttribute("action", "/admin"); // Setting Action Attribute on Form
    createFormBackup.setAttribute("method", "post"); // Setting Method Attribute on Form
    backupDiv.appendChild(createFormBackup);


    var submitelement = document.createElement('input'); // Append Submit Button
    submitelement.setAttribute("type", "submit");
    submitelement.setAttribute("name", "backupSubmit");
    submitelement.setAttribute("value", "Backup");
    createFormBackup.appendChild(submitelement);    
}

function createFormSettings(){

    var settingsDiv = document.getElementById("settingsDiv");

    var createFormSettings = document.createElement('form'); // Create New Element Form
    createFormSettings.setAttribute("action", "/admin"); // Setting Action Attribute on Form
    createFormSettings.setAttribute("method", "post"); // Setting Method Attribute on Form
    settingsDiv.appendChild(createFormSettings);
    
    //loop to populate user settings, obviously password is encrypted
    //for key, value in list_settings.iteritems():
    %for key, value in list_settings.iteritems():

        var textbox{{key}} = document.createElement("input");
        createFormSettings.appendChild(document.createTextNode(" {{key}} "));
        textbox{{key}}.type = "text";
        textbox{{key}}.name = "{{key}}";
        textbox{{key}}.value = "{{value}}";
        createFormSettings.appendChild(textbox{{key}});
        createFormSettings.appendChild(document.createElement('br'));
        
    %end
    

    var submitelement = document.createElement('input'); // Append Submit Button
    submitelement.setAttribute("type", "submit");
    submitelement.setAttribute("name", "settingsSubmit");
    submitelement.setAttribute("value", "Submit");
    createFormSettings.appendChild(submitelement);
}

function createFormUser(){

    var userDiv = document.getElementById("userDiv");

    var createFormUser = document.createElement('form'); // Create New Element Form
    createFormUser.setAttribute("action", "/admin"); // Setting Action Attribute on Form
    createFormUser.setAttribute("method", "post"); // Setting Method Attribute on Form
    userDiv.appendChild(createFormUser);

    var textboxRole = document.createElement("input");
    createFormUser.appendChild(document.createTextNode("User Role "));
    textboxRole.type = "text";
    textboxRole.name = "user_role";
    textboxRole.placeholder = "{{list_user[0]}}";
    createFormUser.appendChild(textboxRole);
    createFormUser.appendChild(document.createElement('br'));
    
    var textboxUserName = document.createElement("input");
    createFormUser.appendChild(document.createTextNode("User Name "));
    textboxUserName.type = "text";
    textboxUserName.name = "user_username";
    textboxUserName.placeholder = "{{list_user[1]}}";
    createFormUser.appendChild(textboxUserName);
    createFormUser.appendChild(document.createElement('br'));
    
    var textboxPassword = document.createElement("input");
    createFormUser.appendChild(document.createTextNode("User Password "));
    textboxPassword.type = "text";
    textboxPassword.name = "user_password";
    textboxPassword.placeholder = "********";
    createFormUser.appendChild(textboxPassword);
    createFormUser.appendChild(document.createElement('br'));
    
    var submitelement = document.createElement('input'); // Append Submit Button
    submitelement.setAttribute("type", "submit");
    submitelement.setAttribute("name", "userSubmit");
    submitelement.setAttribute("value", "Submit");
    createFormUser.appendChild(submitelement);
}

function createHistoryForm(){
    var selectDiv = document.getElementById("selectHistDiv");

    //Create array of options to be added
    //var array = ["Volvo2","Saab","Mercades","Audi"];
    var array = {{!cook_list}};

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
    for (var i = 0; i < array.length; i++) {
        var option = document.createElement("option");
        option.setAttribute("value", array[i]);
        option.text = array[i];
        selectList.appendChild(option);
    }

    var submitelement = document.createElement('input'); // Append Submit Button
    submitelement.setAttribute("type", "submit");
    submitelement.setAttribute("name", 'deleteSubmit');
    submitelement.setAttribute("value", "Delete Cook");
    createform.appendChild(submitelement);
};


// jQuery(document).ready(function() {
    // jQuery('.tabs .tab-links a').on('click', function(e)  {
        // var currentAttrValue = jQuery(this).attr('href');

        // // Show/Hide Tabs
        // //jQuery('.tabs ' + currentAttrValue).show().siblings().hide();
        // window.location.href = currentAttrValue;
        // //alert(currentAttrValue);

        // //Change/remove current tab to active
        // jQuery(this).parent('li').addClass('active').siblings().removeClass('active');

        // e.preventDefault();
    // });
// });



</script>

</head>

<body onload="start()">




<div class="tabs">
    <ul class="tab-links">
        <li><a href="/main">Main</a></li>
        <li><a href="/history">History</a></li>
        <li class="active"><a href="/admin">Admin</a></li>
    </ul>

</div>



Backup Database
<div id="backupDiv"> </div>
<br>
<div id="selectHistDiv"> Delete Cook </div>
<br>
<div id="settingsDiv"> </div>
<br>
<div id="userDiv"> </div>
<br>
<div id="testEmail">

<form action="/main" method="POST">
    Test Email
    <input type="submit" name="testMail" value="Send">
</form>
</div>

</body>

</html>
