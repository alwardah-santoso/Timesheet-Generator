function doGet(e) {
  var id = e.parameter.id;
  var tab = e.parameter.tab;
  var ss = id ? SpreadsheetApp.openById(id) : SpreadsheetApp.getActiveSpreadsheet();
  var sheet = tab ? ss.getSheetByName(tab) : ss.getActiveSheet();
  var data = sheet.getDataRange().getValues();
  return ContentService.createTextOutput(JSON.stringify(data)).setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  var body = JSON.parse(e.postData.contents);
  var act = body.action;
  
  if (act === 'create_spreadsheet') {
    var title = body.title || 'Spreadsheet Baru';
    var newSs = SpreadsheetApp.create(title);
    var res = {status: 'success', id: newSs.getId(), url: newSs.getUrl()};
    return ContentService.createTextOutput(JSON.stringify(res)).setMimeType(ContentService.MimeType.JSON);
  }
  
  var ss = body.id ? SpreadsheetApp.openById(body.id) : SpreadsheetApp.getActiveSpreadsheet();
  
  if (act === 'add_tab') {
    var newTab = ss.insertSheet(body.tab_name || 'Tab Baru');
    var resTab = {status: 'success', tab: newTab.getName()};
    return ContentService.createTextOutput(JSON.stringify(resTab)).setMimeType(ContentService.MimeType.JSON);
  }
  
  var sheet = body.tab_name ? (ss.getSheetByName(body.tab_name) || ss.insertSheet(body.tab_name)) : ss.getActiveSheet();
  
  if (act === 'append') {
    sheet.appendRow(body.row);
  } else if (act === 'update') {
    if (body.values) {
      sheet.getRange(body.range).setValues(body.values);
    } else {
      sheet.getRange(body.range).setValue(body.value);
    }
  } else if (act === 'clear') {
    sheet.clearContents();
  }
  
  var finalRes = {status: 'success', url: ss.getUrl()};
  return ContentService.createTextOutput(JSON.stringify(finalRes)).setMimeType(ContentService.MimeType.JSON);
}
