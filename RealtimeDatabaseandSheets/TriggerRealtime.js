//Add in your database secret
var secret = 'sB0UkoogfjKIVs71rFsk0RvLRkyrZ3MAcKQe97gv'

function getFirebaseUrl(jsonPath) {
  /*
  We then make a URL builder
  This takes in a path, and
  returns a URL that updates the data in that path
  */
  return (
    'https://compostable-cup-bin-project.firebaseio.com/' +
    jsonPath +
    '.json?auth=' +
    secret
  )
}

function syncMasterSheet(excelData) {
  /*
  We make a PUT (update) request,
  and send a JSON payload
  More info on the REST API here : https://firebase.google.com/docs/database/rest/start
  */
  var options = {
    method: 'put',
    contentType: 'application/json',
    payload: JSON.stringify(excelData)
  }
  var fireBaseUrl = getFirebaseUrl('masterSheet')

  /*\
  We use the UrlFetchApp google scripts module
  More info on this here : https://developers.google.com/apps-script/reference/url-fetch/url-fetch-app
  */
  UrlFetchApp.fetch(fireBaseUrl, options)
}

function startSync() {
  //Get the currently active sheet
  var sheet = SpreadsheetApp.getActiveSheet()
  //Get the number of rows and columns which contain some content
  var [rows, columns] = [sheet.getLastRow(), sheet.getLastColumn()]
  //Get the data contained in those rows and columns as a 2 dimensional array
  var data = sheet.getRange(1, 1, rows, columns).getValues()

  //Use the syncMasterSheet function defined before to push this data to the "masterSheet" key in the firebase database
  syncMasterSheet(data)
  Logger.log("Updated data sent to Firebase");
}