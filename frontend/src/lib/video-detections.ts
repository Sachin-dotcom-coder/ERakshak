export interface RealCheckpointEvent {
  timeSec: number;
  frame: number;
  event: 'vehicle_entry' | 'vehicle_exit' | 'lane_violation' | 'brts_intrusion';
  objectClass: 'car' | 'bus' | 'two-wheeler' | 'truck' | 'auto';
  confidence: number;
  lane: string;
  note?: string;
}

export interface VideoCheckpoint {
  timeSec: number;
  events: RealCheckpointEvent[];
}

export const VIDEO_DETECTIONS: Record<string, VideoCheckpoint[]> = {
  "traffic1": [
    {
      "timeSec": 0.35,
      "events": [
        {
          "timeSec": 0.35,
          "frame": 7,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 31,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 0.7,
      "events": [
        {
          "timeSec": 0.7,
          "frame": 14,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 52,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 0.7,
          "frame": 14,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 33,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 1.05,
      "events": [
        {
          "timeSec": 1.05,
          "frame": 21,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 51,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 1.4,
      "events": [
        {
          "timeSec": 1.4,
          "frame": 28,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 41,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 1.75,
      "events": [
        {
          "timeSec": 1.75,
          "frame": 35,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 54,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 2.1,
      "events": [
        {
          "timeSec": 2.1,
          "frame": 42,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 67,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 2.1,
          "frame": 42,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 40,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 2.1,
          "frame": 42,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 35,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 2.1,
          "frame": 42,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 33,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 2.1,
          "frame": 42,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 25,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 2.45,
      "events": [
        {
          "timeSec": 2.45,
          "frame": 49,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 51,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 2.45,
          "frame": 49,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 28,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 2.45,
          "frame": 49,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 25,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 2.8,
      "events": [
        {
          "timeSec": 2.8,
          "frame": 56,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 69,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 3.15,
      "events": [
        {
          "timeSec": 3.15,
          "frame": 63,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 51,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 3.15,
          "frame": 63,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 25,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 3.5,
      "events": [
        {
          "timeSec": 3.5,
          "frame": 70,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 76,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 3.5,
          "frame": 70,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 27,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 3.5,
          "frame": 70,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 25,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 3.85,
      "events": [
        {
          "timeSec": 3.85,
          "frame": 77,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 74,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 3.85,
          "frame": 77,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 37,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 3.85,
          "frame": 77,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 37,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 3.85,
          "frame": 77,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 33,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 3.85,
          "frame": 77,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 31,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 4.2,
      "events": [
        {
          "timeSec": 4.2,
          "frame": 84,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 85,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 4.2,
          "frame": 84,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 47,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 4.2,
          "frame": 84,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 26,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 4.2,
          "frame": 84,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 25,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 4.55,
      "events": [
        {
          "timeSec": 4.55,
          "frame": 91,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 82,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 4.55,
          "frame": 91,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 61,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 4.55,
          "frame": 91,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 50,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 4.55,
          "frame": 91,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 49,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 4.55,
          "frame": 91,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 48,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 4.55,
          "frame": 91,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 31,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 4.55,
          "frame": 91,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 31,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 4.55,
          "frame": 91,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 28,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 4.55,
          "frame": 91,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 28,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 4.9,
      "events": [
        {
          "timeSec": 4.9,
          "frame": 98,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 81,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 4.9,
          "frame": 98,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 57,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 4.9,
          "frame": 98,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 49,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 4.9,
          "frame": 98,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 46,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 4.9,
          "frame": 98,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 42,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 4.9,
          "frame": 98,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 39,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 4.9,
          "frame": 98,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 33,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 4.9,
          "frame": 98,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 33,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 4.9,
          "frame": 98,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 30,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 4.9,
          "frame": 98,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 29,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 4.9,
          "frame": 98,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 25,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 5.25,
      "events": [
        {
          "timeSec": 5.25,
          "frame": 105,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 84,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 5.25,
          "frame": 105,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 63,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 5.25,
          "frame": 105,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 59,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 5.25,
          "frame": 105,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 51,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 5.25,
          "frame": 105,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 45,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 5.25,
          "frame": 105,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 41,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 5.25,
          "frame": 105,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 33,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 5.25,
          "frame": 105,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 31,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 5.25,
          "frame": 105,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 28,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 5.6,
      "events": [
        {
          "timeSec": 5.6,
          "frame": 112,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 90,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 5.6,
          "frame": 112,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 64,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 5.6,
          "frame": 112,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 59,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 5.6,
          "frame": 112,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 46,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 5.6,
          "frame": 112,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 41,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 5.6,
          "frame": 112,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 36,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 5.6,
          "frame": 112,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 33,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 5.95,
      "events": [
        {
          "timeSec": 5.95,
          "frame": 119,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 85,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 5.95,
          "frame": 119,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 61,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 5.95,
          "frame": 119,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 59,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 5.95,
          "frame": 119,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 55,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 5.95,
          "frame": 119,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 43,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 5.95,
          "frame": 119,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 40,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 5.95,
          "frame": 119,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 31,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 6.3,
      "events": [
        {
          "timeSec": 6.3,
          "frame": 126,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 92,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 6.3,
          "frame": 126,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 46,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 6.3,
          "frame": 126,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 42,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 6.3,
          "frame": 126,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 35,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 6.3,
          "frame": 126,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 29,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 6.3,
          "frame": 126,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 29,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 6.65,
      "events": [
        {
          "timeSec": 6.65,
          "frame": 133,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 91,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 6.65,
          "frame": 133,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 64,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 6.65,
          "frame": 133,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 59,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 6.65,
          "frame": 133,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 26,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 6.65,
          "frame": 133,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 26,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 7.0,
      "events": [
        {
          "timeSec": 7.0,
          "frame": 140,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 62,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 7.0,
          "frame": 140,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 49,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 7.0,
          "frame": 140,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 34,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 7.0,
          "frame": 140,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 32,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 7.35,
      "events": [
        {
          "timeSec": 7.35,
          "frame": 147,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 67,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 7.35,
          "frame": 147,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 45,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 7.35,
          "frame": 147,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 40,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 7.35,
          "frame": 147,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 34,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 7.35,
          "frame": 147,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 34,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 7.7,
      "events": [
        {
          "timeSec": 7.7,
          "frame": 154,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 37,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 7.7,
          "frame": 154,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 25,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 8.05,
      "events": [
        {
          "timeSec": 8.05,
          "frame": 161,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 65,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 8.05,
          "frame": 161,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 34,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 8.05,
          "frame": 161,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 33,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 8.05,
          "frame": 161,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 32,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 8.4,
      "events": [
        {
          "timeSec": 8.4,
          "frame": 168,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 72,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 8.4,
          "frame": 168,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 41,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 8.4,
          "frame": 168,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 27,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 8.4,
          "frame": 168,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 26,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 8.4,
          "frame": 168,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 26,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 8.75,
      "events": [
        {
          "timeSec": 8.75,
          "frame": 175,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 74,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 8.75,
          "frame": 175,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 49,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 8.75,
          "frame": 175,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 39,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 8.75,
          "frame": 175,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 31,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 8.75,
          "frame": 175,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 27,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 9.1,
      "events": [
        {
          "timeSec": 9.1,
          "frame": 182,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 75,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 9.1,
          "frame": 182,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 72,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 9.1,
          "frame": 182,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 38,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 9.1,
          "frame": 182,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 25,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 9.45,
      "events": [
        {
          "timeSec": 9.45,
          "frame": 189,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 81,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 9.45,
          "frame": 189,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 74,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 9.45,
          "frame": 189,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 69,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 9.45,
          "frame": 189,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 31,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 9.45,
          "frame": 189,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 31,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 9.45,
          "frame": 189,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 28,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 9.45,
          "frame": 189,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 25,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 9.8,
      "events": [
        {
          "timeSec": 9.8,
          "frame": 196,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 83,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 9.8,
          "frame": 196,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 67,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 9.8,
          "frame": 196,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 52,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 9.8,
          "frame": 196,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 44,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 9.8,
          "frame": 196,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 27,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 10.15,
      "events": [
        {
          "timeSec": 10.15,
          "frame": 203,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 89,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 10.15,
          "frame": 203,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 79,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 10.15,
          "frame": 203,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 55,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 10.15,
          "frame": 203,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 39,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 10.15,
          "frame": 203,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 32,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 10.15,
          "frame": 203,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 30,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 10.5,
      "events": [
        {
          "timeSec": 10.5,
          "frame": 210,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 88,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 10.5,
          "frame": 210,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 64,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 10.5,
          "frame": 210,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 62,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 10.5,
          "frame": 210,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 56,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 10.5,
          "frame": 210,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 39,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 10.5,
          "frame": 210,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 33,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 10.5,
          "frame": 210,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 31,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 10.5,
          "frame": 210,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 30,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 10.85,
      "events": [
        {
          "timeSec": 10.85,
          "frame": 217,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 92,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 10.85,
          "frame": 217,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 73,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 10.85,
          "frame": 217,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 65,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 10.85,
          "frame": 217,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 39,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 10.85,
          "frame": 217,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 37,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 10.85,
          "frame": 217,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 37,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 10.85,
          "frame": 217,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 25,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 11.2,
      "events": [
        {
          "timeSec": 11.2,
          "frame": 224,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 94,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 11.2,
          "frame": 224,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 71,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 11.2,
          "frame": 224,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 43,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 11.2,
          "frame": 224,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 41,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 11.2,
          "frame": 224,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 34,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 11.2,
          "frame": 224,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 34,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 11.2,
          "frame": 224,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 32,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 11.55,
      "events": [
        {
          "timeSec": 11.55,
          "frame": 231,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 89,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 11.55,
          "frame": 231,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 80,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 11.55,
          "frame": 231,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 58,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 11.55,
          "frame": 231,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 57,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 11.9,
      "events": [
        {
          "timeSec": 11.9,
          "frame": 238,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 84,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 11.9,
          "frame": 238,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 75,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 11.9,
          "frame": 238,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 59,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 11.9,
          "frame": 238,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 32,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 12.25,
      "events": [
        {
          "timeSec": 12.25,
          "frame": 245,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 91,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 12.25,
          "frame": 245,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 81,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 12.25,
          "frame": 245,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 50,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 12.25,
          "frame": 245,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 42,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 12.25,
          "frame": 245,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 40,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 12.25,
          "frame": 245,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 30,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 12.25,
          "frame": 245,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 27,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 12.6,
      "events": [
        {
          "timeSec": 12.6,
          "frame": 252,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 94,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 12.6,
          "frame": 252,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 67,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 12.6,
          "frame": 252,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 62,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 12.6,
          "frame": 252,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 56,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 12.6,
          "frame": 252,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 43,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 12.6,
          "frame": 252,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 35,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 12.95,
      "events": [
        {
          "timeSec": 12.95,
          "frame": 259,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 72,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 12.95,
          "frame": 259,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 56,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 12.95,
          "frame": 259,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 43,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 12.95,
          "frame": 259,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 30,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 12.95,
          "frame": 259,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 30,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 13.3,
      "events": [
        {
          "timeSec": 13.3,
          "frame": 266,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 76,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 13.3,
          "frame": 266,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 57,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 13.3,
          "frame": 266,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 45,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 13.3,
          "frame": 266,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 40,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 13.65,
      "events": [
        {
          "timeSec": 13.65,
          "frame": 273,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 73,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 13.65,
          "frame": 273,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 53,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 13.65,
          "frame": 273,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 35,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 13.65,
          "frame": 273,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 29,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 14.0,
      "events": [
        {
          "timeSec": 14.0,
          "frame": 280,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 93,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 14.0,
          "frame": 280,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 65,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 14.0,
          "frame": 280,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 51,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 14.0,
          "frame": 280,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 39,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 14.0,
          "frame": 280,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 29,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 14.0,
          "frame": 280,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 26,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 14.35,
      "events": [
        {
          "timeSec": 14.35,
          "frame": 287,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 41,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 14.35,
          "frame": 287,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 38,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 14.35,
          "frame": 287,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 32,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 14.35,
          "frame": 287,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 31,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 14.35,
          "frame": 287,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 31,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 14.35,
          "frame": 287,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 30,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 14.35,
          "frame": 287,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 29,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 14.35,
          "frame": 287,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 27,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 14.35,
          "frame": 287,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 26,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 14.7,
      "events": [
        {
          "timeSec": 14.7,
          "frame": 294,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 72,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 14.7,
          "frame": 294,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 69,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 14.7,
          "frame": 294,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 47,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 14.7,
          "frame": 294,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 39,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 14.7,
          "frame": 294,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 33,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 14.7,
          "frame": 294,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 25,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 14.7,
          "frame": 294,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 25,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    }
  ],
  "traffic2": [
    {
      "timeSec": 0.0,
      "events": [
        {
          "timeSec": 0.0,
          "frame": 0,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 89,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 0.0,
          "frame": 0,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 88,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 0.0,
          "frame": 0,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 77,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 0.0,
          "frame": 0,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 77,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 0.0,
          "frame": 0,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 73,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 0.0,
          "frame": 0,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 67,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 0.0,
          "frame": 0,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 63,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 0.0,
          "frame": 0,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 58,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 0.0,
          "frame": 0,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 56,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 0.0,
          "frame": 0,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 51,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 0.0,
          "frame": 0,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 50,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 0.0,
          "frame": 0,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 50,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 0.0,
          "frame": 0,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 48,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 0.0,
          "frame": 0,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 46,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 0.0,
          "frame": 0,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 40,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 0.0,
          "frame": 0,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 35,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 0.0,
          "frame": 0,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 29,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 0.0,
          "frame": 0,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 28,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 0.0,
          "frame": 0,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 25,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 0.35,
      "events": [
        {
          "timeSec": 0.35,
          "frame": 7,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 87,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 0.35,
          "frame": 7,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 82,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 0.35,
          "frame": 7,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 79,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 0.35,
          "frame": 7,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 74,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 0.35,
          "frame": 7,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 71,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 0.35,
          "frame": 7,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 70,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 0.35,
          "frame": 7,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 69,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 0.35,
          "frame": 7,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 68,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 0.35,
          "frame": 7,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 53,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 0.35,
          "frame": 7,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 48,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 0.35,
          "frame": 7,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 42,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 0.35,
          "frame": 7,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 32,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 0.35,
          "frame": 7,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 31,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 0.35,
          "frame": 7,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 28,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 0.35,
          "frame": 7,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 28,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 0.35,
          "frame": 7,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 28,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 0.35,
          "frame": 7,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 26,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 0.7,
      "events": [
        {
          "timeSec": 0.7,
          "frame": 14,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 85,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 0.7,
          "frame": 14,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 81,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 0.7,
          "frame": 14,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 66,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 0.7,
          "frame": 14,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 64,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 0.7,
          "frame": 14,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 62,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 0.7,
          "frame": 14,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 60,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 0.7,
          "frame": 14,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 59,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 0.7,
          "frame": 14,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 48,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 0.7,
          "frame": 14,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 43,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 0.7,
          "frame": 14,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 40,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 0.7,
          "frame": 14,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 37,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 0.7,
          "frame": 14,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 36,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 0.7,
          "frame": 14,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 32,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 0.7,
          "frame": 14,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 30,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 0.7,
          "frame": 14,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 27,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 0.7,
          "frame": 14,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 26,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 1.05,
      "events": [
        {
          "timeSec": 1.05,
          "frame": 21,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 81,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 1.05,
          "frame": 21,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 73,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 1.05,
          "frame": 21,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 58,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 1.05,
          "frame": 21,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 54,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 1.05,
          "frame": 21,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 51,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 1.05,
          "frame": 21,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 50,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 1.05,
          "frame": 21,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 43,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 1.05,
          "frame": 21,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 41,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 1.05,
          "frame": 21,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 39,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 1.05,
          "frame": 21,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 38,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 1.05,
          "frame": 21,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 38,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 1.05,
          "frame": 21,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 37,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 1.05,
          "frame": 21,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 33,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 1.05,
          "frame": 21,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 33,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 1.05,
          "frame": 21,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 33,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 1.05,
          "frame": 21,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 32,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 1.05,
          "frame": 21,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 31,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 1.05,
          "frame": 21,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 30,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 1.05,
          "frame": 21,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 28,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 1.05,
          "frame": 21,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 26,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 1.05,
          "frame": 21,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 25,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 1.4,
      "events": [
        {
          "timeSec": 1.4,
          "frame": 28,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 84,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 1.4,
          "frame": 28,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 81,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 1.4,
          "frame": 28,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 81,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 1.4,
          "frame": 28,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 80,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 1.4,
          "frame": 28,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 76,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 1.4,
          "frame": 28,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 66,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 1.4,
          "frame": 28,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 56,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 1.4,
          "frame": 28,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 55,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 1.4,
          "frame": 28,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 54,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 1.4,
          "frame": 28,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 33,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 1.4,
          "frame": 28,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 30,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 1.4,
          "frame": 28,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 26,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 1.4,
          "frame": 28,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 26,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 1.4,
          "frame": 28,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 25,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 1.75,
      "events": [
        {
          "timeSec": 1.75,
          "frame": 35,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 87,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 1.75,
          "frame": 35,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 87,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 1.75,
          "frame": 35,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 82,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 1.75,
          "frame": 35,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 76,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 1.75,
          "frame": 35,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 69,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 1.75,
          "frame": 35,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 56,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 1.75,
          "frame": 35,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 54,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 1.75,
          "frame": 35,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 52,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 1.75,
          "frame": 35,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 45,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 1.75,
          "frame": 35,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 45,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 1.75,
          "frame": 35,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 43,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 1.75,
          "frame": 35,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 42,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 1.75,
          "frame": 35,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 40,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 1.75,
          "frame": 35,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 35,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 1.75,
          "frame": 35,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 34,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 1.75,
          "frame": 35,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 33,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 1.75,
          "frame": 35,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 29,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 1.75,
          "frame": 35,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 29,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 1.75,
          "frame": 35,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 27,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 2.1,
      "events": [
        {
          "timeSec": 2.1,
          "frame": 42,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 90,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 2.1,
          "frame": 42,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 85,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 2.1,
          "frame": 42,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 84,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 2.1,
          "frame": 42,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 82,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 2.1,
          "frame": 42,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 74,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 2.1,
          "frame": 42,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 73,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 2.1,
          "frame": 42,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 71,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 2.1,
          "frame": 42,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 55,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 2.1,
          "frame": 42,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 49,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 2.1,
          "frame": 42,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 47,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 2.1,
          "frame": 42,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 47,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 2.1,
          "frame": 42,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 45,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 2.1,
          "frame": 42,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 44,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 2.1,
          "frame": 42,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 36,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 2.1,
          "frame": 42,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 34,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 2.1,
          "frame": 42,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 33,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 2.1,
          "frame": 42,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 30,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 2.45,
      "events": [
        {
          "timeSec": 2.45,
          "frame": 49,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 80,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 2.45,
          "frame": 49,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 77,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 2.45,
          "frame": 49,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 76,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 2.45,
          "frame": 49,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 76,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 2.45,
          "frame": 49,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 73,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 2.45,
          "frame": 49,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 65,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 2.45,
          "frame": 49,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 56,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 2.45,
          "frame": 49,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 54,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 2.45,
          "frame": 49,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 53,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 2.45,
          "frame": 49,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 50,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 2.45,
          "frame": 49,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 50,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 2.45,
          "frame": 49,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 45,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 2.45,
          "frame": 49,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 44,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 2.45,
          "frame": 49,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 44,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 2.45,
          "frame": 49,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 37,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 2.45,
          "frame": 49,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 33,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 2.45,
          "frame": 49,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 26,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 2.8,
      "events": [
        {
          "timeSec": 2.8,
          "frame": 56,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 86,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 2.8,
          "frame": 56,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 80,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 2.8,
          "frame": 56,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 77,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 2.8,
          "frame": 56,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 77,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 2.8,
          "frame": 56,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 74,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 2.8,
          "frame": 56,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 68,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 2.8,
          "frame": 56,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 57,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 2.8,
          "frame": 56,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 47,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 2.8,
          "frame": 56,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 46,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 2.8,
          "frame": 56,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 45,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 2.8,
          "frame": 56,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 44,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 2.8,
          "frame": 56,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 42,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 2.8,
          "frame": 56,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 41,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 2.8,
          "frame": 56,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 40,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 2.8,
          "frame": 56,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 36,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 2.8,
          "frame": 56,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 35,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 2.8,
          "frame": 56,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 34,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 2.8,
          "frame": 56,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 28,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 2.8,
          "frame": 56,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 25,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 2.8,
          "frame": 56,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 25,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 2.8,
          "frame": 56,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 25,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 3.15,
      "events": [
        {
          "timeSec": 3.15,
          "frame": 63,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 87,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 3.15,
          "frame": 63,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 85,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 3.15,
          "frame": 63,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 82,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 3.15,
          "frame": 63,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 74,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 3.15,
          "frame": 63,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 69,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 3.15,
          "frame": 63,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 68,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 3.15,
          "frame": 63,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 65,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 3.15,
          "frame": 63,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 61,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 3.15,
          "frame": 63,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 60,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 3.15,
          "frame": 63,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 51,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 3.15,
          "frame": 63,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 42,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 3.15,
          "frame": 63,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 42,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 3.15,
          "frame": 63,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 41,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 3.15,
          "frame": 63,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 38,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 3.15,
          "frame": 63,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 36,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 3.15,
          "frame": 63,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 32,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 3.5,
      "events": [
        {
          "timeSec": 3.5,
          "frame": 70,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 92,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 3.5,
          "frame": 70,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 70,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 3.5,
          "frame": 70,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 67,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 3.5,
          "frame": 70,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 59,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 3.5,
          "frame": 70,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 53,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 3.5,
          "frame": 70,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 48,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 3.5,
          "frame": 70,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 46,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 3.5,
          "frame": 70,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 46,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 3.5,
          "frame": 70,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 45,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 3.5,
          "frame": 70,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 40,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 3.5,
          "frame": 70,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 38,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 3.5,
          "frame": 70,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 36,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 3.5,
          "frame": 70,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 36,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 3.5,
          "frame": 70,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 36,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 3.5,
          "frame": 70,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 36,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 3.5,
          "frame": 70,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 35,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 3.5,
          "frame": 70,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 33,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 3.5,
          "frame": 70,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 31,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 3.5,
          "frame": 70,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 30,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 3.5,
          "frame": 70,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 30,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 3.5,
          "frame": 70,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 28,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 3.5,
          "frame": 70,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 25,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 3.85,
      "events": [
        {
          "timeSec": 3.85,
          "frame": 77,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 87,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 3.85,
          "frame": 77,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 79,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 3.85,
          "frame": 77,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 74,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 3.85,
          "frame": 77,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 68,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 3.85,
          "frame": 77,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 65,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 3.85,
          "frame": 77,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 54,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 3.85,
          "frame": 77,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 49,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 3.85,
          "frame": 77,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 46,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 3.85,
          "frame": 77,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 46,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 3.85,
          "frame": 77,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 42,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 3.85,
          "frame": 77,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 41,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 3.85,
          "frame": 77,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 41,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 3.85,
          "frame": 77,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 39,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 3.85,
          "frame": 77,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 39,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 3.85,
          "frame": 77,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 31,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 3.85,
          "frame": 77,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 31,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 3.85,
          "frame": 77,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 30,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 3.85,
          "frame": 77,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 30,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 3.85,
          "frame": 77,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 30,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 3.85,
          "frame": 77,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 30,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 3.85,
          "frame": 77,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 29,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 3.85,
          "frame": 77,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 28,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 3.85,
          "frame": 77,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 26,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 4.2,
      "events": [
        {
          "timeSec": 4.2,
          "frame": 84,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 92,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 4.2,
          "frame": 84,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 87,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 4.2,
          "frame": 84,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 76,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 4.2,
          "frame": 84,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 71,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 4.2,
          "frame": 84,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 67,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 4.2,
          "frame": 84,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 66,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 4.2,
          "frame": 84,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 65,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 4.2,
          "frame": 84,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 64,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 4.2,
          "frame": 84,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 63,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 4.2,
          "frame": 84,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 62,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 4.2,
          "frame": 84,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 51,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 4.2,
          "frame": 84,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 49,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 4.2,
          "frame": 84,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 48,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 4.2,
          "frame": 84,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 47,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 4.2,
          "frame": 84,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 46,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 4.2,
          "frame": 84,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 32,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 4.2,
          "frame": 84,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 29,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 4.2,
          "frame": 84,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 29,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 4.55,
      "events": [
        {
          "timeSec": 4.55,
          "frame": 91,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 86,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 4.55,
          "frame": 91,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 78,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 4.55,
          "frame": 91,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 72,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 4.55,
          "frame": 91,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 72,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 4.55,
          "frame": 91,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 69,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 4.55,
          "frame": 91,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 68,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 4.55,
          "frame": 91,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 68,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 4.55,
          "frame": 91,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 66,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 4.55,
          "frame": 91,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 66,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 4.55,
          "frame": 91,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 62,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 4.55,
          "frame": 91,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 60,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 4.55,
          "frame": 91,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 52,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 4.55,
          "frame": 91,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 51,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 4.55,
          "frame": 91,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 48,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 4.55,
          "frame": 91,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 46,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 4.55,
          "frame": 91,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 38,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 4.55,
          "frame": 91,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 34,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 4.55,
          "frame": 91,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 33,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 4.55,
          "frame": 91,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 31,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 4.55,
          "frame": 91,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 30,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 4.55,
          "frame": 91,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 26,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 4.55,
          "frame": 91,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 25,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 4.9,
      "events": [
        {
          "timeSec": 4.9,
          "frame": 98,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 83,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 4.9,
          "frame": 98,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 81,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 4.9,
          "frame": 98,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 77,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 4.9,
          "frame": 98,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 74,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 4.9,
          "frame": 98,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 74,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 4.9,
          "frame": 98,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 73,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 4.9,
          "frame": 98,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 63,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 4.9,
          "frame": 98,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 57,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 4.9,
          "frame": 98,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 53,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 4.9,
          "frame": 98,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 51,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 4.9,
          "frame": 98,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 47,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 4.9,
          "frame": 98,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 45,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 4.9,
          "frame": 98,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 44,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 4.9,
          "frame": 98,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 42,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 4.9,
          "frame": 98,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 41,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 4.9,
          "frame": 98,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 39,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 4.9,
          "frame": 98,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 36,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 4.9,
          "frame": 98,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 35,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 4.9,
          "frame": 98,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 33,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 4.9,
          "frame": 98,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 31,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 4.9,
          "frame": 98,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 28,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 4.9,
          "frame": 98,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 27,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 4.9,
          "frame": 98,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 26,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 4.9,
          "frame": 98,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 25,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 4.9,
          "frame": 98,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 25,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 5.25,
      "events": [
        {
          "timeSec": 5.25,
          "frame": 105,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 81,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 5.25,
          "frame": 105,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 79,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 5.25,
          "frame": 105,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 78,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 5.25,
          "frame": 105,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 72,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 5.25,
          "frame": 105,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 72,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 5.25,
          "frame": 105,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 57,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 5.25,
          "frame": 105,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 57,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 5.25,
          "frame": 105,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 52,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 5.25,
          "frame": 105,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 48,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 5.25,
          "frame": 105,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 44,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 5.25,
          "frame": 105,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 43,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 5.25,
          "frame": 105,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 43,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 5.25,
          "frame": 105,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 37,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 5.25,
          "frame": 105,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 36,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 5.25,
          "frame": 105,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 35,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 5.25,
          "frame": 105,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 33,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 5.25,
          "frame": 105,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 31,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 5.25,
          "frame": 105,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 30,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 5.25,
          "frame": 105,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 30,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 5.25,
          "frame": 105,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 29,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 5.25,
          "frame": 105,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 27,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 5.25,
          "frame": 105,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 26,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 5.6,
      "events": [
        {
          "timeSec": 5.6,
          "frame": 112,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 84,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 5.6,
          "frame": 112,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 83,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 5.6,
          "frame": 112,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 76,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 5.6,
          "frame": 112,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 72,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 5.6,
          "frame": 112,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 71,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 5.6,
          "frame": 112,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 60,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 5.6,
          "frame": 112,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 60,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 5.6,
          "frame": 112,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 60,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 5.6,
          "frame": 112,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 56,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 5.6,
          "frame": 112,
          "event": "brts_intrusion",
          "objectClass": "truck",
          "confidence": 54,
          "lane": "BRTS Corridor",
          "note": "\u26a0\ufe0f Corridor Intrusion \u2022 BRTS Corridor"
        },
        {
          "timeSec": 5.6,
          "frame": 112,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 50,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 5.6,
          "frame": 112,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 49,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 5.6,
          "frame": 112,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 43,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 5.6,
          "frame": 112,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 40,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 5.6,
          "frame": 112,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 34,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 5.6,
          "frame": 112,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 33,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 5.6,
          "frame": 112,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 30,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 5.6,
          "frame": 112,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 30,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 5.6,
          "frame": 112,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 28,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 5.6,
          "frame": 112,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 26,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 5.6,
          "frame": 112,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 25,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 5.95,
      "events": [
        {
          "timeSec": 5.95,
          "frame": 119,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 84,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 5.95,
          "frame": 119,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 83,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 5.95,
          "frame": 119,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 78,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 5.95,
          "frame": 119,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 77,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 5.95,
          "frame": 119,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 76,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 5.95,
          "frame": 119,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 75,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 5.95,
          "frame": 119,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 65,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 5.95,
          "frame": 119,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 59,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 5.95,
          "frame": 119,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 57,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 5.95,
          "frame": 119,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 50,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 5.95,
          "frame": 119,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 42,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 5.95,
          "frame": 119,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 37,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 5.95,
          "frame": 119,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 35,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 5.95,
          "frame": 119,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 35,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 5.95,
          "frame": 119,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 33,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 5.95,
          "frame": 119,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 31,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 5.95,
          "frame": 119,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 28,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 5.95,
          "frame": 119,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 25,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 6.3,
      "events": [
        {
          "timeSec": 6.3,
          "frame": 126,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 88,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 6.3,
          "frame": 126,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 80,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 6.3,
          "frame": 126,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 79,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 6.3,
          "frame": 126,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 78,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 6.3,
          "frame": 126,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 77,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 6.3,
          "frame": 126,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 75,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 6.3,
          "frame": 126,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 67,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 6.3,
          "frame": 126,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 66,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 6.3,
          "frame": 126,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 60,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 6.3,
          "frame": 126,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 57,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 6.3,
          "frame": 126,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 46,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 6.3,
          "frame": 126,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 45,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 6.3,
          "frame": 126,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 43,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 6.3,
          "frame": 126,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 37,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 6.3,
          "frame": 126,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 36,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 6.3,
          "frame": 126,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 35,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 6.3,
          "frame": 126,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 35,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 6.3,
          "frame": 126,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 34,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 6.3,
          "frame": 126,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 31,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 6.3,
          "frame": 126,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 27,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 6.3,
          "frame": 126,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 26,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 6.65,
      "events": [
        {
          "timeSec": 6.65,
          "frame": 133,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 81,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 6.65,
          "frame": 133,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 77,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 6.65,
          "frame": 133,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 71,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 6.65,
          "frame": 133,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 66,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 6.65,
          "frame": 133,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 64,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 6.65,
          "frame": 133,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 64,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 6.65,
          "frame": 133,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 57,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 6.65,
          "frame": 133,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 56,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 6.65,
          "frame": 133,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 55,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 6.65,
          "frame": 133,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 51,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 6.65,
          "frame": 133,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 51,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 6.65,
          "frame": 133,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 33,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 6.65,
          "frame": 133,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 32,
          "lane": "BRTS Corridor",
          "note": "Authorized BRTS Transit"
        },
        {
          "timeSec": 6.65,
          "frame": 133,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 31,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 6.65,
          "frame": 133,
          "event": "brts_intrusion",
          "objectClass": "truck",
          "confidence": 31,
          "lane": "BRTS Corridor",
          "note": "\u26a0\ufe0f Corridor Intrusion \u2022 BRTS Corridor"
        },
        {
          "timeSec": 6.65,
          "frame": 133,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 30,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 6.65,
          "frame": 133,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 27,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 6.65,
          "frame": 133,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 26,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 7.0,
      "events": [
        {
          "timeSec": 7.0,
          "frame": 140,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 83,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 7.0,
          "frame": 140,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 81,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 7.0,
          "frame": 140,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 77,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 7.0,
          "frame": 140,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 71,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 7.0,
          "frame": 140,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 56,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 7.0,
          "frame": 140,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 56,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 7.0,
          "frame": 140,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 56,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 7.0,
          "frame": 140,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 54,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 7.0,
          "frame": 140,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 52,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 7.0,
          "frame": 140,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 50,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 7.0,
          "frame": 140,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 49,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 7.0,
          "frame": 140,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 34,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 7.0,
          "frame": 140,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 32,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 7.0,
          "frame": 140,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 30,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 7.0,
          "frame": 140,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 30,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 7.0,
          "frame": 140,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 29,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 7.0,
          "frame": 140,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 27,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 7.35,
      "events": [
        {
          "timeSec": 7.35,
          "frame": 147,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 89,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 7.35,
          "frame": 147,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 78,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 7.35,
          "frame": 147,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 78,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 7.35,
          "frame": 147,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 76,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 7.35,
          "frame": 147,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 75,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 7.35,
          "frame": 147,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 62,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 7.35,
          "frame": 147,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 62,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 7.35,
          "frame": 147,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 61,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 7.35,
          "frame": 147,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 60,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 7.35,
          "frame": 147,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 55,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 7.35,
          "frame": 147,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 53,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 7.35,
          "frame": 147,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 52,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 7.35,
          "frame": 147,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 48,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 7.35,
          "frame": 147,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 48,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 7.35,
          "frame": 147,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 45,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 7.35,
          "frame": 147,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 44,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 7.35,
          "frame": 147,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 44,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 7.35,
          "frame": 147,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 41,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 7.35,
          "frame": 147,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 40,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 7.35,
          "frame": 147,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 38,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 7.35,
          "frame": 147,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 36,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 7.35,
          "frame": 147,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 33,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 7.35,
          "frame": 147,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 27,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 7.7,
      "events": [
        {
          "timeSec": 7.7,
          "frame": 154,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 87,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 7.7,
          "frame": 154,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 87,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 7.7,
          "frame": 154,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 86,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 7.7,
          "frame": 154,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 77,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 7.7,
          "frame": 154,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 74,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 7.7,
          "frame": 154,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 66,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 7.7,
          "frame": 154,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 64,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 7.7,
          "frame": 154,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 62,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 7.7,
          "frame": 154,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 61,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 7.7,
          "frame": 154,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 57,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 7.7,
          "frame": 154,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 57,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 7.7,
          "frame": 154,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 56,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 7.7,
          "frame": 154,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 56,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 7.7,
          "frame": 154,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 50,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 7.7,
          "frame": 154,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 46,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 7.7,
          "frame": 154,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 46,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 7.7,
          "frame": 154,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 32,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 7.7,
          "frame": 154,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 30,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 7.7,
          "frame": 154,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 29,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 7.7,
          "frame": 154,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 27,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 7.7,
          "frame": 154,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 26,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 7.7,
          "frame": 154,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 26,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 7.7,
          "frame": 154,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 25,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 8.05,
      "events": [
        {
          "timeSec": 8.05,
          "frame": 161,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 88,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 8.05,
          "frame": 161,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 86,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 8.05,
          "frame": 161,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 79,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 8.05,
          "frame": 161,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 76,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 8.05,
          "frame": 161,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 74,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 8.05,
          "frame": 161,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 71,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 8.05,
          "frame": 161,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 68,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 8.05,
          "frame": 161,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 68,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 8.05,
          "frame": 161,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 68,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 8.05,
          "frame": 161,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 63,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 8.05,
          "frame": 161,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 56,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 8.05,
          "frame": 161,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 55,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 8.05,
          "frame": 161,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 50,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 8.05,
          "frame": 161,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 45,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 8.05,
          "frame": 161,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 43,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 8.05,
          "frame": 161,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 41,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 8.05,
          "frame": 161,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 41,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 8.05,
          "frame": 161,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 40,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 8.05,
          "frame": 161,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 38,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 8.05,
          "frame": 161,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 37,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 8.05,
          "frame": 161,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 31,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 8.05,
          "frame": 161,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 29,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 8.05,
          "frame": 161,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 27,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 8.4,
      "events": [
        {
          "timeSec": 8.4,
          "frame": 168,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 91,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 8.4,
          "frame": 168,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 89,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 8.4,
          "frame": 168,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 89,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 8.4,
          "frame": 168,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 86,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 8.4,
          "frame": 168,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 75,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 8.4,
          "frame": 168,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 70,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 8.4,
          "frame": 168,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 67,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 8.4,
          "frame": 168,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 54,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 8.4,
          "frame": 168,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 53,
          "lane": "BRTS Corridor",
          "note": "Authorized BRTS Transit"
        },
        {
          "timeSec": 8.4,
          "frame": 168,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 53,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 8.4,
          "frame": 168,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 52,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 8.4,
          "frame": 168,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 48,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 8.4,
          "frame": 168,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 46,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 8.4,
          "frame": 168,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 42,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 8.4,
          "frame": 168,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 40,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 8.4,
          "frame": 168,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 39,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 8.4,
          "frame": 168,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 36,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 8.4,
          "frame": 168,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 31,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 8.4,
          "frame": 168,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 30,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 8.4,
          "frame": 168,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 28,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 8.4,
          "frame": 168,
          "event": "brts_intrusion",
          "objectClass": "truck",
          "confidence": 26,
          "lane": "BRTS Corridor",
          "note": "\u26a0\ufe0f Corridor Intrusion \u2022 BRTS Corridor"
        }
      ]
    },
    {
      "timeSec": 8.75,
      "events": [
        {
          "timeSec": 8.75,
          "frame": 175,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 94,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 8.75,
          "frame": 175,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 91,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 8.75,
          "frame": 175,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 86,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 8.75,
          "frame": 175,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 84,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 8.75,
          "frame": 175,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 82,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 8.75,
          "frame": 175,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 81,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 8.75,
          "frame": 175,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 63,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 8.75,
          "frame": 175,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 62,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 8.75,
          "frame": 175,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 55,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 8.75,
          "frame": 175,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 46,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 8.75,
          "frame": 175,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 44,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 8.75,
          "frame": 175,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 44,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 8.75,
          "frame": 175,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 43,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 8.75,
          "frame": 175,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 42,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 8.75,
          "frame": 175,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 36,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 8.75,
          "frame": 175,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 34,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 8.75,
          "frame": 175,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 33,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 8.75,
          "frame": 175,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 31,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 8.75,
          "frame": 175,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 30,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 8.75,
          "frame": 175,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 29,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 8.75,
          "frame": 175,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 28,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 8.75,
          "frame": 175,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 27,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 9.1,
      "events": [
        {
          "timeSec": 9.1,
          "frame": 182,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 91,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 9.1,
          "frame": 182,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 91,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 9.1,
          "frame": 182,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 74,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.1,
          "frame": 182,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 69,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.1,
          "frame": 182,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 67,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.1,
          "frame": 182,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 66,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.1,
          "frame": 182,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 65,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.1,
          "frame": 182,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 52,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.1,
          "frame": 182,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 43,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.1,
          "frame": 182,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 39,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.1,
          "frame": 182,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 39,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.1,
          "frame": 182,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 39,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 9.1,
          "frame": 182,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 35,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.1,
          "frame": 182,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 35,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 9.1,
          "frame": 182,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 35,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 9.1,
          "frame": 182,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 34,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.1,
          "frame": 182,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 32,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 9.1,
          "frame": 182,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 31,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 9.1,
          "frame": 182,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 30,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.1,
          "frame": 182,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 28,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.1,
          "frame": 182,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 28,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 9.1,
          "frame": 182,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 27,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.1,
          "frame": 182,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 26,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 9.1,
          "frame": 182,
          "event": "brts_intrusion",
          "objectClass": "truck",
          "confidence": 25,
          "lane": "BRTS Corridor",
          "note": "\u26a0\ufe0f Corridor Intrusion \u2022 BRTS Corridor"
        }
      ]
    },
    {
      "timeSec": 9.45,
      "events": [
        {
          "timeSec": 9.45,
          "frame": 189,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 88,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 9.45,
          "frame": 189,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 84,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 9.45,
          "frame": 189,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 78,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 9.45,
          "frame": 189,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 77,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.45,
          "frame": 189,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 76,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.45,
          "frame": 189,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 72,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 9.45,
          "frame": 189,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 70,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 9.45,
          "frame": 189,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 68,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.45,
          "frame": 189,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 67,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.45,
          "frame": 189,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 52,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 9.45,
          "frame": 189,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 47,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 9.45,
          "frame": 189,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 47,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.45,
          "frame": 189,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 47,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 9.45,
          "frame": 189,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 46,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.45,
          "frame": 189,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 45,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.45,
          "frame": 189,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 43,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.45,
          "frame": 189,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 40,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.45,
          "frame": 189,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 38,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.45,
          "frame": 189,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 36,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.45,
          "frame": 189,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 34,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 9.45,
          "frame": 189,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 34,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.45,
          "frame": 189,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 32,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.45,
          "frame": 189,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 30,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 9.45,
          "frame": 189,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 29,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.45,
          "frame": 189,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 29,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.45,
          "frame": 189,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 27,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 9.45,
          "frame": 189,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 26,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.45,
          "frame": 189,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 26,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.45,
          "frame": 189,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 25,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 9.8,
      "events": [
        {
          "timeSec": 9.8,
          "frame": 196,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 90,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 9.8,
          "frame": 196,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 85,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.8,
          "frame": 196,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 84,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 9.8,
          "frame": 196,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 84,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 9.8,
          "frame": 196,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 73,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.8,
          "frame": 196,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 72,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.8,
          "frame": 196,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 63,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 9.8,
          "frame": 196,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 59,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.8,
          "frame": 196,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 53,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.8,
          "frame": 196,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 52,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.8,
          "frame": 196,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 51,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 9.8,
          "frame": 196,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 47,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.8,
          "frame": 196,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 44,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 9.8,
          "frame": 196,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 40,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.8,
          "frame": 196,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 39,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 9.8,
          "frame": 196,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 38,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 9.8,
          "frame": 196,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 37,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 9.8,
          "frame": 196,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 36,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.8,
          "frame": 196,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 35,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.8,
          "frame": 196,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 34,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 9.8,
          "frame": 196,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 34,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 9.8,
          "frame": 196,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 28,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 9.8,
          "frame": 196,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 27,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 9.8,
          "frame": 196,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 25,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 10.15,
      "events": [
        {
          "timeSec": 10.15,
          "frame": 203,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 92,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 10.15,
          "frame": 203,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 91,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 10.15,
          "frame": 203,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 79,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 10.15,
          "frame": 203,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 78,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 10.15,
          "frame": 203,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 76,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 10.15,
          "frame": 203,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 70,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 10.15,
          "frame": 203,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 69,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 10.15,
          "frame": 203,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 69,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 10.15,
          "frame": 203,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 57,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 10.15,
          "frame": 203,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 54,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 10.15,
          "frame": 203,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 53,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 10.15,
          "frame": 203,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 50,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 10.15,
          "frame": 203,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 49,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 10.15,
          "frame": 203,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 40,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 10.15,
          "frame": 203,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 39,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 10.15,
          "frame": 203,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 35,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 10.15,
          "frame": 203,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 34,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 10.15,
          "frame": 203,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 34,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 10.15,
          "frame": 203,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 33,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 10.15,
          "frame": 203,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 30,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 10.15,
          "frame": 203,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 30,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 10.15,
          "frame": 203,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 28,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 10.5,
      "events": [
        {
          "timeSec": 10.5,
          "frame": 210,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 90,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 10.5,
          "frame": 210,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 88,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 10.5,
          "frame": 210,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 87,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 10.5,
          "frame": 210,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 81,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 10.5,
          "frame": 210,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 79,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 10.5,
          "frame": 210,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 76,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 10.5,
          "frame": 210,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 71,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 10.5,
          "frame": 210,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 70,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 10.5,
          "frame": 210,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 68,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 10.5,
          "frame": 210,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 59,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 10.5,
          "frame": 210,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 49,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 10.5,
          "frame": 210,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 47,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 10.5,
          "frame": 210,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 43,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 10.5,
          "frame": 210,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 34,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 10.5,
          "frame": 210,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 34,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 10.5,
          "frame": 210,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 27,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 10.85,
      "events": [
        {
          "timeSec": 10.85,
          "frame": 217,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 92,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 10.85,
          "frame": 217,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 91,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 10.85,
          "frame": 217,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 88,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 10.85,
          "frame": 217,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 83,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 10.85,
          "frame": 217,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 79,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 10.85,
          "frame": 217,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 79,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 10.85,
          "frame": 217,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 77,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 10.85,
          "frame": 217,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 77,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 10.85,
          "frame": 217,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 70,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 10.85,
          "frame": 217,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 56,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 10.85,
          "frame": 217,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 49,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 10.85,
          "frame": 217,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 47,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 10.85,
          "frame": 217,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 44,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 10.85,
          "frame": 217,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 44,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 10.85,
          "frame": 217,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 43,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 10.85,
          "frame": 217,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 39,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 10.85,
          "frame": 217,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 33,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 10.85,
          "frame": 217,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 33,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 10.85,
          "frame": 217,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 31,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 10.85,
          "frame": 217,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 31,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 11.2,
      "events": [
        {
          "timeSec": 11.2,
          "frame": 224,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 92,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 11.2,
          "frame": 224,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 88,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 11.2,
          "frame": 224,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 81,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 11.2,
          "frame": 224,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 80,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 11.2,
          "frame": 224,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 80,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 11.2,
          "frame": 224,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 69,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 11.2,
          "frame": 224,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 68,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 11.2,
          "frame": 224,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 58,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 11.2,
          "frame": 224,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 56,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 11.2,
          "frame": 224,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 48,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 11.2,
          "frame": 224,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 47,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 11.2,
          "frame": 224,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 44,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 11.2,
          "frame": 224,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 41,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 11.2,
          "frame": 224,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 37,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 11.2,
          "frame": 224,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 37,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 11.2,
          "frame": 224,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 35,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 11.2,
          "frame": 224,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 33,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 11.2,
          "frame": 224,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 28,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 11.2,
          "frame": 224,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 25,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 11.55,
      "events": [
        {
          "timeSec": 11.55,
          "frame": 231,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 92,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 11.55,
          "frame": 231,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 90,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 11.55,
          "frame": 231,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 88,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 11.55,
          "frame": 231,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 86,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 11.55,
          "frame": 231,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 86,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 11.55,
          "frame": 231,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 82,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 11.55,
          "frame": 231,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 81,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 11.55,
          "frame": 231,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 78,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 11.55,
          "frame": 231,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 74,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 11.55,
          "frame": 231,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 61,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 11.55,
          "frame": 231,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 52,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 11.55,
          "frame": 231,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 48,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 11.55,
          "frame": 231,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 42,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 11.55,
          "frame": 231,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 40,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 11.55,
          "frame": 231,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 40,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 11.55,
          "frame": 231,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 39,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 11.55,
          "frame": 231,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 36,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 11.55,
          "frame": 231,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 35,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 11.55,
          "frame": 231,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 32,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 11.55,
          "frame": 231,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 32,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 11.55,
          "frame": 231,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 31,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 11.55,
          "frame": 231,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 31,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 11.55,
          "frame": 231,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 27,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 11.55,
          "frame": 231,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 27,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 11.55,
          "frame": 231,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 26,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 11.55,
          "frame": 231,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 25,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 11.9,
      "events": [
        {
          "timeSec": 11.9,
          "frame": 238,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 89,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 11.9,
          "frame": 238,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 88,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 11.9,
          "frame": 238,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 87,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 11.9,
          "frame": 238,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 83,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 11.9,
          "frame": 238,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 83,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 11.9,
          "frame": 238,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 79,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 11.9,
          "frame": 238,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 77,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 11.9,
          "frame": 238,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 77,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 11.9,
          "frame": 238,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 74,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 11.9,
          "frame": 238,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 64,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 11.9,
          "frame": 238,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 57,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 11.9,
          "frame": 238,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 57,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 11.9,
          "frame": 238,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 56,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 11.9,
          "frame": 238,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 51,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 11.9,
          "frame": 238,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 39,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 11.9,
          "frame": 238,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 37,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 11.9,
          "frame": 238,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 37,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 11.9,
          "frame": 238,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 36,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 11.9,
          "frame": 238,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 34,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 11.9,
          "frame": 238,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 33,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 11.9,
          "frame": 238,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 30,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 11.9,
          "frame": 238,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 25,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 12.25,
      "events": [
        {
          "timeSec": 12.25,
          "frame": 245,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 90,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 12.25,
          "frame": 245,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 89,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 12.25,
          "frame": 245,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 89,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 12.25,
          "frame": 245,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 85,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 12.25,
          "frame": 245,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 84,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 12.25,
          "frame": 245,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 81,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 12.25,
          "frame": 245,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 80,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 12.25,
          "frame": 245,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 70,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 12.25,
          "frame": 245,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 59,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 12.25,
          "frame": 245,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 54,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 12.25,
          "frame": 245,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 52,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 12.25,
          "frame": 245,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 44,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 12.25,
          "frame": 245,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 41,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 12.25,
          "frame": 245,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 37,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 12.25,
          "frame": 245,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 36,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 12.25,
          "frame": 245,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 33,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 12.25,
          "frame": 245,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 33,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 12.25,
          "frame": 245,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 32,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 12.25,
          "frame": 245,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 30,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 12.25,
          "frame": 245,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 30,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 12.25,
          "frame": 245,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 27,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 12.25,
          "frame": 245,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 26,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 12.6,
      "events": [
        {
          "timeSec": 12.6,
          "frame": 252,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 89,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 12.6,
          "frame": 252,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 88,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 12.6,
          "frame": 252,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 87,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 12.6,
          "frame": 252,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 85,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 12.6,
          "frame": 252,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 74,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 12.6,
          "frame": 252,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 73,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 12.6,
          "frame": 252,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 64,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 12.6,
          "frame": 252,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 57,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 12.6,
          "frame": 252,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 51,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 12.6,
          "frame": 252,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 42,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 12.6,
          "frame": 252,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 41,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 12.6,
          "frame": 252,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 37,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 12.6,
          "frame": 252,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 37,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 12.6,
          "frame": 252,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 35,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 12.6,
          "frame": 252,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 27,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 12.6,
          "frame": 252,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 26,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 12.6,
          "frame": 252,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 26,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 12.6,
          "frame": 252,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 25,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 12.6,
          "frame": 252,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 25,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 12.6,
          "frame": 252,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 25,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 12.6,
          "frame": 252,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 25,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 12.95,
      "events": [
        {
          "timeSec": 12.95,
          "frame": 259,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 91,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 12.95,
          "frame": 259,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 89,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 12.95,
          "frame": 259,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 81,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 12.95,
          "frame": 259,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 79,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 12.95,
          "frame": 259,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 70,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 12.95,
          "frame": 259,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 70,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 12.95,
          "frame": 259,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 65,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 12.95,
          "frame": 259,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 58,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 12.95,
          "frame": 259,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 57,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 12.95,
          "frame": 259,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 53,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 12.95,
          "frame": 259,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 51,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 12.95,
          "frame": 259,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 50,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 12.95,
          "frame": 259,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 34,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 12.95,
          "frame": 259,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 33,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 12.95,
          "frame": 259,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 30,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 12.95,
          "frame": 259,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 28,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 12.95,
          "frame": 259,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 28,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 12.95,
          "frame": 259,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 27,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 12.95,
          "frame": 259,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 26,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 12.95,
          "frame": 259,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 25,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 13.3,
      "events": [
        {
          "timeSec": 13.3,
          "frame": 266,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 90,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 13.3,
          "frame": 266,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 89,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 13.3,
          "frame": 266,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 88,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 13.3,
          "frame": 266,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 85,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 13.3,
          "frame": 266,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 76,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 13.3,
          "frame": 266,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 62,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 13.3,
          "frame": 266,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 53,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 13.3,
          "frame": 266,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 51,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 13.3,
          "frame": 266,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 40,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 13.3,
          "frame": 266,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 34,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 13.3,
          "frame": 266,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 31,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 13.3,
          "frame": 266,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 30,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 13.3,
          "frame": 266,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 30,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 13.3,
          "frame": 266,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 30,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 13.3,
          "frame": 266,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 30,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 13.3,
          "frame": 266,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 27,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 13.3,
          "frame": 266,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 27,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 13.3,
          "frame": 266,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 26,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 13.3,
          "frame": 266,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 25,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 13.65,
      "events": [
        {
          "timeSec": 13.65,
          "frame": 273,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 92,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 13.65,
          "frame": 273,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 90,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 13.65,
          "frame": 273,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 90,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 13.65,
          "frame": 273,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 85,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 13.65,
          "frame": 273,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 79,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 13.65,
          "frame": 273,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 66,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 13.65,
          "frame": 273,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 60,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 13.65,
          "frame": 273,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 53,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 13.65,
          "frame": 273,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 47,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 13.65,
          "frame": 273,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 41,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 13.65,
          "frame": 273,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 40,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 13.65,
          "frame": 273,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 37,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 13.65,
          "frame": 273,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 36,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 13.65,
          "frame": 273,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 35,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 13.65,
          "frame": 273,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 29,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 13.65,
          "frame": 273,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 28,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 13.65,
          "frame": 273,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 26,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 13.65,
          "frame": 273,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 25,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 14.0,
      "events": [
        {
          "timeSec": 14.0,
          "frame": 280,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 93,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 14.0,
          "frame": 280,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 88,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 14.0,
          "frame": 280,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 82,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 14.0,
          "frame": 280,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 79,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 14.0,
          "frame": 280,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 64,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 14.0,
          "frame": 280,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 63,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 14.0,
          "frame": 280,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 59,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 14.0,
          "frame": 280,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 38,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 14.0,
          "frame": 280,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 37,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 14.0,
          "frame": 280,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 33,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 14.0,
          "frame": 280,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 33,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 14.0,
          "frame": 280,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 32,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 14.0,
          "frame": 280,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 32,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 14.0,
          "frame": 280,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 29,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 14.0,
          "frame": 280,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 28,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 14.0,
          "frame": 280,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 27,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 14.0,
          "frame": 280,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 26,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 14.0,
          "frame": 280,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 25,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 14.35,
      "events": [
        {
          "timeSec": 14.35,
          "frame": 287,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 94,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 14.35,
          "frame": 287,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 87,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 14.35,
          "frame": 287,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 85,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 14.35,
          "frame": 287,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 84,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 14.35,
          "frame": 287,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 83,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 14.35,
          "frame": 287,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 71,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 14.35,
          "frame": 287,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 63,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 14.35,
          "frame": 287,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 62,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 14.35,
          "frame": 287,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 58,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 14.35,
          "frame": 287,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 45,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 14.35,
          "frame": 287,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 41,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 14.35,
          "frame": 287,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 35,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 14.35,
          "frame": 287,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 34,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 14.35,
          "frame": 287,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 30,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 14.35,
          "frame": 287,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 30,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 14.35,
          "frame": 287,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 27,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 14.35,
          "frame": 287,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 26,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 14.7,
      "events": [
        {
          "timeSec": 14.7,
          "frame": 294,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 94,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 14.7,
          "frame": 294,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 88,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 14.7,
          "frame": 294,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 85,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 14.7,
          "frame": 294,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 81,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 14.7,
          "frame": 294,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 79,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 14.7,
          "frame": 294,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 76,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 14.7,
          "frame": 294,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 76,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 14.7,
          "frame": 294,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 71,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 14.7,
          "frame": 294,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 55,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 14.7,
          "frame": 294,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 48,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 14.7,
          "frame": 294,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 47,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 14.7,
          "frame": 294,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 43,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 14.7,
          "frame": 294,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 42,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 14.7,
          "frame": 294,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 40,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 14.7,
          "frame": 294,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 39,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 14.7,
          "frame": 294,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 38,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 14.7,
          "frame": 294,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 32,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 14.7,
          "frame": 294,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 30,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 14.7,
          "frame": 294,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 28,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 14.7,
          "frame": 294,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 25,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 14.7,
          "frame": 294,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 25,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 14.7,
          "frame": 294,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 25,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        }
      ]
    }
  ],
  "traffic3": [
    {
      "timeSec": 0.0,
      "events": [
        {
          "timeSec": 0.0,
          "frame": 0,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 25,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 0.67,
      "events": [
        {
          "timeSec": 0.67,
          "frame": 16,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 30,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 1.0,
      "events": [
        {
          "timeSec": 1.0,
          "frame": 24,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 35,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 1.33,
      "events": [
        {
          "timeSec": 1.33,
          "frame": 32,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 37,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 1.67,
      "events": [
        {
          "timeSec": 1.67,
          "frame": 40,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 44,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 3.0,
      "events": [
        {
          "timeSec": 3.0,
          "frame": 72,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 36,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 3.0,
          "frame": 72,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 26,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 3.33,
      "events": [
        {
          "timeSec": 3.33,
          "frame": 80,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 82,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 3.67,
      "events": [
        {
          "timeSec": 3.67,
          "frame": 88,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 71,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 5.33,
      "events": [
        {
          "timeSec": 5.33,
          "frame": 128,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 26,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 5.67,
      "events": [
        {
          "timeSec": 5.67,
          "frame": 136,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 41,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 5.67,
          "frame": 136,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 27,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    }
  ],
  "traffic4": [
    {
      "timeSec": 0.33,
      "events": [
        {
          "timeSec": 0.33,
          "frame": 8,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 47,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 0.67,
      "events": [
        {
          "timeSec": 0.67,
          "frame": 16,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 35,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 1.0,
      "events": [
        {
          "timeSec": 1.0,
          "frame": 24,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 33,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 1.33,
      "events": [
        {
          "timeSec": 1.33,
          "frame": 32,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 69,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 2.0,
      "events": [
        {
          "timeSec": 2.0,
          "frame": 48,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 34,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 2.67,
      "events": [
        {
          "timeSec": 2.67,
          "frame": 64,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 30,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 3.0,
      "events": [
        {
          "timeSec": 3.0,
          "frame": 72,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 29,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 3.33,
      "events": [
        {
          "timeSec": 3.33,
          "frame": 80,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 38,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 3.33,
          "frame": 80,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 26,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 3.67,
      "events": [
        {
          "timeSec": 3.67,
          "frame": 88,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 36,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 4.0,
      "events": [
        {
          "timeSec": 4.0,
          "frame": 96,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 65,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 4.0,
          "frame": 96,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 59,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 4.33,
      "events": [
        {
          "timeSec": 4.33,
          "frame": 104,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 32,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 4.67,
      "events": [
        {
          "timeSec": 4.67,
          "frame": 112,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 59,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 4.67,
          "frame": 112,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 57,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 5.0,
      "events": [
        {
          "timeSec": 5.0,
          "frame": 120,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 84,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 5.0,
          "frame": 120,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 26,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 5.33,
      "events": [
        {
          "timeSec": 5.33,
          "frame": 128,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 33,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 5.33,
          "frame": 128,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 26,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 5.67,
      "events": [
        {
          "timeSec": 5.67,
          "frame": 136,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 67,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 5.67,
          "frame": 136,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 35,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 5.67,
          "frame": 136,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 31,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 5.67,
          "frame": 136,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 25,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    }
  ],
  "traffic5": [
    {
      "timeSec": 0.67,
      "events": [
        {
          "timeSec": 0.67,
          "frame": 16,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 32,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 2.67,
      "events": [
        {
          "timeSec": 2.67,
          "frame": 64,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 25,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 4.0,
      "events": [
        {
          "timeSec": 4.0,
          "frame": 96,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 35,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 4.33,
      "events": [
        {
          "timeSec": 4.33,
          "frame": 104,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 75,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 4.67,
      "events": [
        {
          "timeSec": 4.67,
          "frame": 112,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 92,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    }
  ],
  "traffic6": [
    {
      "timeSec": 1.0,
      "events": [
        {
          "timeSec": 1.0,
          "frame": 24,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 37,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 2.67,
      "events": [
        {
          "timeSec": 2.67,
          "frame": 64,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 81,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 2.67,
          "frame": 64,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 51,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 3.0,
      "events": [
        {
          "timeSec": 3.0,
          "frame": 72,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 56,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 3.0,
          "frame": 72,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 30,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 3.33,
      "events": [
        {
          "timeSec": 3.33,
          "frame": 80,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 85,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 3.33,
          "frame": 80,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 75,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 3.67,
      "events": [
        {
          "timeSec": 3.67,
          "frame": 88,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 79,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 3.67,
          "frame": 88,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 34,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 4.0,
      "events": [
        {
          "timeSec": 4.0,
          "frame": 96,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 79,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 4.33,
      "events": [
        {
          "timeSec": 4.33,
          "frame": 104,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 66,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 4.33,
          "frame": 104,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 48,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 4.67,
      "events": [
        {
          "timeSec": 4.67,
          "frame": 112,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 36,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 5.33,
      "events": [
        {
          "timeSec": 5.33,
          "frame": 128,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 73,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 5.67,
      "events": [
        {
          "timeSec": 5.67,
          "frame": 136,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 75,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 5.67,
          "frame": 136,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 35,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        },
        {
          "timeSec": 5.67,
          "frame": 136,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 27,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        }
      ]
    }
  ],
  "traffic7": [
    {
      "timeSec": 2.33,
      "events": [
        {
          "timeSec": 2.33,
          "frame": 56,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 31,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 3.67,
      "events": [
        {
          "timeSec": 3.67,
          "frame": 88,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 29,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 4.0,
      "events": [
        {
          "timeSec": 4.0,
          "frame": 96,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 30,
          "lane": "Lane 3",
          "note": "Lane 3 \u2022 Active Flow"
        }
      ]
    }
  ],
  "traffic8": [
    {
      "timeSec": 0.67,
      "events": [
        {
          "timeSec": 0.67,
          "frame": 16,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 27,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 1.0,
      "events": [
        {
          "timeSec": 1.0,
          "frame": 24,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 25,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 1.33,
      "events": [
        {
          "timeSec": 1.33,
          "frame": 32,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 43,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 1.33,
          "frame": 32,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 30,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 1.67,
      "events": [
        {
          "timeSec": 1.67,
          "frame": 40,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 42,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 1.67,
          "frame": 40,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 31,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 2.0,
      "events": [
        {
          "timeSec": 2.0,
          "frame": 48,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 78,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 2.0,
          "frame": 48,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 30,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 2.0,
          "frame": 48,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 27,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 2.0,
          "frame": 48,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 25,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 2.33,
      "events": [
        {
          "timeSec": 2.33,
          "frame": 56,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 90,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 2.33,
          "frame": 56,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 30,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 2.33,
          "frame": 56,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 26,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 2.67,
      "events": [
        {
          "timeSec": 2.67,
          "frame": 64,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 90,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 3.0,
      "events": [
        {
          "timeSec": 3.0,
          "frame": 72,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 93,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 3.0,
          "frame": 72,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 66,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 3.0,
          "frame": 72,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 34,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 3.0,
          "frame": 72,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 31,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 3.33,
      "events": [
        {
          "timeSec": 3.33,
          "frame": 80,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 90,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 3.33,
          "frame": 80,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 67,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 3.67,
      "events": [
        {
          "timeSec": 3.67,
          "frame": 88,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 47,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 4.0,
      "events": [
        {
          "timeSec": 4.0,
          "frame": 96,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 60,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 4.33,
      "events": [
        {
          "timeSec": 4.33,
          "frame": 104,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 87,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 4.33,
          "frame": 104,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 29,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 4.67,
      "events": [
        {
          "timeSec": 4.67,
          "frame": 112,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 81,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 5.0,
      "events": [
        {
          "timeSec": 5.0,
          "frame": 120,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 72,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 5.0,
          "frame": 120,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 48,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 5.0,
          "frame": 120,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 46,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 5.33,
      "events": [
        {
          "timeSec": 5.33,
          "frame": 128,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 68,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 5.33,
          "frame": 128,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 45,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 5.33,
          "frame": 128,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 39,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    }
  ],
  "traffic9": [
    {
      "timeSec": 0.33,
      "events": [
        {
          "timeSec": 0.33,
          "frame": 8,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 26,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 0.67,
      "events": [
        {
          "timeSec": 0.67,
          "frame": 16,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 25,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 1.0,
      "events": [
        {
          "timeSec": 1.0,
          "frame": 24,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 63,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 1.0,
          "frame": 24,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 25,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 1.33,
      "events": [
        {
          "timeSec": 1.33,
          "frame": 32,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 82,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 1.33,
          "frame": 32,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 34,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 1.33,
          "frame": 32,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 33,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 1.67,
      "events": [
        {
          "timeSec": 1.67,
          "frame": 40,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 64,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 2.33,
      "events": [
        {
          "timeSec": 2.33,
          "frame": 56,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 53,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 2.67,
      "events": [
        {
          "timeSec": 2.67,
          "frame": 64,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 68,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 2.67,
          "frame": 64,
          "event": "brts_intrusion",
          "objectClass": "car",
          "confidence": 38,
          "lane": "BRTS Corridor",
          "note": "\u26a0\ufe0f Corridor Intrusion \u2022 BRTS Corridor"
        },
        {
          "timeSec": 2.67,
          "frame": 64,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 34,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 3.0,
      "events": [
        {
          "timeSec": 3.0,
          "frame": 72,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 81,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 3.0,
          "frame": 72,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 81,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 3.0,
          "frame": 72,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 53,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 3.0,
          "frame": 72,
          "event": "brts_intrusion",
          "objectClass": "car",
          "confidence": 26,
          "lane": "BRTS Corridor",
          "note": "\u26a0\ufe0f Corridor Intrusion \u2022 BRTS Corridor"
        }
      ]
    },
    {
      "timeSec": 3.33,
      "events": [
        {
          "timeSec": 3.33,
          "frame": 80,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 81,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 3.33,
          "frame": 80,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 64,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 3.33,
          "frame": 80,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 45,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 3.67,
      "events": [
        {
          "timeSec": 3.67,
          "frame": 88,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 80,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 3.67,
          "frame": 88,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 29,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 4.0,
      "events": [
        {
          "timeSec": 4.0,
          "frame": 96,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 73,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 4.0,
          "frame": 96,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 57,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 4.0,
          "frame": 96,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 39,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 4.33,
      "events": [
        {
          "timeSec": 4.33,
          "frame": 104,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 94,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        },
        {
          "timeSec": 4.33,
          "frame": 104,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 31,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 4.67,
      "events": [
        {
          "timeSec": 4.67,
          "frame": 112,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 78,
          "lane": "Lane 2",
          "note": "Lane 2 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 5.0,
      "events": [
        {
          "timeSec": 5.0,
          "frame": 120,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 85,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 5.0,
          "frame": 120,
          "event": "brts_intrusion",
          "objectClass": "car",
          "confidence": 25,
          "lane": "BRTS Corridor",
          "note": "\u26a0\ufe0f Corridor Intrusion \u2022 BRTS Corridor"
        }
      ]
    },
    {
      "timeSec": 5.33,
      "events": [
        {
          "timeSec": 5.33,
          "frame": 128,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 50,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 5.67,
      "events": [
        {
          "timeSec": 5.67,
          "frame": 136,
          "event": "brts_intrusion",
          "objectClass": "car",
          "confidence": 51,
          "lane": "BRTS Corridor",
          "note": "\u26a0\ufe0f Corridor Intrusion \u2022 BRTS Corridor"
        }
      ]
    }
  ],
  "traffic_demo": [
    {
      "timeSec": 0.35,
      "events": [
        {
          "timeSec": 0.35,
          "frame": 7,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 44,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 0.7,
      "events": [
        {
          "timeSec": 0.7,
          "frame": 14,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 47,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 0.7,
          "frame": 14,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 44,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 0.7,
          "frame": 14,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 26,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 0.7,
          "frame": 14,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 26,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 1.05,
      "events": [
        {
          "timeSec": 1.05,
          "frame": 21,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 53,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 1.05,
          "frame": 21,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 28,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 1.75,
      "events": [
        {
          "timeSec": 1.75,
          "frame": 35,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 55,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 1.75,
          "frame": 35,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 46,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 1.75,
          "frame": 35,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 39,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 1.75,
          "frame": 35,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 32,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 1.75,
          "frame": 35,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 27,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 2.1,
      "events": [
        {
          "timeSec": 2.1,
          "frame": 42,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 34,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 2.1,
          "frame": 42,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 32,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 2.1,
          "frame": 42,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 29,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 2.45,
      "events": [
        {
          "timeSec": 2.45,
          "frame": 49,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 61,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 2.45,
          "frame": 49,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 52,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 2.45,
          "frame": 49,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 40,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 2.8,
      "events": [
        {
          "timeSec": 2.8,
          "frame": 56,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 40,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 2.8,
          "frame": 56,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 33,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 2.8,
          "frame": 56,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 31,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 3.15,
      "events": [
        {
          "timeSec": 3.15,
          "frame": 63,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 44,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 3.15,
          "frame": 63,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 31,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 3.15,
          "frame": 63,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 27,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 3.5,
      "events": [
        {
          "timeSec": 3.5,
          "frame": 70,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 67,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 3.5,
          "frame": 70,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 51,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 3.5,
          "frame": 70,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 35,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 3.5,
          "frame": 70,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 30,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 3.85,
      "events": [
        {
          "timeSec": 3.85,
          "frame": 77,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 31,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 4.2,
      "events": [
        {
          "timeSec": 4.2,
          "frame": 84,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 48,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 4.2,
          "frame": 84,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 47,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 4.2,
          "frame": 84,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 32,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 4.2,
          "frame": 84,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 31,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 4.2,
          "frame": 84,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 29,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 4.55,
      "events": [
        {
          "timeSec": 4.55,
          "frame": 91,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 49,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 4.55,
          "frame": 91,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 36,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 4.55,
          "frame": 91,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 29,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 4.55,
          "frame": 91,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 26,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 4.9,
      "events": [
        {
          "timeSec": 4.9,
          "frame": 98,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 51,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 4.9,
          "frame": 98,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 32,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 4.9,
          "frame": 98,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 31,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 4.9,
          "frame": 98,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 29,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 4.9,
          "frame": 98,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 25,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 5.25,
      "events": [
        {
          "timeSec": 5.25,
          "frame": 105,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 79,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 5.25,
          "frame": 105,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 45,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 5.25,
          "frame": 105,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 41,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 5.25,
          "frame": 105,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 36,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 5.25,
          "frame": 105,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 32,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 5.25,
          "frame": 105,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 32,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 5.25,
          "frame": 105,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 27,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 5.6,
      "events": [
        {
          "timeSec": 5.6,
          "frame": 112,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 86,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 5.6,
          "frame": 112,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 52,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 5.6,
          "frame": 112,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 49,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 5.6,
          "frame": 112,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 42,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 5.6,
          "frame": 112,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 32,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 5.6,
          "frame": 112,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 32,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 5.6,
          "frame": 112,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 26,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 5.95,
      "events": [
        {
          "timeSec": 5.95,
          "frame": 119,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 51,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 5.95,
          "frame": 119,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 44,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 5.95,
          "frame": 119,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 39,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 5.95,
          "frame": 119,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 35,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 5.95,
          "frame": 119,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 31,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 5.95,
          "frame": 119,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 28,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 5.95,
          "frame": 119,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 26,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 6.3,
      "events": [
        {
          "timeSec": 6.3,
          "frame": 126,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 76,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 6.3,
          "frame": 126,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 42,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 6.3,
          "frame": 126,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 30,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 6.3,
          "frame": 126,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 29,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 6.3,
          "frame": 126,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 26,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 6.65,
      "events": [
        {
          "timeSec": 6.65,
          "frame": 133,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 57,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 6.65,
          "frame": 133,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 34,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 6.65,
          "frame": 133,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 30,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 6.65,
          "frame": 133,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 28,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 7.0,
      "events": [
        {
          "timeSec": 7.0,
          "frame": 140,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 49,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 7.0,
          "frame": 140,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 37,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 7.0,
          "frame": 140,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 35,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 7.0,
          "frame": 140,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 26,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 7.35,
      "events": [
        {
          "timeSec": 7.35,
          "frame": 147,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 44,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 7.35,
          "frame": 147,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 44,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 7.35,
          "frame": 147,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 43,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 7.35,
          "frame": 147,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 34,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 7.35,
          "frame": 147,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 30,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 7.35,
          "frame": 147,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 30,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 7.7,
      "events": [
        {
          "timeSec": 7.7,
          "frame": 154,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 71,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 7.7,
          "frame": 154,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 38,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 7.7,
          "frame": 154,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 37,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 7.7,
          "frame": 154,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 37,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 7.7,
          "frame": 154,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 30,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 7.7,
          "frame": 154,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 29,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 7.7,
          "frame": 154,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 25,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 8.05,
      "events": [
        {
          "timeSec": 8.05,
          "frame": 161,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 62,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 8.05,
          "frame": 161,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 42,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 8.05,
          "frame": 161,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 34,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 8.05,
          "frame": 161,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 33,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 8.05,
          "frame": 161,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 26,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 8.05,
          "frame": 161,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 25,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 8.4,
      "events": [
        {
          "timeSec": 8.4,
          "frame": 168,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 62,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 8.4,
          "frame": 168,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 35,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 8.4,
          "frame": 168,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 27,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 8.75,
      "events": [
        {
          "timeSec": 8.75,
          "frame": 175,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 66,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 8.75,
          "frame": 175,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 42,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 8.75,
          "frame": 175,
          "event": "vehicle_entry",
          "objectClass": "truck",
          "confidence": 32,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 8.75,
          "frame": 175,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 30,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 9.1,
      "events": [
        {
          "timeSec": 9.1,
          "frame": 182,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 63,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 9.1,
          "frame": 182,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 40,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 9.45,
      "events": [
        {
          "timeSec": 9.45,
          "frame": 189,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 91,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 9.45,
          "frame": 189,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 43,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 9.8,
      "events": [
        {
          "timeSec": 9.8,
          "frame": 196,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 59,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 9.8,
          "frame": 196,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 37,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 9.8,
          "frame": 196,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 31,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 10.15,
      "events": [
        {
          "timeSec": 10.15,
          "frame": 203,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 48,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 10.15,
          "frame": 203,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 39,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 10.5,
      "events": [
        {
          "timeSec": 10.5,
          "frame": 210,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 79,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 10.5,
          "frame": 210,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 43,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 10.5,
          "frame": 210,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 39,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 10.5,
          "frame": 210,
          "event": "vehicle_entry",
          "objectClass": "bus",
          "confidence": 29,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 10.85,
      "events": [
        {
          "timeSec": 10.85,
          "frame": 217,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 39,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 10.85,
          "frame": 217,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 34,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 10.85,
          "frame": 217,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 30,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 11.2,
      "events": [
        {
          "timeSec": 11.2,
          "frame": 224,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 27,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 11.2,
          "frame": 224,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 25,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 11.2,
          "frame": 224,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 25,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 11.55,
      "events": [
        {
          "timeSec": 11.55,
          "frame": 231,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 60,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 11.55,
          "frame": 231,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 57,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 11.9,
      "events": [
        {
          "timeSec": 11.9,
          "frame": 238,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 59,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 11.9,
          "frame": 238,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 46,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 11.9,
          "frame": 238,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 27,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 12.25,
      "events": [
        {
          "timeSec": 12.25,
          "frame": 245,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 32,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 12.25,
          "frame": 245,
          "event": "vehicle_entry",
          "objectClass": "two-wheeler",
          "confidence": 30,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 12.6,
      "events": [
        {
          "timeSec": 12.6,
          "frame": 252,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 38,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 12.95,
      "events": [
        {
          "timeSec": 12.95,
          "frame": 259,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 39,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 12.95,
          "frame": 259,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 35,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 12.95,
          "frame": 259,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 33,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 13.3,
      "events": [
        {
          "timeSec": 13.3,
          "frame": 266,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 63,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 13.3,
          "frame": 266,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 44,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 13.65,
      "events": [
        {
          "timeSec": 13.65,
          "frame": 273,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 40,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    },
    {
      "timeSec": 14.7,
      "events": [
        {
          "timeSec": 14.7,
          "frame": 294,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 42,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        },
        {
          "timeSec": 14.7,
          "frame": 294,
          "event": "vehicle_entry",
          "objectClass": "car",
          "confidence": 30,
          "lane": "Lane 1",
          "note": "Lane 1 \u2022 Active Flow"
        }
      ]
    }
  ]
};

export function getVideoKeyForFeed(feedIdOrJunction?: string | null): string {
  if (!feedIdOrJunction) return 'traffic3';
  const idStr = feedIdOrJunction.toUpperCase();
  if (idStr.includes('09') || idStr.includes('TRAFFIC9') || idStr.includes('MAJURA') || idStr.includes('M09')) return 'traffic9';
  if (idStr.includes('04') || idStr.includes('PIPLOD') || idStr.includes('P04')) return 'traffic4';
  if (idStr.includes('01') || idStr.includes('UDHNA') || idStr.includes('U01')) return 'traffic1';
  if (idStr.includes('02') || idStr.includes('RING') || idStr.includes('R02')) return 'traffic2';
  if (idStr.includes('03') || idStr.includes('ADAJAN') || idStr.includes('A03')) return 'traffic3';
  if (idStr.includes('05') || idStr.includes('VARACHHA') || idStr.includes('V05')) return 'traffic5';
  if (idStr.includes('06') || idStr.includes('KARGIL') || idStr.includes('K06')) return 'traffic6';
  if (idStr.includes('07') || idStr.includes('TEXTILE') || idStr.includes('T07')) return 'traffic7';
  if (idStr.includes('08') || idStr.includes('DELHI') || idStr.includes('D08')) return 'traffic8';
  return 'traffic3';
}

export function getRealDetectionsForVideoTime(videoKey: string, currentTimeSec: number): RealCheckpointEvent[] {
  const checkpoints = VIDEO_DETECTIONS[videoKey] || VIDEO_DETECTIONS['traffic3'] || [];
  if (checkpoints.length === 0) return [];

  let closest = checkpoints[0];
  let minDiff = Math.abs(closest.timeSec - currentTimeSec);
  for (const cp of checkpoints) {
    const diff = Math.abs(cp.timeSec - currentTimeSec);
    if (diff < minDiff) {
      minDiff = diff;
      closest = cp;
    }
  }
  return closest.events;
}
