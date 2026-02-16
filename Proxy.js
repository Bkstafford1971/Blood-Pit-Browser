// server.js
const express = require('express');
const fetch = require('node-fetch');
const cors = require('cors');
const app = express();

app.use(cors());

app.get('/proxy/roster', async (req, res) => {
    try {
        const response = await fetch('https://bloodpit.net/reports/roster.php');
        const text = await response.text();
        res.send(text);
    } catch (error) {
        res.status(500).send('Error fetching roster');
    }
});

app.listen(3000, () => console.log('Proxy server running on port 3000'));