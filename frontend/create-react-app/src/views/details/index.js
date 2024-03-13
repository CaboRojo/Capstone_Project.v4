import React, { useEffect, useState } from 'react';
import { Button, Grid } from '@mui/material';
import { useNavigate, useParams } from 'react-router-dom'; // Import useParams for handling dynamic parameters
import IndividualROICard from './IndividualROICard';
import StockLine from './StockLine';
import StockTotalValueCard from './StockTotalValueCard';
import { gridSpacing } from 'store/constant';

// Assuming you have a way to retrieve the userId, maybe from a global state or context
// For this example, let's just set it statically or you can replace it with your actual logic
const mockGetUserId = () => "exampleUserId";

const AssetDetailsPage = () => {
    const [isLoading, setLoading] = useState(true);
    const navigate = useNavigate(); // Hook for navigation
    const { symbol } = useParams(); // Corrected to use destructuring to get symbol
    const userId = mockGetUserId(); // Here you should replace this with your actual logic to get userId

    useEffect(() => {
        setLoading(false); // Simulating data loading. Adjust accordingly.
    }, []);

    return (
        <Grid container spacing={gridSpacing}>
            <Grid item xs={12} sm={12} md={6}>
                <IndividualROICard symbol={symbol} userId={userId} isLoading={isLoading} />
            </Grid>
            <Grid item xs={12} sm={12} md={6}>
                <StockTotalValueCard symbol={symbol} userId={userId} isLoading={isLoading} />
            </Grid>
            <Grid item xs={12}>
                <StockLine symbol={symbol} userId={userId} isLoading={isLoading} />
            </Grid>
            <Grid item xs={12} container spacing={gridSpacing} justifyContent="space-between" sx={{ mt: 2 }}>
                <Grid item>
                    <Button variant="contained" onClick={() => navigate('/dashboard')}>Return to Dashboard</Button>
                </Grid>
                <Grid item>
                    <Button variant="contained" color="primary" onClick={() => { /* Implement buy logic */ }}>Buy</Button>
                </Grid>
                <Grid item>
                    <Button variant="contained" color="secondary" onClick={() => { /* Implement sell logic */ }}>Sell</Button>
                </Grid>
            </Grid>
        </Grid>
    );
};

export default AssetDetailsPage;



