const axios = require('axios')

const metrics = require('./metrics')

// how frequently this script will be run via cron
// IMPORTANT: a mismatch between this value and the actual call frequency will
// cause either extraneous or missing notifications
const CALL_FREQUENCY_MINS = 5

// keep the ntfy topic out of version control because anyone with it could
// send notifications to my phone
const { NTFY_TOPIC } = process.env
if (!NTFY_TOPIC) {
  throw Error('Missing `NTFY_TOPIC` environment variable')
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

// get air condition readings since the last call, plus the readings from the
// previous call for comparison
const getReadings = async (query) => {
  const sampleWindow = `${CALL_FREQUENCY_MINS*2}m`
  const res = await axios.get(`http://pi:9090/api/v1/query?query=${query}[${sampleWindow}]`)
  return res.data.data.result[0].values.map(([_, val]) => Number(val))
}

// given an array of readings, return an array containing 2 items: the
// median of the first half and the median of the second half of readings
const getReadingMedians = (values) => {
  const midpoint = Math.floor(values.length / 2)
  return [ values.slice(0, midpoint), values.slice(midpoint) ].map(getMedian)
}

// given a reference `pastValue` and a `currentValue`, returns `true` if 
// `threshold` was crossed between the two values in either direction
const isCrossingThreshold = ([ pastValue, currentValue ], threshold) => 
  (currentValue > threshold && pastValue < threshold) ||
  (currentValue < threshold && pastValue > threshold)

// send a crossed-threshold alert notification via ntfy
const notify = async ({
  alert,
  latestReading,
  isIncreasing,
  metric
}) => {
  const { displayName, displayFunc } = metric
  const { threshold, priority, icon, isUpperBound } = alert
  // indicates that the alert is resolving; i.e. coming back within bounds
  const isResolved = isUpperBound ? !isIncreasing : isIncreasing

  // https://docs.ntfy.sh/publish/#publish-as-json
  await axios.post(
    'https://ntfy.sh',
    {
      topic: NTFY_TOPIC,
      title: `${displayName} ${isIncreasing ? 'above' : 'below'} ${displayFunc(threshold)}`,
      message: `${displayName} is ${displayFunc(latestReading)} and ${isIncreasing ? 'rising' : 'falling'}.`,
      // don't send an audible / vibration notification for resolved alerts
      priority: isResolved ? 2 : priority,
      tags: [isResolved ? 'green_circle' : icon],
      click: 'https://liddiard.grafana.net/d/n_atfpfnz/air-condition'
    }
  )
}

// get air condition readings, process alert rules, and notify of any
// thresholds crossed
const processMetrics = async (metric) => {
  const readings = await getReadings(metric.query)
  const latestReading = readings[readings.length - 1]
  const medians = getReadingMedians(readings)
  const [ pastMedian, currentMedian ] = medians

  // console.log(metric.displayName, medians)
  const alerts = metric.rules
  .filter(({ threshold }) =>
    isCrossingThreshold(medians, threshold))

  alerts.forEach(alert => {
    const isIncreasing = currentMedian > pastMedian
    notify({ alert, latestReading, isIncreasing, metric })
  })
}

const main = () => {
  Object.values(metrics)
  .forEach(processMetrics)
}

main()