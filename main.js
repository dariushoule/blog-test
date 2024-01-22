const express = require('express')
const app = express()
const port = 3000

app.get('/', (req, res) => {
    res.send('Hello World!')
})

app.get('/blog', (req, res) => {
    res.send('My cool blog')
})

app.listen(port, () => {
  console.log(`Blog app listening on port ${port}`)
})