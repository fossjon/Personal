/* hide non-important elements */
document.getElementsByTagName("header")[0].style.display = "none";
for (var x = 0; x < 2; ++x) {
  document.getElementsByClassName("reg-upsell")[x].style.display = "none";
  document.getElementsByTagName("footer")[x].style.display = "none";
}
document.getElementById("aux").style.display = "none";
document.getElementById("directory").style.display = "none";
document.getElementById("groups").style.display = "none";
document.getElementById("volunteering").style.display = "none";
/* re-size important elements */
var wide = 945;
document.body.style.backgroundColor = "white";
document.body.style.paddingLeft = "32px";
document.getElementById("wrapper").style.backgroundColor = "white";
document.getElementById("wrapper").style.marginTop = "32px";
document.getElementById("profile").style.width = wide + "px";
document.getElementsByClassName("profile-overview")[0].style.width = (wide - 256) + "px";
/* adjust the profile picture */
document.getElementsByClassName("profile-picture")[0].style.marginTop = "8px";
document.getElementsByClassName("profile-picture")[0].style.marginBottom = "8px";
document.getElementsByClassName("profile-picture")[0].style.paddingLeft = "8px";
document.getElementsByClassName("profile-picture")[0].getElementsByTagName("img")[0].style.boxShadow = "none";
/* adjust the top banner section */
document.getElementsByClassName("profile-picture")[0].style.display = "none";
document.getElementsByClassName("profile-overview")[0].style.width = ((document.getElementsByClassName("profile-overview")[0].parentNode.offsetWidth-50)+"px");
document.getElementsByClassName("profile-overview-content")[0].style.paddingTop = "0px";
document.getElementsByClassName("profile-overview-content")[0].style.display = "inline-block";
document.getElementsByClassName("profile-overview-content")[0].style.position = "relative";
document.getElementsByClassName("profile-overview-content")[0].style.top = "-10px";
document.getElementsByClassName("member-connections")[0].style.display = "none";
document.getElementsByClassName("extra-info")[0].style.display = "inline-block";
document.getElementsByClassName("extra-info")[0].style.marginTop = "0px";
document.getElementsByClassName("profile-overview")[0].innerHTML += document.getElementsByClassName("extra-info")[0].outerHTML;
document.getElementsByClassName("extra-info")[0].style.display = "none";
/* adjust sub-title positions */
var l = document.getElementsByClassName("title");
for (var i = 1; i < l.length; ++i) {
  l[i].style.paddingTop = "10px";
}
/* add a left side border to the resume sections */
var l = document.getElementsByClassName("profile-section");
for (var i = 0; i < l.length; ++i) {
  try {
    l[i].style.boxShadow = "none";
    l[i].style.borderLeft = "2px solid #444444";
    l[i].style.borderRadius = "2px";
    var hr = document.createElement("hr");
    hr.style.borderTop = "1px solid #ddd";
    hr.style.borderBottom = "0px";
    hr.style.margin = "0px 0px 0px 8px";
    hr.style.width = "97%";
    l[i].appendChild(hr);
  }
  catch(e) { }
}
/* see more skills */
document.getElementsByClassName("see-more")[0].getElementsByTagName("*")[0].click();
document.getElementsByClassName("see-less")[0].getElementsByTagName("*")[0].style.display = "none";
/* remove the box shadow on skills and interests */
var s = document.getElementsByClassName("skill");
for (var i = 0; i < s.length; ++i) {
  try {
    s[i].style.boxShadow = "none";
  }
  catch(e) { }
}
var s = document.getElementsByClassName("interest");
for (var i = 0; i < s.length; ++i) {
  try {
    s[i].style.boxShadow = "none";
  }
  catch(e) { }
}
/* load all images instead of their load delays */
var t = document.getElementsByTagName("img");
for (var i = 0; i < t.length; ++i) {
  try {
    var d = t[i].getAttribute("data-delayed-url");
    if (d && d.match(/^.*http.*$/i)) {
      var w = "width='60'", h = "";
      if (d.match(/^.*shrink_[^\/]*.*$/)) {
        d = d.replace(/shrink_[^\/]*/ig, "");
      }
      t[i].parentNode.innerHTML = ("<img src='"+d+"' "+w+" "+h+" />");
    }
  }
  catch(e) { }
}
/* allow the user to click on a section to move it up or down */
var u = document.getElementsByTagName("li");
for (var i = 0; i < u.length; ++i) {
  try {
    u[i].onclick = function() {
      var v = this.parentNode.getElementsByTagName("li");
      for (var j = 0; j < v.length; ++j) {
        if (v[j] == this) {
          var p = parseInt(prompt("Move:"));
          if (j == 0) { v[j].parentNode.parentNode.style.marginTop = (p + "px"); }
          else { v[j-1].style.paddingBottom = (p + "px"); }
          location.href = location.href.replace(/#.*$/ig,"") + "#" + p;
        }
      }
    }
  }
  catch(e) { }
}
/* add some white space to the end so we can cut it off nicely */
for (var i = 0; i < 100; ++i) {
  var br = document.createElement("br");
  document.body.appendChild(br);
}
/* translate external links so they are visible */
var v = document.getElementsByTagName("a");
for (var i = 0; i < v.length; ++i) {
  if (v[i].href.match(/^.*redirect.*$/i)) {
    v[i].innerHTML = (v[i].innerHTML + ": " + decodeURIComponent(v[i].href).replace(/^.*url=[^\/]*\/\//i, "").replace(/&.*$/i, ""));
  }
}
/* turn stars into bullet points with indentation */
var ps = document.getElementsByTagName("p");
for (var i = 0; i < ps.length; ++i) {
  if (ps[i].innerHTML.replace(/[\t\r\n]/ig, " ").match(/^.*\*.*$/i)) {
    ps[i].innerHTML = ps[i].innerHTML.replace(/\*/ig, "&bull;");
  }
  var r = "<table style='display:inline-block; padding-left:16px;'><tbody><tr><td style='vertical-align:top; padding-right:4px; white-space:nowrap;'>$1</td><td>$2</td></tr></tbody></table>";
  for (var j = 0; j < 4; ++j) {
    ps[i].innerHTML = ps[i].innerHTML.replace(/•(•+)([^<]+)/ig, r);
  }
  r = r.replace(/padding.left.16px./ig, " ");
  ps[i].innerHTML = ps[i].innerHTML.replace(/(•)([^<]+)/ig, r);
}
