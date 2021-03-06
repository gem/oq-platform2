/*
   Copyright (c) 2014-2016, GEM Foundation.

      This program is free software: you can redistribute it and/or modify
      it under the terms of the GNU Affero General Public License as
      published by the Free Software Foundation, either version 3 of the
      License, or (at your option) any later version.

      This program is distributed in the hope that it will be useful,
      but WITHOUT ANY WARRANTY; without even the implied warranty of
      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
      GNU Affero General Public License for more details.

      You should have received a copy of the GNU Affero General Public License
      along with this program.  If not, see <https://www.gnu.org/licenses/agpl.html>.
*/

var widgetsAndButtons = {
    'projDef':    {'widget':     '#project-def-widget',
                   'button':     '#toggleProjDefWidgetBtn',
                   'buttonText': 'Show Project Definition'},
    'iri':        {'widget':     '#iri-chart-widget',
                   'button':     '#toggleIriChartWidgetBtn',
                   'buttonText': 'Show IRI Chart Widget'},
    'svi':        {'widget':     '#cat-chart-widget',
                   'button':     '#toggleSviThemeWidgetBtn',
                   'buttonText': 'Show SVI Theme Chart'},
    'indicators': {'widget':     '#primary-tab-widget',
                   'button':     '#toggleCompIndWidgetBtn',
                   'buttonText': 'Show Composite Indicator Chart'}
};

// NOTE: In order to add a new operator, we have to add a new key to
//       the 'operators' object and the corresponding lookup to the
//       'namesToOperators' object
var operators = {
    'SUM_S': {
        'code': 'SUM_S',
        'ignoresWeights': true,
        'multiplies': false
    },
    'SUM_W': {
        'code': 'SUM_W',
        'ignoresWeights': false,
        'multiplies': false
    },
    'AVG': {
        'code': 'AVG',
        'ignoresWeights': true,
        'multiplies': false
    },
    'MUL_S': {
        'code': 'MUL_S',
        'ignoresWeights': true,
        'multiplies': true
    },
    'MUL_W': {
        'code': 'MUL_W',
        'ignoresWeights': false,
        'multiplies': true
    },
    'GEOM_MEAN': {
        'code': 'GEOM_MEAN',
        'ignoresWeights': true,
        'multiplies': true
    },
    'CUSTOM': {
        'code': 'CUSTOM',
        'ignoresWeights': true,
        'multiplies': false
    }
};

var namesToOperators = {
    'Simple sum (ignore weights)':            operators.SUM_S,
    'Weighted sum':                           operators.SUM_W,
    'Average (ignore weights)':               operators.AVG,
    'Simple multiplication (ignore weights)': operators.MUL_S,
    'Weighted multiplication':                operators.MUL_W,
    'Geometric mean (ignore weights)':        operators.GEOM_MEAN,
    'Use a custom field':                     operators.CUSTOM,
    // the following is for backwards compatibility
    'Use a custom field (no recalculation)':  operators.CUSTOM
};

var nodeTypes = {
    'IRI': 'Integrated Risk Index',
    'RI': 'Risk Index',
    'RISK_INDICATOR': 'Risk Indicator',
    'SVI': 'Social Vulnerability Index',
    'SV_THEME': 'Social Vulnerability Theme',
    'SV_INDICATOR': 'Social Vulnerability Indicator',
};

var iriChartElems = {"graph": "iriGraph",
                     "grid": "iriGrid",
                     "gridId": "#iri-grid",
                     "dataOfSelectedRegions": [],
                     "dispRowsId": "#iriDisplayedRows"};
var themeChartElems = {"graph": "themeGraph",
                       "grid": "themeGrid",
                       "gridId": "#cat-grid",
                       "dataOfSelectedRegions": [],
                       "dispRowsId": "#catDisplayedRows"};
var primaryChartElems = {"graph": "primaryGraph",
                         "grid": "primaryGrid",
                         "gridId": "#primary-grid",
                         "dataOfSelectedRegions": [],
                         "dispRowsId": "#primaryDisplayedRows"};
var chartElems = {"iri": iriChartElems, "theme": themeChartElems, "primary": primaryChartElems};

$(document).ready(function() {
    var baseMapUrl = new L.TileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png');
    var app = new OQLeaflet.OQLeafletApp(baseMapUrl);
    app.initialize(startApp);
    $('#cover').remove();
    // FIXME: We are never showing alert-unscaled-data currently
    $('.alert-unscaled-data').hide();
    $('.alert-custom-operators').hide();
    $('#absoluteSpinner').hide();
    $('#loadProjectBtn').show();
});

var layerAttributes;
var sessionProjectDef = [];
var zoneLabelField;
var selectedIndicator;
var selectedLayer;
var tempProjectDef;
var COMPATIBILITY_VERSION = '1.7.0';
var thematicLayer;
var leafletBoundingBox = [];
var mapboxBoundingBox = [];
var license;
var webGl;
var projectChange = false;
var projDefChange = false;
var verticesCount = 0;
var VERTICES_THRESHOLD = 500000;

var mappingLayerAttributes = {};

// sessionProjectDef is the project definition as it was when uploaded from the QGIS tool.
// While projectDef includes modified weights and is no longer the version that was uploaded from the QGIS tool
var projectLayerAttributes;
var regionNames = [];
var indicatorChildrenKey = [];
var projDefOperatorsAreStandard = false;

function setWidgetsToDefault(){
    $('#pdSelection').empty();
    // set tabs back default
    $('#projectDef-spinner').text('Loading ...');
    $('#projectDef-spinner').append('<img id="download-button-spinner" src="/static/img/ajax-loader.gif" />');
    $('#projectDef-spinner').show();
    $('#iri-spinner').show();
    $('#regionSelectionDialog').empty();
    $('#projectDef-tree').empty();
    $('#iri-chart').empty();
    $('#cat-chart').empty();
    $('#primary-chart').empty();
    resetDataOfSelectedRegions();
}

function scaleTheData() {
    // Create a list of primary indicators that need to be scaled
    // We are not scaling any of the IR indicators
    var indicatorsToBeScaled = {};
    for (var i = 0; i < projectDef.children[1].children.length; i++) {
        for (var j = 0; j < projectDef.children[1].children[i].children.length; j++) {
            var tempName = projectDef.children[1].children[i].children[j].field;
            indicatorsToBeScaled[tempName] = {};
        }
    }

    // Populate the list with values
    for (var key in indicatorsToBeScaled) {
        for (var i = 0; i < layerAttributes.features.length; i++) {
            var tempRegion = layerAttributes.features[i].properties[zoneLabelField];
            indicatorsToBeScaled[key][tempRegion] = layerAttributes.features[i].properties[key];
        }
    }

    for (var k in indicatorsToBeScaled) {
        scale(indicatorsToBeScaled[k]);
    }

    // Put values back into the layerAttributes obj
    for (var key in indicatorsToBeScaled) {
        for (var i = 0; i < layerAttributes.features.length; i++) {
            for (var layerAttributesKey in layerAttributes.features[i].properties) {
                if (key === layerAttributesKey) {
                    for(var indicatorKey in indicatorsToBeScaled[key]) {
                        if (layerAttributes.features[i].properties[zoneLabelField] == indicatorKey) {
                            layerAttributes.features[i].properties[layerAttributesKey] = indicatorsToBeScaled[key][indicatorKey];
                        }
                    }
                }
            }
        }
    }
    // Process the indicators again
    processIndicators(layerAttributes, sessionProjectDef);
}

function getRegionNames(la, zoneLabelField) {
    var regionNames = [];
    for (var i = 0; i < la.length; i++) {
        var regionName = la[i].properties[zoneLabelField];
        regionNames.push(regionName);
    }
    return regionNames;
}

function createRiskIndicator(la, index, zoneLabelField) {
    var indicator = [];
    // setup the indicator with all the regions
    for (var i = 0; i < la.length; i++) {
        var region = la[i].properties[zoneLabelField];
        indicator.push({'Region': region});
    }

    for (var i = 0; i < index.length; i++) {
        for (var j = 0; j < la.length; j++) {
            if (indicator[j].Region == la[j].properties[zoneLabelField]) {
                var tempName = index[i].name;
                var tempVal = la[j].properties[tempName];
                indicator[j][tempName] = tempVal;
            }
        }
    }
    // Get the indicators children keys
    for (var i = 0; i < index.length; i++) {
        indicatorChildrenKey.push(index[i].field);
    }

    return indicator;
}

function combineIndicators(nameLookUp, themeObj, JSONthemes) {
    //  Set the projectDef equal to testSessionProjectDef if sessionProjectDef is
    // an empty object in order to test the function
    if (arguments[3]) {
        projectDef = arguments[3];
    }
    else if (!jQuery.isEmptyObject(sessionProjectDef)) {
       projectDef = sessionProjectDef;
    }
    else {
       return false;
    }

    var subIndex = {};
    var operator;

    // Get the theme operator
    for (var i = 0; i < projectDef.children.length; i++) {
        if (projectDef.children[i].name == nameLookUp) {
            operator = namesToOperators[projectDef.children[i].operator];
        }
    }

    // first create an object with all of the district names
    for (var i = 0; i < themeObj.length; i++) {
        var tempRegion = themeObj[i].Region;
        subIndex[tempRegion] = 0;
    }

    // get some info about the themes
    var themeKeys = [];
    var themeInversionObj = {};
    var themeWeightObj = {};
    for (var i = 0; i < JSONthemes.length; i++) {
        var themeName = JSONthemes[i].name;
        var themeWeight = JSONthemes[i].weight;
        themeKeys.push(themeName);
        themeWeightObj[themeName] = themeWeight;
        // identify if the node has been inverted
        if (JSONthemes[i].isInverted === true) {
            themeInversionObj[themeName] = -1;
        } else {
            themeInversionObj[themeName] = 1;
        }
    }

    var tempElementValue;
    // NOTE: themeObj: a list containing for each region the values for each item to combine
    // compute the subIndex values based on operator
    for (var idx=0; idx < themeObj.length; idx++) {
        if (operator.multiplies) {
            tempElementValue = 1;
        } else {
            tempElementValue = 0;
        }
        var themeObjRegion = themeObj[idx].Region;
        var nullWasFound = false;
        // NOTE: themeKeys contains the list of names of all items to combine
        // compute the themes
        for (var themeKey = 0; themeKey < themeKeys.length; themeKey++) {
            // Get inversion factor
            var themeInversionFactor = themeInversionObj[themeKeys[themeKey]];
            var tempThemeName = themeKeys[themeKey];
            var themeWeightVal;
            var newElementValue = themeObj[idx][tempThemeName];
            if (!isValidNumber(newElementValue)) {
                tempElementValue = null;
                nullWasFound = true;
                break;
            }
            if (operator.ignoresWeights) {
                themeWeightVal = 1;
            } else {
                themeWeightVal = themeWeightObj[tempThemeName];
            }
            if (themeWeightVal > 0) {
                if (operator.multiplies) {
                    tempElementValue = tempElementValue * newElementValue * themeWeightVal * themeInversionFactor;
                } else {
                    tempElementValue = tempElementValue + newElementValue * themeWeightVal * themeInversionFactor;
                }
            }
        }
        if (!nullWasFound) {
            if (operator.code == 'AVG') {
                tempElementValue = tempElementValue / themeKeys.length;
            } else if (operator.code == 'GEOM_MEAN') {
                tempElementValue = Math.pow(tempElementValue, 1 / themeKeys.length);
            }
        }
        subIndex[themeObjRegion] = tempElementValue;
    }
    return subIndex;
}

function processIndicators(layerAttributes, projectDef) {
    var weightChange = 0;
    if (arguments[2]) {
        weightChange = arguments[2];
    }
    regionNames = [];
    var allSVIThemes = [];
    var allPrimaryIndicators = [];
    var allRiskIndicators = [];

    /////////////////////////////////////////////
    //// Create the primary indicator objects ///
    /////////////////////////////////////////////

    var svThemes;
    var riskIndicators;

    // Find all the nodes of type social vulnerability and risk index in the project def
    for (var k in projectDef.children) {
        if (projectDef.children[k].type == "Social Vulnerability Index") {
            svThemes = projectDef.children[k].children;
        } else if (projectDef.children[k].type == "Risk Index") {
            riskIndicators = projectDef.children[k].children;
        }
    }

    // process each Social Vulnerability Index nodes
    // Get all the primary indicators
    if (svThemes) {
        for (var i = 0; i < svThemes.length; i++) {
            if (svThemes[i].children) {
                for (var e = 0 ; e < svThemes[i].children.length; e++ ) {
                    allPrimaryIndicators.push(svThemes[i].children[e].field);
                }
            }
        }
    }

    //////////////////////////////////////
    //// Compute the theme indicators ////
    //////////////////////////////////////

    //build the theme indicator object
    var themeData = [];
    indicatorInfo = [];
    var laValuesArray = [];

    function generateThemeObject(indicatorObj) {
        var region = indicatorObj.Region;
        var theme = indicatorObj.theme;
        var value = indicatorObj.value;
        // add the theme and value to each theme data object
        for (var i = 0; i < themeData.length; i++) {
            if (themeData[i].Region == region) {
                if (!isValidNumber(value)) {
                    delete themeData[i][theme];
                } else {
                    themeData[i][theme] = value;
                }
            }
        }
    }

    // setup themeData with all the regions
    var la = layerAttributes.features;
    for (var s = 0; s < la.length; s++) {
        var temp = {};
        temp.Region = la[s].properties[zoneLabelField];
        themeData.push(temp);
    }

    // Find the theme information
    if (svThemes) {
        for (var m = 0; m < svThemes.length; m++) {
            var operator = namesToOperators[svThemes[m].operator];
            var name = svThemes[m].name;
            allSVIThemes.push(name);
            var tempChildren = svThemes[m].children;
            var tempIndicatorChildrenKeys = [];

            if (tempChildren) {
                for (var q = 0; q < tempChildren.length; q++) {
                    // Get the indicators children keys
                    tempIndicatorChildrenKeys.push(tempChildren[q].field);
                }
            }

            for (var o = 0; o < la.length; o++) {
                var region = la[o].properties[zoneLabelField];
                var theme = name;
                var primaryInversionFactor;

                var tempValue;
                if (operator.multiplies) {
                    tempValue = 1;
                } else {
                    tempValue = 0;
                }
                var nullWasFound = false;
                for (var prop in la[o].properties) {
                    // iterate over the indicator child keys
                    if (nullWasFound) {
                        break;
                    }
                    for (var r = 0; r < tempIndicatorChildrenKeys.length; r++) {
                        if (prop == tempIndicatorChildrenKeys[r]) {
                            newValue = la[o].properties[prop];
                            if (!isValidNumber(newValue)) {
                                tempValue = null;
                                nullWasFound = true;
                                break;
                            }
                            if (tempChildren[r].isInverted === true) {
                                primaryInversionFactor = -1;
                            } else {
                                primaryInversionFactor = 1;
                            }
                            // Sum the theme indicators
                            var weight;
                            if (operator.ignoresWeights) {
                                weight = 1;
                            } else {
                                weight = tempChildren[r].weight;
                            }
                            if (operator.multiplies) {
                                tempValue = tempValue * newValue * primaryInversionFactor * weight;
                            } else {
                                tempValue = tempValue + newValue * primaryInversionFactor * weight;
                            }
                            // NOTE: Ben had the following line only in case of weighted sum,
                            //       but I guess it should be there in all cases
                            // Collect an array of all the values that pass through the loop
                            laValuesArray.push(newValue);
                        }
                    }
                }
                if (!nullWasFound) {
                    if (operator.code == 'AVG') {
                        tempValue = tempValue / tempIndicatorChildrenKeys.length;
                    } else if (operator.code == 'GEOM_MEAN') {
                        tempValue = Math.pow(tempValue, 1 / tempIndicatorChildrenKeys.length);
                    }
                }
                indicatorInfo.push({'Region':region, 'theme':theme, 'value':tempValue});
            }
        }
    }

    ////////////////////////////////
    //// Check for scaled values ///
    ////////////////////////////////

    var maxValue = Math.max.apply(null, laValuesArray);
    var minValue = Math.min.apply(null, laValuesArray);

    if (minValue === 0 && maxValue === 1) {
        $('.alert-unscaled-data').hide();
    } else {
        $('.alert-unscaled-data').show();
        $('.scaleTheData').click(function() {
            // Scale the primary indicators
            scaleTheData();
        });
    }

    for (var p = 0; p < indicatorInfo.length; p++) {
        // process the object for each record
        var indicatorObj = indicatorInfo[p];
        indicatorObj.value = indicatorObj.value;
        generateThemeObject(indicatorObj);
    }

    regionNames = getRegionNames(la, zoneLabelField);
    Primary_PCP_Chart(projectDef, layerAttributes, zoneLabelField);
    Theme_PCP_Chart(themeData);

    /////////////////////////
    //// Compute the SVI ////
    /////////////////////////

    var SVI = {};
    var sviNameLookUp = 'SVI';
    var sviJSONthemes = svThemes;
    // SVI is an object with region and value
    if (svThemes) {
        SVI = combineIndicators(sviNameLookUp, themeData, sviJSONthemes );
        scale(SVI);
    }

    ////////////////////////////////
    //// Compute the risk index ////
    ////////////////////////////////

    // Create the risk index only if it has children
    var RI = {};
    var riskIndicator;
    if (riskIndicators !== undefined) {
        riskIndicator = createRiskIndicator(la, riskIndicators, zoneLabelField);

        // capture all risk indicators for selection menu
        for (var key in riskIndicator[0]) {
            if (key != 'Region') {
                allRiskIndicators.push(key);
            }
        }

        // Compute the Risk Indicator
        var nameLookUp = 'RI';
        var riJSONthemes = riskIndicators;
        RI = combineIndicators(nameLookUp, riskIndicator, riJSONthemes);
        scale(RI);
    }

    ///////////////////////////////
    //// Compute the IRI index ////
    ///////////////////////////////

    var IRI = {};
    if (svThemes === undefined || riskIndicators === undefined) {
        //return;
    } else if (namesToOperators[projectDef.operator].code == 'CUSTOM') {
        // the IRI operator is set to use a custom field without recalculating
        var la = layerAttributes.features;
        for (var s = 0; s < la.length; s++) {
            var regionName = la[s].properties[zoneLabelField];
            IRI[regionName] = la[s].properties[projectDef.field];
        }
        scale(IRI);
    } else {
        var sviWeight;
        var riWeight;
        var riInversionFactor;
        var sviInversionFactor;
        var iriOperator = namesToOperators[projectDef.operator];

        for (var i = 0; i < projectDef.children.length; i++) {
            if (projectDef.children[i].name == 'RI') {
                riWeight = projectDef.children[i].weight;
                if (projectDef.children[i].isInverted === true) {
                    riInversionFactor = -1;
                } else {
                    riInversionFactor = 1;
                }
            } else if (projectDef.children[i].name == 'SVI') {
                sviWeight = projectDef.children[i].weight;
                if (projectDef.children[i].isInverted === true) {
                    sviInversionFactor = -1;
                } else {
                    sviInversionFactor = 1;
                }
            }
        }

        if (iriOperator.ignoresWeights) {
            riWeight = 1;
            sviWeight = 1;
        }
        for (var regionName in SVI) {
            var sviValue = SVI[regionName];
            var riValue = RI[regionName];
            if (!isValidNumber(sviValue) || !isValidNumber(riValue)) {
                IRI[regionName] = null;
            } else {
                sviComponent = sviValue * sviWeight * sviInversionFactor;
                riComponent = riValue * riWeight * riInversionFactor;
                if (iriOperator.multiplies) {
                    tempVal = sviComponent * riComponent;
                } else {
                    tempVal = sviComponent + riComponent;
                }
                if (iriOperator.code == 'AVG') {
                    tempVal = tempVal / 2;
                } else if (iriOperator.code == 'GEOM_MEAN') {
                    tempVal = Math.pow(tempVal, 0.5);
                }
                IRI[regionName] = tempVal;
            }
        }
        scale(IRI);
    }


    ////////////////////////////////////
    //// Prep data for thematic map ////
    ////////////////////////////////////
    var tmpVal;
    // Pass indicators into a 'newProperties' element
    for (var i = 0; i < la.length; i++) {
        la[i].newProperties = {};
        for (var key in IRI) {
            if (key == la[i].properties[zoneLabelField]) {
                try {
                    tmpVal = (IRI[key]).toPrecision(5);
                    tmpVal = parseFloat(tmpVal);
                } catch (exc) {
                    tmpVal = null;
                }
                la[i].newProperties.IRI = tmpVal;
            }
        }
        if (svThemes) {
            for (var key in SVI) {
                if (key == la[i].properties[zoneLabelField]) {
                    try {
                        tmpVal = (SVI[key]).toPrecision(5);
                        tmpVal = parseFloat(tmpVal);
                    } catch (exc) {
                        tmpVal = null;
                    }
                    la[i].newProperties.SVI = tmpVal;
                }
            }
        }

        if (riskIndicators !== undefined) {
            for (var key in RI) {
                if (key == la[i].properties[zoneLabelField]) {
                    try {
                        tmpVal = (RI[key]).toPrecision(5);
                        tmpVal = parseFloat(tmpVal);
                    } catch (exc) {
                        tmpVal = null;
                    }
                    la[i].newProperties.RI = tmpVal;
                }
            }

            for (var key in riskIndicator[i]) {
                if (riskIndicator[i] != 'Region') {
                    tempThemeName = riskIndicator[i][key];
                    la[i].newProperties[key] = tempThemeName;
                }
            }
        }

        for (var key in themeData[i]) {
            if (key != 'Region') {
                tempThemeName = themeData[i][key];
                la[i].newProperties[key] = tempThemeName;
            } else if (key == 'Region') {
                la[i].newProperties.region = themeData[i][key];
            }
        }
    }

    // Pass primary indicators into a 'newProperties' element
    if (svThemes) {
        for (var i = 0; i < svThemes.length; i++) {
            var indicatorChildrenKey = [];
            var tmpChildren = svThemes[i].children;
            // Get the indicators children keys
            if (tmpChildren) {
                for (var childIdx = 0; childIdx < tmpChildren.length; childIdx++) {
                    indicatorChildrenKey.push(tmpChildren[childIdx].field);
                }
            }

            for (var j = 0; j < la.length; j++) {
                for (var k in la[j].properties) {
                    for (var l = 0; l < indicatorChildrenKey.length; l++) {
                        if (k == indicatorChildrenKey[l]) {
                            la[j].newProperties[k] = la[j].properties[k];
                        }
                    }
                }
            }
        }
    }


    // If the browser does not support web-gl, then use traditional (limited) vector data.
    // If the browser does support web-gl, then use Mapbox-gl.
    if (webGl === true) {

        ////////////////////////////////////////
        // Deep copy the layer attributes obj //
        ////////////////////////////////////////

        // This application modifies the layer attributes based on changes to the indicator weights.
        // The app also need to keep track of the original layer attributes values.
        // Thus, the layerAttributes obj contains "properties" and "newProperties".
        // This presents an issue when using the object as a data source in Mapbox-GL, because
        // it is hard coded to use properties. In order to get around this issue, we need to
        // deep copy the layerAttributes, and replace "properties" with newProperties

        mappingLayerAttributes = JSON.parse(JSON.stringify(layerAttributes));

        for (var idx = 0; idx < mappingLayerAttributes.features.length; idx++) {
            delete mappingLayerAttributes.features[idx].properties;
        }

        for (var idx = 0; idx < mappingLayerAttributes.features.length; idx++) {
            var tempProperties = JSON.parse(JSON.stringify(mappingLayerAttributes.features[idx].newProperties));
            mappingLayerAttributes.features[idx].properties = tempProperties;
        }

        for (var idx = 0; idx < mappingLayerAttributes.features.length; idx++) {
            delete mappingLayerAttributes.features[idx].newProperties;
        }

        // Emptry any existing interactivity
        $('#mapInfo').empty();

        mapBoxThematicMap(layerAttributes, allSVIThemes, allPrimaryIndicators, allRiskIndicators, weightChange);
    } else {
        leafletThematicMap(layerAttributes, allSVIThemes, allPrimaryIndicators, allRiskIndicators, weightChange);
    }

    var iriPcpData = [];
    for (var region_idx in regionNames) {
        var regionName = regionNames[region_idx];
        var regionData = {"Region": regionName};
        if (isValidNumber(IRI[regionName])) {
            regionData.IRI = IRI[regionName];
        }
        if (isValidNumber(SVI[regionName])) {
            regionData.SVI = SVI[regionName];
        }
        if (isValidNumber(RI[regionName])) {
            regionData.RI = RI[regionName];
        }
        iriPcpData.push(regionData);
    }
    if (iriPcpData.length > 1) {
        var meanValuesArray = calculateMeanValues(iriPcpData);
        meanValuesArray[0].Region = "(mean)";
        iriPcpData = iriPcpData.concat(meanValuesArray);
    }
    if (iriPcpData.length > 0) {
        IRI_PCP_Chart(iriPcpData);
    } else {
        disableWidget(widgetsAndButtons.iri);
    }

} // End processIndicators

function disableWidget(widgetAndBtn) {
    // if the widget is visible, click the button to toggle it
    if ($(widgetAndBtn.widget).is(':visible')) {
        $(widgetAndBtn.button).click();
    }
    // in any case, disable the button that shows the widget
    $(widgetAndBtn.button).prop('disabled', true);
}

function scale(IndicatorObj) {
    var ValueArray = [];
    var scaledValues = [];
    for (var v in IndicatorObj) {
        ValueArray.push(IndicatorObj[v]);
    }
    var notNullElements = ValueArray.filter(isValidNumber);
    var tempMin = Math.min.apply(null, notNullElements),
        tempMax = Math.max.apply(null, notNullElements);

    for (var j = 0; j < ValueArray.length; j++) {
        if (!isValidNumber(ValueArray[j])) {
            scaledValues.push(null);
        }
        // make sure not to divide by zero
        // 1 is an arbitrary choice to translate a flat array into an array where each element equals to 1
        else if (tempMax == tempMin) {
            scaledValues.push(1);
            // FIXME: check if we want to disable the chart tabs here
            // Not using $.each in this case, just to avoid a syntax warning
            // about defining a function within a loop
            // disableWidget(widgetsAndButtons.indicators);
            // disableWidget(widgetsAndButtons.svi);
            // disableWidget(widgetsAndButtons.iri);
        } else {
            scaledValues.push( (ValueArray[j] - tempMin) / (tempMax - tempMin) );
        }
    }

    var tempKeys = Object.keys(IndicatorObj);

    for (var i = 0; i < tempKeys.length; i++) {
        IndicatorObj[tempKeys[i]] = scaledValues[i];
    }
    return IndicatorObj;
}

// Mapbox-gl stuff
function setupMapboxGlMap() {

    // Create mapbox map element
    mapboxgl.accessToken = 'pk.eyJ1IjoiZ2VtZGV2IiwiYSI6ImNqbG1kamlmYTE3MHUzdWxkZWEweHRoeHUifQ.wErApo8meMm031A9a2n26Q';

    map = new mapboxgl.Map({
        container: 'map',
        // Load default mapbox basemap
        style: 'mapbox://styles/mapbox/streets-v8',
        center: [0, 20],
        zoom: 2,
    });
}

function mapBoxThematicMap(layerAttributes, allSVIThemes, allPrimaryIndicators, allRiskIndicators, weightChange) {
    $('#webGlThematicSelection').empty();

    // Add IRI SVI and RI options to the webGlThematicSelection menu
    if (mappingLayerAttributes.features[0].properties.IRI !== undefined) {
        $('#webGlThematicSelection').append('<option class="2">IRI</option>');
    }

    if (mappingLayerAttributes.features[0].properties.SVI !== undefined) {
        $('#webGlThematicSelection').append('<option class="2">SVI</option>');
    }

    if (mappingLayerAttributes.features[0].properties.RI !== undefined) {
        $('#webGlThematicSelection').append('<option class="2">RI</option>');
    }

    // Add IR children themes to selection menu
    if (allRiskIndicators.length > 0) {
        $('#webGlThematicSelection').append('<optgroup label="RI Themes">');
        for (var idx = 0; idx < allRiskIndicators.length; idx++) {
            $('#webGlThematicSelection').append('<option class="1">'+allRiskIndicators[idx]+'</option>');
        }
    }

    // Add SVI children themes to selection menu
    if (allSVIThemes.length > 0) {
        $('#webGlThematicSelection').append('<optgroup label="SVI Themes">');
        for (var idx = 0; idx < allSVIThemes.length; idx++) {
            $('#webGlThematicSelection').append('<option class="3">'+allSVIThemes[idx]+'</option>');
        }
    }

    // Add primary indicators to selection menu
    if (allPrimaryIndicators.length > 0) {
        $('#webGlThematicSelection').append('<optgroup label="Primary Indicators">');
        for (var idx = 0; idx < allPrimaryIndicators.length; idx++) {
            $('#webGlThematicSelection').append('<option class="4">'+allPrimaryIndicators[idx]+'</option>');
        }
    }

    $('#webGlThematicSelection').show();

    // Manage the thematic map selection menu
    // Set the map selection menu to the first multi group dropdown option
    if (selectedIndicator === undefined) {
        $("#webGlThematicSelection").val($("#webGlThematicSelection option:first").val());
        mapboxGlLayerCreation();
    } else {
        $('#webGlThematicSelection').val(selectedIndicator);
    }

    // Execute the mapboxGlLayerCreation when there has been a weight change
    if (weightChange > 0 || projDefChange) {
        mapboxGlLayerCreation(weightChange);
    }

    $('#webGlThematicSelection').change(function() {
        mapboxGlLayerCreation();
    });
}

// Default color
var colorsPal = ['#fee5d9', '#fcbba1', '#fc9272', '#fb6a4a', '#de2d26', '#a50f15'];

function mapboxGlLayerCreation() {
    // There are 5 cases for managing the state of the map:

    // Case 1:
    // The map is created for the first time

    // Case 2:
    // The data used for thematic map has not changed, so we
    // keep the map source, destroy and recreate the map layers

    // Case 3:
    // The weight change will alter the underlying data, so we
    // update the map style and source

    // Case 3.1
    // Only reload the map for the appropriate weight change level

    // Case 4:
    // A new project has been loaded into the application

    // Case 5:
    // A new color scheme has been selected

    // Case 6:
    // A different project definition for the current project
    // has been selected, so we need to proceed as in Case 3

    var weightChange = 0;

    if (arguments[0]) {
        weightChange = arguments[0];
    }

    selectedIndicator = $('#webGlThematicSelection').val();

    // Avoid unnecessarily redrawing the map.
    // Only redraw the map when:
        // 1) the level of the weight changes is lower than the level of the thematic map menu.
            // Example 1: if the user is viewing the SVI thematic map, and then changes any theme, or
            // primary indicator weight, the map must be refreshed.
            // Example 2: If the user is viewing a theme thematic map (e.g. Economy), and then changes
            // the SVI weight, the map should not be redrawn.
        // 2) the thematic map menu has been changes
        // 3) a new project is loaded into the map (case: weightChange = 0)
        // 5) (partial reload) a new color scheme has been selected, only recreate the layers, NOT the data source
        // 6) a different project definition has been selected. Different weights can cause changes to the data source values.

    // weightChange can be a interger value form 0 to 4, 0 being no change been made to the tree chart
    // weightChange 1 = IRI, 2 = SVI or RI, 3 = a theme, 4 = is a primary indicator.
    // selectedIndicatorLabel is a value from 1 - 4, where 1 = IRI, 2 = SVI or RI, 3 = a theme, 4 is a primary indicator.
    // The selectedIndicatorLabel determines the thematic map layer to be rendered.
    var selectedIndicatorLabel = $('#webGlThematicSelection option:selected').attr('class');

    if (weightChange < parseInt(selectedIndicatorLabel) || parseInt(selectedIndicatorLabel) == 4) {
        if (weightChange !== 0) {
            $('#absoluteSpinner').hide();
            return;
        }
    }

    // Find the values to create categorized color ramp
    // First find the min and max vales
    var minMaxArray = [];
    for (var i = 0; i < mappingLayerAttributes.features.length; i++) {
        var match = false;
        for (var k in mappingLayerAttributes.features[i].properties) {
            if (k == selectedIndicator) {
                match = true;
                minMaxArray.push(mappingLayerAttributes.features[i].properties[k]);
                break;
            }
            else {
                match = false;
            }
        }
        if (match === false) {
            return;
        }
    }

    // Focus map on layer
    if (projectChange) {
        map.fitBounds(mapboxBoundingBox);
    }

    var min = Math.min.apply(null, minMaxArray).toFixed(2);
    var max = Math.max.apply(null, minMaxArray).toFixed(2);
    min = (parseFloat(min) - 0.1);
    // Round up the max
    max = Math.ceil(max * 10) / 10;

    var breaks = [];

    function getColor() {
        var interval = (max - min) / 6;
        var tempStep = min;
        for (var i = 0; i < 5; i++) {
            tempStep += interval;
            breaks.push(tempStep);
        }
        breaks.unshift(min);
        breaks.push(max);
    }

    getColor();

    // Case 2, and 4, try to remove any existing layers
    try {
        for (var idx = 0; idx < 6; idx++) {
            map.removeLayer(idx);
        }
    } catch (exc) {
        // continue
    }


    // Case 3 update the source
    if (weightChange) {
        //map.update(true); // Not working for unknown reason.

        // FIXME would really prefer to update the map source here
        map.removeSource('projectSource');
    }

    // Case 4 destory the source
    // Here we use a try catch to manage 3 cases:
    // 1. When a project is loaded for the first time. In this case there is no existing map source or layer,
    // so we try to remove them, but as they do not exist, the app moves on and builds a new source and layer.
    // 2. When a project is loaded for the 2nd, 3rd, nth time. In this case we find that there is a map source
    // and layer that need to be removed, after being removed, the new map source and layers are created.
    // The same logic applies to removeing layers.
    // 3. For the current project, a different project definition has been selected. The different weights
    // can cause changes in the values of the data source
    if (projectChange || projDefChange) {
        try {
            map.removeSource('projectSource');
        } catch (exc) {
            // continue
        }
    }

    // Case 1 and 4
    // **TEMP** also case 3 and 6
    // Populate the mapbox source with GeoJson from Geoserver
    // Only create a new source when the project has been changed
    if (map.style.sources.projectSource === undefined || projectChange || weightChange || projDefChange) {
        map.addSource('projectSource', {
            'type': 'geojson',
            'data': mappingLayerAttributes,
        });
        projectChange = false;
        projDefChange = false;
    }

    $('#mapLegend').remove();
    // Create the map legend
    $('#map-tools').append(
        '<div id="mapLegend" class="my-legend">'+
            '<div class="legend-title">'+selectedIndicator+'</div>'+
            '<div class="legend-scale">'+
                '<ul id="legendLables" class="legend-labels">'+
                '</ul>'+
            '</div>'+
        '</div>'
    );

    // Cases 1, 2, 3, 4, 5 and 6
    // Create a new mapbox layers
    for (var idx = 0; idx < 6; idx++) {
        map.addLayer({
            'id': idx,
            'type': 'fill',
            'source': 'projectSource',
            "source-layer": "eq-simple",
            'interactive': true,
            'paint': {
                'fill-color': colorsPal[idx],
                'fill-opacity': 0.8,
                'fill-outline-color': '#000066'
            },
            'filter': ['all',['>', selectedIndicator, breaks[idx]], ['<=', selectedIndicator, breaks[idx+1]]]
        });
        // Create legend elements
        $('#legendLables').append('<li><span style="background:'+colorsPal[idx]+';"></span>'+breaks[idx].toFixed(2)+'</li>');
    }

    $('#absoluteSpinner').hide();

    // Map interactivity
    $('#map-tools').append(
        '<div id="mapInfo"></div>'
    );

    function findNameAndTypeInProjDef(field, treeNode) {
        // NOTE: in the project definition,
        //       'name' is the extended name of a variable
        //       'field' is the variable reference in the layer
        //       (we are inspecting the project definition
        //       to find the given field and to return the
        //       corresponding extended name)
        retDict = {'type': treeNode.type};
        if (typeof treeNode.field !== 'undefined' && treeNode.field == field) {
            try {
                retDict.name = treeNode.name;
                return retDict;
            } catch(exc) {
                // if the name is undefined, but the field was found, then return the field
                retDict.name = field;
                return retDict;
            }
        } else if (treeNode.name !== 'undefined' && treeNode.name == field) {
            retDict.name = field;
            return retDict;
        } else if (typeof treeNode.children !== 'undefined') {
            for (var i = 0; i < treeNode.children.length; i++) {
                var child = treeNode.children[i];
                var nameAndType = findNameAndTypeInProjDef(field, child);
                if ('name' in nameAndType) {
                    retDict.name = nameAndType.name;
                    retDict.type = nameAndType.type;
                    return retDict;
                }
            }
            return {};
        } else {
            return {};
        }
    }

    // NOTE: It would be better to define the click event handler somewhere else,
    //       but it is not so obvious, so for now I am removing the handler and
    //       redefining it.
    //       Without removing the handler, after switching projects, clicking a
    //       zone in the map would cause the handler to be called multiple times,
    //       causing issues in toggling the highlighting of the clicked zone.
    map.off('click');
    map.on('click', function(e) {
        map.featuresAt(e.point, { radius : 6}, function(err, features) {
            if (err) throw err;
            $('#mapInfo').empty();
            $('#mapInfo').css({'visibility': 'visible'});
            var region;
            try {
                region = features[0].properties.region;
            } catch(exc) {
                // do not show info
            }
            if (typeof region !== 'undefined') {
                toggleRegionInCharts(region);
                $('#mapInfo').append($('<h4/>').html(region));
            }
            var structuredInfo = {
                'compositeIndices': [],
                'svThemes': [],
                'svIndicators': [],
                'riskIndicators': []
            };
            var isDataAvailable = false;
            if (typeof features[0] !== 'undefined' && typeof features[0].properties !== 'undefined') {
                for (var field in features[0].properties) {
                    var nameAndType = findNameAndTypeInProjDef(field, sessionProjectDef);
                    if ('name' in nameAndType) {
                        isDataAvailable = true;
                        var nameAndValue = {
                            'name': nameAndType.name,
                            'value': features[0].properties[field]
                        };
                        switch (nameAndType.type) {
                            case nodeTypes.IRI:
                            case nodeTypes.RI:
                            case nodeTypes.SVI:
                                structuredInfo.compositeIndices.push(nameAndValue);
                                break;
                            case nodeTypes.SV_THEME:
                                structuredInfo.svThemes.push(nameAndValue);
                                break;
                            case nodeTypes.SV_INDICATOR:
                                structuredInfo.svIndicators.push(nameAndValue);
                                break;
                            case nodeTypes.RISK_INDICATOR:
                                structuredInfo.riskIndicators.push(nameAndValue);
                                break;
                            default:
                                // This should never happen, unless the project definition is wrong
                                alert('Wrong project definition: unknown node type [' + nameAndType.type + ']');
                        }
                    }
                }
            }
            if (isDataAvailable) {
                $.each(['compositeIndices', 'riskIndicators', 'svThemes', 'svIndicators'], function(ind, key) {
                    if (structuredInfo[key].length) {
                        $('#mapInfo').append('<hr>');
                    }
                    for (var i = 0; i < structuredInfo[key].length; i++) {
                        var name = structuredInfo[key][i].name;
                        var value = structuredInfo[key][i].value;
                        $('#mapInfo').append(name + ': ' + value + '</br>');
                    }
                });
            } else {
                $('#mapInfo').append('No data available');
            }
        });
    });
}

function setupLeafletMap() {
    map = new L.Map('map', {
        minZoom: 2,
        scrollWheelZoom: false,
        attributionControl: false,
        maxBounds: new L.LatLngBounds(new L.LatLng(-90, -180), new L.LatLng(90, 180)),
    });
    map.setView(new L.LatLng(10, -10), 2).addLayer(baseMapUrl);
}

function toggleRegionInCharts(region) {
    $.each(chartElems, function(key, elem){
        var allGraphData = map[elem.graph].data();
        var deletedSelectedData;
        for (var i=0; i<allGraphData.length; i++) {
            var regionData = allGraphData[i];
            if (region == regionData.Region) {
                for (var j = 0; j < elem.dataOfSelectedRegions.length; j++) {
                    if (elem.dataOfSelectedRegions[j].Region == region) {
                        // remove the region data from the array of selected items
                        deletedSelectedData = elem.dataOfSelectedRegions.splice(j, 1);
                        break;
                    }
                }
                if (typeof deletedSelectedData == "undefined") { // it was not already selected
                    elem.dataOfSelectedRegions.push(regionData);
                }
            }
        }
        map[elem.graph].brushReset();
        if (elem.dataOfSelectedRegions.length) {
            map[elem.graph].highlight(elem.dataOfSelectedRegions);
            d3.select(elem.gridId)
                .datum(elem.dataOfSelectedRegions.slice(0,MAX_ROWS_TO_DISPLAY))
                .call(map[elem.grid])
                .selectAll(".divgrid-row")
                .on({
                    "mouseover": function(d) {
                        map[elem.graph].highlight([d]);
                    },
                    "mouseout": function(d) {
                        map[elem.graph].highlight(elem.dataOfSelectedRegions);
                    }
                });
            updateNumDisplayedRows(elem.dispRowsId, elem.dataOfSelectedRegions);
        } else {
            highlightRegionsInCharts([]);
        }
    });
}

function highlightRegionsInCharts(regions) {
    if (!regions.length) {
        // if nothing is selected, unhighlight all and display all rows in the tables
        $.each(chartElems, function(key, elem){
            map[elem.graph].unhighlight();
            var allGraphData = map[elem.graph].data();
            d3.select(elem.gridId)
                .datum(allGraphData.slice(0,MAX_ROWS_TO_DISPLAY))
                .call(map[elem.grid])
                .selectAll(".divgrid-row")
                .on({
                    "mouseover": function(d) {
                        map[elem.graph].highlight([d]);
                    },
                    "mouseout": function(d) {
                        highlightRegionsInCharts(regions);
                    }
                });
            updateNumDisplayedRows(elem.dispRowsId, allGraphData);
        });
    }
    for (var reg_idx=0; reg_idx<regions.length; reg_idx++) {
        region = regions[reg_idx];
        highlightRegionInCharts(region);
    }
}

function highlightRegionInCharts(region) {
    $.each(chartElems, function(key, elem){
        var allGraphData = map[elem.graph].data();
        for (var i=0; i<allGraphData.length; i++) {
            var regionData = allGraphData[i];
            if (region == regionData.Region) {
                elem.dataOfSelectedRegions.push(regionData);
            }
        }
        map[elem.graph].highlight(elem.dataOfSelectedRegions);
        d3.select(elem.gridId)
            .datum(elem.dataOfSelectedRegions.slice(0,MAX_ROWS_TO_DISPLAY))
            .call(map[elem.grid])
            .selectAll(".divgrid-row")
            .on({
                "mouseover": function(d) {
                    map[elem.graph].highlight([d]);
                },
                "mouseout": function(d) {
                    map[elem.graph].highlight(elem.dataOfSelectedRegions);
                }
            });
        updateNumDisplayedRows(elem.dispRowsId, elem.dataOfSelectedRegions);
    });
}

function resetBrushesInOtherCharts(key) {
    $.each(chartElems, function(chartKey, chartElem) {
        if (chartKey !== key) {
            map[chartElem.graph].brushReset();
        }
    });
}

function getRegions(d){
    var regions = [];
    for (var i=0; i<d.length; i++) {
        regions.push(d[i].Region);
    }
    return regions;
}

function assignIRIChartAndGridToMap(graph, grid) {
    map.iriGraph = graph;
    map.iriGrid = grid;
}

function assignThemeChartAndGridToMap(graph, grid) {
    map.themeGraph = graph;
    map.themeGrid = grid;
}

function assignPrimaryChartAndGridToMap(graph, grid) {
    map.primaryGraph = graph;
    map.primaryGrid = grid;
}

function resetDataOfSelectedRegions(){
    chartElems = {"iri": iriChartElems, "theme": themeChartElems, "primary": primaryChartElems};
    $.each(chartElems, function(key, chartElem) {
        chartElem.dataOfSelectedRegions = [];
    });
}

function leafletThematicMap(layerAttributes, allSVIThemes, allPrimaryIndicators, allRiskIndicators, weightChange) {

    // Add main indicators to selection menu
    $('#leafletThematicSelection').empty();
    $('#leafletThematicSelection').append(
        '<optgroup label="Indicators">'+
        '<option>IRI</option>'+
        '<option>SVI</option>'+
        '<option>IR</option>'
    );

    // Add SVI themes to selection menu
    $('#leafletThematicSelection').append('<optgroup label="SVI Indicators">');
    for (var i = 0; i < allSVIThemes.length; i++) {
        $('#leafletThematicSelection').append('<option>'+allSVIThemes[i]+'</option>');
    }

    try {
        if (riskIndicators !== undefined) {
            // Add IR themes to selection menu
            $('#leafletThematicSelection').append('<optgroup label="IR Indicators">');
            for (var i = 0; i < allRiskIndicators.length; i++) {
                $('#leafletThematicSelection').append('<option>'+allRiskIndicators[i]+'</option>');
            }
        }
    } catch (exc) {
        // continue
    }

    // Add all primary indicators to selection menu
    $('#leafletThematicSelection').append('<optgroup label="Composite Indicators">');
    for (var i = 0; i < allPrimaryIndicators.length; i++) {
        $('#leafletThematicSelection').append('<option>'+allPrimaryIndicators[i]+'</option>');
    }

    // set the map selection menu to IRI or previously selected indicator value
    if (typeof selectedIndicator === 'undefined') {
        // TODO fix this to use optgroup:first
        //$('#leafletThematicSelection').val('IRI');
        $('#leafletThematicSelection option').eq(3).attr("selected", "selected");
        thematicMapCreation();
    } else {
        $('#leafletThematicSelection').val(selectedIndicator);
    }

    // Execute the thematicMapCreation when there has been a weight change
    if (weightChange > 0) {
        thematicMapCreation();
    }

    $('#leafletThematicSelection').change(function() {
        thematicMapCreation();
    });
}


function thematicMapCreation() {
    $('#leafletThematicSelection').show();
    // Initialize the legend
    var legendControl = new L.Control.Legend();
    legendControl.addTo(map);

    // find the indicator that has been selected
    selectedIndicator = $('#leafletThematicSelection').val();

    var displayElement = 'newProperties.'+selectedIndicator;
    var la = layerAttributes.features;

    // find the min and max values for the selected indicator
    var minMaxArray = [];
    for (var i = 0; i < la.length; i++) {
        for (var k in la[i].newProperties) {
            if (k == selectedIndicator) {
                minMaxArray.push(la[i].newProperties[k]);
            }
        }
    }

    map.fitBounds(leafletBoundingBox);

    var min = Math.min.apply(null, minMaxArray).toFixed(2);
    var max = Math.max.apply(null, minMaxArray).toFixed(2);

    try {
        map.removeLayer(thematicLayer);
    } catch (exc) {
        // continue
    }
    try {
        $('.leaflet-control-legend').empty();
    } catch (exc) {
        // continue
    }

    // vary the color from yellow (60) to red(0) from min to max values
    var yellowToRed = new L.HSLHueFunction(new L.Point(min, 60), new L.Point(max, 0), {
        //outputHue: 60
    });

    // Set the thematic layer options
    var options = {
        recordsField: 'features',
        locationMode: L.LocationModes.GEOJSON,
        geoJSONField: 'geometry',
        layerOptions: {
            fillOpacity: 0.5,
            opacity: 0.5,
            weight: 1,
            stroke: true,
            color: '#0000FF'
        },
        displayOptions: {}
    };

    options.displayOptions[displayElement] = {
        displayName: selectedIndicator,
        fillColor: yellowToRed
    };

    thematicLayer = new L.ChoroplethDataLayer(layerAttributes, options);
    map.addLayer(thematicLayer);

    legendControl = new L.Control.Legend();
    legendControl.addTo(map);
    $('#absoluteSpinner').hide();
}

function whenProjDefSelected() {
    projDefChange = true;
    $('#projectDef-spinner').show();
    var pdSelection = $('#pdSelection').val();
    for (var i = 0; i < tempProjectDef.length; i++) {
        if (tempProjectDef[i].title === pdSelection) {
            // Deep copy the temp project definition object
            sessionProjectDef = jQuery.extend(true, {}, tempProjectDef[i]);
            if (has_custom_fields(sessionProjectDef)) {
                projDefOperatorsAreStandard = false;
                $('.alert-custom-operators').show();
            } else {
                projDefOperatorsAreStandard = true;
                $('.alert-custom-operators').hide();
            }
            loadPD(sessionProjectDef);
            $('#iri-spinner').hide();
            $('#project-definition-svg').show();
            processIndicators(layerAttributes, sessionProjectDef);
        }
    }
}

function has_custom_fields(projDef) {
    if (typeof(projDef.operator) !== 'undefined' && namesToOperators[projDef.operator].code == 'CUSTOM') {
        return true;
    }
    for (var childIdx in projDef.children) {
        var child = projDef.children[childIdx];
        if (has_custom_fields(child)) {
            return true;
        }
    }
    return false;
}

function getGeoServerLayers() {
    $('#load-project-spinner').show();
    var IRMTLayerNames = [];
    var IRMTLayerTitle = [];
    var url = "/geoserver/ows?service=WFS&version=1.0.0&REQUEST=GetCapabilities&SRSNAME=EPSG:4326&outputFormat=json&format_options=callback:getJson";
    // Get layers from GeoServer and populate the layer selection menu

    $.ajax({
        url: url,
        contentType: 'application/json',
        success: function(xml) {


            //convert XML to JSON
            var xmlText = new XMLSerializer().serializeToString(xml);
            var x2js = new X2JS();

            var jsonElement = x2js.xml_str2json(xmlText);

            var featureType = jsonElement.WFS_Capabilities.FeatureTypeList.FeatureType;

            // Find the IRMT keywords
            var stringsToLookFor = ['SVIR_QGIS_Plugin', 'IRMT_QGIS_Plugin'];
            // Reload if the api call was incomplete
            if (featureType.length === undefined) {
                getGeoServerLayers();
                return;
            }

            for (var i = 0; i < featureType.length; i++) {
                for (var j=0; j < stringsToLookFor.length; j++) {
                    stringToLookFor = stringsToLookFor[j];
                    if (featureType[i].Keywords.indexOf(stringToLookFor) > -1) {
                        // IRMTLayerNames.push(featureType[i].Title + " (" + featureType[i].Name + ")");
                        IRMTLayerNames.push(featureType[i].Name);
                        IRMTLayerTitle.push(featureType[i].Title);
                        break;
                    }
                }
            }

            if (IRMTLayerNames.length == 0) {
		        $('#load-project-spinner').hide();
		        $('#ajaxErrorDialog').empty();
		        $('#ajaxErrorDialog').append(
		            '<p>No layer found.</p>'
		        );
		        $('#ajaxErrorDialog').dialog('open');
            }



            // Create AngularJS dropdown menu
            var mapLayerList = [];

            function target_location(hostname, lp_name) {
                return function() { window.location = '/irv/' + lp_name; };
            };

            for (var ij = 0; ij < IRMTLayerNames.length; ij++) {
                var layerProperties = {};
                layerProperties.name = IRMTLayerNames[ij];
                layerProperties.title = IRMTLayerTitle[ij];

                console.log(layerProperties.name);

                $('#layer-list').append('<div id="list' + ij +'">' + layerProperties.title + '</div>');

                $('#list'+ ij).on('click', target_location(location.hostname, layerProperties.name));
            }

            $('#load-project-spinner').hide();
        },
        error: function() {
            console.log('error')
            $('#ajaxErrorDialog').empty();
            $('#ajaxErrorDialog').append(
                '<p>This application was not able to get a list of layers from GeoServer</p>'
            );
            $('#ajaxErrorDialog').dialog('open');
        }
    });
}

var app = angular.module('myApp', []);
app.controller('myCtrl', function($scope) {
        $scope.count = 0;
});

angular.module('angularBootstrap.dropdown', []).directive('bootstrapDropdown', function () {
    return function(scope, element, attrs) {

        jQuery('html').on('click', function () {
            element.removeClass('open')
        })

        jQuery('.dropdown-toggle', element).on('click', function(e) {
            element.toggleClass('open');
            return false;
        });
    };
});

var startApp = function() {

    // Check the browser for webGL support
    function webglDetect(return_context) {
        if (!!window.WebGLRenderingContext) {
            var canvas = document.createElement("canvas"),
                names = ["webgl", "experimental-webgl", "moz-webgl", "webkit-3d"],
                context = false;

            for(var i=0;i<4;i++) {
                try {
                    context = canvas.getContext(names[i]);
                    if (context && typeof context.getParameter == "function") {
                        // WebGL is enabled
                        if (return_context) {
                            // Return WebGL object if the function's argument is present
                            return {name:names[i], gl:context};
                        }
                        // Else, return just true
                        return true;
                    }
                } catch(exc) {}
            }

            // WebGL is supported, but disabled
            return false;
        }

        // WebGL not supported
        return false;
    }


    webGl = webglDetect();

    // using the list, otherwise we would lose the order
    $.each(['projDef', 'iri', 'svi', 'indicators'], function(i, widgetName) {
        // Theme tabs behavior
        var widget = $(widgetsAndButtons[widgetName].widget);
        widget.resizable({
            minHeight: 220,
            minWidth: 220
        });

        widget.tabs({
            collapsible: false,
            selected: -1,
            active: false,
        });

        widget.draggable({
            stack: "div",  // put on top of the others when dragging
            distance: 0,   // do it even if it's not actually moved
            cancel: "#project-def, #primary-chart, #cat-chart, #iri-chart, #iri-chart, #themeSelector"
        });
        widget.css({
            'display': 'none',
            // perhaps we should not set width and height here, and let things automatically resize
            'width': '860px',
            'height': '600px',
            'overflow': 'hidden',
            // 'overflow': 'auto',  // to add scrollbars (but they should be added to the chart, not to the widget)
            'position': 'fixed',
            'left': (10 + i * 40) + 'px',
            'top': (110 + i * 40) + 'px'
        });
    });

    $('#cover').remove();
    $('#projectDef-spinner').hide();
    $('#iri-spinner').hide();
    $('#themeSelector').hide();
    $('#saveBtn').prop('disabled', true);
    $('#saveBtn').addClass('btn-disabled');

    // Slider
    $(function() {
        $( '#slider-vertical' ).slider({
            orientation: 'vertical',
            range: 'min',
            min: 0,
            max: 100,
            value: 16.666,
            slide: function( event, ui ) {
                $( '#econ-weight' ).val( ui.value );
            }
        });
        $( '#econ-weight' ).val( $( '#slider-vertical' ).slider( 'value' ) );
    });

    $('#map-tools').append(
        '<div class="l_proj"><button id="loadProjectdialogBtn" type="button" class="btn btn-blue">Load Project</button></div>'
    );
    // Using the list in order to keep the order
    $.each(['indicators', 'svi', 'iri', 'projDef'], function(i, widgetName) {
        // slice(1) removes the heading # from the selector
        var buttonId = widgetsAndButtons[widgetName].button.slice(1);
        var buttonText = widgetsAndButtons[widgetName].buttonText;
        $('#map-tools').append(
            '<div class="but_l_proj"><button id="' + buttonId + '" type="button" class="btn btn-blue" disabled>' + buttonText + '</button></div>'
        );
    });

    if (webGl === false) {
        $('#map-tools').append(
            '<div><select id="leafletThematicSelection">'+
                '<option>Select Indicator</option>'+
            '</select><div>'
        );

        $('#leafletThematicSelection').hide();

        setupLeafletMap();
    } else {
        $('#map-tools').append(
            '<div><select id="webGlThematicSelection">'+
                '<option>Select Indicator</option>'+
            '</select></div>'
        );

        $('#webGlThematicSelection').hide();

        setupMapboxGlMap();
    }

    $('#loadProjectdialogBtn').click(function() {
        getGeoServerLayers();
        $('#loadProjectDialog').dialog('open');
    });

    function toggleWidget(widgetAndBtn) {
        // toggle widget and change text on the corresponding button
        var btnText = $(widgetAndBtn.button).html();
        // If the widget is visible, the button text is 'Hide Widgetname'
        // Otherwise it is 'Show Widgetname'
        // Let's change the button text before toggling the widget
        if (btnText.indexOf('Hide ') >= 0) {  // Change Hide -> Show
            btnText = 'Show ' + btnText.slice(5);
            $(widgetAndBtn.button).css({
                'background': '#f7931e'
            });
        } else {                              // Change Show -> Hide
            btnText = 'Hide ' + btnText.slice(5);
            $(widgetAndBtn.button).css({
                'background': '#f05a24'
            });
        }
        $(widgetAndBtn.button).html(btnText);
        $(widgetAndBtn.widget).toggle();
    }

    $.each(widgetsAndButtons, function(key, widgetAndBtn) {
        $(widgetAndBtn.button).click(function() {
            toggleWidget(widgetAndBtn);
        });
    });

    // TODO check these are all needed
    $('#region-selection-list').hide();
    $('#svir-project-list').hide();

    $('#svir-project-list').css({ 'margin-bottom' : 0 });
    // $('#loadProjectBtn').prop('disabled', true);

    // Enable the load project button once a project has been selected
    $('#layer-list').change(function() {
        // $('#loadProjectBtn').prop('disabled', false);
    });

    $('#loadProjectBtnx').click(function() {
        // setWidgetsToDefault();

        // // FIXME This will not work if the title contains '(' or ')'
        // // Get the selected layer
        // var scope = angular.element($("#layer-list")).scope();
        // selectedLayer = scope.selected_map.name;

        // // clean the selected layer to get just the layer name
        // selectedLayer = selectedLayer.substring(selectedLayer.indexOf("(") + 1);
        // selectedLayer = selectedLayer.replace(/[)]/g, '');
        // loadProject();
    });

    // AJAX error dialog
    $('#ajaxErrorDialog').dialog({
        'autoOpen': false,
        'height': 150,
        'width': 400,
        'z-index': 999,
        'closeOnEscape': true,
        'modal': true,
    });

    $('#saveStateDialog').dialog({
        autoOpen: false,
        height: 520,
        width: 620,
        closeOnEscape: true,
        position: {at: 'right bottom'}
    });

    $('#loadProjectDialog').dialog({
        autoOpen: false,
        height: 520,
        width: 620,
        // closeOnEscape: true
    });

    $('#loadProjectDialog').draggable({
        stack: "div",  // put on top of the others when dragging
        distance: 0,   // do it even if it's not actually moved
    });

    $('#map-tools').css({
        'padding': '6px',
        'position': 'absolute',
        'top': '43px',
        'left': '39px',
        'width': '93.3%',
        'z-index': 6
    });

    $('.l_proj').css({
        'float': 'left',
        'border-bottom': '2px solid #d9edf7',
        'border-color': '#bce8f1',
        'color': '#31708f',
        'padding': '10px'
    });

    $('.but_l_proj').css({
        'float': 'right',
        'border-bottom': '2px solid #d9edf7',
        'border-color': '#bce8f1',
        'color': '#31708f',
        'padding': '10px 4px',
    });
    $.each(widgetsAndButtons, function(key, widgetAndBtn) {
        $(widgetAndBtn.button).css({
            'position': 'relative',
            'float': 'right',
            'margin-left': '2px'
        });
    });

    $('#base-map-menu').css({
        'position': 'fixed',
        'left': '390px'
    });

    $('#leafletThematicSelection').css({
        'position': 'fixed',
        'left': '160px',
        'margin-bottom' : 0
    });

    $('#webGlThematicSelection').css({
        'position': 'absolute',
        'right': '15px',
        'top': '125px',
        'margin-bottom' : 0
    });

    // Check the URL for layer parameter
    var urlLayerParameter = location.href;
    urlLayerParameter = urlLayerParameter.split('irv/')[1];

    if (urlLayerParameter) {
        selectedLayer = urlLayerParameter;
        loadProject();
    }
};

function loadProject() {
    setWidgetsToDefault();
    $('#thematic-map-selection').show();
    attributeInfoRequest(selectedLayer);
    $.each(widgetsAndButtons, function(key, widgetAndBtn) {
        // just enable buttons without opening widgets
        $(widgetAndBtn.button).prop('disabled', false);
    });
    // open the project definition widget if it's not already open
    if (!$(widgetsAndButtons.projDef.widget).is(':visible')) {
        $(widgetsAndButtons.projDef.button).click();
    }
}

function attributeInfoRequest(selectedLayer) {
    $('#loadProjectDialog').dialog('close');
    // Get layer attributes from GeoServer
    return $.ajax({
        type: 'get',
        url: '/geoserver/oqplatform/ows?service=WFS&version=1.0.0&request=GetFeature&typeName='+ selectedLayer +'&maxFeatures=50&outputFormat=application%2Fjson',
        success: function(data) {
            projectChange = true;
            // Make a global variable used by the d3-tree chart
            // when a weight is modified
            layerAttributes = data;
            projectLayerAttributes = layerAttributes;

            // provide a dropdown menu to select the region field
            var layerFields = [];
            // get all the field name out of the layer attributes object
            for (var key in layerAttributes.features[0].properties) {
                layerFields.push(key);
            }
            projDefJSONRequest(selectedLayer);

        },
        error: function() {
            $('#ajaxErrorDialog').empty();
            $('#ajaxErrorDialog').append(
                '<p>This application was not able to get information about the selected layer</p>'
            );
            $('#ajaxErrorDialog').dialog('open');
        }
    });
}

function projDefJSONRequest(selectedLayer) {
    // Get the project definition
    return $.ajax({
        type: 'get',
        url: '/svir/get_supplemental_information?layer_name='+ selectedLayer,
        success: function(data) {
            // Stop the application and provide an error if webGL is not supported
            // and the vertices count is greater then the vertices threshold
            verticesCount = data.vertices_count;
            if (webGl === false && verticesCount > VERTICES_THRESHOLD) {
                $('#ajaxErrorDialog').empty();
                $('#ajaxErrorDialog').append(
                    '<p>The project geometry is too complex for your browser to manage. Please try using a browser that has WebGL support</p>'
                );
                $('#ajaxErrorDialog').dialog('open');
                $('#absoluteSpinner').hide();
                $('#projectDef-spinner').hide();
                return;
            }

            license = data.license;
            tempProjectDef = data.project_definitions;
            zoneLabelField = data.zone_label_field;
            selectedIndicator = undefined;
            projectTitle = data.title;
            $('a#project-def-title').text('Project: ' + projectTitle);

            // Remove alert div
            $('#alert').remove();

            // Check the svir plugin version
            // Provide some backwards compatibility for old naming convention
            var thisVersion = null;
            if (data.hasOwnProperty('svir_plugin_version')) {
                thisVersion = data.svir_plugin_version;
            } else if (data.hasOwnProperty('irmt_plugin_version')) {
                thisVersion = data.irmt_plugin_version;
            } else {
                $('#projectDef-spinner').hide();
                $('#project-def').append(
                    '<div id="alert" class="alert alert-danger" role="alert">' +
                        'The project you are trying to load was created with a version of the SVIR QGIS tool kit that is not compatible with this application' +
                    '</div>'
                );
                return;
            }

            // Populate global bounding box array
            leafletBoundingBox = [
                [data.bounding_box.miny, data.bounding_box.minx],
                [data.bounding_box.maxy, data.bounding_box.maxx]
            ];

            mapboxBoundingBox = [
                [data.bounding_box.minx,data.bounding_box.miny],
                [data.bounding_box.maxx, data.bounding_box.maxy]
            ];
            if (data.bounding_box.minx < -180 || data.bounding_box.minx > 180 ||
                    data.bounding_box.maxx < -180 || data.bounding_box.maxx > 180 ||
                    data.bounding_box.miny < -90  || data.bounding_box.miny > 90  ||
                    data.bounding_box.maxy < -90  || data.bounding_box.maxy > 90) {
                $('#ajaxErrorDialog').empty();
                $('#ajaxErrorDialog').append(
                    '<p>The project you are trying to load has a bounding box that can not be correctly loaded by this application. Please check the projection.</p>'
                );
                $('#ajaxErrorDialog').dialog('open');
                $('#projectDef-spinner').hide();
                $('#absoluteSpinner').hide();
                return;
            }

            if ($('#pdSelection').length > 0) {
                $('#pdSelection').remove();
            }

            // Create the pd selection menu
            $('#project-def').prepend('<select id="pdSelection" onChange="whenProjDefSelected();"><option value"" disabled selected>Select a Project Definition</option></select>');
            var pdTitles = [];

            // break the array into objects, present the user with a choice of PDs
            for (var i = 0; i < tempProjectDef.length; i++) {
                // Get the PD title
                pdTitles.push(tempProjectDef[i].title);
            }
            // Provide the user with a selection dropdown of the available PDs
            for (var ia = 0; ia < pdTitles.length; ia++) {
                $('#pdSelection').append(
                    '<option value="'+ pdTitles[ia] +'">'+ pdTitles[ia] +'</option>'
                );
            }

            // select the first project definition in menu dropdown list
            try {
                var menuOption = $('#pdSelection');
                menuOption[0].selectedIndex = 1;
            } catch (exc) {
                // continue
            }

            triggerPdSelection();
            $('#projectDef-spinner').hide();
        },
        error: function() {
            $('#ajaxErrorDialog').empty();
            $('#ajaxErrorDialog').append(
                '<p>The project you are trying to load does not apear to be valid.</p>'
            );
            $('#ajaxErrorDialog').dialog('open');
        }
    });
}

// Trigger first project definition selection
function triggerPdSelection () {
    $('#pdSelection').trigger('change');
}
