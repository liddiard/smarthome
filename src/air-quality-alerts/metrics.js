module.exports = {
  airTemperature: {
    query: 'atmp{}',
    displayName: 'Temperature',
    displayFunc: t => `${t}°C`,
    rules: [
      {
        threshold: 12,
        isUpperBound: false,
        priority: 5,
        icon: "cold_face"
      },
      {
        threshold: 15,
        isUpperBound: false,
        priority: 4,
        icon: "cold_face"
      },
      {
        threshold: 18,
        isUpperBound: false,
        priority: 3,
        icon: "cold_face"
      },
      {
        threshold: 25,
        isUpperBound: true,
        priority: 3,
        icon: "hot_face"
      },
      {
        threshold: 28,
        isUpperBound: true,
        priority: 4,
        icon: "hot_face"
      },
      {
        threshold: 31,
        isUpperBound: true,
        priority: 5,
        icon: "hot_face"
      }
    ]
  },
  relativeHumidity: {
    query: 'rhum{}',
    displayName: 'Relative humidity',
    displayFunc: rh => `${rh}%`,
    rules: [
      {
        threshold: 20,
        isUpperBound: false,
        priority: 4,
        icon: "cactus"
      },
      {
        threshold: 35,
        isUpperBound: false,
        priority: 3,
        icon: "cactus"
      },
      {
        threshold: 65,
        isUpperBound: true,
        priority: 3,
        icon: "droplet"
      },
      {
        threshold: 80,
        isUpperBound: true,
        priority: 4,
        icon: "droplet"
      }
    ]
  },
  co2: {
    query: 'rco2{}',
    displayName: 'CO₂',
    displayFunc: co2 => `${co2} ppm`,
    rules: [
      {
        threshold: 1200,
        isUpperBound: true,
        priority: 3,
        icon: "face_exhaling"
      },
      {
        threshold: 1500,
        isUpperBound: true,
        priority: 3,
        icon: "face_exhaling"
      },
      {
        threshold: 2000,
        isUpperBound: true,
        priority: 4,
        icon: "face_exhaling"
      },
      {
        threshold: 3000,
        isUpperBound: true,
        priority: 5,
        icon: "face_exhaling"
      }
    ]
  },
  pm25: {
    query: 'particle_count{type=\"PM2.5\"}',
    displayName: 'PM2.5',
    displayFunc: pm25 => `${pm25} µg/m³`,
    rules: [
      {
        threshold: 60,
        isUpperBound: true,
        priority: 2,
        icon: "mask"
      },
      {
        threshold: 90,
        isUpperBound: true,
        priority: 3,
        icon: "mask"
      },
      {
        threshold: 120,
        isUpperBound: true,
        priority: 3,
        icon: "mask"
      },
      {
        threshold: 200,
        isUpperBound: true,
        priority: 4,
        icon: "mask"
      }
    ]
  }
}