function getUrlFormat(urlBase, paraDic) {
  var url = urlBase + '?'
  for (var key in paraDic)
    url = url + key + '=' + paraDic[key] + '&'
  return url
}


// this is the helper function for getting csrf_token
function getCookie(name) {
  var cookieValue = null
  if (document.cookie && document.cookie != '') {
    var cookies = document.cookie.split(';')
    for (var i = 0; i < cookies.length; i++) {
      var cookie = cookies[i].trim()
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) == (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}


function hexToRgb(hex) {
  // Expand shorthand form (e.g. "03F") to full form (e.g. "0033FF")
  var shorthandRegex = /^#?([a-f\d])([a-f\d])([a-f\d])$/i
  hex = hex.replace(shorthandRegex, function(m, r, g, b) {
    return r + r + g + g + b + b
  })

  var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
  return result ? {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16)
  } : null
}


function getValFromUrlParam(key) {
  return new URL(window.location.href).searchParams.get(key)
}


function copyToClipboard(content) {
  const temp = document.createElement('input')
  temp.style.hidden = true
  document.body.appendChild(temp)
  temp.value = content
  temp.select()
  document.execCommand('copy')
  document.body.removeChild(temp)
}


String.prototype.format = function() {
  let a = this
  for (let k in arguments) {
    a = a.replace('{' + k + '}', arguments[k])
  }
  return a
}


export {
  getCookie,
  copyToClipboard,
  getUrlFormat,
  hexToRgb,
  getValFromUrlParam,
}




