function StartPoint() {
    Logger.log("starting ....");
  }
  
  function onEdit(e) {
    var sheet = e.source.getActiveSheet();
    var range = e.range;
    var rowNumber = range.getRow()
    var column = range.getColumn();
    var newValue = e.value;
    var previousValue = e.oldValue;
  

    if (rowNumber === 1) {
      if (column === 1 && (newValue === 'id')) {
        var payload = {
          "action": "create",
          "columns": sheet.getRange(rowNumber, 1, 1, sheet.getMaxColumns()).getValues()[0],
          "sheetName": sheet.getName(),
          "sheetId": SpreadsheetApp.getActiveSpreadsheet().getId()
        }
        payload = JSON.stringify(payload);
  

        var options = {
          'method': 'post',
          'contentType': 'application/json',
          'payload': payload
        };
  

        try {
          UrlFetchApp.fetch("https://first-rewse.run-ap-south1.goorm.site/create", options);
          Logger.log("API call successful");
        } catch (error) {
          Logger.log("Error making API call: " + error);
        }
      }
      else if (column != 1 && sheet.getRange(1, 1).getValue() === 'id') {
        var payload = {
          "action": "create",
          "columns": [newValue],
          "sheetName": sheet.getName(),
          "sheetId": SpreadsheetApp.getActiveSpreadsheet().getId()
        }
        payload = JSON.stringify(payload);
  

        var options = {
          'method': 'post',
          'contentType': 'application/json',
          'payload': payload
        };
  

        try {
          UrlFetchApp.fetch("https://first-rewse.run-ap-south1.goorm.site/create", options);
          Logger.log("API call successful");
        } catch (error) {
          Logger.log("Error making API call: " + error);
        }
      }
    }
    if (rowNumber != 1) {
      if (column === 1) {

        if (newValue === undefined && previousValue !== undefined && previousValue !== "") {
          Logger.log("First column value deleted");

          var payload = {
            "pk": previousValue,
            "action": "delete",
            "sheetName": sheet.getName(),
          };
  

          payload = JSON.stringify(payload);

          var options = {
            'method': 'post',
            'contentType': 'application/json',
            'payload': payload
          };
  

          try {
            UrlFetchApp.fetch("https://first-rewse.run-ap-south1.goorm.site/syncc", options);
            Logger.log("API call successful");
          } catch (error) {
            Logger.log("Error making API call: " + error);
          }
        }
        else if (previousValue === undefined && newValue !== "") {
          Logger.log("First column value Inserting");
  

          var payload = {
            "sheetName": sheet.getName(),
            "pk": newValue,
            "action": "insert"
          };
  

          payload = JSON.stringify(payload);
  

          var options = {
            'method': 'post',
            'contentType': 'application/json',
            'payload': payload
          };
  

          try {
            UrlFetchApp.fetch("https://first-rewse.run-ap-south1.goorm.site/syncc", options);
            Logger.log("API call successful");
          } catch (error) {
            Logger.log("Error making API call: " + error);
          }
        }
  
      }
      else {
        if (previousValue === undefined && newValue !== "") {
          Logger.log("First column value Inserting");
  

          var payload = {
            "sheetName": sheet.getName(),
            "pk": sheet.getRange(rowNumber, 1).getValue(),
            "attr": sheet.getRange(1, column).getValue(),
            "action": "update",
            "old": "",
            "updatedvalue": newValue
          };
  

          payload = JSON.stringify(payload);

          var options = {
            'method': 'post',
            'contentType': 'application/json',
            'payload': payload
          };
  

          try {
            UrlFetchApp.fetch("https://first-rewse.run-ap-south1.goorm.site/syncc", options);
            Logger.log("API call successful");
          } catch (error) {
            Logger.log("Error making API call: " + error);
          }
        }
        else if (previousValue !== "" && newValue !== "") {
          Logger.log("First column value Inserting");

          var payload = {
            "sheetName": sheet.getName(),
            "pk": sheet.getRange(rowNumber, 1).getValue(),
            "attr": sheet.getRange(1, column).getValue(),
            "action": "update",
            "old": previousValue,
            "updatedvalue": newValue
          };
  

          payload = JSON.stringify(payload);
  

          var options = {
            'method': 'post',
            'contentType': 'application/json',
            'payload': payload
          };
  

          try {
            UrlFetchApp.fetch("https://first-rewse.run-ap-south1.goorm.site/syncc", options);
            Logger.log("API call successful");
          } catch (error) {
            Logger.log("Error making API call: " + error);
          }
        }
        else if (previousValue !== "" && newValue === undefined) {
          Logger.log("First column value Inserting");
  

          var payload = {
            "sheetName": sheet.getName(),
            "pk": sheet.getRange(rowNumber, 1).getValue(),
            "attr": sheet.getRange(1, column).getValue(),
            "action": "update",
            "old": previousValue,
            "updatedvalue": "asdf",
          };
  

          payload = JSON.stringify(payload);
  

          var options = {
            'method': 'post',
            'contentType': 'application/json',
            'payload': payload
          };
  

          try {
            UrlFetchApp.fetch("https://first-rewse.run-ap-south1.goorm.site/syncc", options);
            Logger.log("API call successful");
          } catch (error) {
            Logger.log("Error making API call: " + error);
          }
        }
      }
    }
  }
  
  function onSheetCreate(e) {
  
    if (e && e.changeType === 'INSERT_GRID') {
      var sheet = e.source.getActiveSheet();
  
     
      Utilities.sleep(100);
  
      
      var firstCell = sheet.getRange("A1").getValue();
  
      if (firstCell.toLowerCase() === "id") {
    
        var firstRow = sheet.getRange("1:1").getValues()[0];
  
 
        var columns = firstRow.filter(function (cell) { return cell !== ""; });
  

        var payload = {
          "action": "create",
          "columns": columns,
          "sheetName": sheet.getName(),
          "sheetId": SpreadsheetApp.getActiveSpreadsheet().getId()
        };
  
  
        payload = JSON.stringify(payload);
  

        var options = {
          'method': 'post',
          'contentType': 'application/json',
          'payload': payload
        };

        try {
          var response = UrlFetchApp.fetch("https://first-rewse.run-ap-south1.goorm.site/create", options);
          Logger.log("API call successful: " + response.getContentText());
          SpreadsheetApp.getUi().alert('Table created successfully!');
        } catch (error) {
          Logger.log("Error making API call: " + error);
          SpreadsheetApp.getUi().alert('Error creating table. Please check the logs for details.');
        }
      } else {
        Logger.log("First cell does not contain 'id'. No action taken.");
      }
    }
  }