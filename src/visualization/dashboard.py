<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Supply Chain Reconstruction Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
            border: 1px solid rgba(255, 255, 255, 0.18);
        }
        
        .header h1 {
            color: #2c3e50;
            font-size: 2.5em;
            font-weight: 700;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #3498db, #9b59b6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .header p {
            color: #7f8c8d;
            font-size: 1.1em;
        }
        
        .controls {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
        }
        
        .controls h3 {
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.3em;
        }
        
        .input-group {
            display: flex;
            gap: 20px;
            align-items: center;
            flex-wrap: wrap;
        }
        
        .input-group label {
            font-weight: 600;
            color: #34495e;
        }
        
        .input-group select,
        .input-group input {
            padding: 12px 16px;
            border: 2px solid #e1e8ed;
            border-radius: 8px;
            font-size: 1em;
            transition: all 0.3s ease;
        }
        
        .input-group select:focus,
        .input-group input:focus {
            outline: none;
            border-color: #3498db;
            box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2);
        }
        
        .btn {
            background: linear-gradient(45deg, #3498db, #2980b9);
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(52, 152, 219, 0.3);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin-bottom: 30px;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
            border: 1px solid rgba(255, 255, 255, 0.18);
            transition: transform 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
        }
        
        .card h3 {
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.3em;
            border-bottom: 2px solid #e1e8ed;
            padding-bottom: 10px;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding: 12px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        
        .metric-label {
            font-weight: 600;
            color: #34495e;
        }
        
        .metric-value {
            font-weight: 700;
            font-size: 1.2em;
            color: #3498db;
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-operational { background-color: #27ae60; }
        .status-warning { background-color: #f39c12; }
        .status-error { background-color: #e74c3c; }
        
        .journey-step {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
            padding: 15px;
            background: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 8px;
            border-left: 4px solid #3498db;
            transition: all 0.3s ease;
        }
        
        .journey-step:hover {
            transform: translateX(5px);
            box-shadow: 0 4px 15px rgba(52, 152, 219, 0.2);
        }
        
        .step-icon {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: linear-gradient(45deg, #3498db, #2980b9);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            margin-right: 15px;
        }
        
        .step-content {
            flex: 1;
        }
        
        .step-title {
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 5px;
        }
        
        .step-details {
            color: #7f8c8d;
            font-size: 0.9em;
        }
        
        .chart-container {
            position: relative;
            height: 300px;
            margin-top: 20px;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 40px;
            color: #7f8c8d;
            font-style: italic;
        }
        
        .loading.show {
            display: block;
        }
        
        .full-width {
            grid-column: 1 / -1;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .pulsing {
            animation: pulse 2s infinite;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏭 Supply Chain Reconstruction Dashboard</h1>
            <p>Real-time monitoring and control of end-to-end material flow from raw extraction to customer delivery</p>
        </div>
        
        <div class="controls">
            <h3>⚙️ Simulation Controls</h3>
            <div class="input-group">
                <label for="oreType">Ore Type:</label>
                <select id="oreType">
                    <option value="Phosphorite Ore">Phosphorite Ore</option>
                    <option value="Iron Ore">Iron Ore</option>
                </select>
                
                <label for="quantity">Quantity (tons):</label>
                <input type="number" id="quantity" value="1000" min="100" max="50000" step="100">
                
                <button class="btn" onclick="startSimulation()">🚀 Start Simulation</button>
                <button class="btn" onclick="loadClientData()" style="background: linear-gradient(45deg, #27ae60, #219a52);">📊 Load Client Data</button>
            </div>
        </div>
        
        <div class="dashboard-grid">
            <div class="card">
                <h3>📊 System Overview</h3>
                <div class="metric">
                    <span class="metric-label">Status</span>
                    <span class="metric-value">
                        <span class="status-indicator status-operational"></span>
                        Operational
                    </span>
                </div>
                <div class="metric">
                    <span class="metric-label">Active Traces</span>
                    <span class="metric-value" id="activeTraces">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Total Agents</span>
                    <span class="metric-value">5</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Pending Requests</span>
                    <span class="metric-value" id="pendingRequests">0</span>
                </div>
            </div>
            
            <div class="card">
                <h3>⛏️ Mining Operations</h3>
                <div class="metric">
                    <span class="metric-label">Extraction Rate</span>
                    <span class="metric-value" id="extractionRate">2,000 tons/hr</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Total Extracted</span>
                    <span class="metric-value" id="totalExtracted">0 tons</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Equipment Efficiency</span>
                    <span class="metric-value" id="equipmentEfficiency">95%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Ore Quality</span>
                    <span class="metric-value" id="oreQuality">85%</span>
                </div>
            </div>
            
            <div class="card">
                <h3>⚗️ Processing Status</h3>
                <div class="metric">
                    <span class="metric-label">Active Jobs</span>
                    <span class="metric-value" id="processingJobs">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Processing Efficiency</span>
                    <span class="metric-value" id="processingEfficiency">82%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Output Quality</span>
                    <span class="metric-value" id="processingQuality">87%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Energy Cost</span>
                    <span class="metric-value" id="energyCost">$0</span>
                </div>
            </div>
            
            <div class="card">
                <h3>🏭 Manufacturing</h3>
                <div class="metric">
                    <span class="metric-label">Production Lines</span>
                    <span class="metric-value" id="productionLines">3</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Units Produced</span>
                    <span class="metric-value" id="unitsProduced">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Quality Control</span>
                    <span class="metric-value" id="qualityControl">95%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Production Cost</span>
                    <span class="metric-value" id="productionCost">$0</span>
                </div>
            </div>
            
            <div class="card">
                <h3>📦 Distribution</h3>
                <div class="metric">
                    <span class="metric-label">Warehouse Utilization</span>
                    <span class="metric-value" id="warehouseUtil">0%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Active Shipments</span>
                    <span class="metric-value" id="activeShipments">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Shipping Accuracy</span>
                    <span class="metric-value" id="shippingAccuracy">98%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Export Zones</span>
                    <span class="metric-value" id="exportZones">5</span>
                </div>
            </div>
            
            <div class="card">
                <h3>🛒 Retail Sales</h3>
                <div class="metric">
                    <span class="metric-label">Total Revenue</span>
                    <span class="metric-value" id="totalRevenue">$0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Units Sold</span>
                    <span class="metric-value" id="unitsSold">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Customer Satisfaction</span>
                    <span class="metric-value" id="customerSat">4.2/5.0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Sales Channels</span>
                    <span class="metric-value" id="salesChannels">3</span>
                </div>
            </div>
        </div>
        
        <div class="dashboard-grid">
            <div class="card full-width">
                <h3>🔍 Material Journey Tracking</h3>
                <div id="materialJourney">
                    <div class="loading show">
                        <p>No active material traces. Start a simulation to begin tracking.</p>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="dashboard-grid">
            <div class="card">
                <h3>📈 Production Flow Chart</h3>
                <div class="chart-container">
                    <canvas id="flowChart"></canvas>
                </div>
            </div>
            
            <div class="card">
                <h3>💰 Cost Breakdown</h3>
                <div class="chart-container">
                    <canvas id="costChart"></canvas>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Global variables
        let currentTraceId = null;
        let simulationActive = false;
        let flowChart = null;
        let costChart = null;

        // Initialize charts
        function initializeCharts() {
            // Production Flow Chart
            const flowCtx = document.getElementById('flowChart').getContext('2d');
            flowChart = new Chart(flowCtx, {
                type: 'line',
                data: {
                    labels: ['Mining', 'Processing', 'Manufacturing', 'Distribution', 'Retail'],
                    datasets: [{
                        label: 'Material Quantity (tons)',
                        data: [0, 0, 0, 0, 0],
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(0,0,0,0.1)'
                            }
                        },
                        x: {
                            grid: {
                                color: 'rgba(0,0,0,0.1)'
                            }
                        }
                    }
                }
            });

            // Cost Breakdown Chart
            const costCtx = document.getElementById('costChart').getContext('2d');
            costChart = new Chart(costCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Mining', 'Processing', 'Manufacturing', 'Distribution', 'Retail'],
                    datasets: [{
                        data: [20, 30, 25, 15, 10],
                        backgroundColor: [
                            '#e74c3c',
                            '#f39c12',
                            '#3498db',
                            '#27ae60',
                            '#9b59b6'
                        ],
                        borderWidth: 2,
                        borderColor: '#fff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }

        // Simulate starting a supply chain simulation
        async function startSimulation() {
            const oreType = document.getElementById('oreType').value;
            const quantity = parseInt(document.getElementById('quantity').value);

            // Update UI to show simulation starting
            simulationActive = true;
            document.getElementById('activeTraces').textContent = '1';
            document.getElementById('pendingRequests').textContent = '4';

            // Show material journey
            showMaterialJourney(oreType, quantity);

            // Simulate data updates
            await simulateDataFlow(quantity);
        }

        // Simulate material journey
        function showMaterialJourney(oreType, quantity) {
            const journeyContainer = document.getElementById('materialJourney');
            const traceId = 'TRACE_' + Math.random().toString(36).substr(2, 9);
            currentTraceId = traceId;

            journeyContainer.innerHTML = `
                <div style="margin-bottom: 20px;">
                    <strong>Trace ID:</strong> ${traceId} | 
                    <strong>Material:</strong> ${oreType} | 
                    <strong>Quantity:</strong> ${quantity} tons
                </div>
            `;

            const stages = [
                { icon: '⛏️', title: 'Mining Extraction', details: `Extracted ${quantity} tons of ${oreType}`, stage: 'mining' },
                { icon: '⚗️', title: 'Processing', details: 'Converting ore to processed materials', stage: 'processing' },
                { icon: '🏭', title: 'Manufacturing', details: 'Producing finished goods', stage: 'manufacturing' },
                { icon: '📦', title: 'Distribution', details: 'Warehousing and export preparation', stage: 'distribution' },
                { icon: '🛒', title: 'Retail Sales', details: 'Customer delivery and sales', stage: 'retail' }
            ];

            stages.forEach((stage, index) => {
                setTimeout(() => {
                    const stepElement = document.createElement('div');
                    stepElement.className = 'journey-step';
                    stepElement.innerHTML = `
                        <div class="step-icon">${stage.icon}</div>
                        <div class="step-content">
                            <div class="step-title">${stage.title}</div>
                            <div class="step-details">${stage.details}</div>
                        </div>
                    `;
                    journeyContainer.appendChild(stepElement);

                    // Add pulsing effect to current stage
                    stepElement.classList.add('pulsing');
                    setTimeout(() => stepElement.classList.remove('pulsing'), 2000);

                }, index * 2000);
            });
        }

        // Simulate data flow through the system
        async function simulateDataFlow(initialQuantity) {
            const stages = [
                { name: 'Mining', efficiency: 1.0 },
                { name: 'Processing', efficiency: 0.82 },
                { name: 'Manufacturing', efficiency: 0.94 },
                { name: 'Distribution', efficiency: 0.98 },
                { name: 'Retail', efficiency: 0.90 }
            ];

            let currentQuantity = initialQuantity;
            const flowData = [];
            let totalCosts = 0;

            for (let i = 0; i < stages.length; i++) {
                await new Promise(resolve => setTimeout(resolve, 2000));

                currentQuantity *= stages[i].efficiency;
                flowData.push(currentQuantity);

                // Update flow chart
                flowChart.data.datasets[0].data = [...flowData, ...new Array(5 - flowData.length).fill(0)];
                flowChart.update();

                // Update stage-specific metrics
                updateStageMetrics(stages[i].name.toLowerCase(), currentQuantity, i);

                // Simulate costs
                const stageCost = currentQuantity * (10 + Math.random() * 20);
                totalCosts += stageCost;
            }

            // Final updates
            document.getElementById('pendingRequests').textContent = '0';
            document.getElementById('totalRevenue').textContent = `$${(totalCosts * 1.3).toLocaleString()}`;
        }

        // Update stage-specific metrics
        function updateStageMetrics(stage, quantity, stageIndex) {
            switch(stage) {
                case 'mining':
                    document.getElementById('totalExtracted').textContent = `${quantity.toFixed(0)} tons`;
                    break;
                case 'processing':
                    document.getElementById('processingJobs').textContent = '1';
                    document.getElementById('energyCost').textContent = `$${(quantity * 45).toLocaleString()}`;
                    break;
                case 'manufacturing':
                    document.getElementById('unitsProduced').textContent = quantity.toFixed(0);
                    document.getElementById('productionCost').textContent = `$${(quantity * 22).toLocaleString()}`;
                    break;
                case 'distribution':
                    document.getElementById('warehouseUtil').textContent = `${Math.min(quantity / 1000 * 100, 100).toFixed(1)}%`;
                    document.getElementById('activeShipments').textContent = '1';
                    break;
                case 'retail':
                    document.getElementById('unitsSold').textContent = quantity.toFixed(0);
                    break;
            }
        }

        // Load client data simulation
        function loadClientData() {
            alert('📊 Client Data Loader\n\nThis would load your Excel file and configure the system based on historical data.\n\nFeatures:\n• Auto-configure agent capacities\n• Set production targets\n• Map export destinations\n• Generate data-driven scenarios');
        }

        // Real-time updates simulation
        function startRealTimeUpdates() {
            setInterval(() => {
                if (simulationActive) {
                    // Simulate minor fluctuations in efficiency
                    const currentEfficiency = document.getElementById('equipmentEfficiency').textContent;
                    const newEfficiency = (95 + Math.random() * 4).toFixed(1);
                    document.getElementById('equipmentEfficiency').textContent = newEfficiency + '%';
                    
                    // Update processing efficiency
                    const newProcessingEff = (80 + Math.random() * 10).toFixed(1);
                    document.getElementById('processingEfficiency').textContent = newProcessingEff + '%';
                }
            }, 5000);
        }

        // Export simulation results
        function exportResults() {
            if (!currentTraceId) {
                alert('No simulation data to export. Please run a simulation first.');
                return;
            }

            const results = {
                traceId: currentTraceId,
                timestamp: new Date().toISOString(),
                metrics: {
                    totalExtracted: document.getElementById('totalExtracted').textContent,
                    totalRevenue: document.getElementById('totalRevenue').textContent,
                    efficiency: document.getElementById('equipmentEfficiency').textContent,
                    customerSatisfaction: document.getElementById('customerSat').textContent
                }
            };

            const dataStr = JSON.stringify(results, null, 2);
            const dataBlob = new Blob([dataStr], {type: 'application/json'});
            const url = URL.createObjectURL(dataBlob);
            
            const link = document.createElement('a');
            link.href = url;
            link.download = `supply_chain_results_${currentTraceId}.json`;
            link.click();
        }

        // Add export button functionality
        function addExportButton() {
            const controlsDiv = document.querySelector('.controls .input-group');
            const exportBtn = document.createElement('button');
            exportBtn.className = 'btn';
            exportBtn.style.background = 'linear-gradient(45deg, #e67e22, #d35400)';
            exportBtn.innerHTML = '📁 Export Results';
            exportBtn.onclick = exportResults;
            controlsDiv.appendChild(exportBtn);
        }

        // WebSocket simulation for real-time data
        function simulateWebSocketUpdates() {
            // Simulate receiving real-time updates from Python backend
            const updateTypes = ['mining', 'processing', 'manufacturing', 'distribution', 'retail'];
            
            setInterval(() => {
                if (simulationActive) {
                    const randomUpdate = updateTypes[Math.floor(Math.random() * updateTypes.length)];
                    
                    // Simulate operator request completion
                    const currentPending = parseInt(document.getElementById('pendingRequests').textContent);
                    if (currentPending > 0 && Math.random() < 0.3) {
                        document.getElementById('pendingRequests').textContent = Math.max(0, currentPending - 1);
                    }
                }
            }, 3000);
        }

        // Enhanced material tracking with progress bars
        function addProgressBars() {
            const style = document.createElement('style');
            style.textContent = `
                .progress-bar {
                    width: 100%;
                    height: 8px;
                    background-color: #e1e8ed;
                    border-radius: 4px;
                    overflow: hidden;
                    margin-top: 8px;
                }
                
                .progress-fill {
                    height: 100%;
                    background: linear-gradient(90deg, #3498db, #2980b9);
                    width: 0%;
                    transition: width 0.5s ease;
                }
                
                .stage-progress {
                    margin-bottom: 15px;
                    padding: 15px;
                    background: #f8f9fa;
                    border-radius: 8px;
                    border-left: 4px solid #3498db;
                }
                
                .stage-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 8px;
                }
                
                .stage-name {
                    font-weight: 600;
                    color: #2c3e50;
                }
                
                .stage-percentage {
                    color: #3498db;
                    font-weight: 600;
                }
            `;
            document.head.appendChild(style);
        }

        // Initialize dashboard with all features
        document.addEventListener('DOMContentLoaded', function() {
            initializeCharts();
            addExportButton();
            addProgressBars();
            startRealTimeUpdates();
            simulateWebSocketUpdates();
            
            // Simulate some initial baseline data
            setTimeout(() => {
                // Show baseline production capacity
                flowChart.data.datasets[0].data = [0, 0, 0, 0, 0];
                flowChart.update();
                
                // Update cost chart with realistic percentages
                costChart.data.datasets[0].data = [15, 25, 30, 20, 10];
                costChart.update();
            }, 1000);
            
            console.log('🏭 Supply Chain Dashboard initialized successfully');
            console.log('💡 Ready to track materials from mining to customer delivery');
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case 's':
                        e.preventDefault();
                        startSimulation();
                        break;
                    case 'e':
                        e.preventDefault();
                        exportResults();
                        break;
                    case 'l':
                        e.preventDefault();
                        loadClientData();
                        break;
                }
            }
        });

        // Add tooltips for better UX
        function addTooltips() {
            const tooltipStyle = `
                .tooltip {
                    position: relative;
                    cursor: help;
                }
                
                .tooltip::after {
                    content: attr(data-tooltip);
                    position: absolute;
                    bottom: 125%;
                    left: 50%;
                    transform: translateX(-50%);
                    background: #2c3e50;
                    color: white;
                    padding: 8px 12px;
                    border-radius: 6px;
                    font-size: 0.8em;
                    white-space: nowrap;
                    opacity: 0;
                    pointer-events: none;
                    transition: opacity 0.3s;
                    z-index: 1000;
                }
                
                .tooltip:hover::after {
                    opacity: 1;
                }
            `;
            
            const style = document.createElement('style');
            style.textContent = tooltipStyle;
            document.head.appendChild(style);

            // Add tooltips to key elements
            document.getElementById('activeTraces').closest('.metric').classList.add('tooltip');
            document.getElementById('activeTraces').closest('.metric').setAttribute('data-tooltip', 'Number of material batches currently being tracked through the system');
            
            document.getElementById('pendingRequests').closest('.metric').classList.add('tooltip');
            document.getElementById('pendingRequests').closest('.metric').setAttribute('data-tooltip', 'Operator input requests waiting to be processed');
        }

        // Call addTooltips after DOM is loaded
        document.addEventListener('DOMContentLoaded', function() {
            addTooltips();
        });
    </script>
</body>
</html>