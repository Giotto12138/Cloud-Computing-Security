function preParseDate(dates){
  // Make a rule in index.html: the format should be "yyyy-mm-dd" or "mm-dd"
  // Convert string {dates} to {date_list[y,m,d]}
  // @parameter {dates} the string format should be "yyyy-mm-dd" or "mm-dd"
  // @return {date_list} convert the string to a list [yyyy,mm,dd]
  var date_list = dates.split('-');
  if (date_list.length == 2){
    var today = new Date();
    if(today.getMonth()+1 > date_list[0] || (today.getMonth()+1 == date_list[0] && today.getDate() > date_list[1])){
      date_list.unshift(today.getFullYear() + 1);
    }
    else date_list.unshift(today.getFullYear());
  }
  else if (date_list.length != 3)
    return [-1,-1,-1];
  return date_list;
}

function parseDate(dates){
  //@parameter {dates} the string format should be "yyyy-mm-dd" or "mm-dd"
  //@return Date object
  var date_list = preParseDate(dates);
  return new Date(Number.parseInt(date_list[0]), Number.parseInt(date_list[1] - 1), Number.parseInt(date_list[2]));
}

function Countdown(dates){
  //Calculate the remaining time and return the string of the count down result
  //@parameter {dates} the string format should be "yyyy-mm-dd" or "mm-dd"
  //@return the string of the count down result
  var now = new Date();
  var eventDate = parseDate(dates);
  var currentTime = now.getTime();
  var eventTime = eventDate.getTime();
  var remTime = eventTime - currentTime;
  if (remTime < 0)
    return "Expired";
  var s = Math.floor(remTime / 1000);
  var m = Math.floor(s / 60);
  var h = Math.floor(m / 60);
  var d = Math.floor(h / 24);

  h %= 24;
  m %= 60;
  s %= 60;

  h = (h < 10) ? "0" + h : h;
  m = (m < 10) ? "0" + m : m;
  s = (s < 10) ? "0" + s : s;

  return `${d} Days ${h} Hours ${m} Minutes ${s} Seconds`;
}

function remainingTime(dates) {
  //Calculate the remaining time and return the string of the count down result
  //@parameter {dates} the string format should be "yyyy-mm-dd" or "mm-dd"
  //@return the remaining time
  var now = new Date();
  var eventDate = parseDate(dates);
  var currentTime = now.getTime();
  var eventTime = eventDate.getTime();
  var remTime = eventTime - currentTime;
  return remTime;
}

function reqJSON(method, url, data) {
  //@parameter ${method} the method such as "POST", "GET", "DELETE"
  //@parameter ${url} the url like "/event", "/events"
  //@parameter ${data} JSON send to the server
  return new Promise((resolve, reject) => {
    let xhr = new XMLHttpRequest();
    xhr.open(method, url);
    xhr.responseType = 'json';
    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve({status: xhr.status, data: xhr.response});
      } else {
        reject({status: xhr.status, data: xhr.response});
      }
    };
    xhr.onerror = () => {
      reject({status: xhr.status, data: xhr.response});
    };
    xhr.send(data);
  });
}

function postEvent(){
  //Get value from html and make a POST request to url "/event"
  //The value contain name and date.
  //If the format is invalid, return false.
  //Send json data via XMLHttpRequest() and shows "Successfully stored"
  var t = document.getElementById("add_event");
  var date_prep = preParseDate(t.elements[1].value);
  var date_p = parseDate(t.elements[1].value);
  var event_name = t.elements[0].value;

  if (event_name == null || event_name == undefined || event_name == "" || date_p.getFullYear() != date_prep[0] || date_p.getMonth() != date_prep[1] - 1 || date_p.getDate() != date_prep[2]){
    alert("Invalid Format!");
    return false;
  }
  if (remainingTime(t.elements[1].value) < 0) alert("Please input a future date")
  else if (remainingTime(t.elements[1].value) > 0) {
    var data = JSON.stringify({name: t.elements[0].value, date: t.elements[1].value});
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "event");
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send(JSON.stringify(data));
    alert("Successfully stored");
  }
}

function getEvents(){
  //Make a "GET" request to url "/events"
  //Use the function Countdown to calculate the remaining time and add rows and button in the table in html
  //Refresh this function per second
  reqJSON('GET','events')
      .then(({status, data}) => {
        let h = '<tr><th>Event Name:</th><th>Event Date:</th><th>Count Down:</th><th>Event ID:</th>';
        for (let event of data.events){
          var t = Countdown(event.date);
          if (remainingTime(event.date) < 0) continue;
          var button = `<td><button type = "button" onclick = "deleteEvent(${event.id})">Delete</button></td>`;
          h += `<tr><td> ${event.name} </td><td> ${event.date} </td><td> ${t} </td><td>${event.id}</td>${button}</tr>`;
        }
        document.getElementById('event_list').innerHTML = h;
      })
      .catch(({status, data}) => {
        document.getElementById('events').innerHTML = 'ERROR: ' + JSON.stringify(data);
          });
  setTimeout(getEvents, 1000);
}

function deleteEvent(id){
  reqJSON('POST', '/event/' + id)
  .then(({status, data}) => {
    alert(id + " Successfully deleted")
  })
  .catch(({status, data}) => {
    // Display an error.
    document.getElementById('events').innerHTML = 'ERROR: ' +
      JSON.stringify(data);
  });
}

function deleteCookie(){
  document.cookie = "cookie_t=; expires= Thu, 01 Jan 1970 00:00:00 GMT; path=/"
}




