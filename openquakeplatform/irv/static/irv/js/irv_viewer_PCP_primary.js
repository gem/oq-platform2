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


/////////////////////////////////////////////////
////// Category Parallel Coordinates Chart //////
/////////////////////////////////////////////////

function Primary_PCP_Chart(projectDef, layerAttributes, zoneLabelField) {
    // Find the theme data and create selection dropdown menu
    var themesWithChildren = [];
    var sum = {};
    var sumMean = {};
    var sumMeanArray = [];

    for (var i = 0; i < projectDef.children.length; i++) {
        try {
            for (var j = 0; j < projectDef.children[i].children.length; j++) {
                if (projectDef.children[i].children[j].children) {
                    themesWithChildren.push(projectDef.children[i].children[j].name);
                }
            }
        } catch (e) {
            // continue
        }
    }
    if (themesWithChildren) {
        $(widgetsAndButtons.indicators.button).prop('disabled', false);
    }

    $('#themeSelector').empty();
    $('#themeSelector').append('<option value="" disabled>Select a Theme</option>');

    for (var l = 0; l < themesWithChildren.length; l++) {
        var theme = themesWithChildren[l];
        $('#themeSelector').append('<option value="'+ theme +'">' + theme + '</option>');
    }
    $('#themeSelector').show();

    // select the first indicator
    var menuOption = $('#themeSelector');
    menuOption[0].selectedIndex = 1;
    // trigger first indicator
    setTimeout(function() {
        $('#themeSelector').trigger('change');
    }, 100);

    $('#themeSelector').change(function() {
        var highlightedRegions = [];
        try {
            var highlightedElements = map.primaryGraph.highlighted();
            for (var i = 0; i < highlightedElements.length; i++) {
                highlightedRegions.push(highlightedElements[i].Region);
            }
        } catch (exc) {
            // highlightedRegions remains empty
        }
        resetDataOfSelectedRegions();
        var selectedTheme = $('#themeSelector').val();
        // Find the children of selected theme
        var selectedThemeChildren = [];
        for (var i = 0; i < projectDef.children.length; i++) {
            try {
                for (var j = 0; j < projectDef.children[i].children.length; j++) {
                    if (projectDef.children[i].children[j].name === selectedTheme) {
                        selectedThemeChildren = projectDef.children[i].children[j].children;
                    }
                }
            } catch (e) {
                // continue
            }
        }

        var dataToPlot = [];
        var regionNames = [];
        for (var regionIdx = 0; regionIdx < layerAttributes.features.length; regionIdx++) {
            var regionName = layerAttributes.features[regionIdx].properties[zoneLabelField];
            regionNames.push(regionName);
            var regionData = {"Region": regionName};
            for (var indicatorIdx = 0; indicatorIdx < selectedThemeChildren.length; indicatorIdx++) {
                var indicatorField = selectedThemeChildren[indicatorIdx].field;
                var indicatorValue = layerAttributes.features[regionIdx].properties[indicatorField];
                if (typeof indicatorValue !== 'undefined' && !isNaN(indicatorValue) && indicatorValue !== null) {
                    regionData[indicatorField] = indicatorValue;
                }
            }
            dataToPlot.push(regionData);
        }
        if (dataToPlot.length < 1) {
            return;
        }
        if (dataToPlot.length > 1) {
            var meanValuesArray = calculateMeanValues(dataToPlot);
            meanValuesArray[0].Region = "(mean)";
            dataToPlot = dataToPlot.concat(meanValuesArray);
        }

        $('#primary-tab').css({'height': '100%'});
        $('#primary-tab').append('<div id="primary-chart"></div>');

        $("#primary-chart").empty();
        updateNumDisplayedRows("#primaryDisplayedRows", dataToPlot);

        var color = d3.scale.category20();

        var graph = d3.parcoords(
                {nullValueSeparator: "bottom",
                 nullValueSeparatorPadding: { "top": 15, "right": 0, "bottom": 8, "left": 0 }
                })("#primary-chart")
            // .width(600 + horizontalSpacer)
            // .height(300 + verticalSpacer)
            .width(calculateWidth(dataToPlot))
            .height(400)
            .data(dataToPlot)
            // .hideAxis(["plotElement"])  // if we want to use a legend instead
            .alpha(0.3)
            .margin({
                top: 30,
                left: calculateLeftMargin(dataToPlot),
                right: 0,
                bottom: 20
            })
            .mode("queue")
            .color(function(d) {return color(d.Region);})
            .composite("darker")
            .render()
            .shadows()
            .createAxes()
            .reorderable()
            .brushMode("1D-axes");

        // create data table, row hover highlighting
        var grid = d3.divgrid();
        d3.select("#primary-grid")
            .datum(dataToPlot.slice(0,MAX_ROWS_TO_DISPLAY))
            .call(grid)
            .selectAll(".divgrid-row")
            .on({
                "mouseover": function(d) {
                    graph.highlight([d]);
                },
                "mouseout": graph.unhighlight
            });

        // update data table on brush event
        graph.on("brush", function(d) {
            graph.unhighlight();
            d3.select("#primary-grid")
            .datum(d.slice(0,MAX_ROWS_TO_DISPLAY))
            .call(grid)
            .selectAll(".divgrid-row")
            .on({
                "mouseover": function(d) {
                    graph.highlight([d]);
                },
                "mouseout": graph.unhighlight
            });
            updateNumDisplayedRows("#primaryDisplayedRows", d);
            resetDataOfSelectedRegions();
            resetBrushesInOtherCharts("primary");
        });

        graph.on("brushend", function(d) {
            graph.unhighlight();
            var regions = [];
            if (!$.isEmptyObject(graph.brushExtents())) {
                regions = getRegions(d);
            }
            highlightRegionsInCharts(regions);
        });

        assignPrimaryChartAndGridToMap(graph, grid);

        // if something was selected before switching theme, select it again
        if (highlightedRegions.length) {
            // NOTE: ugly, but otherwise it messes up with colors
            setTimeout(function() {
                highlightRegionsInCharts(highlightedRegions);
            }, 100);
        }
    });
}
