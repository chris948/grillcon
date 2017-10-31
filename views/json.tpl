<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />


<script type="text/javascript"
    src="http://code.jquery.com/jquery-1.10.1.min.js"></script>
<script>
    $(document).ready(
            function() {
                setInterval(function() {
                    xmlhttp.open("GET", "/getallitems.json", true);
                    xmlhttp.send();
                    //alert("test")
                }, 5000);
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

    var output = xmlhttp.responseText;
    document.getElementById("raw").innerHTML = output;

    output = "";

    for (i in jsonobj) {
      output += '<p>';
      output += i + " : " + jsonobj[i];
      output += '</p>';
    }

    document.getElementById("forin").innerHTML = output;

  } else {
    alert("data not available");
  }
}

// xmlhttp.onreadystatechange = GetArticles;
// the GetItems function will be triggered once the ajax
// request is terminated.
xmlhttp.onload = GetItems;

// send the request in an async way
xmlhttp.open("GET", "/getallitems.json", true);
xmlhttp.send();
</script>






</head>

<body>
  <p>The raw result from the ajax json request is:</p>
  <div id="raw"></div>
  <br />
  <p>The for cycle produces :</p>
  <div id="forin"></div>
</body>
</html>