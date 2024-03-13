import React, { useEffect, useState } from 'react';
import axios from 'axios';
import ReactApexChart from 'react-apexcharts';

const LineGraph = ({ isLoading }) => { // Removed setLoading from props
  const [series, setSeries] = useState([]);
  const [error, setError] = useState(null);

  // Retrieve 'userId' from localStorage, assuming this is your method of user management
  const userId = localStorage.getItem('userId');

  const fetchStockData = async () => {
    if (!userId) {
      setError("User ID not found");
      return; // No need to set loading state here
    }

    try {
      // setLoading(true); removed to avoid using an undefined function.
      const response = await axios.get(`/api/user/${userId}/portfolio/stocks`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`, // Assuming token is stored in localStorage
        },
      });
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
      // setLoading(false); removed as we're no longer managing loading state here.
    }
  };

  useEffect(() => {
    if (!isLoading) { // If not already loading, proceed to fetch data.
      fetchStockData();
    }
  }, [isLoading]); // Removed setLoading from the dependency array

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
      text: error || 'No data available',
      align: 'center',
      verticalAlign: 'middle',
      offsetX: 0,
      offsetY: 0,
      style: {
        color: "#ffffff",
        fontSize: '16px',
        fontFamily: undefined
      }
    }
  };

  return (
    <div id="chart">
      {error ? (
        <div role="alert" style={{ color: 'red', textAlign: 'center', paddingTop: '20px' }}>
          {error}
        </div>
      ) : (
        <ReactApexChart options={options} series={series} type="line" height={350} />
      )}
    </div>
  );
};

export default LineGraph;
