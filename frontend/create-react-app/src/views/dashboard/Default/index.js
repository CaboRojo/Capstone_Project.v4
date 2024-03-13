import React, { useEffect, useState } from 'react';

// material-ui
import { Grid } from '@mui/material';

// project imports
import TotalPortfolioValueCard from './TotalPortfolioValueCard';
import PortfolioROICard from './PortfolioROICard';
import LineGraph from './LineGraph';
import PortfolioStockTickerDisplay from './PortfolioStockTickerDisplay';
import { gridSpacing } from 'store/constant';

// ==============================|| DEFAULT DASHBOARD ||============================== //

const Dashboard = () => {
    const [isLoading, setLoading] = useState(true);

    useEffect(() => {
        setLoading(prevLoading => !prevLoading);
    }, [setLoading]);

    return (
        <Grid container spacing={gridSpacing}>
            <Grid item xs={12} sm={12} md={8}>
                <Grid container spacing={gridSpacing}>
                    {/* Replace EarningCard with TotalPortfolioValueCard and adjust the Grid item size accordingly */}
                    <Grid item lg={6} md={6} sm={6} xs={12}>
                        <TotalPortfolioValueCard isLoading={isLoading} />
                    </Grid>
                    {/* Add the PortfolioROICard next to the TotalPortfolioValueCard */}
                    <Grid item lg={6} md={6} sm={6} xs={12}>
                        <PortfolioROICard isLoading={isLoading} setLoading={setLoading}/>
                    </Grid>
                </Grid>
            </Grid>
            <Grid item xs={12}>
                <LineGraph isLoading={isLoading} setLoading={setLoading} />
            </Grid>
            <Grid item xs={12}>
                <PortfolioStockTickerDisplay isLoading={isLoading} />
            </Grid>
        </Grid>
    );
};

export default Dashboard;
