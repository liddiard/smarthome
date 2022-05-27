const fs = require('fs/promises')
const path = require('path')

const express = require('express')
const bodyParser = require('body-parser')
const axios = require('axios')


const app = express()
app.use(bodyParser.json())

const port = 3000
const thermostatFilename = path.join(__dirname, 'thermostat.json')


const getThermostat = async () => {
  const text = await fs.readFile(thermostatFilename, 'utf8')
  return JSON.parse(text)
}

const isValidThermostatPatch = (req) => {
  // map from valid request body keys to data types
  const validKeys = {
    on: 'boolean',
    temp: 'number',
    unit: 'string'
  }
  return Object.entries(req.body)
  .every(([key, value]) =>
    validKeys.hasOwnProperty(key) &&
    typeof value === validKeys[key])
}

// https://stackoverflow.com/a/45309555
const getMedian = (arr = []) => {
  const values = [...arr]
  values.sort((a,b) => a - b)
  const half = Math.floor(values.length / 2)
  return values.length % 2 ?
    values[half] :
    (values[half - 1] + values[half]) / 2
}

app.get('/', (req, res) =>
  res.sendFile(path.join(__dirname, 'index.html')))

app.get('/api/v1/temp/', async (req, res) => {
  const prometheusRes = await axios.get('http://pi:9090/api/v1/query?query=atmp{}[5m]')
  const temps = prometheusRes.data.data.result[0].values.map(([_, temp]) => Number(temp))
  return res.json(getMedian(temps))
})

app.get('/api/v1/thermostat/', async (req, res) =>
  res.json(await getThermostat()))

app.patch('/api/v1/thermostat/', async (req, res) => {
  if (!isValidThermostatPatch(req)) {
    return res.status(400).send()
  }
  const thermostat = await getThermostat()
  const newThermostat = {
    ...thermostat,
    ...req.body
  }
  await fs.writeFile(thermostatFilename, JSON.stringify(newThermostat, null, 2))
  return res.json(newThermostat)
})

app.listen(port, () => {
  console.log(`Server listening on port ${port}`)
})