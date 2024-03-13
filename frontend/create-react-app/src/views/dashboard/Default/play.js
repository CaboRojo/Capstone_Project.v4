import React, { useEffect, useState } from 'react';
import Chart from 'react-apexcharts';
import axios from 'axios';

const LineGraph = ({ userId }) => {
  const [series, setSeries] = useState([]);
  const [error, setError] = useState(null);
  const [isLoading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStockData = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`/api/user/${userId}/portfolio/stocks`);
        if (response.data && Array.isArray(response.data)) {
          const transformedSeries = response.data.map(stock => ({
            name: stock.symbol,
            data: stock.data.map(point => [new Date(point.date).getTime(), point.price]),
          }));
          setSeries(transformedSeries);
          setError(null);
        } else {
          throw new Error('Unexpected response structure');
        }
      } catch (error) {
        console.error('Failed to fetch stock data:', error);
        setError("Data failed to load, please try refreshing the page.");
      } finally {
        setLoading(false);
      }
    };

    fetchStockData();
  }, [userId]);

  const options = {
    chart: {
      id: 'stocks-performance',
      type: 'line',
      height: 350,
      toolbar: {
        show: true,
      },
      animations: {
        enabled: true,
      },
    },
    stroke: {
      curve: 'smooth',
      width: 2,
    },
    markers: {
      size: 0,
    },
    colors: ['#007bff', '#ff4560', '#00e396', '#feb019', '#775dd0'],
    fill: {
      type: 'solid',
      opacity: 0.3,
    },
    xaxis: {
      type: 'datetime',
    },
    tooltip: {
      theme: 'dark',
      x: {
        format: 'dd MMM yyyy',
      },
    },
    yaxis: {
      labels: {
        formatter: function (value) {
          return "$" + value.toFixed(2);
        },
      },
    },
    legend: {
      position: 'top',
      horizontalAlign: 'right',
      floating: true,
      offsetY: -25,
      offsetX: -5,
    },
    noData: {
      text: error || (isLoading ? 'Loading...' : 'No data available'),
      align: 'center',
      verticalAlign: 'middle',
      offsetX: 0,
      offsetY: 0,
      style: {
        color: "#ffffff",
        fontSize: '16px',
        fontFamily: undefined
      }
    },
    loading: {
      enabled: isLoading,
      text: 'Loading...',
    },
  };