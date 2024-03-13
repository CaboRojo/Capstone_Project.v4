import React, { useEffect, useState } from 'react';
import axios from 'axios';
import LineGraph from '../dashboard/Default/LineGraph'; // Adjust import path as necessary

const StockLine = ({ userId, symbol }) => {
    const [performanceData, setPerformanceData] = useState(null);

    useEffect(() => {
        const fetchPerformanceData = async () => {
            try {
                const response = await axios.get(`/api/user/${userId}/portfolio/stock/${encodeURIComponent(symbol)}/performance`);
                if (response.status === 200) {
                    setPerformanceData(response.data.historicalPrices);
                } else {
                    console.error('Failed to fetch performance data');
                }
            } catch (error) {
                console.error('Error fetching performance data:', error);
            }
        };

        fetchPerformanceData();
    }, [userId, symbol]);

    return (
        <div>
            {/* Other asset details components */}
            {performanceData && <LineGraph data={performanceData} />}
        </div>
    );
};

export default StockLine;
