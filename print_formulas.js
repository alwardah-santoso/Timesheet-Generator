var formulas = [];
var colLetters = [
  "B","C","D","E","F","G","H","I","J","K",
  "L","M","N","O","P","Q","R","S","T","U",
  "V","W","X","Y","Z","AA","AB","AC","AD",
  "AE","AF","AG","AH","AI","AJ","AK","AL"
];

for (var r = 11; r <= 11; r++) {
  var cLet = colLetters[r - 11];
  var fA = "=DATE(2026, 7, 'Jadwal Shifting'!" + cLet + "$1)";
  
  var fB = "=IF(OR(A" + r + '="", $C$4=""), "", ' +
           "INDEX('Jadwal Shifting'!$B$2:$AF$50, " +
           "MATCH($C$4, 'Jadwal Shifting'!$A$2:$A$50, 0), " +
           "MATCH(DAY(A" + r + "), 'Jadwal Shifting'!$B$1:$AF$1, 0)))";
           
  var fC = "=IFERROR(IFS(" +
           "B" + r + '="1", "06:00 — 15:00", ' +
           "B" + r + '="2", "14:00 — 23:00", ' +
           "B" + r + '="3", "22:00 — 07:00", ' +
           "B" + r + '="1.2", "06:00 — 23:00", ' +
           "B" + r + '="2.3", "14:00 — 07:00", ' +
           'TRUE, "-"), "-")';
           
  var getCond = function(sheetName, startH, endH, addDay) {
    var start = "(A" + r + " + TIME(" + startH + ",0,0))";
    var end = "(A" + r + (addDay ? " + 1" : "") + " + TIME(" + endH + ",0,0))";
    return "SUMPRODUCT(('" + sheetName + "'!$C:$C=$C$4) * " +
           "(IFERROR(VALUE('" + sheetName + "'!$A:$A), 0) >= " + start + ") * " +
           "(IFERROR(VALUE('" + sheetName + "'!$A:$A), 0) < " + end + "))";
  };
  
  var fD = "=IFERROR(IFS(OR(B" + r + '="OFF", LEFT(B' + r + ',2)="IS", B' + 
           r + '=""), "-", ' +
           'B' + r + '="1", ' + getCond('Open Insiden', 6, 15, false) + ', ' +
           'B' + r + '="2", ' + getCond('Open Insiden', 14, 23, false) + ', ' +
           'B' + r + '="3", ' + getCond('Open Insiden', 22, 7, true) + ', ' +
           'B' + r + '="1.2", ' + getCond('Open Insiden', 6, 23, false) + ', ' +
           'B' + r + '="2.3", ' + getCond('Open Insiden', 14, 7, true) + ', ' +
           'TRUE, 0), "-")';
           
  formulas.push([fA, fB, fC, fD]);
}

console.log(formulas[0].join("\n\n"));
