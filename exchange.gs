function setupSummaryDesign() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("summary");
  if (!sheet) {
    sheet = ss.insertSheet("summary");
  } else {
    sheet.clear();
  }

  sheet.setHiddenGridlines(false);
  
  sheet.getRange("B2:F2").merge()
    .setValue("DATA PREVIEW TIMESHEET")
    .setBackground("#16161f")
    .setFontColor("#e2e8f0")
    .setFontSize(14)
    .setFontWeight("bold")
    .setVerticalAlignment("middle")
    .setHorizontalAlignment("left");
  sheet.setRowHeight(2, 40);

  sheet.getRange("B4").setValue("Pilih Konsultan:")
    .setFontColor("#8892a4")
    .setFontWeight("bold")
    .setVerticalAlignment("middle");
  
  var nameRange = sheet.getRange("C4");
  nameRange.setBackground("#1e1e2a")
    .setFontColor("#6366f1")
    .setFontWeight("bold")
    .setFontSize(11)
    .setBorder(
      true, true, true, true, false, false, 
      "#6366f1", SpreadsheetApp.BorderStyle.SOLID
    );

  var rule = SpreadsheetApp.newDataValidation()
    .requireValueInRange(ss.getRange("Jadwal Shifting!$A$2:$A$50"), true)
    .setAllowInvalid(true)
    .build();
  nameRange.setDataValidation(rule);

  var defaultName = ss.getRange("Jadwal Shifting!A2").getValue();
  if (defaultName !== "") {
    nameRange.setValue(defaultName);
  } else {
    nameRange.setValue("Nur Rifda Ellysa");
  }

  var kpiValues = [[
    '=COUNTIFS(B11:B47, "<>OFF", B11:B47, "<>IS*", B11:B47, "<>-", B11:B47, "<>")',
    '=COUNTIF(B11:B47, "OFF")', 
    '=SUM(D11:D47)', 
    '=SUM(E11:E47)'
  ]];
  var kpiLabels = [['HARI KERJA', 'HARI OFF', 'OPEN TICKET', 'CLOSED TICKET']];
  var kpiColors = ['#60a5fa', '#f59e0b', '#10b981', '#a855f7'];

  sheet.getRange("B6:E6").setFormulas(kpiValues)
    .setFontSize(18).setFontWeight("bold")
    .setHorizontalAlignment("center").setVerticalAlignment("middle")
    .setBackground("#16161f");
    
  sheet.getRange("B7:E7").setValues(kpiLabels)
    .setFontSize(9).setFontColor("#8892a4")
    .setHorizontalAlignment("center").setVerticalAlignment("middle")
    .setBackground("#16161f");

  for (var i = 0; i < 4; i++) {
    var col = i + 2;
    sheet.getRange(6, col).setFontColor(kpiColors[i]);
    sheet.getRange(6, col, 2, 1).setBorder(
      true, true, true, true, false, false, 
      "#2a2a3a", SpreadsheetApp.BorderStyle.SOLID
    );
  }
  sheet.setRowHeight(6, 36);
  sheet.setRowHeight(7, 24);

  var headers = [["TANGGAL", "SHIFT", "JAM", "OPEN", "CLOSED", "REMARK"]];
  sheet.getRange("A10:F10").setValues(headers)
    .setBackground("#2a2a3a")
    .setFontColor("#ffffff")
    .setFontWeight("bold")
    .setHorizontalAlignment("center")
    .setVerticalAlignment("middle");
  sheet.setRowHeight(10, 32);

  var formulas = [];
  var colLetters = [
    "B","C","D","E","F","G","H","I","J","K",
    "L","M","N","O","P","Q","R","S","T","U",
    "V","W","X","Y","Z","AA","AB","AC","AD",
    "AE","AF","AG","AH","AI","AJ","AK","AL"
  ];
  
  var getCond = function(r, sheetName, startH, endH, addDay) {
    var start = "(A" + r + " + TIME(" + startH + ",0,0))";
    var end = "(A" + r + (addDay ? " + 1" : "") + " + TIME(" + endH + ",0,0))";
    return "SUMPRODUCT(('" + sheetName + "'!$C:$C=$C$4) * " +
           "(IFERROR(VALUE('" + sheetName + "'!$A:$A), 0) >= " + start + ") * " +
           "(IFERROR(VALUE('" + sheetName + "'!$A:$A), 0) < " + end + "))";
  };

  for (var r = 11; r <= 47; r++) {
    var cLet = colLetters[r - 11];
    var fA = "=DATE(2026, 7, 'Jadwal Shifting'!" + cLet + "$1)";
    
    var fB = "=IF(OR(A" + r + '="", $C$4=""), "", ' +
             "INDEX('Jadwal Shifting'!$B$2:$AF$50, " +
             "MATCH($C$4, 'Jadwal Shifting'!$A$2:$A$50, 0), " +
             "MATCH(DAY(A" + r + "), 'Jadwal Shifting'!$B$1:$AF$1, 0)))";
             
    var fC = "=IFERROR(IFS(" +
             "B" + r + '="1", "06:00 - 15:00", ' +
             "B" + r + '="2", "14:00 - 23:00", ' +
             "B" + r + '="3", "22:00 - 07:00", ' +
             "B" + r + '="1.2", "06:00 - 23:00", ' +
             "B" + r + '="2.3", "14:00 - 07:00", ' +
             'TRUE, "-"), "-")';
             
    var fD = "=IFERROR(IFS(OR(B" + r + '="OFF", LEFT(B' + r + ',2)="IS", B' + 
             r + '=""), "-", ' +
             'B' + r + '="1", ' + getCond(r, 'Open Insiden', 6, 15, false) + ', ' +
             'B' + r + '="2", ' + getCond(r, 'Open Insiden', 14, 23, false) + ', ' +
             'B' + r + '="3", ' + getCond(r, 'Open Insiden', 22, 7, true) + ', ' +
             'B' + r + '="1.2", ' + getCond(r, 'Open Insiden', 6, 23, false) + ', ' +
             'B' + r + '="2.3", ' + getCond(r, 'Open Insiden', 14, 7, true) + ', ' +
             'TRUE, 0), "-")';
             
    var fE = "=IFERROR(IFS(OR(B" + r + '="OFF", LEFT(B' + r + ',2)="IS", B' + 
             r + '=""), "-", ' +
             'B' + r + '="1", ' + getCond(r, 'Closed Insiden', 6, 15, false) + ', ' +
             'B' + r + '="2", ' + getCond(r, 'Closed Insiden', 14, 23, false) + ', ' +
             'B' + r + '="3", ' + getCond(r, 'Closed Insiden', 22, 7, true) + ', ' +
             'B' + r + '="1.2", ' + getCond(r, 'Closed Insiden', 6, 23, false) + ', ' +
             'B' + r + '="2.3", ' + getCond(r, 'Closed Insiden', 14, 7, true) + ', ' +
             'TRUE, 0), "-")';
             
    var fF = "=IFERROR(IFS(B" + r + '="OFF", "OFF", ' +
             'LEFT(B' + r + ',2)="IS", "Izin Sakit", ' +
             'B' + r + '="1", "Shift 1", ' +
             'B' + r + '="2", "Shift 2", ' +
             'B' + r + '="3", "Shift 3", ' +
             'B' + r + '="1.2", "Shift 1 & 2", ' +
             'B' + r + '="2.3", "Shift 2 & 3", ' +
             'TRUE, B' + r + '), "-")';
             
    formulas.push([fA, fB, fC, fD, fE, fF]);
  }
  
  var bodyRange = sheet.getRange("A11:F47");
  bodyRange.setFormulas(formulas);
  
  sheet.getRange("A11:A47").setNumberFormat("dd/mm/yyyy")
    .setHorizontalAlignment("center");
  sheet.getRange("B11:C47").setHorizontalAlignment("center")
    .setFontFamily("Consolas");
  sheet.getRange("D11:E47").setHorizontalAlignment("center")
    .setFontWeight("bold");
  sheet.getRange("F11:F47").setHorizontalAlignment("left")
    .setFontColor("#8892a4");
  
  bodyRange.setBorder(
    true, true, true, true, true, true, 
    "#2a2a3a", SpreadsheetApp.BorderStyle.SOLID
  );

  sheet.setColumnWidth(1, 110);
  sheet.setColumnWidth(2, 80);
  sheet.setColumnWidth(3, 130);
  sheet.setColumnWidth(4, 90);
  sheet.setColumnWidth(5, 90);
  sheet.setColumnWidth(6, 160);

  sheet.setFrozenRows(10);
}
