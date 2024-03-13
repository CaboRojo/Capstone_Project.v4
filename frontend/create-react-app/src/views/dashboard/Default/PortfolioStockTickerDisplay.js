import React, { useEffect, useState } from 'react';
import { Card, CardContent, Grid, Link, Typography } from '@mui/material';
import axios from 'axios';
import { gridSpacing } from 'store/constant';

const PortfolioStockTickerDisplay = ({ isLoading }) => {
  const [stockData, setStockData] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchStockData = async () => {
      setError('');
      const userId = localStorage.getItem('userId'); // Retrieve the user ID from local storage
      const token = localStorage.getItem('token'); // Retrieve the token from local storage

      if (!userId || !token) {
        setError('User ID or token not found');
        return;
      }

      try {
        const response = await axios.get(`/api/user/${userId}/portfolio/stocks`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        if (response.data && Array.isArray(response.data)) {
          setStockData(response.data);
        } else {
          throw new Error('Unexpected response structure');
        }
      } catch (error) {
        console.error('Failed to fetch stock data:', error);
        setError(error.message);
      }
    };

    if (!isLoading) {
      fetchStockData();
    }
  }, [isLoading]);

  if (isLoading) {
    return <Typography>Loading...</Typography>;
  }

  if (error) {
    return <Typography>Error: {error}</Typography>;
  }

  return (
    <Card>
      <CardContent>
        <Grid container spacing={gridSpacing}>
          <Grid item xs={12}>
            <Typography variant="h5" gutterBottom>
              Portfolio Stocks
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="h6">Stock Ticker</Typography>
          </Grid>
          <Grid item xs={6} style={{ textAlign: 'right' }}>
            <Typography variant="h6">Last Closing Price</Typography>
          </Grid>
          {stockData.map((stock, index) => (
            <React.Fragment key={index}>
              <Grid item xs={6}>
                <Link to={`/asset-details/${stock.symbol}`} style={{ textDecoration: 'none' }}>
                  <Typography variant="subtitle1">{stock.symbol}</Typography>
                </Link>
              </Grid>
              <Grid item xs={6} style={{ textAlign: 'right' }}>
                <Typography variant="subtitle1">{`$${stock.lastClosingPrice.toFixed(2)}`}</Typography>
              </Grid>
            </React.Fragment>
          ))}
        </Grid>
      </CardContent>
    </Card>
  );
};

export default PortfolioStockTickerDisplay;
