// These two global variables are for the arrows and switching between the graphs
let currentGraphIndex = 0;
let validGraphs = [];

// These are the event listeners for the clicking of the left and right arrow to switch graphs
document.addEventListener("DOMContentLoaded", () => {

    // When left arrow is clicked
    document.querySelector('.left-arrow').addEventListener('click', () => {
        console.log('Left arrow clicked');
        if (validGraphs.length > 0) {
            currentGraphIndex = (currentGraphIndex - 1 + validGraphs.length) % validGraphs.length;
            d3.select("#graphArea").selectAll("*").remove(); // Clear previous graph
            displaySleekGraph(validGraphs[currentGraphIndex]); // Display the new graph
        }
    });

    // When right arrow is clicked
    document.querySelector('.right-arrow').addEventListener('click', () => {
        console.log('Right arrow clicked');
        if (validGraphs.length > 0) {
            currentGraphIndex = (currentGraphIndex + 1) % validGraphs.length;
            d3.select("#graphArea").selectAll("*").remove(); // Clear previous graph
            displaySleekGraph(validGraphs[currentGraphIndex]); // Display the new graph
        }
    });
});

// Async function for handling form submission
async function formSubmitHandler(event) {

    // Need to do this preventDefault to stop page from refreshing when form is submitted. 
    event.preventDefault(); 

    const ip = document.getElementById("ip").value;
    const file = document.getElementById("pcapFile").files[0];
    const dialog = document.getElementById("loadingDialog");
    const submitButton = document.getElementById("formSubmitButton");
    const errorDialog = document.getElementById("errorDialog");
    const errorP = document.getElementById("errorP");

    // Clear previous content
    document.querySelector(".imageContainer").innerHTML = "";// Clear previous image
    document.querySelector(".mapContainer").innerHTML = ""; // Clear previous map

    // Validation to make sure its only .pcap and .pcapng files
    const fileInput = document.getElementById("pcapFile");
    const allowedExtensions = /\.(pcap|pcapng)$/i;
    if (!file || !allowedExtensions.exec(file.name)) {
        errorP.innerHTML = "Only .pcap and .pcapng files allowed";
        errorDialog.showModal();
        fileInput.value = '';
        return;
    }

    dialog.showModal(); // Show loading dialog
    submitButton.disabled = true; // Disable submit button during submission

    if (file) {
        const formData = new FormData();
        formData.append("ip", ip);
        formData.append("file", file);

        try {
            // Send form data to backend
            const data = await sendFileToBackend(formData);

            console.log(`data from backend = ${JSON.stringify(data)}`);

            // If theres an error, just show an error
            if (data.error) {
                dialog.close();
                errorDialog.showModal();
                errorP.innerHTML = data.error;
            }

            else {
                // Display the geoip2 map
                if (data.map) {
                    displayMap(data.map);
                }

                // Store all the valid graphs
                validGraphs = data.graphObjects || [];

                // Initially display the first graph if graphs are available
                if (validGraphs.length > 0) {
                    currentGraphIndex = 0; 
                    displaySleekGraph(validGraphs[currentGraphIndex]);
                }
            }

        } catch (error) {
            document.getElementById("errorP").innerHTML = error
            errorDialog.showModal();
            console.error('Error sending file to backend:', error);
        }
    }

    dialog.close(); // Close loading dialog
    submitButton.disabled = false; // Enable submit button
}

// Send the file to the backend to process and create the map and graphs
async function sendFileToBackend(formData) {
    try {
        const res = await fetch("http://localhost:5432", { // Change url as needed depending on open port of flask app
            method: "POST",
            body: formData
        });
        const json = await res.json();
        return json; // Parse and return the JSON response
    }
    catch (error) {
        return {"error": error};
    }
}

// Display the geoip2 map
function displayMap(mapBase64) {
    const mapContainer = document.querySelector(".mapContainer");
    const caption = document.createElement("h3");
    caption.text = "Locations of IPs that traffic was sent to"
    const mapElement = document.createElement("iframe");
    mapElement.src = `data:text/html;base64,${mapBase64}`;
    mapElement.width = "100%";
    mapElement.height = "40rem";
    mapContainer.appendChild(caption);
    mapContainer.appendChild(mapElement);
}

// This massive function is to make those really nice graphs.
function displaySleekGraph(images) {

// Getting the chartcontainer ready
// -----------------------------------------------------------------------------------------
    console.log('Rendering graph for valid data:', images);

    // Clear the previous graph, but keep the arrows intact
    d3.select("#graphArea").selectAll("*").remove();

    // Pull up the chart container because it starts off with no display
    d3.select(".chartContainer").style("display", "flex");
    
    // Create the container for the graph within #graphArea
    const chartContainer = d3.select("#graphArea")
        .append("div")
        .attr("class", "graphContainer")
        .style("position", "relative");

    const width = 800;
    const height = 400;
    const margin = { top: 70, right: 70, bottom: 125, left: 100 };

    // This block of code creates an empty SVG element inside the chartContainer, sets its size (width and height), and gives it a dark background color. The SVG will act as the canvas where the graph is rendered.
    const svgContainer = chartContainer.append("svg")
        .attr("width", width)
        .attr("height", height)
        .style("background-color", "#121212");

// -----------------------------------------------------------------------------------------





// BACKGROUND PARTICLE STUFF
// -----------------------------------------------------------------------------------------
    
    // Add ambient particles
    const numParticles = 50; // Number of ambient particles
    const particles = svgContainer.append("g")
        .attr("class", "particles"); // Group for the particles

    // Generate random particle data for the visual effect
    const particleData = d3.range(numParticles).map(() => ({
        x: Math.random() * width, // Random x-position
        y: Math.random() * height, // Random y-position
        r: Math.random() * 2 + 1, // Random size
        dx: (Math.random() - 0.5) * 0.5, // Random horizontal movement speed
        dy: (Math.random() - 0.5) * 0.5  // Random vertical movement speed
    }));

    // Append particles (as circles) to the SVG
    particles.selectAll("circle")
        .data(particleData)
        .enter().append("circle")
        .attr("cx", d => d.x) // Set x-position
        .attr("cy", d => d.y) // Set y-position
        .attr("r", d => d.r) // Set radius
        .attr("fill", "#ffffff") // Set color
        .attr("opacity", 0.1); // Set opacity 

    // Function to animate the particles by updating their positions
    function animateParticles() {
        particles.selectAll("circle")
            .data(particleData)
            .attr("cx", function(d) {
                d.x += d.dx; // Move particle in x-direction
                if (d.x > width) d.x = 0; // Wrap around the width boundary
                if (d.x < 0) d.x = width; // Wrap around the width boundary
                return d.x;
            })
            .attr("cy", function(d) {
                d.y += d.dy; // Move particle in y-direction
                if (d.y > height) d.y = 0; // Wrap around the height boundary
                if (d.y < 0) d.y = height; // Wrap around the height boundary
                return d.y;
            });
        requestAnimationFrame(animateParticles); // Continuously animate the particles
    }

    animateParticles(); // Start the particle animation

// -----------------------------------------------------------------------------------------





// CREATING THE GRAPHS
// -----------------------------------------------------------------------------------------
    // Add the main group element for the graph inside the SVG
    const svg = svgContainer.append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`); // Apply margins for the graph area

    // Check if the x-axis data is numeric
    const xIsNumeric = images.xAxis.every(d => !isNaN(d));

    let xScale, xAxisGenerator;
    // If X is numerical
    if (xIsNumeric) {
        xScale = d3.scaleLinear()
            .domain([d3.min(images.xAxis, d => +d), d3.max(images.xAxis, d => +d)]) // Numeric range for x-axis
            .range([0, width - margin.left - margin.right]);
        xAxisGenerator = d3.axisBottom(xScale)
            .ticks(10) // Number of ticks on the x-axis
            .tickSize(- (height - margin.top - margin.bottom)) // Extend tick lines across the graph
            .tickPadding(10); // Space between tick labels and the axis line

    // If X is categorical
    } else {
        xScale = d3.scalePoint() // Point scale for categorical data
            .domain(images.xAxis)
            .range([0, width - margin.left - margin.right])
            .padding(0.5);
        xAxisGenerator = d3.axisBottom(xScale)
            .tickSize(- (height - margin.top - margin.bottom)) // Extend tick lines across the graph
            .tickPadding(10); // Space between tick labels and the axis line
    }

    // Check if the y-axis data is numeric
    const yIsNumeric = images.yAxis.every(d => !isNaN(d));
    let yScale, yAxisGenerator;

    // If Y is numerical
    if (yIsNumeric) {
        yScale = d3.scaleLinear()
            .domain([0, d3.max(images.yAxis, d => +d)]) // Numeric range for y-axis
            .nice() // Adjust the domain to nice round values
            .range([height - margin.top - margin.bottom, 0]); // Inverted range (higher values at the top)
        yAxisGenerator = d3.axisLeft(yScale)
            .ticks(10) // Set number of ticks on the y-axis
            .tickSize(- (width - margin.left - margin.right))
            .tickPadding(10); // Space between tick labels and the axis line

    // If Y is categorical
    } else {
        yScale = d3.scalePoint() // Point scale for categorical data
            .domain(images.yAxis)
            .range([height - margin.top - margin.bottom, 0])
            .padding(0.5);
        yAxisGenerator = d3.axisLeft(yScale)
            .tickPadding(10); // Space between tick labels and the axis line
    }

    // Prepare the data for the graph by combining x and y data into objects
    const data = images.xAxis.map((xValue, i) => ({
        x: xIsNumeric ? +xValue : xValue,
        y: yIsNumeric ? +images.yAxis[i] : images.yAxis[i]
    }));

    // Create a color gradient if the graph type is line and both x and y data are numeric (NOT CURRENTLY BEING USED SINCE WE ARE DOING JUST SCATTER PLOTS)
    const gradientId = `gradient-${Math.random().toString(36).substr(2, 9)}`;
    const color = images.color || "#00ffc8"; 
    if (images.type === 'line' && xIsNumeric && yIsNumeric) {
        const defs = svg.append("defs");
        const gradient = defs.append("linearGradient")
            .attr("id", gradientId)
            .attr("x1", "0%")
            .attr("y1", "0%")
            .attr("x2", "100%")
            .attr("y2", "0%");

        gradient.append("stop")
            .attr("offset", "0%")
            .attr("stop-color", "#00f5ff") // Start color
            .attr("stop-opacity", 1);

        gradient.append("stop")
            .attr("offset", "100%")
            .attr("stop-color", "#ff00d4") // End color
            .attr("stop-opacity", 1);
    }

    // Draw the line or scatter plot based on the data type
    if (images.type === 'scatter' || images.type === 'line') {

        // For line plots (with numeric x and y data) (NOT CURRENTLY BEING USED SINCE WE ARE DOING JUST SCATTER PLOTS)
        if (images.type === 'line' && xIsNumeric && yIsNumeric) {
            const line = d3.line()
                .x(d => xScale(d.x)) // Map x-data to x-scale
                .y(d => yScale(d.y)) // Map y-data to y-scale
                .curve(d3.curveMonotoneX); // Smooth line

            svg.append("path")
                .datum(data)
                .attr("class", "line")
                .attr("d", line) // Draw the line path
                .attr("fill", "none")
                .attr("stroke", `url(#${gradientId})`) // Use gradient for line stroke
                .attr("stroke-width", 3)
                .attr("stroke-linejoin", "round")
                .attr("stroke-linecap", "round")
                .style("filter", "url(#glow)") // Apply a glow effect
                .transition()
                .duration(2000)
                .ease(d3.easeCubicInOut) // Animate the line drawing
                .attrTween("stroke-dasharray", function() {
                    const length = this.getTotalLength();
                    return function(t) { return `${t * length},${length}`; };
                });
        }

        // Add data points with animations for both line and scatter plots
        svg.selectAll("circle")
            .data(data)
            .enter().append("circle")
            .attr("class", "data-point")
            .attr("cx", d => xScale(d.x)) // Set x position
            .attr("cy", d => yScale(d.y)) // Set y position
            .attr("r", 0) // Initially set radius to 0 (for animation)
            .attr("fill", color) // Set fill color for points
            .style("filter", "url(#glow)") // Apply glow effect
            .transition()
            .delay((d, i) => i * 50) // Stagger the animation
            .duration(500) // Duration of the animation
            .attr("r", 6); // Final radius
    }

    // Add x-axis to the graph
    const xAxis = svg.append("g")
        .attr("transform", `translate(0,${height - margin.top - margin.bottom})`)
        .call(xAxisGenerator)
        .attr("class", "x-axis");

    // Rotate x-axis labels if x data is categorical to try to fit in the categories
    if (!xIsNumeric) {
        xAxis.selectAll("text")
            .attr("transform", "rotate(-45)") // Rotate the labels
            .style("text-anchor", "end")
            .attr("dx", "-0.8em")
            .attr("dy", "0.15em");
    }

    // Add y-axis to the graph
    svg.append("g")
        .call(yAxisGenerator)
        .attr("class", "y-axis");

    // Style the x and y axis labels for better readability
    svg.selectAll('.x-axis text').style('fill', '#cccccc'); // Light grey for x-axis text
    svg.selectAll('.y-axis text').style('fill', '#cccccc'); // Light grey for y-axis text
    svg.selectAll('.x-axis line').style('stroke', '#444444'); // Grey gridlines for x-axis
    svg.selectAll('.y-axis line').style('stroke', '#444444'); // Grey gridlines for y-axis

    // Add a label for the x-axis title
    svg.append("text")
        .attr("transform", `translate(${(width - margin.left - margin.right)/2},${height - margin.top - margin.bottom + 75})`)
        .style("text-anchor", "middle")
        .style("font-size", "14px")
        .style("fill", "#ffffff")
        .style("font-family", "'Orbitron', sans-serif")
        .text(images.xTitle || "X Axis"); // Use provided x-title or default "X Axis"

    // Add a label for the y-axis title
    svg.append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", -50)
        .attr("x", - (height - margin.top - margin.bottom)/2)
        .attr("dy", "-1.5em")
        .style("text-anchor", "middle")
        .style("font-size", "14px")
        .style("fill", "#ffffff")
        .style("font-family", "'Orbitron', sans-serif")
        .text(images.yTitle || "Y Axis"); // Use provided y-title or default "Y Axis"

    // Add a main title to the chart
    svg.append("text")
        .attr("x", (width - margin.left - margin.right)/2)
        .attr("y", -30)
        .style("text-anchor", "middle")
        .style("font-size", "20px")
        .style("font-weight", "bold")
        .style("fill", "#ffffff")
        .style("font-family", "'Orbitron', sans-serif")
        .text(images.title || "Chart Title"); // Use provided title or default "Chart Title"

    // Add a glow filter definition (for the neon/glow effect on lines and circles)
    const defs = svg.append("defs");
    const filter = defs.append("filter")
        .attr("id", "glow");
    filter.append("feGaussianBlur")
        .attr("stdDeviation", "3.5") // Blur effect
        .attr("result", "coloredBlur");
    const feMerge = filter.append("feMerge");
    feMerge.append("feMergeNode").attr("in", "coloredBlur");
    feMerge.append("feMergeNode").attr("in", "SourceGraphic"); // Combine the blur with the original graphics

// -----------------------------------------------------------------------------------------





// TOOLTIP STUFF FROM HERE DOWN WHENEVER THE POINT IS HOVERED OVER
// -----------------------------------------------------------------------------------------

    // Creating tooltip and tooltip starts as hidden
    let tooltip = chartContainer.select(".tooltip");
    if (tooltip.empty()) {
        tooltip = chartContainer.append("div")
            .attr("class", "tooltip")
            .style("position", "absolute")
            .style("opacity", 0); 
    }

    // When hovering over a data point thi happens
    svg.selectAll(".data-point")
        .on("mouseover", function (event, d) {
            // Format X and Y values for the tooltip
            let xValue = d.x;
            let yValue = d.y;
            if (xIsNumeric && typeof xValue === 'number') {
                xValue = xValue.toFixed(2); // Format as number with 2 decimal places
            }
            if (yIsNumeric && typeof yValue === 'number') {
                yValue = yValue.toFixed(2); // Format as number with 2 decimal places
            }

            // Show tooltip with x and y values
            tooltip.html(`<strong>X:</strong> ${xValue}<br><strong>Y:</strong> ${yValue}`)
                .style("opacity", 1); // Show the tooltip

            // Highlight the hovered point
            d3.select(this)
                .transition()
                .duration(200)
                .attr("r", 9) // Increase the hovered point on hover
                .attr("fill", "#ff00d4"); // Change color of the hovered point on hover
        })

        // Move the tooltip with the mouse cursor
        .on("mousemove", function(event) {
            const [x, y] = d3.pointer(event, chartContainer.node());
            tooltip.style("left", `${x + 10}px`)
                   .style("top", `${y - 40}px`);
        })

        // Hide the tooltip and reset the point to a regular non-hovered point
        .on("mouseout", function () {
            tooltip.style("opacity", 0);
            d3.select(this)
                .transition()
                .duration(200)
                .attr("r", 6)
                .attr("fill", color);
        });

    // -----------------------------------------------------------------------------------------
}
// Massive display graphs function is done finally...