<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Live Calls</title>
    <style>
        /* General Styles */
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f0f0f0;
        }
        h1 {
            text-align: center;
            color: #333;
            margin-top: 60px; /* Add margin to ensure space below the banner */
        }
        /* Table Styles */
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            background-color: #fff;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        th, td {
            border: 1px solid #ddd;
            padding: 10px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        /* Counters and Notifications */
        .counter {
            font-size: 18px;
            margin-bottom: 10px;
            text-align: center;
        }
        .counter span {
            font-weight: bold;
            color: #007bff;
        }
        /* Notification Button */
        #playSoundBtn {
            display: block;
            margin: 0 auto;
            padding: 10px 20px;
            font-size: 16px;
            background-color: #007bff;
            color: #fff;
            border: none;
            cursor: pointer;
            outline: none;
            border-radius: 4px;
            transition: background-color 0.3s;
        }
        #playSoundBtn:hover {
            background-color: #0056b3;
        }
        /* Date Filter */
        .date-filter {
            text-align: center;
            margin-bottom: 20px;
        }
        .date-filter input {
            padding: 5px;
            margin: 5px;
        }
        .date-filter button {
            padding: 5px 10px;
            font-size: 16px;
            background-color: #007bff;
            color: #fff;
            border: none;
            cursor: pointer;
            outline: none;
            border-radius: 4px;
        }
        .date-filter button:hover {
            background-color: #0056b3;
        }
        /* Money Effect */
        @keyframes money-effect {
            0% { color: #007bff; transform: scale(1); }
            50% { color: #28a745; transform: scale(1.5); }
            100% { color: #007bff; transform: scale(1); }
        }
        .money-effect {
            animation: money-effect 1.5s ease-in-out;
        }
        /* Dropdown Banner */
        @keyframes dropdown {
            0% { top: -50px; opacity: 0; }
            100% { top: 0; opacity: 1; }
        }
        .dropdown-banner {
            position: fixed;
            top: -50px;
            left: 0;
            right: 0;
            background-color: #46c35f;
            color: white;
            text-align: center;
            padding: 10px 0;
            font-size: 18px;
            display: none;
            z-index: 1000;
            animation: dropdown 0.5s forwards;
        }
    </style>
</head>
<body>
    <br>
    <h1>Live Calls</h1>
    <div class="counter">
        Current Calls: <span id="currentResponsesCount">0</span><br>
        Total Calls: <span id="totalResponsesCount">0</span><br>
        Total Cost: $<span id="totalCost">0</span>
    </div>
    <div class="date-filter">
        Start Date: <input type="date" id="startDate">
        End Date: <input type="date" id="endDate">
        <button id="filterBtn" onclick="fetchCDRCost()">Filter</button>
    </div>
    <div class="dropdown-banner" id="dropdownBanner"></div>
    <table id="callsTable">
        <thead>
            <tr>
                <th>Range</th>
                <th>A Number</th>
                <th>B Number</th>
                <th>Call Key</th>
                <th>Duration</th>
                <th>A Subdestination Name</th>
                <th>B Subdestination Name</th>
            </tr>
        </thead>
        <tbody>
            <!-- Data will be inserted here -->
        </tbody>
    </table>
    <audio id="notificationSound" src="{{ url_for('static', filename='notification.mp3') }}" preload="auto"></audio>
    <audio id="updateNotificationSound" src="{{ url_for('static', filename='notification1.mp3') }}" preload="auto"></audio>
    <script>
        let previousDataKeys = new Set();
        let totalResponsesCount = 0;
        let lastTotalCost = 0;

        async function fetchLiveCalls() {
            try {
                const response = await fetch('/live_calls');
                const data = await response.json();
                const newCalls = data.filter(call => !previousDataKeys.has(call.call_key));

                const tableBody = document.getElementById('callsTable').getElementsByTagName('tbody')[0];
                tableBody.innerHTML = ''; // Clear previous data

                data.forEach(call => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${call.range}</td>
                        <td>${call.a_number}</td>
                        <td>${call.b_number}</td>
                        <td>${call.call_key}</td>
                        <td>${call.duration}</td>
                        <td>${call.a_subdestination_name}</td>
                        <td>${call.b_subdestination_name}</td>
                    `;
                    tableBody.appendChild(row);
                    previousDataKeys.add(call.call_key);
                });

                // Update the counters
                document.getElementById('currentResponsesCount').textContent = data.length;
                totalResponsesCount += newCalls.length;
                document.getElementById('totalResponsesCount').textContent = totalResponsesCount;

                if (newCalls.length > 0) {
                    playNotificationSound();
                }
            } catch (error) {
                console.error('Error fetching live calls:', error);
            }
        }

        async function fetchCDRCost() {
            const startDate = document.getElementById('startDate').value;
            const endDate = document.getElementById('endDate').value;
            if (!startDate || !endDate) {
                alert('Please select both start and end dates.');
                return;
            }
            const filterData = {
                "a_number": "",
                "end_date": endDate + "T23:59:59.000Z",
                "start_date": startDate + "T00:00:00.000Z"
            };
            try {
                const response = await fetch('/cdr_cost', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(filterData)
                });
                const data = await response.json();
                if (data.error) {
                    alert(data.error);
                } else {
                    const totalCostElement = document.getElementById('totalCost');
                    const newTotalCost = parseFloat(data.cost);
                    if (newTotalCost !== lastTotalCost) {
                        const difference = newTotalCost - lastTotalCost;
                        lastTotalCost = newTotalCost;
                        totalCostElement.textContent = data.cost;
                        totalCostElement.classList.add('money-effect');
                        setTimeout(() => {
                            totalCostElement.classList.remove('money-effect');
                        }, 1500);
                        showDropdownBanner(`Balance Added! $${difference.toFixed(2)}`);
                        playUpdateNotificationSound();
                    }
                }
            } catch (error) {
                console.error('Error fetching CDR cost:', error);
            }
        }

        function showDropdownBanner(message) {
            const banner = document.getElementById('dropdownBanner');
            banner.textContent = message;
            banner.style.display = 'block';
            setTimeout(() => {
                banner.style.display = 'none';
            }, 6000);
        }

        function playNotificationSound() {
            const sound = document.getElementById('notificationSound');
            sound.play().then(() => {
                console.log('Notification sound played for new calls');
            }).catch(error => {
                console.error('Error playing notification sound for new calls:', error);
            });
        }

        function playUpdateNotificationSound() {
            const sound = document.getElementById('updateNotificationSound');
            sound.play().then(() => {
                console.log('Update notification sound played for total cost change');
            }).catch(error => {
                console.error('Error playing update notification sound for total cost change:', error);
            });
        }

        // Fetch data every 5 seconds
        setInterval(() => {
            fetchLiveCalls();
        }, 500);

        // Click the filter button every 1 minute to refresh the total cost
        setInterval(() => {
            document.getElementById('filterBtn').click();
        }, 15000);

        // Initial fetch
        fetchLiveCalls();
    </script>
</body>
</html>